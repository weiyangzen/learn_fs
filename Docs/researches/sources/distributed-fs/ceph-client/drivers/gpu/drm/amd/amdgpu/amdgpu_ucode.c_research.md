<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ucode.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ucode.c

## Purpose
`amdgpu_ucode.c` centralizes AMDGPU firmware metadata handling. It prints typed firmware headers for debugging, validates firmware blobs, determines firmware load strategy, exposes firmware versions through sysfs, packs firmware payloads into the PSP/SMU load buffer, derives legacy and IP-version-based firmware names, handles required/optional `request_firmware`, and releases firmware references.

## Important APIs, Types, And Functions
The `amdgpu_ucode_print_*_hdr` family decodes MC, SMC, GFX, RLC, SDMA, PSP, and GPU-info headers by major/minor version. `amdgpu_ucode_validate` checks the firmware file size against the common header. `amdgpu_ucode_hdr_version` compares header versions. `amdgpu_ucode_get_load_type` maps ASIC generation and module load type to direct, SMU, PSP, or RLC-backdoor firmware loading. `amdgpu_ucode_name` maps `enum AMDGPU_UCODE_ID` to human-readable strings, including UMSCH MM, VPE, RS64, JPEG, and ISP IDs.

Sysfs firmware version reporting is generated with `FW_VERSION_ATTR`, then filtered by `amdgpu_ucode_sys_visible`. BO handling is split into `amdgpu_ucode_create_bo`, `amdgpu_ucode_init_bo`, and `amdgpu_ucode_free_bo`. The critical payload extraction is `amdgpu_ucode_init_single_fw`, which switches on ucode ID for PSP-loaded firmware and computes the exact byte range to copy from the firmware blob into `adev->firmware.fw_buf_ptr`. `amdgpu_ucode_patch_jt` appends MEC jump-table data for non-PSP loading. `amdgpu_ucode_ip_version_decode` chooses legacy names or generic `gc_maj_min_rev`, `sdma_...`, `psp_...`, etc. `amdgpu_ucode_request` formats the filename, performs required or no-warn optional firmware request, validates size, and returns errors without directly releasing the firmware on validation failure.

## Control Flow
IP-block early init code typically calls `amdgpu_ucode_ip_version_decode` and `amdgpu_ucode_request` to load firmware and populate `adev->firmware.ucode[]` entries. During PSP-style loading, `amdgpu_ucode_create_bo` allocates a shared firmware BO in VRAM or GTT depending on SR-IOV/debug/XGMI constraints. `amdgpu_ucode_init_bo` chooses `max_ucodes`, refreshes the firmware buffer MC address for XGMI migration, iterates all registered `ucode` records, calls `amdgpu_ucode_init_single_fw`, and advances a page-aligned offset by the copied payload size. Later PSP/SMU code consumes the buffer and the per-ucode MC/kaddr/size metadata.

## State And Persistence
State lives in `adev->firmware`: load type, `fw_buf`, buffer size, current max ucode count, per-ID firmware descriptors, sysfs-visible versions stored elsewhere on `adev`, GPU-info firmware pointer, MC address, and PLDM version. Firmware pointers are retained until matching release paths in IP blocks or `amdgpu_ucode_release`.

## Dependencies And Integration Points
This file depends on Linux firmware loading, DRM sysfs/device attributes, AMDGPU ASIC/IP-version metadata, PSP firmware loading, SR-IOV, XGMI migration, Kicker firmware identification, and all IP-block firmware header layouts from `amdgpu_ucode.h`. It directly integrates with UMSCH MM by recognizing `AMDGPU_UCODE_ID_UMSCH_MM_UCODE`, `AMDGPU_UCODE_ID_UMSCH_MM_DATA`, and command-buffer IDs.

## Risks
Payload extraction is offset-heavy and version-specific; a wrong `ucode_size` or offset can make PSP load invalid data. Validation only checks total size, not per-section bounds or CRC. The filename buffer check tests `r == sizeof(fname)` rather than `r >= sizeof(fname)`, so truncation edge cases deserve attention. Sysfs visibility depends on zero firmware versions being invalid. `amdgpu_ucode_request` documents that callers must release firmware even after validation failure, so caller consistency matters.

## Test Signals
Exercise firmware requests for required and optional files, validation failure paths, sysfs visibility with zero/nonzero versions, PSP buffer packing for MES/RLC/RS64/VPE/UMSCH entries, non-PSP MEC jump-table packing, legacy and generic firmware name generation across IP versions, SR-IOV zeroed firmware buffers, and XGMI migration MC-address refresh.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ucode.c -->
