# subset-b-002745 research

This grouped report covers AMDGPU HDP register offset and shift/mask headers under `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/hdp/`. Each section is bounded for reconciliation into the mapped per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/hdp/hdp_4_0_offset.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/hdp/hdp_4_0_offset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/hdp/hdp_4_0_sh_mask.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/hdp/hdp_4_0_sh_mask.h

## Purpose

`hdp_4_0_sh_mask.h` is the field-description companion for the HDP 4.0 offset header. It defines `__SHIFT` and `_MASK` macros for fields inside the HDP 4.0 registers, allowing AMDGPU helpers such as `REG_SET_FIELD()` and `WREG32_FIELD15()` to update individual hardware fields without hard-coded bit arithmetic at call sites.

## Important APIs, types, and macros

This file defines only macros. Important field groups include:

- MMHUB routing fields: `HDP_MMHUB_TLVL__*` and `HDP_MMHUB_UNITID__*` describe HDP, XDP, and XDP mailbox traffic levels/unit IDs.
- Non-surface aperture fields: `HDP_NONSURFACE_BASE__NONSURF_BASE_39_8`, `HDP_NONSURFACE_BASE_HI__NONSURF_BASE_47_40`, `HDP_NONSURFACE_INFO__NONSURF_SWAP`, and `HDP_NONSURFACE_INFO__NONSURF_VMID`.
- Host path fields: `HDP_HOST_PATH_CNTL__WR_STALL_TIMER`, `RD_STALL_TIMER`, write-combine controls, `ALL_SURFACES_DIS`, `WRITE_THROUGH_CACHE_DIS`, and `LIN_RD_CACHE_DIS`.
- Cache and request fields: `HDP_READ_CACHE_INVALIDATE__READ_CACHE_INVALIDATE`, `HDP_OUTSTANDING_REQ__WRITE_REQ/READ_REQ`, and `HDP_MISC_CNTL__FLUSH_INVALIDATE_CACHE`, `READ_BUFFER_WATERMARK`, cacheline-size, pending-write-tag, and burst fields.
- Power/clock fields: `HDP_MEM_POWER_LS__LS_ENABLE/LS_HOLD` and `HDP_CLK_CNTL__*SOFT_OVERRIDE`.
- MEMIO fields: `HDP_MEMIO_CNTL__MEMIO_SEND`, operation, byte enables, strobes, address upper bits, error-clear bits, VF/VFID, plus status/data fields.
- XDP direct-to-HDP and P2P fields: flush number, mailbox encoded data and address select, BAR update address/flush/BAR number, P2P mailbox addresses, P2P BAR address/flush/valid, and BAR high address bits.
- Diagnostic/security fields: `HDP_XDP_BUSY_STS__BUSY_BITS`, `HDP_XDP_STICKY__STICKY_STS/W1C`, `HDP_XDP_GPU_IOV_VIOLATION_LOG__*`, and `HDP_XDP_MMHUB_ERROR__*`.

## Control flow

There is no runtime control flow. The macros are consumed by preprocessor-expansion in AMDGPU register helpers. For example, `WREG32_FIELD15(HDP, 0, HDP_MISC_CNTL, FLUSH_INVALIDATE_CACHE, 1)` relies on `HDP_MISC_CNTL__FLUSH_INVALIDATE_CACHE__SHIFT` and `HDP_MISC_CNTL__FLUSH_INVALIDATE_CACHE_MASK`. `REG_SET_FIELD()` similarly uses the field macros to construct read-modify-write values.

## State and persistence behavior

The file has no state, but it describes stateful hardware fields. Several fields are sticky or write-one-to-clear by convention (`HDP_XDP_STICKY__STICKY_W1C`, `*_FLAGS_CLR`). Others gate power or clocks, trigger cache invalidation, hold RAS/error counters, or encode SR-IOV violation details. Field values persist in the GPU register file according to hardware reset and power-domain behavior; the header must therefore match silicon bit layout exactly.

## Dependencies and integration points

This header is directly paired with `hdp_4_0_offset.h` and is included by `hdp_v4_0.c`. It depends on AMDGPU naming conventions: register field macros must be named `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` so helper macros can derive them from register and field tokens. The constants integrate with `amdgpu_ip_version()` branches in `hdp_v4_0.c`, which select behavior for HDP 4.0/4.1, 4.2.1, and 4.4.x devices.

## Risks

