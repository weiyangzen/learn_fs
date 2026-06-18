# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/hdp/hdp_4_0_offset.h

## Purpose

`hdp_4_0_offset.h` is a generated AMDGPU register-offset contract for the HDP 4.0 `hdp_hdpdec` address block at base address `0x3c80`. It exports preprocessor constants for HDP MMIO register offsets and their `_BASE_IDX` values. The HDP block is the Host Data Path used by the driver for host/device coherency actions, HDP cache invalidation, non-surface aperture programming, RAS counter access, and XDP/HDP mailbox and peer-to-peer register programming.

## Important APIs, types, and macros

This file defines no C types or functions. Its API is entirely macro based:

- `mmHDP_MMHUB_TLVL`, `mmHDP_MMHUB_UNITID`: MMHUB traffic-level and unit-id register offsets.
- `mmHDP_NONSURFACE_BASE`, `mmHDP_NONSURFACE_INFO`, `mmHDP_NONSURFACE_BASE_HI`: non-surface aperture configuration offsets used by `hdp_v4_0_init_registers()` to program VRAM base information.
- `mmHDP_NONSURF_FLAGS`, `mmHDP_NONSURF_FLAGS_CLR`: non-surface read/write flag and clear registers.
- `mmHDP_HOST_PATH_CNTL`, `mmHDP_SW_SEMAPHORE`, `mmHDP_DEBUG0`, `mmHDP_LAST_SURFACE_HIT`: host path control, software semaphore, debug, and last surface hit offsets.
- `mmHDP_READ_CACHE_INVALIDATE`: read-cache invalidation trigger register used by `hdp_v4_0_invalidate_hdp()` except for newer 4.4.x variants that skip this path.
- `mmHDP_OUTSTANDING_REQ`, `mmHDP_MISC_CNTL`, `mmHDP_MEM_POWER_LS`, `mmHDP_MMHUB_CNTL`, `mmHDP_EDC_CNT`, `mmHDP_VERSION`, `mmHDP_CLK_CNTL`: request, cache-control, light-sleep, MMHUB, RAS/EDC, version, and clock-control offsets.
- `mmHDP_MEMIO_*`: indirect memory I/O control, address, status, write-data, and read-data offsets.
- `mmHDP_XDP_*`: XDP direct-to-HDP, flush, BAR update, P2P mailbox, P2P BAR, busy/sticky/status, framebuffer-location, GPU IOV violation, and MMHUB error offsets.

All `_BASE_IDX` macros in this file are `0`, matching the first base segment used by `SOC15_REG_OFFSET()` and related AMDGPU register helpers.

## Control flow

There is no executable control flow. The practical control flow is in consumers such as `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/hdp_v4_0.c`: the driver includes this header, computes SOC15 register addresses from these offsets, then performs MMIO reads/writes through `RREG32*`, `WREG32*`, `WREG32_FIELD15()`, or ring-emitted write-register packets.

## State and persistence behavior

The header itself stores no state. Its constants name hardware registers whose values persist in GPU MMIO state until reset, power transition, or explicit driver programming. Registers represented here include sticky/clearable state (`*_FLAGS`, `*_CLR`, `HDP_XDP_STICKY` in the paired mask header), cache-invalidation triggers, RAS counters (`mmHDP_EDC_CNT`), and clock/power-control state (`mmHDP_MEM_POWER_LS`, `mmHDP_CLK_CNTL`). A wrong offset can therefore persistently program the wrong hardware register until the next corrective write or reset.

## Dependencies and integration points

The direct dependency is the paired `hdp_4_0_sh_mask.h`, which supplies field masks and shifts for the offsets here. `hdp_v4_0.c` directly includes both headers. Integration is through the AMDGPU SOC15 register access layer: `SOC15_REG_OFFSET(HDP, 0, mm...)`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_NO_KIQ`, `WREG32_FIELD15`, and ring `emit_wreg` paths. The macros also align with IP-base headers such as `*_ip_offset.h`, where `HDP_BASE` defines the base segment used with these relative offsets.

## Risks

The highest risk is silent hardware misprogramming: offsets are untyped numeric macros, so the compiler cannot detect an offset copied from the wrong HDP generation. The 4.0 map uses `mmHDP_MEM_POWER_LS` at `0x00d4`; `hdp_v4_0.c` manually aliases `mmHDP_MEM_POWER_CTRL` to the same offset for Vega20 name differences, so future edits must preserve version-specific naming. The file lacks the 4.4/5.x surface flag offsets at `0x00c4` through `0x00c7`, so consumers must not assume all HDP revisions expose the same named offset set. Reserved XDP ranges are deliberately named and should not be repurposed without matching hardware documentation.

## Test signals

Useful validation signals include successful compilation of `hdp_v4_0.c`, boot-time HDP initialization without MMIO faults, working HDP cache invalidate paths under CPU/GPU coherency tests, correct VRAM non-surface base programming, and RAS EDC counter reads/resets on devices that report `AMDGPU_RAS_BLOCK__HDP`. Regression tests should exercise clock-gating reporting and update paths for HDP 4.0/4.1 versus 4.4.x devices, because those paths branch around registers defined in this file.
