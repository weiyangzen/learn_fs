# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/discovery.h

## Purpose
This header defines AMDGPU's packed firmware discovery-table ABI. It describes PSP discovery binaries, per-die IP discovery records, harvested-IP metadata, graphics-core capability tables, VCN feature fuses, MALL information, and NPS memory-partition ranges.

## Important APIs, Types, And Data
Top-level constants identify binary and table signatures: `BINARY_SIGNATURE`, `DISCOVERY_TABLE_SIGNATURE`, `GC_TABLE_ID`, `HARVEST_TABLE_SIGNATURE`, `VCN_INFO_TABLE_ID`, `MALL_INFO_TABLE_ID`, and `NPS_INFO_TABLE_ID`. `enum table` indexes the legacy fixed table list.

`struct table_info`, `struct binary_header`, and `struct binary_header_v2` describe discovery binary layout. V2 adds `num_tables` and a counted flexible `table_list`. `struct ip_discovery_header` describes the IP table, including per-die offsets and a version-4 flag that tells consumers whether IP base addresses are 64-bit. `struct ip`, `struct ip_v3`, and `struct ip_v4` represent versioned IP entries with flexible base-address arrays and endian-sensitive bitfields for harvest/variant/sub-revision.

`struct gc_info_v1_0` through `gc_info_v2_1` record graphics topology and cache parameters. `harvest_table` records disabled IP instances. `mall_info_v1_0` and `mall_info_v2_0` report MALL capacity/configuration. `vcn_info_v1_0` reports per-instance codec-disable fuse bits. `nps_info_v1_0` reports NPS type and up to twelve base/limit address ranges.

## Control Flow
This file has no functions, but its layout drives `amdgpu_discovery.c`. That code validates the binary, locates table offsets, walks dies and IP entries, interprets 32-bit versus 64-bit base arrays, applies harvest data, and imports GC/MALL/VCN/NPS records into `adev` capability structures.

## State And Persistence
The structures are views over firmware-provided binary data. Parsed values persist in `adev->discovery`, IP-version tables, harvest masks, graphics topology, video capabilities, MALL properties, and NPS ranges. The header itself has no mutable state, but its packed field layout is persistent ABI with PSP/discovery firmware.

## Dependencies And Integration Points
It relies on fixed-width integer types, `DECLARE_FLEX_ARRAY`, `__counted_by`, `#pragma pack(1)`, and endian macros. Integration is centered on `amdgpu/amdgpu_discovery.c`, which consumes these records during probe and uses the result to select IP block implementations, register bases, feature masks, and topology-dependent resource limits.

## Risks
Packing, flexible-array sizing, and endian-sensitive bitfields are critical. A wrong field size or version branch can mis-parse firmware data, causing missing IP blocks, wrong register bases, incorrect harvest masks, or unsafe feature enablement. `binary_header_v2` has a variable table count, so validation must bound offsets and sizes before dereferencing. `ip_v4` can hold either 32-bit or 64-bit base addresses depending on the discovery header flag; treating it as the wrong width corrupts iteration.

## Test Signals
Test with discovery binaries across legacy header, V2 header, IP table versions, single-die and multi-die devices, 32-bit and 64-bit base-address modes, harvested configurations, and GC/MALL/VCN/NPS table variants. Probe logs, `amdgpu_discovery` debug output, IP block versions, harvested instance masks, register-base setup, VCN codec exposure, and memory-partition reporting are key signals.