Because these are untyped bit constants, mask/shift drift can compile cleanly while corrupting hardware behavior. Notable version-sensitive fields include `HDP_MMHUB_TLVL`, where the 4.0 masks are 3-bit wide while 4.4.2 widens them to 4 bits, and `HDP_MEM_POWER_LS`, which is superseded by `HDP_MEM_POWER_CTRL` in later naming. Cache-control fields such as `FLUSH_INVALIDATE_CACHE` and read/write cache disable bits can cause coherency bugs if wrong. Security/virtualization fields in GPU IOV logging and MMHUB error registers can hide or misattribute faults if masks are wrong.

## Test signals

Compilation of field-based register writes in `hdp_v4_0.c` is the first signal. Runtime signals include successful HDP invalidate operations, stable display/compute memory coherency, correct clock-gating state reporting for HDP light sleep, expected RAS EDC counter behavior, and absence of MMHUB/XDP error logs during normal DMA and P2P workloads. A useful static check is comparing every `HDP_*__FIELD` macro here against the official generated register database for HDP 4.0 silicon.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/hdp/hdp_4_0_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/hdp/hdp_4_4_2_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/hdp/hdp_4_4_2_offset.h

## Purpose

`hdp_4_4_2_offset.h` is the generated register-offset map for HDP IP 4.4.2, address block `aid_hdp_hdpdec`, base address `0x3c80`. It uses the newer `regHDP_*` macro prefix rather than the older `mmHDP_*` prefix. The register map describes the AID-scoped HDP interface used for host-path coherency, non-surface access, surface read/write flags, MEMIO, XDP-to-HDP flush/mailbox operations, P2P BAR programming, GPU IOV violation logging, and MMHUB error status.

## Important APIs, types, and macros

No functions or types are declared. The exported macro families are:

- `regHDP_MMHUB_TLVL`, `regHDP_MMHUB_UNITID`: traffic and unit ID offsets.
- `regHDP_NONSURFACE_BASE`, `regHDP_NONSURFACE_INFO`, `regHDP_NONSURFACE_BASE_HI`: non-surface address configuration.
- `regHDP_SURFACE_WRITE_FLAGS`, `regHDP_SURFACE_READ_FLAGS`, and their `_CLR` registers: surface read/write flag tracking introduced relative to the 4.0 offset header.
- `regHDP_NONSURF_FLAGS`, `regHDP_NONSURF_FLAGS_CLR`, `regHDP_HOST_PATH_CNTL`, `regHDP_SW_SEMAPHORE`, `regHDP_DEBUG0`, `regHDP_LAST_SURFACE_HIT`, `regHDP_OUTSTANDING_REQ`, `regHDP_MISC_CNTL`, and `regHDP_MEM_POWER_CTRL`.
- `regHDP_MMHUB_CNTL`, `regHDP_EDC_CNT`, `regHDP_VERSION`, `regHDP_CLK_CNTL`, `regHDP_MEMIO_*`.
- `regHDP_XDP_*` offsets for direct-to-HDP reserved slots, flush, BAR update, mailbox configuration, P2P BARs, status/sticky registers, BAR high address bits, framebuffer location, `GPU_IOV_VIOLATION_LOG`, `GPU_IOV_VIOLATION_LOG2`, and `MMHUB_ERROR`.

All `_BASE_IDX` values are `0`.

## Control flow

The file has no executable logic. Consumers use the `regHDP_*` names with SOC15 register helpers. In this tree, `hdp_v4_0.c` special-cases HDP 4.4.x behavior while including the 4.0 headers, and no direct C include of this exact 4.4.2 header was found. That makes this file a generated hardware contract available for AID-specific or future platform code rather than an active direct include in the visible AMDGPU C sources.

## State and persistence behavior

The constants refer to persistent MMIO register state. Compared with the 4.0 offset header, this map moves the power register naming to `MEM_POWER_CTRL`, adds surface read/write flag registers, omits `READ_CACHE_INVALIDATE`, and splits GPU IOV initiator ID into `GPU_IOV_VIOLATION_LOG2`. Those deltas affect which hardware state a driver can safely poll or write on HDP 4.4.2 devices.

## Dependencies and integration points

The paired dependency is `hdp_4_4_2_sh_mask.h`. The `regHDP_*` prefix aligns with newer generated register headers and with AMDGPU code paths that use `reg`-prefixed offsets in later HDP generations. The address block name `aid_hdp_hdpdec` signals integration with multi-AID GPU register layouts where each AID may expose an HDP instance or address-space view.

## Risks

A major risk is mixing `mmHDP_*` and `regHDP_*` macro names across generations: the numeric offsets may look similar, but helper call sites and generated mask headers expect matching tokens. Another risk is assuming `READ_CACHE_INVALIDATE` exists because it does in 4.0 and 5.0; 4.4.2 omits it, and `hdp_v4_0_invalidate_hdp()` already skips HDP 4.4.2. Surface flag registers and `GPU_IOV_VIOLATION_LOG2` are version additions, so backporting field logic to 4.0 would reference undefined offsets.

