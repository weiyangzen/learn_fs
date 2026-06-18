<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-nct6694.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-nct6694.c

## Purpose
USB/MFD-backed GPIO driver for the Nuvoton NCT6694. It registers one eight-line GPIO chip per allocated hardware group, supports direction, input/output values, open-drain versus push-pull output config, valid-line masks, and nested edge IRQs.

## Important APIs, types, and functions
`struct nct6694_gpio_data` holds the parent `struct nct6694`, chip, locks, cached byte value, rising/falling trigger masks, group, and parent IRQ. GPIO callbacks are `nct6694_get_direction()`, `nct6694_direction_input()`, `nct6694_direction_output()`, `nct6694_get_value()`, `nct6694_set_value()`, `nct6694_set_config()`, and `nct6694_init_valid_mask()`. IRQ handling uses `nct6694_irq_handler()`, `nct6694_irq_set_type()`, mask/unmask, and bus lock/sync.

## Control flow
Each operation builds an `nct6694_cmd_header` with module `NCT6694_GPIO_MOD` and a group-relative register offset, then uses `nct6694_read_msg()` or `nct6694_write_msg()`. Direction and output updates are read-modify-write sequences under `data->lock`. `get_value()` chooses `GPO_DATA` for output lines and `GPI_DATA` for input lines after reading direction. The threaded parent IRQ reads `GPI_STS`, dispatches mapped child IRQs, and writes `GPI_CLR`.

## State and persistence behavior
The driver keeps cached rising/falling IRQ trigger bytes and temporary register bytes; direction and data state live in hardware. Trigger masks are initialized from hardware during probe and later written during bus sync. Group allocation is lifetime-managed by devm actions.

## Dependencies and integration points
Depends on the NCT6694 MFD command API, parent GPIO IDA, parent irqdomain, gpiolib, pinconf, threaded IRQs, and platform binding `nct6694-gpio`.

## Risks and edge cases
Transport failures propagate to GPIO callers. `can_sleep = false` is risky if the USB command path sleeps. `irq_set_type()` ORs trigger bits without clearing prior edge selections, so type changes may leave stale masks. IRQ clear failures are ignored.

## Test signals
Probe, valid-mask contents, direction round trips, output/input register selection, drive mode config, all edge IRQs, and repeated IRQ type changes are the key tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-nct6694.c -->
