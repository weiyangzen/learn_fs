# sources/distributed-fs/ceph-client/drivers/regulator/tps65218-regulator.c

Purpose: Platform child regulator driver for TPS65218 PMIC voltage rails and LS2/LS3 current-limited load switches.

Important APIs/types/functions: `TPS65218_REGULATOR` builds descriptors with voltage selector, enable, current-limit, suspend bypass, ramp, and fixed-voltage metadata. Ops are split for DCDC1/2, DCDC3/4/LDO1, LS2/LS3 current regulators, and fixed DCDC5/6. Custom helpers perform protected enable/disable, voltage changes with GO bit, suspend sequencing, and current limit selection.

Control flow: probe prepares config from parent MFD, allocates `tps->strobes`, registers all descriptors, reads each bypass register, and stores default strobe bits. Voltage setting writes protected VSEL and triggers slew GO for DCDC1/2. Current limit ops choose exact input limit or largest supported value within requested min/max. Suspend disable preserves DCDC3 on revision 2.1 and applies a fallback strobe for DCDC3 when absent.

State and persistence: hardware registers store voltage, enable, current limit, and sequence bits. Driver stores original strobe fields on the parent object.

Dependencies and integration points: TPS65218 MFD, regmap, regulator core, OF matching through descriptor names, protected register helper API, and platform device IDs.

Risks: descriptors for current regulators have zero/unused voltage fields and must only use current ops. Revision-specific DCDC3 behavior prevents poweroff reboot issues and should not regress. Reading bypass register 0 for LS descriptors relies on harmless regmap behavior.

Test signals: DCDC1/2 voltage GO, revision 2.1 DCDC3 suspend behavior, current limit exact/range selection, fixed DCDC5/6 enable-only operation, and strobe restore error paths.
