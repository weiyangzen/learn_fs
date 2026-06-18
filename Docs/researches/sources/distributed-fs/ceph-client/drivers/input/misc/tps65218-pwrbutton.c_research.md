# sources/distributed-fs/ceph-client/drivers/input/misc/tps65218-pwrbutton.c

## Purpose
`tps65218-pwrbutton.c` supports TI TPS65217 and TPS65218 PMIC power buttons. It reads variant-specific status registers on interrupt and reports `KEY_POWER`.

## Important APIs, Types, and Functions
`struct tps6521x_data` stores status register, button mask, and input name. `struct tps6521x_pwrbutton` stores device, regmap, input, data, and phys string. `tps6521x_pb_irq()` reads the status register, reports press or release, and calls `pm_wakeup_event()` on press. `tps6521x_pb_probe()` matches OF data, creates the input device, gets parent regmap, requests an edge-triggered threaded IRQ, and registers input.

## Control Flow
Probe selects TPS65217/TPS65218 data from OF, allocates state/input, configures an I2C input device, initializes wakeup, obtains IRQ 0, requests a rising/falling threaded IRQ, and registers input. The IRQ reads the PMIC status and reports key state based on the variant mask.

## State and Persistence Behavior
Persistent state is the regmap pointer, input device, and variant data. The driver does not write PMIC registers. Device wake capability is persistent in device core.

## Dependencies and Integration Points
Depends on TI TPS65217/TPS65218 MFD regmaps, OF compatibles, platform IRQs, input core, and PM wakeup. It also declares platform IDs for MFD child matching.

## Risks and Edge Cases
If `platform_get_irq()` fails, probe returns `-EINVAL` rather than the original error. `pwr->regmap` is not checked for NULL after `dev_get_regmap()`, so a missing parent regmap can crash in the IRQ. Regmap read failures are logged but still return `IRQ_HANDLED`. There are no suspend/resume IRQ wake hooks despite `device_init_wakeup()`.

## Test Signals
Test both PMIC variants, status mask polarity, missing regmap, missing IRQ, regmap read failures, press wake event, input event delivery, and platform/OF matching.
