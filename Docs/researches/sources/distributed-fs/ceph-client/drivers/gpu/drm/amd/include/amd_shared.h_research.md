# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/amd_shared.h

## Purpose
This header defines shared AMDGPU concepts used across display, KFD, PowerPlay, SMU, and core device code: chip flags, APU flags, IP block types, clock/power gating states, feature masks, debug masks, and the common `amd_ip_funcs` lifecycle callback table.

## Important APIs, Types, And Constants
Chip flags distinguish ASIC identity bits from driver flags such as mobility, APU, PX, and experimental support. APU flags enumerate Raven, Raven2, Picasso, Renoir, Green Sardine, Vangogh, and Cyan Skillfish2.

`enum amd_ip_block_type` classifies GPU IP blocks: common, GMC, IH, SMC, PSP, DCE, GFX, SDMA, UVD, VCE, ACP, VCN, MES, JPEG, VPE, UMSCH_MM, ISP, RAS, and count. `enum amd_clockgating_state` and `enum amd_powergating_state` define gate/ungate control values.

Clock-gating and power-gating support macros define bit flags for GFX, memory controller, SDMA, BIF, UVD, VCE, HDP, ROM, DRM, DF, VCN, ATHUB, JPEG, repeater, IH, and other blocks. `enum PP_FEATURE_MASK` defines boot-tunable PowerPlay feature bits. `enum DC_FEATURE_MASK` and `enum DC_DEBUG_MASK` define display feature and debug toggles.

`struct amd_ip_funcs` is the central lifecycle interface for IP blocks. It contains callbacks for early/late/software/hardware init and fini, suspend/resume, idle checks, soft reset phases, clock/power gating, clock-gating state dump, IP state dump, and devcoredump printing.

## Control Flow
There is no executable code, but `struct amd_ip_funcs` drives AMDGPU device lifecycle control. The core driver builds an ordered list of IP blocks, then calls the appropriate callbacks during probe, init, suspend, resume, reset, power management, and diagnostic dump paths.

## State And Persistence
The header stores no runtime state. It defines enum and mask values that are persisted in device structures, module parameters, DPM state, display debug configuration, and per-IP block descriptors. Feature masks can be influenced by boot/module parameters such as `amdgpu.ppfeaturemask`.

## Dependencies And Integration Points
It includes `<drm/amd_asic_type.h>` and `<drm/drm_print.h>`, forward-declares `struct amdgpu_ip_block`, and references `struct drm_printer`. It is included by AMDGPU core headers, KFD private headers, display manager code, PowerPlay, and CGS common interfaces.

The `amd_ip_funcs` callback table is implemented by many IP-specific files, including GFX, SDMA, JPEG, VCN, VPE, DCE, SMU, and legacy DPM implementations. Power-management code uses `AMD_IP_BLOCK_TYPE_*` values to request gating by block.

## Risks
Enum ordering is semantically important where arrays are sized by `AMD_IP_BLOCK_TYPE_NUM` or indexed by block type. Adding, removing, or reordering values can break existing state arrays unless all users are updated.

Feature/debug mask bits are externally visible through module parameters and diagnostics. Reusing a bit or changing its meaning can silently alter user configuration. Callback pointers in `amd_ip_funcs` are optional in practice, so core callers must check availability or ensure a callback is mandatory for that lifecycle phase.

## Test Signals
Build coverage across AMDGPU is required because this header is broad. Runtime signals include successful IP block init/fini ordering, suspend/resume, GPU reset, clock-gating and power-gating toggles, devcoredump generation, and module-parameter feature-mask behavior. Tests that inspect `AMD_IP_BLOCK_TYPE_NUM`-sized arrays are important after enum changes.
