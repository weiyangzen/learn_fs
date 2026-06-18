# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_6_ppt.h

## Purpose
`smu_v13_0_6_ppt.h` is the shared public and layer-2 internal header for the SMU13.0.6-family PPT backend. It defines UMD pstate level constants, the driver's synthesized PPTable shape, capability bits, sizing constants for multi-instance metrics, exported backend/helper prototypes, and macro-generated GPU and partition metric classes used by the implementation and 13.0.12 companion code.

## Important APIs, Types, And Data
- `smu_v13_0_6_set_ppt_funcs(struct smu_context *smu)` is the backend registration entry point.
- `smu_v13_0_6_cap_supported()`, `smu_v13_0_6_get_static_metrics_table()`, and `smu_v13_0_6_get_metrics_table()` are exported helpers for capability checks and metrics/static-metrics retrieval.
- The header declares a family of 13.0.12 helper APIs used by the 13.0.6 implementation when `MP1_HWIP` is IP 13.0.12: DPM-running detection, max/system metrics sizing, driver PPTable setup, metrics extraction, XCP metrics, table init/fini, NPM/system power sensors, feature/message maps, temp funcs, and RAS driver.
- `METRICS_LIST_e` identifies PMFW metric table layout variants V0, V1, and V2.
- `struct PPTable_t` is the driver-synthesized table storing max socket/node/PPT limits, GFX min/max, frequency tables for FCLK/UCLK/SOCCLK/VCLK/DCLK/LCLK, LCLK range, public serial number, and an `Init` flag.
- `enum smu_v13_0_6_caps` defines runtime capability bits: DPM, DPM policy, other-end PCIe metrics, UCLK max setting, PCIe metrics, MCA debug, per-instance metrics, CTF limits, RMA message, ACA syndrome, SDMA/VCN reset, static metrics, host-limit metrics, board voltage, PLDM version, temp/NPM/system power metrics, RAS EEPROM, FAST_PPT, temperature AID/XCD/HBM metrics, and an ALL sentinel.
- Sizing constants describe maximum XGMI links, GFX clocks/XCCs, clocks, VCN, JPEG rings, AIDs, and HBM stacks.
- `SMU_13_0_6_METRICS_FIELDS()` and `SMU_13_0_6_PARTITION_METRICS_FIELDS()` are field-list macros consumed by `DECLARE_SMU_METRICS_CLASS()` to generate strongly described metric structures and init helpers.

## Control Flow And Behavior
- This header does not execute logic directly, but it shapes how `smu_v13_0_6_ppt.c` compiles under `SWSMU_CODE_LAYER_L2`. When that macro is defined, it includes `smu_cmn.h` and declares macro-generated metric classes for whole-GPU and partition metrics.
- The UMD pstate constants define table indices used by the implementation to choose standard GFX, SOC, and memory clocks when enough DPM levels are available.
- `struct PPTable_t` acts as a persistent normalized view of values that SMU13.0.6 firmware exposes through metrics/static metrics rather than a traditional full PPTable.
- The metrics field macros define names, units, scalar/array type metadata, and array extents for metrics exported to userspace or other driver components.

## State And Persistence
- Header-defined state is structural. Runtime instances of `PPTable_t`, generated GPU metrics, and generated partition metrics are allocated and updated by the `.c` implementation.
- The capability enum values persist as bit positions in `smu_13_0_dpm_context->caps`; changing enum ordering is a compatibility risk inside the driver.
- The max-size constants constrain array storage and loops in metrics export code.

## Dependencies And Integration Points
- Depends on SMU common metric declaration machinery (`DECLARE_SMU_METRICS_CLASS`, `SMU_MATTR`, `SMU_MUNIT`, `SMU_MTYPE`) when compiled in layer-2 mode.
- Integrates with the SMU13.0.6 PPT implementation, SMU13.0.12 companion implementation, AMDGPU XCP partition metrics, RAS SMU driver selection, temperature helper dispatch, and firmware metrics table decoding.
- The exported 13.0.12 symbols allow this family backend to share one public header while routing IP-specific behavior to a companion implementation.

## Risks And Edge Cases
- The generated metrics structures depend on array extents matching firmware-provided arrays. Underestimating constants can truncate data; overestimating requires implementation loops to guard absent instances.
- `PPTable_t` includes `bool Init` after numeric fields; structure layout is internal driver memory, but careless serialization or firmware assumptions would be unsafe.
- Capability enum order must remain consistent with bit operations using `BIT_ULL(cap)`.
- UMD pstate constants are indices, not frequencies. If firmware DPM tables become shallower than expected, implementation must fall back to min values, as it currently does.
- 13.0.12 declarations in this header create tight cross-file coupling; build failures or ABI mismatches will show up in this shared backend even if base 13.0.6 paths do not use the helpers.

## Test Signals
- Build tests should cover both layer-2 compilation and consumers that only need the public prototypes.
- Static assertions or compile-time review should ensure metrics field arrays align with PMFW table definitions for XGMI, GFX/XCC, VCN, JPEG, AID, and HBM counts.
- Capability tests should verify every enum bit used by the implementation maps to the intended feature gate.
- Metrics export tests should verify generated `smu_v13_0_6_gpu_metrics` and `smu_v13_0_6_partition_metrics` structures initialize to the expected version/format and expose declared units/types.
- 13.0.12 integration tests should verify all declared helper symbols are provided and are selected correctly by `smu_v13_0_6_ppt.c`.
