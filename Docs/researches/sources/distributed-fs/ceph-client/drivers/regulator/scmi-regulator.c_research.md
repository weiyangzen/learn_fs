<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/scmi-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/scmi-regulator.c

Purpose: exposes ARM SCMI Voltage Protocol domains as Linux regulators. It maps SCMI voltage-domain metadata and DT `regulators` child nodes into fixed, linear, or discrete regulator descriptors.

Important APIs/types/functions: global `voltage_ops` holds SCMI voltage protocol operations. `struct scmi_regulator` owns the SCMI domain id, protocol handle, OF node, descriptor, config, and registered regulator. `scmi_reg_enable()`, `scmi_reg_disable()`, and `scmi_reg_is_enabled()` wrap SCMI `config_set/get`. `scmi_reg_get_voltage_sel()` and `scmi_reg_set_voltage_sel()` translate between SCMI absolute microvolts and regulator selectors. `scmi_config_linear_regulator_mappings()` and `scmi_config_discrete_regulator_mappings()` build descriptor voltage maps from firmware-reported levels.

Control flow: probe gets the SCMI voltage protocol, queries domain count, allocates a slot array for all domains, scans the SCMI platform node's `regulators` child for entries with a `reg` domain number, rejects duplicate or out-of-range mappings, then initializes and registers each valid domain. Initialization skips domains that support negative voltages, names the descriptor from firmware, sets OF matching to the full child node name, selects fixed/linear/table ops, and stores driver data. Remove drops OF node references.

State and persistence: software state is a per-domain descriptor/config and OF node reference. Persistent regulator state is owned by SCMI firmware; Linux only sends on/off and level commands through the protocol. No local caching of voltage or enable state is kept.

Dependencies and integration: depends on the SCMI bus, voltage protocol, OF regulator children, and regulator framework. It integrates with firmware-defined voltage domains rather than direct hardware registers, so supported operations are intentionally limited to enable state and voltage level.

Risks and test signals: the file-scoped `voltage_ops` pointer is shared, which assumes one effective SCMI voltage ops table. Firmware can provide malformed ranges; negative intervals are rejected but zero step in a nonzero linear range would be dangerous if firmware allowed it. Registration failures are skipped rather than aborting all domains. Test fixed, linear, and discrete domains; negative-voltage skip; duplicate `reg` entries; out-of-range domain IDs; SCMI command failures; remove path OF reference balancing; and DT nodes whose full names must match descriptor OF matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/scmi-regulator.c -->
