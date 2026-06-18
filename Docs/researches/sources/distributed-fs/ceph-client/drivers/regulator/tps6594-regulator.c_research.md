<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/tps6594-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/tps6594-regulator.c

Purpose: Provides regulator-core registration for TPS6594, TPS6593, TPS65224, TPS652G1, and LP8764 PMIC rails, including buck, LDO, and supported multiphase buck configurations.

Important APIs and types: `struct tps6594_regulator_desc` selects per-chip descriptor tables, IRQ tables, and external monitor IRQ tables. `TPS6594_REGULATOR()` builds `struct regulator_desc` entries. Ops are mostly regmap helpers for enable, voltage select, linear-range mapping, bypass, and ramp timing. `tps6594_request_reg_irqs()` wires per-rail faults to regulator notifier events.

Control flow: Probe chooses the descriptor set from the parent MFD `chip_id`, scans regulator DT child names to detect multiphase buck nodes, marks constituent bucks as consumed, registers selected multiphase rails, registers remaining bucks, registers LDOs, then requests per-regulator and external monitor IRQs by name. IRQ handlers log the fault and call `regulator_notifier_call_chain()`.

State and persistence: Runtime state is in devm allocations for IRQ data and regulator devices. Persistent hardware state is PMIC register state accessed through the parent regmap. The multiphase detection state is probe-local booleans.

Dependencies and integration points: Depends on the TPS6594 MFD driver for `struct tps6594`, regmap, IRQ names, and chip IDs; on devicetree regulator nodes under `regulators`; and on regulator core consumers using named supplies.

Risks: DT node-name matching controls multiphase registration and may silently change which individual bucks are exposed. `of_find_node_by_name()` result handling assumes expected nodes exist. IRQ count allocation is based on per-rail counts and must match the tables. Chips with no IRQ tables, such as TPS652G1 here, intentionally skip notification support.

Test signals: Probe all chip IDs, single and multiphase buck DT layouts, missing or invalid IRQ names, voltage set/list paths for each range table, bypass on LDO1-3, external VCCA/VMON events, and notifier delivery for OV/UV/SC/ILIM events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/tps6594-regulator.c -->
