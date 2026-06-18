# sources/distributed-fs/ceph-client/drivers/regulator/pfuze100-regulator.c

Purpose: supports Freescale/NXP PFUZE100, PFUZE200, PFUZE3000, and PFUZE3001 PMIC regulator variants over I2C. It selects variant-specific regulator tables, parses regulator DT nodes, handles ramp delay, optional switcher disable support, and optional system power-off preparation.

Important APIs/types/functions: `struct pfuze_regulator` extends `regulator_desc` with standby register/mask and switcher flag. `struct pfuze_chip` holds chip ID, flags, regmap, copied descriptors, registered regulators, and selected static table. Descriptor macros generate fixed, switcher, SWBST, VGEN, COIN, and PFUZE3000-specific regulators. `pfuze100_set_ramp_delay()` programs ramp bits; `pfuze_power_off_prepare()` changes PFUZE100 standby behavior for poweroff.

Control flow: probe determines chip type from OF or I2C ID, initializes regmap, validates identity and revision/fab registers, selects regulator table and switcher high-bit range, copies descriptors, parses DT, adjusts voltage ranges based on current selector high bits, optionally enables switcher disable semantics for old-DTB compatibility, registers every regulator, and optionally registers the power-off-prepare handler.

State and persistence: per-device descriptor copies are mutated for detected voltage range and optional disable support. The global `pfuze_matches` points at the active match table during probe. Power-off preparation writes PMIC standby mode registers.

Dependencies and integration: depends on I2C, OF, regmap, regulator framework, sys-off handlers, and `linux/regulator/pfuze100.h` IDs.

Risks and test signals: `pfuze_matches` is global, which is fragile for multiple PFUZE instances probing concurrently. Backward compatibility around `fsl,pfuze-support-disable-sw` must be preserved. Test each compatible, ID mismatch, high-bit voltage range selection, DT match ordering, switcher disable behavior, ramp delay, and PFUZE100-only power-off writes.
