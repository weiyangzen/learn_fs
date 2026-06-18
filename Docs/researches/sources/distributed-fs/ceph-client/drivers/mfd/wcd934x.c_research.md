# sources/distributed-fs/ceph-client/drivers/mfd/wcd934x.c

## Purpose
`wcd934x.c` is the SLIMbus MFD core for Qualcomm WCD9340/WCD934x audio codec devices. It manages supplies, reset, external clock, SLIMbus regmap creation, interrupt mapping, basic bring-up sequencing, and MFD child creation for codec, GPIO, and SoundWire functionality.

## Important APIs, Types, And Functions
Child cells are `wcd934x-codec`, `wcd934x-gpio`, and `wcd934x-soundwire`. IRQ metadata is built with `WCD934X_REGMAP_IRQ_REG()` and `wcd934x_irqs[]`, then exposed through `wcd934x_regmap_irq_chip`. Register access is controlled by `wcd934x_is_volatile_register()`, `wcd934x_ranges[]`, and `wcd934x_regmap_config`. Lifecycle functions are `wcd934x_slim_probe()`, `wcd934x_slim_status()`, `wcd934x_slim_status_up()`, `wcd934x_slim_remove()`, and `wcd934x_bring_up()`.

## Control Flow
SLIMbus probe allocates `struct wcd934x_ddata`, gets the first OF IRQ, obtains `extclk`, gets and enables five regulators, waits for buck/SIDO outputs, obtains optional reset GPIO low, waits, drives reset high, stores `ddata`, and returns. Actual register access waits for SLIMbus device status `SLIM_DEVICE_STATUS_UP`: `wcd934x_slim_status_up()` initializes a SLIMbus regmap with windowed range config, reads/logs chip ID bytes, performs a fixed RPM/reset/power sequence with a 1 ms VOUT settle delay, adds a regmap IRQ chip on the parent IRQ, and registers children. Status `DOWN` removes MFD children.

## State, Persistence, And Dependencies
State includes `ddata->regmap`, IRQ number/data, regulator handles, `extclk`, and device pointer. Hardware state includes enabled supplies, reset GPIO, RPM/reset/power registers written by bring-up, regmap IRQ masks/clears, and volatile status/MBHC/SoundWire bridge registers. Dependencies include SLIMbus device status callbacks, regmap SLIMbus support, regmap range windows through selector registers, regmap IRQ type configuration, regulators, optional reset GPIO, OF IRQ parsing, clocks, and WCD934x register definitions.

## Integration Points
The codec, GPIO, and SoundWire child devices are created only after the SLIMbus device reports `UP`, so children can assume regmap access works. The regmap IRQ chip maps SLIMbus, headphone PA over-current, MBHC insertion/button, and SoundWire interrupts across four status/mask/clear registers and supports both-edge type configuration through a shared config base. The range config maps logical 16-bit registers through WCD934x window selector registers.

## Risks
In the IRQ error path of probe, `dev_err_probe(ddata->dev, ...)` is called before `ddata->dev` is assigned, which is a likely NULL-device bug; it should use local `dev`. `regulator_bulk_get()` is not devm-managed and the successful probe path relies on remove for cleanup. If `wcd934x_slim_status_up()` fails after `regmap_init_slimbus()`, the regmap is not explicitly freed because it is not devm-initialized. `wcd934x_bring_up()` ignores return values from its fixed `regmap_write()` sequence after chip ID reads. Status `DOWN` removes children but does not delete the devm regmap IRQ chip. Probe obtains `extclk` but does not prepare/enable it in this file.

## Test Signals
Tests should cover probe with missing IRQ, clock deferral/failure, regulator get/enable failure, reset GPIO failure, and successful reset timing. SLIMbus status tests should transition UP and DOWN, verifying regmap creation, chip ID log, bring-up writes, IRQ chip registration, and child creation/removal. IRQ tests should trigger MBHC, SoundWire, and PA fault bits with rising/falling type configuration. Register tests should exercise windowed range access and volatile MBHC/SoundWire bridge/status registers. Failure-injection should target bring-up writes and child-add errors to detect leaked regmap/IRQ state.
