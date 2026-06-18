# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgv_sriovmsg.h

## Purpose
This header is an ABI definition for AMD GPU SR-IOV shared memory and mailbox communication between host PF and guest VF drivers. It fixes the layout, versions, offsets, packed structures, feature flags, telemetry buffers, mailbox messages, and compile-time size checks for PF2VF, VF2PF, VBIOS, bad-page, and RAS telemetry regions.

## Important APIs, types, and functions
The v1 layout macros define 64 KiB VBIOS, 1 KiB PF2VF, 1 KiB VF2PF, 2 KiB bad-page, and 64 KiB RAS telemetry areas, with offsets and total initialization-data size. `enum amd_sriov_crit_region_version` and `enum amd_sriov_msg_table_id_enum` model v1/v2 discovery, with v2 using an `amd_sriov_msg_init_data_header` that names offsets and sizes for dynamically allocated tables.

`AMD_SRIOV_MSG_FW_VRAM_PF2VF_VER` and `AMD_SRIOV_MSG_FW_VRAM_VF2PF_VER` declare the current PF2VF/VF2PF schema versions. `enum amd_sriov_ucode_engine_id` enumerates firmware engines carried in guest reports. Packed unions define host feature flags, VF register access flags, RAS capabilities, and guest OS flags.

`struct amd_sriov_msg_pf2vf_info` is the 1 KiB host-to-guest payload: checksum, feature flags, video limits, firmware offsets/sizes, bad-page info, update interval, UUID/function identity, register access flags, VCN bandwidth limits, PCIE atomic support, GPU capacity, host BDF, and RAS caps. `struct amd_sriov_msg_vf2pf_info` is the 1 KiB guest-to-host payload: checksum, driver/OS/certification info, FB and engine usage/health, required PF2VF version, firmware versions, dummy page, and MES info.

Mailbox enums define guest requests such as GPU init/fini/reset access, init data, PSP VF command relay, VF error logging, ready-to-reset, RAS poison/count/CPER/bad-page requests, and host responses such as access grants, FLR notifications, success/fail, alive query, init-data ready, RMA, and RAS notifications. RAS telemetry structures define block error counts, CPER dump cursors, critical-hit status, host-push union, UniRAS shared memory, and the top-level telemetry object. `amd_sriov_msg_checksum()` is declared for host/guest checksum agreement.

## Control flow
The header has no runtime control flow. Runtime users map shared memory, use version/offset headers to locate tables, populate PF2VF or VF2PF structures, validate checksums, and exchange mailbox request/response ids. RAS users write or read telemetry bodies according to the selected mailbox event.

## State and persistence behavior
The structures describe persistent shared VRAM/critical-region state visible across PF and VF contexts. Packing and static assertions preserve byte-exact layout. Checksums, versions, and `valid_tables` are state guards. Some fields, such as VF utilization and RAS counts, are periodically updated; others, such as VBIOS offsets and feature flags, are initialization-time data.

## Dependencies
The file depends on fixed-width integer types and Linux compile-time `_Static_assert` when built in kernel context. It intentionally avoids AMDGPU private structures so the ABI can be shared across host, guest, and firmware-adjacent components.

## Integration points
AMDGPU SR-IOV PF/VF code, AMDGIM/GIM history, mailbox handlers, PSP relay paths, RAS telemetry paths, ROCm SMI UUID/function reporting, and VF firmware loading consume these definitions. Firmware and host tools must agree on sizes and field meanings.

## Risks and edge cases
This is ABI-sensitive: changing packing, field order, reserved sizes, or enum values can break host/guest compatibility. The `AMD_SRIOV_MSG_*_FILLED_SIZE` constants must match real field growth or the reserved arrays will no longer keep 1 KiB payloads. Bitfield layout is compiler-sensitive in general, so the code relies on a consistent build environment and packed C layout. The v2 dynamic offset header requires strict validation of sizes and checksums before trusting shared memory.

## Test signals
Compile-time static assertions check PF2VF/VF2PF size, ucode reserve alignment/capacity, and telemetry size. Runtime validation should cover checksum compatibility, version negotiation, v1 and v2 offset parsing, mailbox request/response round trips, and RAS telemetry bounds.
