## sources/distributed-fs/ceph-client/include/linux/mfd/da9062/registers.h

Purpose: This header defines the DA9062AA/DA9061-compatible PMIC device IDs, variant IDs, paged register addresses, and bitfields used by the DA9062 core and children.

Important APIs, types, and constants: IDs define device, metal revision, and variant revision values plus I2C page-select shift. Register constants span page/status/fault/event/IRQ masks, controls A-F, power-down disable, GPIO controls/modes/output/wakeup, four buck controls, four LDO controls, dynamic voltage control, RTC counters/alarms/seconds, sequencer state and step IDs, wait/32 kHz/reset, buck current limits/configs, A/B buck and LDO voltage registers, backup battery charger, interface/config registers, trim, GP IDs, and device/variant/customer/config IDs. Bitfields define page/write/revert, status/event/mask bits, power/watchdog/RTC/shutdown/debounce controls, GPIO modes, regulator enables/GPI/voltage selections/configs, RTC and alarm fields, sequencer steps, buck current/mode/voltage sleep bits, backup charger current/voltage, interface base address, PM/IRQ voltage/type fields, auto modes, shutdown/delay/reset behavior, oscillator trim/frequency, and identity masks.

Control flow: No code executes in the header. The core and child drivers use these definitions with regmap to detect the PMIC variant, configure events/IRQs, program regulators and DVC A/B selections, manage RTC/alarm/tick, sequence power rails, and configure GPIO/wakeup behavior.

State and persistence: Hardware state includes fault logs, event latches, power sequencing, regulator A/B sets, RTC counters, backup charger configuration, trim, GP IDs, and identity/config registers. RTC and selected fault/config registers can persist across low-power states depending on supply domains.

Dependencies and integration points: Paired with `da9062/core.h`; used by regulator, RTC, watchdog, onkey, GPIO, hwmon, and MFD core code. Relies on Linux `BIT` macros via including source.

Risks: Paged addresses above `0x100` require correct regmap paging. DA9061/DA9062 share much of the table but not all events/children. Field names use `AA` silicon suffix throughout and some mixed-case names (`nONKEY`) that must be preserved for compatibility.

Test signals: Regmap paging tests, identity/variant readback, IRQ mask/event mapping, regulator voltage and DVC A/B selection tests, RTC alarm/tick handling, GPIO wake/mode/output programming, sequencer step configuration, and backup battery charger settings.
