# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_data.h

Purpose: Defines the schema for IPA/GSI platform configuration data and declares all supported `struct ipa_data` descriptors. It is the common contract between Device Tree match data and the runtime IPA/GSI initialization code.

Important APIs/types: `IPA_RESOURCE_GROUP_MAX` bounds resource group arrays. `struct ipa_qsb_data` describes QSB outstanding request limits. `struct gsi_channel_data` defines TRE/event ring sizes and TLV FIFO depth. `struct ipa_endpoint_data` carries filtering support and endpoint config. `struct ipa_gsi_endpoint_data` binds EE ID, GSI channel ID, IPA endpoint ID, direction, channel data, and endpoint data. Resource, memory, interconnect, power, and top-level `struct ipa_data` aggregate those tables. Externs declare descriptors from v3.1 through v5.5.

Control flow and integration: Platform match code selects one `struct ipa_data`. IPA init consumes `endpoint_data` for endpoint maps and `gsi_init()`, `resource_data` for IPA resource programming, `mem_data` for local/IMEM/SMEM setup, `power_data` for clock/interconnect votes, QSB data for bus register programming, and `modem_route_count` for route table sizing.

State and persistence: This header defines immutable configuration structures. Runtime consumers keep pointers to static descriptors and program mutable hardware/driver state from them.

Dependencies: Includes Linux types and IPA endpoint, memory, and version headers. It is included by data files, GSI init, command code, and IPA core users.

Risks: Struct layout changes affect every version data file. Comments document deprecated IMEM fallback fields and version-specific fields such as `max_reads_beats` absence on v3.5.1 and `backward_compat` only before v4.5. Incorrect resource or endpoint schema interpretation can break all platforms.

Test signals: Build all data descriptors after schema changes. Probe each supported compatible to ensure tables validate. Static checks should confirm ring counts are powers of two, TLV counts fit, memory descriptors are non-overlapping, and final descriptors point at all required sub-tables.
