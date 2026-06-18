# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_offset.h lines 12438-13625

## Scope

This chunk is the tail of the generated AMD GC 10.3.0 register-offset header. It covers line 12438 through the file end at line 13625 and contains 1,150 preprocessor definitions: 1,027 register index/offset macros plus 123 `*_BASE_IDX` macros. The range starts mid-way through the `SDMA3_RLC5` queue register group, continues through complete `SDMA3_RLC6` and `SDMA3_RLC7` queue groups, and then defines several indirect address blocks: `gccacind`, `secacind`, `spmglbind`, `spmind`, `grtavfsind`, `spiind`, `sqind`, and `didtind`.

The file is declarative. It has no C functions, structs, enums, branches, loops, allocations, locks, or direct side effects. Its exported API is a generated macro namespace used by AMDGPU, KFD, power-management, debug, and performance-monitor code to address GC 10.3.0 MMIO or indexed registers without hard-coded numeric offsets.

## Purpose

`gc_10_3_0_offset.h` maps symbolic GC 10.3.0 register names to register indices and base-index selectors. Consumers pair these offsets with `gc_10_3_0_sh_mask.h` field definitions and AMDGPU register helpers such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_SOC15_IP`, `WREG32_SOC15_IP`, and plain `RREG32`/`WREG32` after computing a dynamic offset.

This slice describes three major hardware surfaces:

- SDMA3 compute/RLC queue registers for queue slots 5 through 7, including ring-buffer, indirect-buffer, doorbell, context-save, preemption, write-pointer polling, AQL, minor-pointer-update, and mid-command preemption state registers.
- GC current-average-current/power and performance-monitor indexed blocks, including CAC weights, accumulators, overrides, stall/release/power-break LUTs, fixed-pattern counters, shader-engine CAC control, global and per-shader-engine SPM sample-delay registers, and RTAVFS indexed registers.
- Shader/debug and dynamic power-control indexed blocks, including SQ wave debug state and TTMP/EXEC registers plus DIDT control, stall-pattern, EDC, throttle, and event-counter registers for SQ, DB, TD, and TCP.

## Exported API Surface

There are no callable APIs or local types. The public interface is the macro set itself:

- `mmSDMA3_RLC5_*`: the chunk begins after the start of this queue group. The visible portion includes IB control/read-pointer/offset/base/size, skip/context status, doorbell/status/log/watermark/offset, CSA address, IB remaining/preempt/dummy, write-pointer poll address, AQL control, minor pointer update, and `MIDCMD_DATA0` through `MIDCMD_DATA10` plus `MIDCMD_CNTL`.
- `mmSDMA3_RLC6_*` and `mmSDMA3_RLC7_*`: complete repeated SDMA RLC queue register groups. They include `RB_CNTL`, ring base high/low, ring read/write pointers high/low, write-pointer polling control and poll-address registers, read-pointer writeback address, IB control/base/size, context status, doorbell control and offset, queue status/log/watermark, CSA address, preemption, AQL control, minor-pointer update, and mid-command state registers.
- `*_BASE_IDX` macros for the visible SDMA3 queue registers: all visible SDMA3 entries use base index `2`, matching the GC base aperture selected by the SOC15 register helper layer for this SDMA instance window.
- `ixPCC_*`, `ixPWRBRK_*`, `ixEDC_*`, `ixGC_CAC_*`, `ixRELEASE_*`, `ixSTALL_*`, `ixFIXED_*`, and `ixHW_LUT_UPDATE_STATUS` in `gccacind`: indirect CAC/power-break/performance-monitor registers for GC-wide power estimation, stall/release pattern control, per-block weights, per-block accumulators, override values, and LUT update status.
- `ixSE_CAC_*` in `secacind`: shader-engine CAC identity/control/override selector/value registers.
- `ixGLB_*_SAMPLEDELAY` in `spmglbind`: global SPM sample-delay registers for CPG/CPC/CPF, GDS/GCR/PH/GE/GUS/CHA/CHC, ATCL2/VML2, SDMA0-3, GL2A/GL2C slices, EA0-15, and CHC/GE2SE paths.
- `ixSE_*_SAMPLEDELAY` in `spmind`: per-shader-engine sample-delay registers for SPI, SQG, CBR/DBR/PA, shader-array GL1/SX/CB/DB/SC/RMI/GL1C blocks, and WGP-local TA/TD/TCP instances for SA0 and SA1.
- `ixRTAVFS_REG0` through `ixRTAVFS_REG165` in `grtavfsind`: a dense RTAVFS indexed register bank.
- `ixSA_WGP_BLK_ID` in `spiind`: a single SPI indirect register identifying or selecting WGP block context.
- `ixSQ_*` and `ixSQ_WAVE_*` in `sqind`: SQ local debug status, wave active/valid state, wave mode/status/trap status, hardware IDs, GPR/LDS allocation, IB state, program counter, instruction word, flat scratch, scheduler mode, VGPR offset, shader cycle counter, TTMP0-15, `M0`, `EXEC_LO`, `EXEC_HI`, and shared interrupt-word aliases.
- `ixDIDT_SQ_*`, `ixDIDT_DB_*`, `ixDIDT_TD_*`, and `ixDIDT_TCP_*` in `didtind`: DIDT control, OCP, stall/tuning/auto-release, stall patterns, MPD scale, stall-release controls, weights, EDC controls/thresholds/patterns/timers/delays/status/overflow/rolling-power-delta/PCC counters, throttle controls, and final per-block stall event counters.

## Control Flow And State Behavior

This header has no local control flow. Runtime behavior appears only when included driver code uses the macros to build MMIO addresses or indexed-register accesses.

The SDMA queue macros describe persistent hardware queue state. KFD and AMDGPU code programs an SDMA RLC queue by computing an engine base plus `queue_id * (mmSDMA0_RLC1_RB_CNTL - mmSDMA0_RLC0_RB_CNTL)`, disabling `RB_ENABLE`, waiting for `CONTEXT_STATUS` idle, programming doorbell offset/enable, ring read/write pointers, ring base, read-pointer writeback address, and then re-enabling the queue. Pointer state, doorbell routing, CSA addresses, AQL mode, preemption state, and mid-command data remain in hardware until queue teardown, reset, suspend/resume restore, firmware/PF intervention, or later writes.

The CAC, SPM, RTAVFS, SQ, and DIDT macros describe indexed register banks rather than plain per-file data. Their state is held in hardware power, performance, debug, and shader-control blocks. Typical access goes through register helper paths that select an indirect index aperture and then read or write the indexed data. Names such as `*_STATUS`, `*_PERF_COUNTER`, `*_OVERFLOW`, `*_ACTIVE`, and `*_VALID_AND_IDLE` imply readback/counter/debug semantics, while `*_CTRL`, `*_CNTL`, `*_TUNING_CTRL`, `*_SAMPLEDELAY`, `*_WEIGHT*`, `*_OVRD*`, and `*_PATTERN*` are configuration-oriented. Exact read-only, write-one-clear, sticky, reset, and ownership semantics are not encoded in this offset header and must be taken from the hardware register database plus caller behavior.

## Dependencies And Integration Points

The syntactic dependency is only the C preprocessor. Semantically, this chunk must stay aligned with the matching GC 10.3.0 bitfield and reset-value headers:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_sh_mask.h`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_default.h`

Important consumers and integration points in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v5_2.c`, which includes this offset header for GC 10.3.0 SDMA setup. The file programs SDMA ring pointers, write-pointer polling, doorbells, ring bases, firmware loading, halt/unhalt, context-switch control, and ring tests. Its register-offset helper maps logical SDMA instances onto the correct GC base aperture and internal offset.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v10_3.c`, which includes this header and computes SDMA RLC queue offsets from `mmSDMA0_RLC0_RB_CNTL`, `mmSDMA1_RLC0_RB_CNTL`, `mmSDMA2_RLC0_RB_CNTL`, `mmSDMA3_RLC0_RB_CNTL`, and queue spacing. That pattern is the direct integration model for the `mmSDMA3_RLC5` through `mmSDMA3_RLC7` offsets in this chunk.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_v10.c` and related KFD MQD managers, which use the matching SDMA RLC bitfields to encode queue size, VMID, read-pointer writeback, doorbell offsets, and queue privilege state before AMDGPU writes the corresponding registers.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v2_1.c`, which includes the GC 10.3.0 generated namespace for GFXHUB/GC VM programming elsewhere in the same header family.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/vangogh_ppt.c`, which includes this offset header for GC 10.3.0 power-management integration.
- Older PM/DPM paths such as `kv_dpm.c`, `smu7_powertune.c`, and `vega10_powertune.c` show the same `ixDIDT_*` conceptual integration pattern through DIDT indexed-register helpers, even though those files target other ASIC generations.

