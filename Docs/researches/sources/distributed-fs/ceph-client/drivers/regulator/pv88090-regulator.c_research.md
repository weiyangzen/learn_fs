# sources/distributed-fs/ceph-client/drivers/regulator/pv88090-regulator.c

Purpose: implements the PV88090 I2C regulator driver. It registers three buck regulators and two LDOs, supports buck mode/current-limit control, dynamically derives BUCK2/BUCK3 voltage ranges, and reports global VDD fault and over-temperature events.

Important APIs/types/functions: `struct pv88090_regulator` wraps descriptors with buck mode/current config registers. `pv88090_buck_get_mode()` and `pv88090_buck_set_mode()` map register mode bits to regulator FAST/NORMAL/STANDBY. Descriptor macros build the regulator table. Probe reads BUCK2/3 `CONF2` and `BUCK_FOLD_RANGE` to select one of three voltage range definitions.

Control flow: probe allocates state, initializes regmap, optionally masks event banks, requests a low-triggered threaded IRQ, unmasks VDD fault and over-temperature events, then registers each regulator. During BUCK2/3 registration it computes a range index from VDAC range and gain bits, rewrites descriptor min/step/count, and registers the regulator.

State and persistence: descriptors live in a static mutable array and are modified at probe based on hardware range bits. Runtime state is otherwise devm-managed with no voltage cache. Optional platform data can feed regulator init data.

Dependencies and integration: depends on I2C, regmap, interrupts, regulator core, optional OF compatible `pvs,pv88090`, and register constants from `pv88090-regulator.h`.

Risks and test signals: static descriptor mutation has multi-instance risk. BUCK2/3 range index validation only accepts indexes up to the enum value for BUCK3, which happens to match the voltage table size but is semantically odd. Test dynamic range calculation, current-limit tables, LDO voltage ranges, IRQ paths, no-IRQ operation, and invalid range combinations.
