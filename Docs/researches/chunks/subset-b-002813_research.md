# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_3_3_0_sh_mask.h lines 1-2363

## Purpose

This chunk is the first portion of the generated MMHUB 3.3.0 shift/mask header used by the AMDGPU driver. It defines C preprocessor constants for bit positions and bit masks in MMHUB hardware registers, with this range focused on the `mmhub_dagbdec` address block and specifically the `DAGB0` data/address global block (DAGB) read/write client arbitration, bandwidth, credit, status, and initial performance counter fields.

The file has no executable logic, storage, or type definitions. Its purpose is to provide exact register-field encodings for `REG_SET_FIELD()`, `REG_GET_FIELD()`, direct mask composition, and register read/modify/write paths in the MMHUB v3.3 code. The paired offset header gives register addresses; this header gives the bit layout inside those registers.

## Important APIs, Types, And Macros

The public surface is entirely macro constants:

- Include guard: `_mmhub_3_3_0_SH_MASK_HEADER`.
- Repeated field encoding pattern: `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`.
- Read client registers: `DAGB0_RDCLI0` through `DAGB0_RDCLI30`.
- Write client registers: `DAGB0_WRCLI0` through `DAGB0_WRCLI30`.
- Read and write global DAGB controls: `DAGB0_RD_CNTL`, `DAGB0_WR_CNTL`, `DAGB0_RD_IO_CNTL`, `DAGB0_WR_IO_CNTL`, `DAGB0_RD_GMI_CNTL`, `DAGB0_WR_GMI_CNTL`.
- DAGB topology and clock controls: `DAGB0_RD_ADDR_DAGB`, `DAGB0_WR_ADDR_DAGB`, `DAGB0_WR_DATA_DAGB`, `DAGB0_RD_CGTT_CLK_CTRL`, `DAGB0_WR_CGTT_CLK_CTRL`, `DAGB0_L1TLB_RD_CGTT_CLK_CTRL`, `DAGB0_L1TLB_WR_CGTT_CLK_CTRL`.
- Per-client burst/timer packing registers: `DAGB0_*_MAX_BURST0..3` and `DAGB0_*_LAZY_TIMER0..3` for read address, write address, and write data paths.
- Virtual-channel controls: `DAGB0_RD_VC0_CNTL` through `DAGB0_RD_VC5_CNTL`, `DAGB0_WR_VC0_CNTL` through `DAGB0_WR_VC5_CNTL`, plus IO/GMI VC controls.
- Credit/status/override registers: TLB credits, storage pool credits, write data and atomic FIFO credits, pending busy bitmaps, no-allocate overrides, GPU snoop overrides, FIFO/credit full and empty status.
- Miscellaneous controls: `DAGB0_DAGB_DLY`, `DAGB0_CNTL_MISC`, `DAGB0_CNTL_MISC2`.
- Performance counter start of range: `DAGB0_PERFCOUNTER_LO`, `DAGB0_PERFCOUNTER_HI`, and the beginning of `DAGB0_PERFCOUNTER0_CFG` through `ENABLE_MASK` at line 2363. The rest of the performance counter configuration is outside this chunk.

The most common client field layout appears in every `DAGB0_RDCLI*` and `DAGB0_WRCLI*` macro family:

- `VIRT_CHAN`: 3-bit virtual channel selector.
- `CHECK_TLB_CREDIT`: single-bit TLB-credit gating.
- `URG_HIGH` and `URG_LOW`: urgency thresholds.
- `MAX_BW_ENABLE` and `MAX_BW`: maximum bandwidth limiter enable/value.
- `MIN_BW_ENABLE` and `MIN_BW`: minimum bandwidth reservation enable/value.
- `OSD_LIMITER_ENABLE` and `MAX_OSD`: outstanding-request limiter enable/value.

## Control Flow

There is no runtime control flow in this header. Control flow is created by code that includes it, notably `drivers/gpu/drm/amd/amdgpu/mmhub_v3_3.c`, which includes both `mmhub_3_3_0_offset.h` and this shift/mask header. That implementation uses the constants through AMDGPU register helpers such as `REG_SET_FIELD()`, `REG_GET_FIELD()`, `RREG32_SOC15()`, `WREG32_SOC15()`, and offset variants.

For this chunk, the effective control pattern is:

1. A caller reads or prepares a 32-bit MMHUB register value.
2. The caller uses a `*_MASK` to clear, test, or isolate a field.
3. The caller uses a `*__SHIFT` to position field values, usually indirectly through `REG_SET_FIELD()` or `REG_GET_FIELD()`.
4. The caller writes the composed value back to the MMHUB register.

