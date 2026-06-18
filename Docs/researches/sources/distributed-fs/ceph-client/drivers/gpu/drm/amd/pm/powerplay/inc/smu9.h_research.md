# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu9.h

## Purpose
`smu9.h` defines a compact SMU9 feature/workload/ULV interface. It enumerates the 32 firmware feature bits and masks for DPM, deep sleep, AVFS, PPT/TDC/thermal, display, fan, EDC, ACG, PCC limit control, plus workload and ULV client masks.

## Important APIs, Types, And Constants
- `ENABLE_DEBUG_FEATURES` is defined for debug feature paths.
- Feature bit macros run from `FEATURE_DPM_PREFETCHER_BIT` through spare bits, with `NUM_FEATURES` set to 32.
- Matching feature masks include `FFEATURE_*` names for most features and several `FEATURE_*_MASK` names for later features.
- Workload bits include VR, FRTC, video, and compute with `NUM_WORKLOADS`.
- ULV client masks cover RLC, UVD, VCE, SDMA0/1, JPEG, and DPM clients for GFXCLK, UVD, VCE, MP0CLK, UCLK, SOCCLK, and DCEFCLK.
- A packed anonymous typedef near the end defines a firmware-visible feature/status style table with bitmaps and enabled/running state fields.

## Control Flow And Data Flow
Host policy code composes feature masks and workload selections, sends them to firmware through SMU9 messaging paths, and firmware uses ULV client masks to decide when low-voltage states are blocked. The file itself has no functions; control is expressed through bitmask protocol.

## State And Persistence
Constants are stateless. The packed struct represents volatile firmware-visible state. Feature enablement survives only for the running firmware session unless re-applied at initialization/resume.

## Dependencies And Integration Points
- Used by SMU9 powerplay and firmware-management code.
- Integrates with later-generation SMU message interfaces, feature enable/disable commands, workload policy selection, and ULV/deep-sleep gating.

## Risks
- The `FEATURE_FAST_PPT_MASK`, `FEATURE_GFX_EDC_MASK`, and `FEATURE_ACG_MASK` definitions reference shift names without the visible `FEATURE_` prefix in this header; compilation depends on whether those names exist elsewhere or this is dead code.
- `FFEATURE_` versus `FEATURE_` mask naming is inconsistent and easy to misuse.
- Feature bit order is firmware ABI; reordering breaks host/firmware negotiation.
- ULV client masks must match firmware blockers or the GPU may enter ULV during active work.

## Test Signals
- Compile all SMU9 users to catch undefined mask-shift names.
- Runtime feature table query should report expected enabled/running bits.
- Workload switching should affect DPM policy, and ULV should stay blocked while media/compute/display clients are active.
