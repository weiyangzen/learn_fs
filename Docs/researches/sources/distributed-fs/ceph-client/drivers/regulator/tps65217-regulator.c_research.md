# sources/distributed-fs/ceph-client/drivers/regulator/tps65217-regulator.c

Purpose: Platform child regulator driver for TPS65217 PMIC DCDC1-3 and LDO1-4 rails.

Important APIs/types/functions: descriptor macro `TPS65217_REGULATOR` defines voltage tables/ranges, enable masks, selector registers, and suspend bypass/strobe registers. Custom ops wrap TPS65217 password-protected set/clear helpers for enable, disable, set voltage, and suspend sequencing. LDO1 uses a table; other adjustable regulators use linear ranges.

Control flow: probe obtains parent MFD and optional board data, allocates `tps->strobes`, registers all regulators with parent regmap and driver data, reads each bypass register, and stores default strobe bits. Voltage setting writes protected selector bits and sets the GO bit for DCDC1-3. Suspend disable restores stored strobe sequencing, while suspend enable clears the bypass mask.

State and persistence: voltage/enable/suspend bits live in parent registers. Driver stores initial strobe values so suspend operations can restore board sequencing. All writes use PMIC protection levels.

Dependencies and integration points: TPS65217 MFD, regmap, regulator core, OF descriptor matching, and legacy board init data.

Risks: protected writes must use the correct level; selector writes for DCDCs require GO bit or voltage may not transition. If stored strobe is zero, suspend-disable returns `-EINVAL`. The probe reads bypass registers even for every descriptor, so invalid bypass metadata would break registration.

Test signals: protected enable/disable paths, DCDC GO bit, LDO1 table vs linear regulators, suspend enable/disable with stored strobes, and parent regmap read/write failures.
