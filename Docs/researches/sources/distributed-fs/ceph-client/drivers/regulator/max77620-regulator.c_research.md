# sources/distributed-fs/ceph-client/drivers/regulator/max77620-regulator.c

Purpose: implements regulators for MAX77620, MAX20024, and MAX77663 PMICs. It covers SD buck and LDO rails, flexible power sequencer slots, power modes, ramp rates, active discharge, and suspend/resume FPS reconfiguration.

Important APIs/types/functions: `struct max77620_regulator_info` describes per-rail registers and masks; `struct max77620_regulator_pdata` stores DT-derived FPS and mode options; `struct max77620_regulator` tracks active FPS sources and current/enable power modes. Key helpers include `max77620_regulator_set_fps_src()`, `max77620_regulator_set_fps_slots()`, `max77620_regulator_set_power_mode()`, `max77620_init_pmic()`, and `max77620_of_parse_cb()`.

Control flow: platform probe selects a static rail table by parent chip ID, reuses the parent OF node, initializes per-rail defaults, reads current slew rates, and registers all supported rails. The OF parse callback applies per-rail FPS, power-ok, and ramp settings during registration. PM sleep callbacks switch to suspend FPS slots/sources and restore active settings on resume.

State and persistence: driver state shadows current power mode, enable mode, active FPS source, and per-rail policy. Hardware registers persist programmed power sequencing and voltage settings.

Dependencies and integration: integrates the MAX77620 MFD regmap, OF regulator nodes, regulator core mode/ramp helpers, and PM sleep ops.

Risks and test signals: rails under FPS control report enabled and software enable/disable becomes a no-op. Error returns in suspend/resume helper calls are ignored. Test all three chip tables, SD4 omission on MAX77620, FPS default readback, invalid mode rejection, ramp override behavior, and suspend/resume register updates.