## Test signals

Static validation should confirm that each `regHDP_*` offset has a matching field group in `hdp_4_4_2_sh_mask.h` where appropriate. Build validation should cover any platform code that includes this header. Runtime validation on HDP 4.4.2 hardware should exercise surface flag clear paths, MEM_POWER_CTRL power gating, MMHUB error reporting, and IOV violation logging with initiator ID read from `LOG2`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/hdp/hdp_4_4_2_offset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/hdp/hdp_4_4_2_sh_mask.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/hdp/hdp_4_4_2_sh_mask.h

## Purpose

`hdp_4_4_2_sh_mask.h` defines bit shifts and masks for the HDP 4.4.2 `aid_hdp_hdpdec` register map. It describes how fields inside the 4.4.2 AID HDP registers are packed, including newer surface flags, power-control fields, wider status fields, and split GPU IOV logging relative to HDP 4.0.

## Important APIs, types, and macros

The file is macro-only. Key field groups are:

- Widened traffic-level masks: `HDP_MMHUB_TLVL__HDP_WR_TLVL_MASK`, `HDP_RD_TLVL_MASK`, `XDP_WR_TLVL_MASK`, `XDP_RD_TLVL_MASK`, and `XDP_MBX_WR_TLVL_MASK` are 4-bit fields in this version.
- Surface access flags: `HDP_SURFACE_WRITE_FLAGS__SURF0/1_WRITE_FLAG`, `HDP_SURFACE_READ_FLAGS__SURF0/1_READ_FLAG`, and corresponding clear fields.
- Host path control fields: write/read stall timers, write-combine controls, 64-byte combine enable, and `ALL_SURFACES_DIS`. Unlike HDP 4.0/5.0 masks, this header does not define `WRITE_THROUGH_CACHE_DIS` or `LIN_RD_CACHE_DIS` for `HDP_HOST_PATH_CNTL`.
- `HDP_MISC_CNTL` fields for idle hysteresis, atomic buffer protection, raw address CAM, early write ack, simultaneous reads/writes, syshub priority, read-buffer watermark, SRAM ECC, FED/atomic FED, MMHUB burst, and pending write tag checks.
- `HDP_MEM_POWER_CTRL` fields for IPH and RC memory power control, light sleep, deep sleep, shutdown, idle hysteresis, power-up recovery delay, and power-down LS enter delay.
- `HDP_MMHUB_CNTL` fields with RO/GCC/SNOOP plus override bits.
- `HDP_CLK_CNTL` fields including IPH and RC memory clock soft overrides plus DBUS, dynamic, XDP, and HDP register clock overrides.
- XDP/P2P/mailbox/status fields, including 24-bit `HDP_XDP_BUSY_STS__BUSY_BITS_MASK`, `HDP_XDP_GPU_IOV_VIOLATION_LOG2__INITIATOR_ID`, and MMHUB error FED bits.

## Control flow

There is no executable code. Runtime control is in callers that expand these field macros via register helper macros. The naming convention remains `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK`, so consumers can use token-pasting helpers without spelling numeric masks directly.

## State and persistence behavior

The described fields cover persistent hardware state: surface and non-surface access flags, memory power gating modes, clock override state, MEMIO command/status fields, P2P BAR validity, sticky XDP bits, IOV violation status, and MMHUB response/error bits. Some fields are clear-on-write or write-one-to-clear style, so mask correctness matters for avoiding accidental loss of diagnostic state.

## Dependencies and integration points

This header pairs with `hdp_4_4_2_offset.h`. It also mirrors later HDP 5.x concepts such as `MEM_POWER_CTRL`, `GPU_IOV_VIOLATION_LOG2`, and richer clock override fields. Although no direct include of this file was found in the visible C sources, its layout is compatible with the AMDGPU `REG_SET_FIELD()`/`REG_GET_FIELD()` macro scheme and with AID-scoped register access patterns.

## Risks

Version skew is the central risk. HDP 4.4.2 differs from HDP 4.0 in traffic-level field width, host-path cache-disable fields, MEM_POWER register naming/layout, EDC counter width, busy status width, and IOV initiator placement. Reusing 4.0 masks on 4.4.2 would truncate fields or write undefined bits; reusing 4.4.2 masks on 4.0 would target fields not present there. Error and IOV fields are security/debug sensitive, so incorrect masks can misreport SR-IOV violations.

## Test signals

