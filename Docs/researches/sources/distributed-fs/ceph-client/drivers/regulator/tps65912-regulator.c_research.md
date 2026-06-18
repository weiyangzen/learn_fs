# sources/distributed-fs/ceph-client/drivers/regulator/tps65912-regulator.c

Purpose: Platform child regulator driver for TPS65912 PMICs with four DCDC regulators and ten LDO regulators.

Important APIs/types/functions: `TPS65912_REGULATOR` builds descriptors with OF names, selector register, enable register, 6-bit selector mask, and linear ranges. DCDC ops use generic regmap enable/disable/get/set/list helpers. LDO ops add linear range voltage mapping.

Control flow: probe gets the parent `struct tps65912`, sets platform driver data, prepares config with parent OF node and regmap, and registers all 14 descriptors. There is no custom runtime state or parsing beyond descriptor metadata; per-regulator init comes from regulator-core OF matching through `of_match` names under `regulators`.

State and persistence: enable and voltage state lives in the parent PMIC registers. The driver holds no mutable per-regulator private state after registration.

Dependencies and integration points: TPS65912 MFD, platform device ID `tps65912-regulator`, regulator core, regmap, and OF regulator child nodes.

Risks: DCDC ops do not provide `map_voltage`, so consumer mapping support differs from LDOs. All descriptors assume 64 selectors and common enable bit 7. Probe aborts on the first registration failure and does not register a partial set.

Test signals: registration of all 14 rails, DCDC/LDO selector boundaries, OF child matching, parent regmap failures, and consumer behavior for DCDC voltage mapping without explicit `map_voltage`.
