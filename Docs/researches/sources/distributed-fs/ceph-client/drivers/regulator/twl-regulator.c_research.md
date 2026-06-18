<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/twl-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/twl-regulator.c

Purpose: Implements TWL4030/TW5030/TPS659x0 regulator support for OMAP-era PMICs, including adjustable LDOs, fixed LDOs, VDD1/VDD2 SMPS rails, power-resource group control, and state-machine mode changes.

Important APIs and types: `struct twlreg_info` combines PM receiver base register, resource ID, VSEL table, remap value, descriptor, feature flags, and board data. `twlreg_read()` and `_write()` access TWL I2C modules. `twl4030reg_enable()`, `_disable()`, `_is_enabled()`, `_set_mode()`, and `_get_status()` manipulate P1/P2/P3 group and power-bus state. Table-driven LDO ops reject unsupported VSEL entries unless `TWL4030_ALLOW_UNSUPPORTED` is set.

Control flow: Probe obtains OF match data, reads regulator init data, copies the immutable template, clamps valid modes and operations, marks critical supplies always-on, registers the regulator, then writes the default `VREG_REMAP`. SMPS voltage is programmed through the TWL4030 SMPS voltage register; LDOs use table-indexed selectors.

State and persistence: Per-rail static templates define register bases and tables; probe creates a mutable copy per platform device. Hardware state persists in PMIC registers, especially DEV_GRP, VREG_REMAP, and voltage fields.

Dependencies and integration points: Depends on the TWL MFD I2C APIs, OF compatible strings for each rail, regulator machine constraints, and OMAP board descriptions.

Risks: DEV_GRP writes assume no other agent concurrently updates group bits. Unsupported table values map to zero volts in list operations, so consumers must handle holes. Power-bus mode writes can time out and only affect P1. Critical rails are forced always-on by the driver.

Test signals: OF matching for all TWL4030/TWL5030 compatibles, unsupported VSEL rejection, P1 enable/disable transitions, power-bus timeout handling, remap register writes, always-on constraint enforcement, and VDD1/VDD2 voltage selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/twl-regulator.c -->
