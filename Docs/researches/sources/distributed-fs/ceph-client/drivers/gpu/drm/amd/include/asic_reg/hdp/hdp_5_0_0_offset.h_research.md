# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/hdp/hdp_5_0_0_offset.h

## Purpose

`hdp_5_0_0_offset.h` is the generated offset map for HDP 5.0.0 `hdp_hdpdec` registers at base address `0x3c80`. It is directly included by `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/hdp_v5_0.c` and supplies the numeric register offsets used for HDP cache invalidation, clock/power gating, miscellaneous cache flush control, MEMIO, XDP direct-to-HDP, P2P, IOV logging, and MMHUB error handling.

## Important APIs, types, and macros

This header exports `mmHDP_*` macros and matching `_BASE_IDX` macros. Major offsets include:

- `mmHDP_SURFACE_WRITE_FLAGS`, `mmHDP_SURFACE_READ_FLAGS`, `mmHDP_SURFACE_WRITE_FLAGS_CLR`, `mmHDP_SURFACE_READ_FLAGS_CLR`, added relative to the 4.0 offset map.
- `mmHDP_READ_CACHE_INVALIDATE`, used by `hdp_v5_0_invalidate_hdp()` through direct MMIO or ring-emitted register writes.
- `mmHDP_MEM_POWER_CTRL`, `mmHDP_CLK_CNTL`, and `mmHDP_MISC_CNTL`, used by `hdp_v5_0_update_mem_power_gating()`, `hdp_v5_0_update_medium_grain_clock_gating()`, `hdp_v5_0_get_clockgating_state()`, and `hdp_v5_0_init_registers()`.
- `mmHDP_MMHUB_CNTL`, `mmHDP_EDC_CNT`, `mmHDP_VERSION`, and `mmHDP_MEMIO_*`.
- `mmHDP_XDP_*` offsets, including `mmHDP_XDP_GPU_IOV_VIOLATION_LOG2` at `0x0149` and `mmHDP_XDP_MMHUB_ERROR` at `0x014a`.

All base indices are `0`.

## Control flow

The header contains no control flow. In `hdp_v5_0.c`, the constants drive the control flow of HDP operations: invalidation writes `mmHDP_READ_CACHE_INVALIDATE`; power gating reads/writes `mmHDP_CLK_CNTL` and `mmHDP_MEM_POWER_CTRL`; clock-gating state checks read those same registers; init sets `HDP_MISC_CNTL__FLUSH_INVALIDATE_CACHE_MASK` at `mmHDP_MISC_CNTL`.

## State and persistence behavior

The macros refer to persistent HDP hardware registers. `MEM_POWER_CTRL` and `CLK_CNTL` retain clock/power-gating configuration until changed or reset. `MISC_CNTL` controls cache flush behavior. XDP/P2P and IOV registers reflect mailbox/BAR/status/error state. `READ_CACHE_INVALIDATE` is a write-trigger style register where write posting is forced by a readback or ring ordering.

## Dependencies and integration points

The primary dependency is `hdp_5_0_0_sh_mask.h`, included beside this file by `hdp_v5_0.c`. Integration relies on `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_NO_KIQ`, `SOC15_REG_OFFSET`, and ring `emit_wreg`. The register map is also tied to clock-gating capability flags such as `AMD_CG_SUPPORT_HDP_LS`, `AMD_CG_SUPPORT_HDP_DS`, `AMD_CG_SUPPORT_HDP_SD`, and `AMD_CG_SUPPORT_HDP_MGCG`.

## Risks

Incorrect offsets can break HDP invalidation and cause CPU/GPU coherency failures. Power-control offsets are particularly risky because `hdp_v5_0_update_mem_power_gating()` performs a multi-step sequence: force memory clocks on, disable gating, choose one LS/DS/SD mode, then clear overrides. If `mmHDP_CLK_CNTL` or `mmHDP_MEM_POWER_CTRL` is wrong, the sequence can hang or leave HDP clocks incorrectly gated. `GPU_IOV_VIOLATION_LOG2` is a 5.x addition relative to 4.0, so mixed-generation diagnostics can read the wrong register.

## Test signals

Build `hdp_v5_0.c` and run HDP cache invalidation paths with and without a ring capable of `emit_wreg`. Runtime test signals include stable memory coherency, successful clock-gating enable/disable, correct `get_clockgating_state()` flags for LS/DS/SD/MGCG, and no spurious MMHUB/XDP errors under normal workloads. SR-IOV and P2P tests should verify IOV log and P2P BAR offsets.
