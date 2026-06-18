# sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/voltage.c

Purpose: This file implements the SCMI Voltage protocol agent. It discovers voltage domains and supported levels, exposes config get/set and level get/set operations, and supports asynchronous voltage level changes when firmware advertises them.

Important APIs/types/functions: `struct voltage_info` stores domain count and the domain array. `struct scmi_voltage_info` is populated for consumers with domain ID, name, levels, segmented flag, negative-voltage allowance, and async-level-set support. Iterator helpers `iter_volt_levels_prepare_message()`, `iter_volt_levels_update_state()`, and `iter_volt_levels_process_response()` parse `VOLTAGE_DESCRIBE_LEVELS`. Protocol ops are `num_domains_get`, `info_get`, `config_set`, `config_get`, `level_set`, and `level_get`.

Control flow: Init reads protocol attributes to get domain count, allocates domain descriptors, and loops over domains. For each domain it sends `VOLTAGE_DOMAIN_ATTRIBUTES`, stores name and flags, optionally fetches extended name, notes async support, then retrieves voltage levels through the iterator. Level descriptors can be a list or segmented triplet; invalid descriptors cause the domain to have zero levels. Config set masks config to low 4 bits. Level set uses synchronous xfer unless the domain supports async and mode is `SCMI_VOLTAGE_LEVEL_SET_AUTO`, in which case it waits for a delayed response and validates the returned domain ID.

State and persistence: Domain metadata and level arrays are devm-managed runtime state. Actual voltage configuration and level are firmware/hardware state. No persistent kernel storage is used.

Dependencies and integration points: It depends on SCMI core xfer and iterator helpers, public voltage protocol types, extended-name helper, and protocol registration as `SCMI_PROTOCOL_VOLTAGE`. Regulator or power clients consume `scmi_voltage_proto_ops`.

Risks and edge cases: Segmented descriptors must return exactly three entries in one response; otherwise the domain is invalidated. Negative voltage values are accepted and flagged. Per-domain attribute xfer errors are skipped with rx reset, so domains can remain default/invalid without failing whole init. `__scmi_voltage_get_u32()` requests rx size 0 but reads `t->rx.buf`, which relies on core behavior and merits testing. Async completion validates domain ID but only logs voltage level.

Test signals: Test no domains, listed vs segmented levels, invalid descriptor counts, extended names, negative values, config mask behavior, sync and async level set, delayed response wrong domain ID, invalid domain IDs, and level get/config get response sizing.
