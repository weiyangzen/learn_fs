# sources/distributed-fs/ceph-client/drivers/regulator/tps65086-regulator.c

Purpose: Platform child regulator driver for TPS65086/TPS650864x PMIC families, registering bucks, LDOs, VTT, and load switches according to chip ID.

Important APIs/types/functions: `struct tps65086_regulator` wraps a `regulator_desc` plus decay register/mask. `struct tps65086_regulator_config` selects a per-chip descriptor array. `reg_ops` handles voltage regulators through linear ranges and regmap helpers; `switch_ops` handles load switches. `tps65086_of_parse_cb` applies DT options for 25 mV buck step size and decay mode.

Control flow: probe reads parent `struct tps65086`, maps parent chip ID to a descriptor array, stores it in `tps->reg_config`, prepares a regulator config with parent OF node and regmap, and registers every descriptor. During OF parsing, buck descriptors can have their linear range table replaced in-place for 25 mV mode; decay mode writes chip-specific decay bits.

State and persistence: descriptor arrays are static and mutated at parse time for step-size selection, so state can persist across probes in the same kernel image. Hardware state is in parent regmap enable, voltage, and decay registers.

Dependencies and integration points: TPS65086 MFD, platform device IDs, OF regulator child nodes, regmap, and regulator core.

Risks: static descriptor mutation can leak one board’s 25 mV selection into later instances if multiple devices differ. Unknown chip IDs fail probe. Decay writes happen during parse and can fail registration. Some variants omit SWB2 or use different enable registers.

Test signals: all chip IDs, 10 mV and 25 mV buck ranges, decay property success/failure, variant-specific regulator counts, switch enable bits, and multiple-instance descriptor mutation behavior.
