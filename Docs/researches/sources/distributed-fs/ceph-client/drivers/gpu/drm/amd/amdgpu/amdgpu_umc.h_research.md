<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_umc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_umc.h

## Purpose
`amdgpu_umc.h` defines shared UMC address macros, channel-iteration macros, RAS callback interfaces, UMC device state, and exported common UMC RAS helpers.

## Important APIs, Types, And Functions
Address macros derive 4 KiB, 8 KiB, 32 KiB, 256-byte block, and 256-byte offset values from MCA/error address fields. Loop macros iterate UMC instances, channels, and node instances using `adev->umc` geometry and active masks. EEPROM encoding helpers include `UMC_ECC_NEW_DETECTED_TAG`, `UMC_CHANNEL_IDX_V2`, `UMC_NPS_SHIFT`, and `UMC_NPS_MASK`. `struct amdgpu_umc_flip_bits` records physical-address bit positions used for bad-page retirement expansion. `struct amdgpu_umc_ras` is the version-specific callback table for RAS registration, poison mode, ECC count/address queries, ECC status updates, error address conversion, die ID lookup, flip-bit discovery, and MCA IPID parsing. `struct amdgpu_umc` stores per-device geometry, callbacks, active masks, RAS interface, and retire-unit data.

## Control Flow
IP-specific UMC implementations fill `adev->umc` and `adev->umc.ras`, then call common RAS init helpers. The common `.c` file uses the function pointers and macros to register RAS blocks, walk UMC topology, translate addresses, log ECC errors, and retire pages.

## State And Persistence
The header defines the state that persists for the UMC IP lifetime: channel/UMC/node counts, active masks, channel interleave table, RAS callback table, and flip-bit configuration. Error address counts and RAS interface pointers are updated as events are processed.

## Dependencies And Integration Points
It includes AMDGPU RAS and MCA headers and exposes interfaces used by IP-version-specific UMC files, PSP RAS queries, DPM/SMU ECC handling, and global RAS manager code.

## Risks
The loop macros assume `adev` is in lexical scope and that geometry fields are initialized correctly. EEPROM bit encodings reuse fields with limited width, so compatibility between legacy and v2/NPS encodings is fragile. Callback presence is optional; common code must consistently guard null pointers and define clear behavior when conversion is unsupported.

## Test Signals
Build all UMC IP implementations, test loop coverage on node-less, node-aware, and multi-AID topologies, validate EEPROM channel/NPS encodings, and exercise callback-null fallbacks versus fully implemented RAS callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_umc.h -->
