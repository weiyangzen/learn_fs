<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/twl6030-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/twl6030-regulator.c

Purpose: Provides the TWL6030/TWL6032 regulator driver split from the older TWL4030 implementation, covering TWL6030 LDOs/fixed supplies, TWL6032 LDOs, and TWL6032 SMPS rails.

Important APIs and types: `struct twlreg_info` stores PM receiver base, resource ID, flags, descriptor, and chip features. `twl6030reg_enable()`, `_disable()`, `_is_enabled()`, `_set_mode()`, and `_get_status()` program `VREG_STATE` differently for TWL6030 and TWL6032 subclass devices. `twl6030smps_list_voltage()` and `_map_voltage()` implement the non-linear SMPS selector map with offset and extended modes.

Control flow: Probe gets an OF template, reads regulator init data, copies the descriptor template, limits valid modes/ops, then inspects TWL6032 EPROM offset/multiplier registers for SMPS3, SMPS4, and VIO to set selector interpretation flags. The optional `ti,retain-on-reset` property sets the warm-reset write bit behavior before registration.

State and persistence: Hardware state is in PM receiver state and voltage registers plus SMPS EPROM offset/multiplier fields. Driver state is the per-device copy of flags and descriptor. Warm-reset retention changes how selector bit 7 is written and masked.

Dependencies and integration points: Depends on TWL MFD I2C access, OF regulator data, TWL class detection, and regulator core selector/mode APIs.

Risks: `twl_get_smps_offset()` and `_mult()` ignore I2C read errors, leaving undefined flag decisions on failures. Core SMPS VDD1/VDD2/VDD3 return `-ENODEV` for voltage operations. Non-linear SMPS maps have boundary-sensitive cases, including zero/off selector handling.

Test signals: TWL6030 and TWL6032 OF compatibles, SMPS offset/extended combinations, retain-on-reset writes, state/mode transitions, invalid voltage requests, fixed-rail constraints, and I2C read/write error injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/twl6030-regulator.c -->
