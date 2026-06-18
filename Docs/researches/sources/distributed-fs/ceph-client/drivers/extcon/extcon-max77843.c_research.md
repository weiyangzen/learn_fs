# sources/distributed-fs/ceph-client/drivers/extcon/extcon-max77843.c

## Purpose
MAX77843 MUIC extcon provider for micro-USB accessory, charger, dock, MHL, JIG, and USB host/device detection. It is a platform child of the MAX77843/MAX77693-style MFD and creates a secondary MUIC I2C client/regmap plus a regmap IRQ chip. Its public kernel-facing output is an `extcon_dev` advertising USB, USB host, SDP/CDP/DCP/fast/slow chargers, MHL, dock, and JIG.

## Important APIs, Types, and Functions
`struct max77843_muic_info` owns the device, parent MFD pointer, extcon device, mutex, IRQ work, delayed initial detect work, last status register snapshot, previous ADC/charger/ground classifications, and pending IRQ flags. The register model is `max77843_muic_regmap_config`, `max77843_muic_irq[]`, and `max77843_muic_irq_chip`. `max77843_muic_set_path()` switches CONTROL1 COM routing and CONTROL2 low-power/charge-pump bits. `max77843_charger_set_otg_vbus()` drives charger OTG/boost mode for USB host. `max77843_muic_get_cable_type()` classifies ADC, charger, and ground-special cables while preserving previous type for detach. Handler functions split policy into ADC ground, JIG, dock, generic ADC, and charger cases. Probe initializes the MUIC regmap, registers extcon, disables auto detection, configures debounce, requests virtual IRQs, and schedules delayed cold-plug detection.

## Control Flow
Probe allocates `max77843_muic_info`, initializes a dummy MUIC I2C client at `I2C_ADDR_MUIC`, creates a regmap, adds a three-register IRQ chip, disables USB/factory auto mode, registers extcon, sets ADC debounce to 25 ms, and reads the current status for possible UART JIG path setup. It then maps every MUIC IRQ to a virtual IRQ and registers `max77843_muic_irq_handler()`. IRQ handlers only set `irq_adc` or `irq_chg` and schedule `irq_work`. `max77843_muic_irq_work()` locks, bulk-reads STATUS1-3, dispatches ADC and charger handlers, clears the pending flags, and unlocks. The delayed cold-plug worker runs after 15 seconds, reads the same status registers, and invokes ADC and charger handlers for already-attached cables.

## State and Persistence
Runtime state is in hardware registers and volatile in-memory fields. `prev_cable_type`, `prev_chg_type`, and `prev_gnd_type` are used to report correct detach events after an open/no-charger reading. `status[]` is a cached bulk-read of STATUS registers during work execution. The driver persists no configuration outside hardware register writes; suspend/resume handling is absent here.

## Dependencies and Integration Points
Depends on Linux extcon provider APIs, I2C/regmap/regmap-irq, workqueues, platform driver core, MAX77843/MAX77693 MFD definitions, and the charger regmap. It integrates with consumers through extcon state and with the parent MFD through `dev_get_drvdata(pdev->dev.parent)`, `max77843->irq`, `max77843->regmap_chg`, and `max77843->irq_data_muic`.

## Risks
The probe path ignores the return from disabling auto detection and from debounce setup, which can hide partial hardware initialization. Error paths manually unregister the dummy I2C client and IRQ chip, so ordering matters. IRQ work reports unused ADC accessory classes as errors/EAGAIN, which can be noisy on boards with unsupported accessories. Host OTG VBUS is controlled through charger mode bits, so misclassification can affect power delivery. There is no explicit cancellation of the delayed cold-plug work in remove.

## Test Signals
Useful signals are MUIC device ID logs, `CONTROL1/CONTROL2` debug logs, extcon uevents for USB/USB_HOST/charger/MHL/dock/JIG, successful virtual IRQ mapping, and attach/detach behavior for ADC ground, SmartDock, JIG USB/UART, SDP/CDP/DCP, special chargers, and MHL with/without VBUS. Fault injection should cover failed regmap reads/writes, missing virtual IRQs, and detach paths that rely on previous type fields.
