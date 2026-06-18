# sources/distributed-fs/ceph-client/drivers/regulator/max77802-regulator.c

Purpose: registers MAX77802 buck and LDO regulators, preserving operating modes across enable/suspend operations and exposing ramp tables for DVS-capable bucks.

Important APIs/types/functions: `struct max77802_regulator_prv` stores an `opmode` shadow indexed by regulator ID. `max77802_get_opmode_shift()`, `max77802_set_suspend_disable()`, `max77802_set_mode()`, `max77802_get_mode()`, `max77802_set_suspend_mode()`, and `max77802_enable()` implement mode semantics. Descriptor macros encode separate LDO logic groups and buck families.

Control flow: platform probe gets the parent MAX77686-compatible MFD regmap, allocates private state, reads each regulator's current enable register to seed `opmode`, normalizes hardware OFF to normal for warm reboot cases, and registers all descriptors.

State and persistence: opmode shadow state is important because disabling for suspend changes future enable behavior. Hardware registers contain actual voltage, enable, and ramp settings.

Dependencies and integration: depends on MAX77686/MAX77802 MFD definitions, DT binding IDs, platform child binding, OF regulator nodes, and regulator core suspend/mode/ramp helpers.

Risks and test signals: unsupported suspend-mode transitions deliberately warn and return success in some cases to avoid blocking other regulators. Descriptor count and `MAX77802_REG_MAX` must stay aligned. Test boot readback fallback, OFF-to-normal warm reboot handling, LDO logic groups, buck ramp masks, and mode mapping through OF.