Expected signals include successful compilation of any AID HDP consumer, correct `REG_SET_FIELD()` expansion for `HDP_MEM_POWER_CTRL` and `HDP_CLK_CNTL`, working surface flag set/clear behavior, valid busy/sticky status readings, and IOV violation logs that preserve address/opcode/VF/VFID in `LOG` and initiator ID in `LOG2`. Static comparison against generated register XML or headers for HDP 4.4.2 is especially valuable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/hdp/hdp_4_4_2_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/hdp/hdp_5_0_0_offset.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/hdp/hdp_5_0_0_offset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/hdp/hdp_5_0_0_sh_mask.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/hdp/hdp_5_0_0_sh_mask.h

## Purpose

`hdp_5_0_0_sh_mask.h` defines the HDP 5.0.0 register field shifts and masks used by AMDGPU read-modify-write helpers. It is the field-level contract for the offsets in `hdp_5_0_0_offset.h` and is directly included by `hdp_v5_0.c`.

## Important APIs, types, and macros

The file defines no functions or structs. Important macro groups include:

- `HDP_MMHUB_TLVL__*` and `HDP_MMHUB_UNITID__*` fields, with 3-bit traffic-level masks as in HDP 4.0.
- Surface and non-surface read/write flag fields and clear fields.
- `HDP_HOST_PATH_CNTL` fields, including write-combine controls, `RD_CPL_BUF_EN`, `ALL_SURFACES_DIS`, `WRITE_THROUGH_CACHE_DIS`, and `LIN_RD_CACHE_DIS`.
- `HDP_READ_CACHE_INVALIDATE__READ_CACHE_INVALIDATE`, used by the invalidation path.
- `HDP_MISC_CNTL` fields for flush invalidate, idle hysteresis, multiple reads, raw address CAM, early write ack, FED/atomic FED, syshub priority, MMHUB burst, pending-write tag checks, and cacheline behavior.
- `HDP_MEM_POWER_CTRL` fields for IPH and RC memory power control, LS, DS, SD, idle hysteresis, power-up recovery, and power-down enter delays.
- `HDP_EDC_CNT` fields for four memory SED counters (`MEM0` through `MEM3`).
- `HDP_CLK_CNTL` fields for IPH/RC memory clock soft overrides plus DBUS, dynamic, XDP, and HDP register clock overrides.
- XDP/P2P and diagnostics fields, including 24-bit busy bits, IOV VFID mask `0x01F00000`, `GPU_IOV_VIOLATION_LOG2__INITIATOR_ID`, and MMHUB error response/NACK bits.

## Control flow

The file has no runtime branching. It enables call-site control flow in `hdp_v5_0.c`: `REG_SET_FIELD()` toggles `HDP_MEM_POWER_CTRL` fields in a defined order; clock-gating code masks `HDP_CLK_CNTL__*SOFT_OVERRIDE_MASK` values; init sets `HDP_MISC_CNTL__FLUSH_INVALIDATE_CACHE_MASK`; invalidation uses the read-cache invalidate field with the offset header.

## State and persistence behavior

The fields represent hardware state in HDP registers. Memory power gating and clock override fields persist until rewritten and control whether HDP SRAMs/clocks can enter LS/DS/SD or medium-grain clock gating. Cache and invalidation fields affect coherency state. Diagnostic fields capture sticky or status information for busy conditions, IOV violations, and MMHUB response errors.

## Dependencies and integration points

This header depends on `hdp_5_0_0_offset.h` for register addresses and on AMDGPU token-pasting register helper conventions. `hdp_v5_0.c` uses these masks with `REG_SET_FIELD()` and direct bitwise checks. The power-gating fields integrate with runtime `adev->cg_flags` and AMD power-management reporting, while the invalidate field integrates with KIQ/no-KIQ and ring write-register paths.

## Risks

Field layout errors can produce subtle runtime failures. The power-gating sequence must not enable multiple mutually exclusive LS/DS/SD modes at once, and wrong masks could do so. Clock override masks must match the bits cleared for MGCG; otherwise `get_clockgating_state()` can report false positives. `HDP_MISC_CNTL__FLUSH_INVALIDATE_CACHE_MASK` is a coherency-critical field. The VFID width differs from 4.4.2 (`0x01F00000` here versus `0x00F00000` there), so diagnostics must use the correct generation.

## Test signals

Compile-time validation should cover all `REG_SET_FIELD()` and bitwise mask users in `hdp_v5_0.c`. Runtime validation should toggle LS/DS/SD and MGCG, confirm clock-gating state reads back correctly, exercise HDP cache invalidation in direct and ring paths, and monitor IOV/MMHUB error decoding under SR-IOV and P2P workloads. Static generation-diff tests should compare masks against the HDP 5.0.0 register source.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/hdp/hdp_5_0_0_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/hdp/hdp_5_2_1_offset.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/hdp/hdp_5_2_1_offset.h -->
