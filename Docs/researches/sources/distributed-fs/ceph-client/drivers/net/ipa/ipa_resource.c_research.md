# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_resource.c

Purpose: programs IPA internal source and destination resource group limits from version-specific configuration data.

Important APIs/functions: `ipa_resource_config()` validates resource data and writes all source and destination resource type limits. Helpers split group pairs across `{SRC,DST}_RSRC_GRP_{01,23,45,67}_RSRC_TYPE` registers, encoding X/Y min/max limits.

Control flow: `ipa_config()` calls this after table and endpoint config. Validation ensures source and destination group counts are nonzero and at most eight, and that unsupported trailing groups have zero limits. For each resource type, group 0/1 are programmed first, then 2/3, 4/5, and 6/7 if supported.

State/persistence: no software state is retained. Register programming persists in hardware until reset/reconfiguration; there is intentionally no deconfig.

Dependencies/integration: depends on `ipa_data` resource tables, `IPA_RESOURCE_GROUP_MAX`, register metadata, and MMIO helpers. Endpoint configuration separately assigns each endpoint to a resource group.

Risks: group count and resource-type array sizes must match hardware/register table expectations. Wrong limits can starve endpoints or over-allocate scarce internal resources. No runtime verification reads the values back.

Test signals: `ipa_resource_config()` returns zero during probe, traffic does not stall under load, resource group registers match data-table expectations, and invalid nonzero limits beyond group count fail probe.