At a hardware level, these macros tie into SDMA queue bring-up/teardown, KFD process queues, doorbell aperture management, SR-IOV PF/VF register ownership, firmware restore, suspend/resume, performance monitoring, power tuning, wave debug, and fault/hang diagnostics.

## Risks

- Generated-header drift is the main risk. A single wrong SDMA3 queue offset or base index can write the wrong queue slot, wrong SDMA instance, or unrelated GC register.
- The visible SDMA groups are highly repetitive and are often addressed by arithmetic spacing. If queue spacing differs from the assumed `RLC1 - RLC0` pattern or if one queue macro is out of sequence, only some queues may fail, making the bug workload- and queue-id-dependent.
- The chunk starts inside `SDMA3_RLC5`, so local completeness checks must not flag the missing beginning of that group as a defect in this chunk.
- Doorbell, read/write pointer, ring base, and pointer-poll address registers are DMA control-plane state. Bad offsets can cause silent queue stalls, writes to stale rings, wrong process signaling, or memory corruption.
- `MINOR_PTR_UPDATE`, `PREEMPT`, `CSA_ADDR_*`, `IB_SUB_REMAIN`, and `MIDCMD_*` registers interact with preemption and context-save/restore. Incorrect addressing can break queue eviction, reset recovery, or mid-command preemption after a timeout.
- SDMA RLC registers may be PF- or firmware-owned in SR-IOV and some reset/power states. Bare-metal sequences in AMDGPU explicitly avoid some writes for VFs; using these offsets from the wrong ownership context can conflict with PF/SMU control.
- CAC, DIDT, PWRBRK, and RTAVFS registers influence power estimation, throttling, and adaptive voltage/frequency behavior. Wrong indices may not fail at compile time but can cause throttling regressions, unstable clocks, performance loss, or thermal/power-limit anomalies.
- SQ wave debug registers are sensitive to selected shader/queue/wave context. Reading or writing them without the correct debug selection/locking path can produce misleading diagnostics or disturb wave state.
- Many `ix*` registers are indirect. Confusing indirect offsets with direct MMIO offsets, or using the wrong indirect aperture helper, can address the wrong register block even when the macro value is numerically correct.

