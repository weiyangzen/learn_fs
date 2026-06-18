# sources/distributed-fs/ceph-client/drivers/gpio/gpio-wcove.c

## Purpose
Implements GPIO and nested IRQ support for the Intel Whiskey Cove PMIC. It exposes 94 logical GPIO numbers, with the first 13 backed by physical GPIO control registers and interrupts.

## Important APIs, Types, And Functions
- `struct wcove_gpio` stores regmap, regmap-IRQ data, GPIO chip, bus lock, and pending IRQ update fields.
- `to_reg` and `to_ireg` translate GPIO offsets to PMIC control, IRQ mask, and IRQ status registers.
- `wcove_gpio_dir_in`, `wcove_gpio_dir_out`, `wcove_gpio_get_direction`, `wcove_gpio_get`, `wcove_gpio_set`, and `wcove_gpio_set_config` implement GPIO operations.
- `wcove_irq_type`, `wcove_irq_mask`, `wcove_irq_unmask`, `wcove_bus_lock`, and `wcove_bus_sync_unlock` stage and commit IRQ type/mask changes.
- `wcove_gpio_irq_handler` reads two status registers, dispatches nested GPIO IRQs, and acks each handled bit.
- `wcove_gpio_dbg_show` reports direction, level, IRQ mask/status, and edge configuration.

## Control Flow
Probe obtains the parent `intel_soc_pmic`, platform IRQ, and regmap IRQ virtual IRQ, initializes a sleepable chip, installs an internal irqchip without a parent handler, requests a threaded handler for the PMIC IRQ, registers the gpiochip, and unmasks the PMIC GPIO interrupt groups. GPIO offsets beyond the 13 physical pins are accepted by the chip but most callbacks become no-ops or fixed outputs through `to_reg` returning `-ENOTSUPP`. IRQ type and mask operations record desired changes under the irq bus lock, then commit register writes in `bus_sync_unlock`.

## State And Persistence
Hardware registers hold direction, value, drive mode, interrupt detect mode, mask, and status. Software state in `update`, `intcnt`, and `set_irq_mask` batches one IRQ configuration transaction between lock and unlock. The PMIC parent owns regmap and regmap IRQ state.

## Dependencies And Integration Points
Depends on `intel_soc_pmic`, parent regmap, regmap IRQ mapping, gpiolib nested threaded IRQ support, debugfs seq output, and the platform device name `bxt_wcove_gpio`.

## Risks And Edge Cases
The advertised `ngpio` is 94 while only 13 physical pins have registers; consumers using virtual offsets get silent no-op behavior for many callbacks. `to_ireg` assumes the caller passes a physical GPIO. Pending IRQ batching uses a single set of fields, so only the current bus-locked line should be modified at a time. The threaded IRQ handler loops until status is clear and must avoid storms if ack writes fail.

## Test Signals
Test physical GPIO 0, 6, 7, and 12 register mapping, virtual GPIO offset behavior, drive open-drain/push-pull pinconf, all supported edge IRQ types, nested IRQ dispatch and ack, PMIC IRQ mapping failure, and debugfs output with register read failures.
