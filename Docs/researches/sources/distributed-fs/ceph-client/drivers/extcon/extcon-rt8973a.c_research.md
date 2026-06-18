# sources/distributed-fs/ceph-client/drivers/extcon/extcon-rt8973a.c

## Purpose
Richtek RT8973A MUIC extcon provider for USB switch, OTG, charger, and JIG detection over I2C. It programs default MUIC control registers, registers a regmap IRQ chip, classifies ADC/DEV1 values, switches DM/DP routing, and publishes USB, USB host, DCP, SDP, and JIG states.

## Important APIs, Types, and Functions
`struct rt8973a_muic_info` owns I2C/regmap, regmap IRQ data, IRQ flags, register initialization table, auto-config flag, mutex, extcon, and delayed cold-plug work. `rt8973a_muic_set_path()` writes `RT8973A_REG_MANUAL_SW1` unless auto-config mode is enabled. `rt8973a_muic_get_cable_type()` reads ADC and DEV1 to disambiguate USB and TA when ADC is open. `rt8973a_muic_cable_handler()` handles attach, detach, OVP, and OTP events, maps cable types to extcon IDs and switch routes, and updates extcon. `rt8973a_init_dev_type()` logs version/vendor, writes initialization data, and detects auto-configuration mode.

## Control Flow
Probe requires OF, allocates state, initializes regmap, adds a two-register regmap IRQ chip, maps/request all logical IRQs, registers extcon, schedules delayed attach detection, and initializes hardware. IRQ handlers map virtual IRQs to logical RT8973A interrupts, set one of `irq_attach`, `irq_detach`, `irq_ovp`, or `irq_otp`, and schedule work. Work serializes under mutex and calls the cable handler for each pending event. Detach/OVP/OTP reuse the previous cable type, while attach reads ADC/DEV1 live.

## State and Persistence
Hardware setup persists in CONTROL1 and MANUAL_SW1. `auto_config` suppresses manual path writes when hardware auto switching is enabled. IRQ flags are per-device fields, but `prev_cable_type` inside `rt8973a_muic_cable_handler()` is a function-static variable shared by all driver instances. That is persistent for the module lifetime and not per device.

## Dependencies and Integration Points
Uses extcon provider, I2C, regmap, regmap IRQ, threaded IRQs, OF match, and PM wake IRQ toggling. Register constants come from `extcon-rt8973a.h`.

## Risks
The function-static `prev_cable_type` can cross-contaminate detach state if more than one RT8973A exists. Probe error paths after `regmap_add_irq_chip()` do not remove the IRQ chip unless remove later runs, so failures during virtual IRQ/extcon registration may leak IRQ-chip setup. Delayed work is not explicitly canceled in remove. Many accessory classes are logged and ignored, so consumer expectations must match the limited extcon set. OVP/OTP forcibly detach the previous extcon state but do not publish a separate fault signal.

## Test Signals
Test ADC OTG, TA, USB via DEV1, JIG USB/UART, open/no cable, attach/detach ordering, OVP/OTP forced detach, auto-config enabled and disabled, suspend/resume wake IRQs, failed ADC/DEV1 reads, and multiple-instance behavior if supported by the platform.
