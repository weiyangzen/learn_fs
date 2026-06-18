# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/hdp/hdp_5_2_1_offset.h

## Purpose

`hdp_5_2_1_offset.h` is the generated offset map for HDP 5.2.1 `hdp_hdpdec` registers at base address `0x3c80`. It uses `regHDP_*` names and is directly included by `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/hdp_v5_2.c`. The map supports HDP 5.2 register access for clock/power gating, MEMIO, non-surface and surface flags, XDP/P2P status, GPU IOV logging, and MMHUB error reporting.

## Important APIs, types, and macros

The file contains only register-offset macros and `_BASE_IDX` constants. Important exported offsets include:

- `regHDP_MMHUB_TLVL`, `regHDP_MMHUB_UNITID`, `regHDP_NONSURFACE_BASE`, `regHDP_NONSURFACE_INFO`, `regHDP_NONSURFACE_BASE_HI`.
- `regHDP_SURFACE_WRITE_FLAGS`, `regHDP_SURFACE_READ_FLAGS`, and corresponding clear registers.
- `regHDP_NONSURF_FLAGS`, `regHDP_NONSURF_FLAGS_CLR`, `regHDP_HOST_PATH_CNTL`, `regHDP_SW_SEMAPHORE`, `regHDP_DEBUG0`, `regHDP_LAST_SURFACE_HIT`, `regHDP_OUTSTANDING_REQ`, `regHDP_MISC_CNTL`, `regHDP_MEM_POWER_CTRL`, `regHDP_MMHUB_CNTL`, `regHDP_VERSION`, and `regHDP_CLK_CNTL`.
- `regHDP_MEMIO_CNTL`, `regHDP_MEMIO_ADDR`, `regHDP_MEMIO_STATUS`, `regHDP_MEMIO_WR_DATA`, `regHDP_MEMIO_RD_DATA`.
- `regHDP_XDP_DIRECT2HDP_FIRST/LAST`, `regHDP_XDP_D2H_FLUSH`, `regHDP_XDP_D2H_BAR_UPDATE`, reserved D2H slots, P2P mailbox/BAR registers, flush/busy/sticky/status registers, `regHDP_XDP_GPU_IOV_VIOLATION_LOG`, `regHDP_XDP_GPU_IOV_VIOLATION_LOG2`, and `regHDP_XDP_MMHUB_ERROR`.

All base indices are `0`.

## Control flow

There is no executable control flow. In `hdp_v5_2.c`, these offsets are used in power and clock-gating control flow with `RREG32_SOC15(HDP, 0, regHDP_CLK_CNTL)` and `RREG32_SOC15/HDP_MEM_POWER_CTRL` reads/writes. Unlike `hdp_v5_0.c`, the 5.2 flush path uses a remapped KFD HDP memory flush control register rather than a `regHDP_READ_CACHE_INVALIDATE` offset, and this offset header does not define `READ_CACHE_INVALIDATE`.

## State and persistence behavior

The described registers hold HDP hardware state. `regHDP_MEM_POWER_CTRL` and `regHDP_CLK_CNTL` persist clock and memory power-gating configuration. Surface/non-surface flags and XDP sticky/status registers retain event state until cleared. IOV and MMHUB error registers capture fault state. The file also omits `EDC_CNT`, so code using this map should not assume HDP 5.2.1 exposes the same RAS counter offset as HDP 5.0.0.

## Dependencies and integration points

This file is paired with `hdp_5_2_1_sh_mask.h`, which is not part of this work item but is included by `hdp_v5_2.c` alongside this offset header. Integration depends on newer `regHDP_*` AMDGPU register naming, `RREG32_SOC15`, `WREG32_SOC15`, and `REG_SET_FIELD()`/mask macros for `HDP_MEM_POWER_CTRL` and `HDP_CLK_CNTL`. It also integrates with KFD remap constants such as `KFD_MMIO_REMAP_HDP_MEM_FLUSH_CNTL` for flush behavior in the 5.2 driver.

## Risks

The biggest risk is porting 5.0 code mechanically to 5.2.1: this header does not define `regHDP_READ_CACHE_INVALIDATE` or `regHDP_EDC_CNT`, and `hdp_v5_2.c` intentionally uses a remapped flush register instead. The `reg` prefix must be matched in call sites; `mmHDP_*` names from 5.0 will not compile. Power-control field names in the paired mask header also differ conceptually from 5.0, using atomic memory controls in the 5.2 driver, so offset/mask pairing must be kept generation-specific.

## Test signals

Compile `hdp_v5_2.c` with this header and its paired mask header. Runtime signals include successful KFD HDP flush through the remapped register, correct LS/DS/SD and MGCG state reporting through `regHDP_MEM_POWER_CTRL` and `regHDP_CLK_CNTL`, absence of invalid reads from missing `READ_CACHE_INVALIDATE` or `EDC_CNT` offsets, and correct decoding of XDP/P2P/IOV/MMHUB status registers on HDP 5.2.1 hardware.
