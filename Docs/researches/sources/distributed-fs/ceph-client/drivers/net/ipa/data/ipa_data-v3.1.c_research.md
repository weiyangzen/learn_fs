# sources/distributed-fs/ceph-client/drivers/net/ipa/data/ipa_data-v3.1.c

## Purpose
`ipa_data-v3.1.c` is the static SoC data description for Qualcomm IPA hardware version 3.1. It defines endpoint/GSI channel topology, resource group limits, IPA-local memory layout, QSB parameters, interconnect bandwidths, and power data used by the generic IPA driver.

## Important APIs, types, and functions
The file exports `const struct ipa_data ipa_data_v3_1`. Supporting static data includes `ipa_qsb_data`, `ipa_gsi_endpoint_data`, `ipa_resource_src`, `ipa_resource_dst`, `ipa_resource_data`, `ipa_mem_local_data`, `ipa_mem_data`, `ipa_interconnect_data`, and `ipa_power_data`. Local enums define IPA v3.1 source/destination resource types and group IDs.

## Control flow
There is no executable algorithm. Runtime IPA selection code uses `ipa_data_v3_1` to size and program endpoints, configure resources, map IPA-resident memory regions, request interconnect bandwidth, set core clock rate, and apply a backward-compatibility flag. Endpoint entries describe AP command, LAN RX, AP modem TX/RX, and modem-owned endpoints with GSI EE/channel/endpoint IDs and endpoint configuration such as aggregation, QMAP, checksum, DMA mode, status, and filter support.

## State and persistence
All data is compile-time constant. At runtime it becomes the authoritative configuration for IPA v3.1 hardware but is not modified or persisted by this file.

## Dependencies and integration points
The file depends on IPA core headers for endpoint IDs, memory IDs, sequence types, resource structures, version IDs, and compatibility flags. It is linked through the IPA Makefile and selected by core version matching.

## Risks and test signals
Risks are incorrect table constants: endpoint IDs, channel/event ring sizes, resource min/max limits, memory offsets/canaries, IMEM/SMEM sizes, interconnect names, or clock rate errors can break modem/AP data path setup. Test signals include build-time structure initialization checks, IPA v3.1 probe on target SoCs, endpoint bring-up, AP/modem traffic, QMAP/checksum/status behavior, resource programming validation, memory canary checks, and interconnect/clock vote verification.