## Test Signals

Useful validation is mostly build-time, generated-data, and hardware-integration oriented:

- Compile or preprocess AMDGPU/KFD code paths that include `gc_10_3_0_offset.h`, `gc_10_3_0_sh_mask.h`, and `gc_10_3_0_default.h`.
- Generated-header checks that every complete visible `mmSDMA3_RLC6_*` and `mmSDMA3_RLC7_*` offset has the expected `*_BASE_IDX`, that offset order and queue spacing are monotonic, and that the `SDMA3_RLC5` start is treated as a chunk-boundary exception.
- Cross-check this chunk against the GC 10.3.0 register database and matching sh/mask/default headers for name, offset, base-index, and field-definition alignment.
- KFD SDMA queue tests on GC 10.3.0-class ASICs: create queues across engines and queue ids including higher RLC slots, submit copies, exercise doorbells, poll read/write pointer progression, then destroy and recreate queues.
- Reset, suspend/resume, GPU timeout recovery, and queue eviction tests that verify SDMA RLC state is stopped, saved, restored, and re-enabled correctly.
- SR-IOV VF/PF tests that confirm VF paths avoid PF-owned SDMA/power registers and that allowed doorbell/wptr paths still work.
- Power/performance validation for CAC, DIDT, PWRBRK, SPM, and RTAVFS paths: confirm counters read sanely, sample-delay programming affects expected streams, and power/throttle behavior remains stable under graphics and compute load.
- Wave-debug diagnostics that read `ixSQ_WAVE_*` state under controlled queue selection and verify PC, EXEC, TTMP, mode/status, and trap status are coherent during hangs or debug capture.

## Chunk Notes For Merge

This document is intentionally source-tree aligned and covers only lines 12438-13625 of `gc_10_3_0_offset.h`. Earlier chunks should cover the beginning of `SDMA3_RLC5` and all preceding GC 10.3.0 register blocks. The final per-file report should treat the whole file as a generated GC 10.3.0 register offset map used by AMDGPU, KFD, PM/SMU, debug, and performance-monitoring paths, not as handwritten executable logic.
