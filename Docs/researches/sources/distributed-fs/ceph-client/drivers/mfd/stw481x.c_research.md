# sources/distributed-fs/ceph-client/drivers/mfd/stw481x.c

## Purpose
`stw481x.c` is the I2C MFD core for STw4810/STw4811 PMICs. It reads power-control configuration, logs startup voltage/status information, creates a shared regmap, and registers the VMMC regulator child.

## Important APIs, Types, and Functions
`stw481x_get_pctl_reg()` accesses one-time-programmable power-control registers through split address bits in `STW_PCTL_REG_HI/LO` and verifies the selected address. `stw481x_startup()` reads configuration and voltage selector registers. `stw481x_probe()` allocates state, initializes the regmap, runs startup, and registers `stw481x-vmmc-regulator`.

## Control Flow
Probe creates an 8-bit regmap, validates readable startup state through several regmap reads, fills the child cell's platform data with the parent `struct stw481x`, and registers the regulator child through `devm_mfd_add_devices()`.

## State and Persistence
Parent state is the I2C client and regmap in `struct stw481x`. The driver reads OTP-backed power-control values but does not modify or persist them.

## Dependencies and Integration Points
It depends on I2C, regmap, `linux/mfd/stw481x.h`, and the child regulator driver. It is OF matched by `st,stw4810` and `st,stw4811`.

## Risks and Edge Cases
Power-control register access relies on write-then-read address latch behavior and returns `-EIO` if verification fails. The driver logs many status fields but does not correct unexpected configuration. Only non-USB register space is accessible through this path.

## Test Signals
Probe on both compatibles, successful power-control register verification, correct logged voltage selectors, regulator child registration, and failure behavior for I2C/regmap errors are key signals.
