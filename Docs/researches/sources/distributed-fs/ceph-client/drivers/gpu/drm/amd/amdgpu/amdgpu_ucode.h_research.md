<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ucode.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ucode.h

## Purpose
`amdgpu_ucode.h` defines the binary firmware header schemas, firmware ID/status/load enums, PSP package descriptors, GPU-info payload structures, and `struct amdgpu_firmware` state consumed by AMDGPU firmware loading code.

## Important APIs, Types, And Functions
`struct common_firmware_header` is the prefix shared by all firmware blobs. Specialized headers cover MC, SMC v1/v2 soft PPTables, PSP v1/v2 descriptors, TA firmware, GFX v1/v2 including RS64 code/data starts, MES, RLC v1 through v2.5, SDMA v1/v2/v3, VPE, UMSCH MM, GPU-info, DMCU, DMCUB, and IMU. `union amdgpu_firmware_header` provides a fixed-size view for common parsing.

`enum AMDGPU_UCODE_ID` is the master index for firmware records, covering classic CP/SDMA/SMC/UVD/VCE/VCN firmware plus RS64 stacks, MES data, IMU, RLC sub-images, VPE, UMSCH MM ucode/data/cmd buffer, P2S table, JPEG RAM, and ISP. `struct amdgpu_firmware_info` stores per-payload ID, firmware pointer, MC address, CPU address, size, and TMR MC address words. `struct amdgpu_firmware` stores all per-device firmware state and the shared firmware BO. The header declares print helpers, request/release helpers, BO lifecycle, sysfs lifecycle, load-type selection, firmware name mapping, IP-version decoding, and kicker detection.

## Control Flow
IP-specific code fills `adev->firmware.ucode[]` entries with IDs and firmware pointers using these schemas. `amdgpu_ucode.c` then interprets the concrete header type to copy sub-images into the load buffer or expose version metadata. PSP package headers use flexible arrays, so consumers must use the count fields before iterating descriptors.

## State And Persistence
The schema definitions are immutable contracts for firmware blobs. Device runtime state is represented by `struct amdgpu_firmware`, which persists across firmware setup, PSP/SMU loading, resets, and teardown until the shared BO and firmware references are released.

## Dependencies And Integration Points
The header includes `amdgpu_socbb.h` for GPU-info bounding-box payloads and is included by PSP, SMU, GFX, SDMA, VCN, VPE, UMSCH, display, and firmware management code. It mirrors external firmware binary layout, so it is coupled to linux-firmware packaging and PSP/SMU expectations.

## Risks
Structure layout changes can silently break binary parsing. Flexible array descriptors require strict bounds checking in users. The union reserves `raw[0x100]`, so new headers larger than that need careful audit. `PSP_FW_TYPE_UNKOWN` and `TA_FW_TYPE_UNKOWN` preserve misspelled enum names that may be externally referenced. New firmware IDs must be added consistently to name mapping, max counts, PSP packing, and IP-block registration.

## Test Signals
Compile-time size/layout checks for representative firmware headers, firmware load tests for each major IP family, PSP package descriptor iteration, UMSCH/VPE/RS64 payload extraction, and sysfs firmware-version visibility are the most valuable signals. Fuzzing malformed header sizes and offsets would strengthen validation coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ucode.h -->
