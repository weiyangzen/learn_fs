# sources/distributed-fs/ceph-client/drivers/input/misc/tps6594-pwrbutton.c

## Purpose
`tps6594-pwrbutton.c` reports TI TPS6594 PMIC push and release interrupts as `KEY_POWER`. It is structurally similar to the TPS65219 power-button driver but without local PMIC register setup.

## Important APIs, Types, and Functions
`struct tps6594_pwrbutton` stores device/input and phys string. `tps6594_pb_push_irq()` reports press and wakeup; `tps6594_pb_release_irq()` reports release. `tps6594_pb_probe()` allocates the input device, obtains two IRQs, requests threaded handlers, and registers the input device.

## Control Flow
Probe creates an I2C input device named from the platform device, enables `EV_KEY/KEY_POWER`, marks the device wake-capable, obtains IRQ 0 and IRQ 1, requests threaded `IRQF_ONESHOT` handlers using resource names, and registers input. Runtime flow is direct press/release event reporting.

## State and Persistence Behavior
No hardware registers are written. State consists of the input device and device pointer. Wake capability persists in the device core.

## Dependencies and Integration Points
Depends on TPS6594 MFD platform child resources, platform IDs, IRQ core, input core, and PM wakeup. It includes TPS6594 and regmap headers but does not use regmap directly.

## Risks and Edge Cases
Missing IRQs return `-EINVAL` rather than specific errors. Handler names use `pdev->resource[0/1].name`, so malformed platform resources can provide NULL or misleading names. There are no explicit wake IRQ suspend/resume ops. The driver assumes IRQ 0 is push and IRQ 1 is release.

## Test Signals
Test correct platform resources, press/release event delivery, missing/misordered IRQs, wake behavior provided by parent PMIC, input registration failure, and module bind/unbind.
