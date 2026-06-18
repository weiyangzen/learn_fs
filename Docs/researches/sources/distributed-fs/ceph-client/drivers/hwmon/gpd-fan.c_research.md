# sources/distributed-fs/ceph-client/drivers/hwmon/gpd-fan.c

## Purpose
`gpd-fan.c` provides hwmon fan RPM and PWM control for selected GPD handheld and mini-PC systems whose embedded controller exposes fan registers through legacy I/O ports. It maps a normalized `pwm1` range of `0..255` onto board-specific EC ranges and supports automatic/manual/disabled modes.

## Important APIs, Types, and Functions
`struct gpd_fan_drvdata` describes a board: module name, board enum, address/data ports, EC offsets, and max PWM. Global `gpd_driver_priv` stores current PWM mode/value and matched board data. The DMI table maps product names to board data, while `gpd_fan_board` allows module-param override. `gpd_ecram_read()` and `gpd_ecram_write()` perform raw EC port I/O. Board-specific helpers implement RPM reads, PWM scaling, dual-register Duo writes, Win Max 2 control-enable behavior, and Win 4 EC initialization. `gpd_fan_hwmon_read()` and `gpd_fan_hwmon_write()` are the hwmon callbacks.

## Control Flow
Module init first matches the override string, then DMI. If matched, it initializes global state to automatic mode and creates a bundled platform device with an I/O resource covering the address/data ports. Probe requests that region, registers the hwmon device with one fan and one PWM channel, and runs board-specific EC initialization. Hwmon reads dispatch by sensor type: RPM reads board EC offsets, `pwm1_enable` returns cached mode, and `pwm1` either returns cached/manual values or reads hardware depending on board. Writes validate ranges, update global state, and then program EC registers when mode permits.

## State and Persistence
Driver state is module-global, assuming only one supported GPD fan controller. PWM mode/value are cached in RAM. Hardware EC writes persist until firmware, reboot, or driver removal changes them. Remove forces automatic mode before unregistering.

## Dependencies and Integration Points
The driver depends on DMI matching, raw x86 I/O port access, platform resources, and the hwmon callback API. It has no ACPI/WMI abstraction; all board knowledge is encoded in local tables and EC offsets.

## Risks
Global state would not support multiple devices. Raw EC I/O is board-sensitive; a wrong DMI match or module override can write unintended EC offsets. There is no mutex around global state or EC access, so concurrent sysfs reads/writes can interleave. Some automatic-mode `pwm1` reads return `-EOPNOTSUPP` by design. Switching to manual sets cached PWM to full speed for safety, which can surprise tests expecting preservation.

## Test Signals
Test DMI and override matching, request-region failure, PWM mode transitions, invalid range handling, board-specific scaling, removal restoring automatic mode, concurrent sysfs access, and Win 4 initialization only on the intended board.