For example, clock-gating and light-sleep control paths in `mmhub_v3_3.c` use fields from this header such as `DAGB0_CNTL_MISC2__DISABLE_RDRET_TAP_CHAIN_FGCG_MASK` and `DAGB0_CNTL_MISC2__DISABLE_WRRET_TAP_CHAIN_FGCG_MASK` when enabling or disabling fine-grain clock gating behavior.

## State And Persistence Behavior

The header itself is stateless and persistent only as source-code metadata. The state it describes lives in MMHUB hardware registers:

- Client arbitration state: virtual-channel assignment, urgency thresholds, bandwidth windows, outstanding depth limits, and TLB-credit checks.
- DAGB routing/configuration state: read address, write address, and write data DAGB enablement, jump-ahead behavior, self-initialization disablement, `WHOAMI`, and write/read jump mode where defined.
- Clock and power state: CGTT on-delay, off-hysteresis, light-sleep assertion hysteresis, minimum memory-gated light sleep, CGLS/LS disables, and busy overrides.
- Credit state: TLB credits, storage pool credits, write data burst credits, atomic credits, data FIFO credits, and atomic FIFO credits.
- Diagnostic state: pending busy bitmaps, FIFO empty/full masks, credit fullness masks, delay injection selector fields, parity controls, and performance counter fields.

Any values programmed with these macros persist in device registers until reset, reprogramming, power-state transitions, or firmware/hardware ownership changes. Driver initialization, suspend/resume, GPU reset, power-management, and fault-recovery paths must assume register contents can change across those events and reapply required programming.

## Dependencies And Integration Points

Primary integration points:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v3_3.c` includes this header for MMHUB 3.3 register-field definitions.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_3_3_0_offset.h` supplies the matching register offsets. The shift/mask constants are only meaningful when paired with the corresponding `reg*` address macros.
- SOC15 register helpers in AMDGPU provide the read/write abstraction and field manipulation contracts.
- Client-ID tables in `mmhub_v3_3.c` align with the read/write client index space exposed here, especially the `DAGB0_RDCLI*` and `DAGB0_WRCLI*` per-client register families.
- MMHUB power, clock-gating, VM, fault, and performance paths rely on consistent field names across generated ASIC headers.

The macro naming is hardware-generated and tightly coupled to the AMD register specification. It is not a stable userspace API.

## Risks And Edge Cases

- Bitfield drift risk: any incorrect shift or mask can silently program the wrong hardware field. This can affect memory translation, client arbitration, power management, or fault handling.
- Cross-header coupling: using masks from this header with offsets from a different MMHUB generation can compile but target incompatible bit layouts.
- Partial-chunk boundary: line 2363 stops in the middle of `DAGB0_PERFCOUNTER0_CFG`; later performance counter fields and later address blocks are intentionally outside this research chunk.
- Repetition risk: the large `RDCLI*`, `WRCLI*`, burst, and lazy-timer families are mechanically repeated. Manual edits are high risk because a single outlier may be hard to notice in review.
- Register ownership risk: some fields are diagnostics or overrides (`*_BUSY_OVERRIDE`, `*_NOALLOC_OVERRIDE`, `*_GPU_SNOOP_OVERRIDE`, parity controls). Setting them outside hardware-recommended sequences can mask hangs, change cache/coherency behavior, or suppress useful error signaling.
- Width risk: all masks are expressed as 32-bit `L` constants. Callers should treat them as 32-bit register values and avoid signed arithmetic assumptions.

## Test Signals

Useful validation signals for this chunk are mostly compile-time and hardware-behavior oriented:

- Build coverage for MMHUB v3.3 targets: the generated macros must compile when included by `mmhub_v3_3.c`.
- Register programming review: `REG_SET_FIELD()` and `REG_GET_FIELD()` uses should resolve to the intended mask/shift pair and not to a similarly named field from another ASIC header.
- Power-management tests: clock-gating and light-sleep paths should toggle the expected `DAGB0_CNTL_MISC2` and `*_CGTT_CLK_CTRL` bits without regressions in suspend/resume or runtime power transitions.
- GPU reset and VM initialization tests: reset paths should reinitialize DAGB/L1TLB-related fields needed after hardware reset.
- Fault and hang diagnostics: pending-busy, FIFO status, parity, and credit-full registers should remain readable and meaningful in debug dumps.
- Performance counter tests: counter low/high and counter configuration fields should expose coherent counter values once the rest of the `DAGB0_PERFCOUNTER*` macros from later lines are included by the final merged research.

## Chunk Scope Notes

The source file is larger than this work item. This document covers only lines 1-2363, which comprise the file prologue and most of the `mmhub_dagbdec` `DAGB0` register-field definitions up through the start of `DAGB0_PERFCOUNTER0_CFG`. Later `DAGB0` perf fields, SDP fields, and MMHUB MMU/L1TLB/L2TLB address blocks are outside this chunk and should be reconciled by the later merge lane with their corresponding chunk documents.
