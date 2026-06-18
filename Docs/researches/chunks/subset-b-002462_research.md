# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_sh_mask.h lines 32521-35035

## Scope And Purpose

This chunk is part of the generated AMD GC 10.1.0 register shift/mask header. It provides preprocessor constants for bit positions (`__SHIFT`) and bit masks (`_MASK`) used when amdgpu and amdkfd code programs or decodes memory-mapped graphics-core registers. The matching `gc_10_1_0_offset.h` file provides register addresses; this header provides field layout.

The requested range starts in the middle of `RLC_SPM_ACCUM_MODE`: the shift definitions and the first three masks for that register are in the previous chunk, while this chunk begins with the remaining masks for global/SE load override and automatic perfmon reset behavior. It then covers a large collection of performance-monitor selectors and result-control fields for RLC, RMI, GCR, UTCL1, PA_PH, GL1A, CHA, GUS, GC ATC L2, and GC VM L2 blocks. The range continues through the `gc_rlcdec`, `gc_rlcrdec`, and `gc_rlcsdec` address blocks, ending inside `RLC_RLCS_GE_FAST_CLOCK`; the remaining masks for that register and following RLCS boot/load/power registers are outside this chunk.

There are no functions, structs, branches, loops, or direct runtime side effects in this chunk. Its exported surface is generated macro metadata. Runtime behavior occurs only when driver code combines these masks and shifts with register addresses and uses helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_SOC15`, `RREG32_SOC15`, and related SOC15 accessors.

## Register Blocks Covered

The opening RLC SPM/perfmon area covers the tail of `RLC_SPM_ACCUM_MODE`, accumulation threshold/sample/write-count fields, SPM perfmon segment sizes for shader engines and global data, virtualization pause/status bits, generic RLC perfmon state/sample enable, RLC perfcounter event selects, GPU IOV performance-counter control/address/data windows, and perfmon clock state controls.

The chunk then defines performance-counter selectors for several graphics sub-blocks:

- `RMI_PERFCOUNTER*` and `RMI_PERF_COUNTER_CNTL` fields for request/memory-interface event selection, counter modes, CID/VMID filters, burst thresholding, soft reset, and SPM routing.
- `GCR_PERFCOUNTER*` fields for graphics-cache-router event selection and counter mode selection.
- `UTCL1_PERFCOUNTER*` fields for UTCL1 event and counter-mode selection.
- `PA_PH_PERFCOUNTER*` fields for primitive-assembler/primitive-hardware event selection across multiple counters and extended select registers.
- `GL1A_PERFCOUNTER*`, `CHA_PERFCOUNTER*`, and `GUS_PERFCOUNTER*` fields for GL1A, CHA, and GUS event selection, counter modes, masks, and mode configuration.

The `gc_gcatcl2pfcntldec`, `gc_gcvml2pldec`, `gc_gcvml2perfsdec`, and `gc_gcatcl2perfsdec` address blocks cover ATC L2 and VM L2 performance-counter configuration. These include per-counter event select fields, clamp/clear/reset behavior, result-control fields for selecting which counter result is exposed, and secondary selector/mode registers for the `PERFCOUNTER2_*` blocks.

The `gc_rlcdec` address block is the largest portion of the chunk. It defines RLC control, status, firmware, safe-mode, memory sleep, SMU handshake, timestamp, timer, interrupt, light-sleep/load-balance, clock-gating, power-gating, WGP status, SERDES, scratch/general-purpose, SPM, SRM, CSIB, PACE, SMU, scheduler, UTCL1, semaphore, CP EOF, prewalker, R2I, SPP, PCC stretch, SPM clock count, doorbell monitor, and related status fields.

The `gc_rlcrdec` block contains RLC SPP CAM and PACE scratch address/data windows. These are small indexed register windows: address fields select an entry or extension, and data fields carry the payload.

The `gc_rlcsdec` block covers RLCS decode/control/status fields. This includes decode start/dump address fields, exception registers, RLCS general registers, CGCG request/status, SMU GFXCLK status/control, SOC and GFX deep-sleep controls, GPM status mirrors, aborted power-down sequence status, DIDT force-stall state, IOV command/context/scheduler/VM-busy status, GPM status 2, GRBM soft reset, power-gating change/read mirrors, load-balance status/control, interrupt-handler semaphore/context fields, WGP status/read mirrors, CP and SPM interrupt ack/info registers, DSM trigger, and the beginning of GE fast-clock status/control.

## Important APIs, Types, And Macros

The important API is the generated macro naming convention:

- `<register>__<field>__SHIFT` gives the bit offset for a field in a 32-bit register.
- `<register>__<field>_MASK` gives the field mask.
- `// addressBlock: ...` comments identify generated register decode blocks.
- `//<register>` comments delimit generated register groups, but they are comments rather than compiled symbols.

The practical consumers are the AMD register helper macros and SOC15 register access paths. Code includes `gc/gc_10_1_0_offset.h` for addresses and `gc/gc_10_1_0_sh_mask.h` for field layouts, then reads, writes, or updates fields with helpers such as `REG_SET_FIELD` and `REG_GET_FIELD`. GC 10.1.0 include sites in this tree include `amdgpu/gfx_v10_0.c`, `amdgpu/gfxhub_v2_0.c`, `amdgpu/mxgpu_nv.c`, `amdgpu/sdma_v5_0.c`, `amdgpu/nv.c`, `amdgpu/amdgpu_amdkfd_gfx_v10.c`, and multiple amdkfd v10 queue/packet/MQD paths.

The chunk itself defines no C types. Its "types" are hardware field classes: single-bit strobes/status bits, narrow enum-like mode fields, event selector fields, VMID/CID/VFID filters, 32-bit data windows, low/high timestamp or counter halves, packed address/size fields, and reserved masks that document bits callers should not modify.

## Functional Field Groups

The RLC SPM accumulation fields describe how streaming performance monitor samples are accumulated and segmented. Threshold, requested sample count, data RAM write count, per-SE segment size, global segment size, pause request/status, and clock state fields are part of the low-level surface used to control and observe SPM capture. The chunk starts after some `RLC_SPM_ACCUM_MODE` definitions, so adjacent chunk data is needed for the full mode register.

The performance-counter selector groups configure which hardware events are counted. Repeated `PERF_SEL`, `PERF_SEL1`, `PERF_SEL2`, `PERF_SEL3`, `PERF_MODE*`, `CNTR_MODE`, and `COUNTER_MODE` fields are the packed selector/mode surfaces for RMI, GCR, PA_PH, GL1A, CHA, GUS, ATC L2, and VM L2 counters. Result-control fields select or reset exposed counter results, while mode fields control counting windows, masks, and SPM integration.

The RLC control and firmware fields expose high-level run-control state: RLC enable/idle/status, firmware version, safe-mode commands, RLCV and SMU safe-mode paths, SMU response/message/command/argument mailboxes, GPM thread reset/priority/enable, jump-table restore, and CP DMA complete indicators. These fields are tied to firmware boot, graphics microcontroller sequencing, and recovery.

The RLC timer, clock, and interrupt fields expose monotonic hardware counters and interrupt conditions. Timer interrupt registers, timer control/status, reference timestamp halves, GPU/GFX/ref clock count registers, capture strobes, 32-bit clock selection, SPM-specific clock count, PACE timer controls, interrupt status/disable/force fields, CP EOF/spare interrupts, and CP stat invalidation fields are all stateful diagnostic or synchronization surfaces.

The power-management and clock-gating fields cover RLC memory sleep, MGCG/CGCG/CGLS controls, clock-gating ramp controls, power-gating control/status/request/delay fields, dynamic/static WGP status, always-on/maximum/initial WGP masks, auto power-gating control, load-balance counters/configuration, SOC/GFX deep-sleep controls, SMU GFXCLK request/status/control, and PCC stretch hysteresis. These fields integrate RLC firmware behavior with GPU power and clock transitions.

The UTCL1/prewalker/error fields configure or report translation/cache behavior for RLC GPM and SPM paths. The chunk includes GPM and SPM UTCL1 control fields, UTCL1 status registers, SPM and GPM per-thread error fields, prewalker controls, trigger fields, prewalker address/size registers, and R2I controls.

The SPP fields configure shader/performance profiling state. They include `RLC_SPP_CTRL`, shader-profile enable masks, SSF capture enable and thresholds, inflight readback address/data, profile info, global shader ID and validity, status, private status registers, private-level maximum, stall-state update, PBB info, reset, CAM address/data windows, and extended CAM windows.

The SRM and indexed-window fields include SRM control/command/status/abort fields plus eight indexed control address/data pairs. These represent command and indirect-access surfaces where write order and selected index matter.

The RLCS fields expose the RLC slave/decode side of this hardware block: exception registers, general registers, clock-gating request/status, deep-sleep controls, GPM status mirrors, IOV command and VM-busy status, power-gating change/read mirrors, load-balance mirrors, interrupt-handler context assembly, CP/SPM interrupt acknowledge and info fields, DSM trigger, and GE fast-clock status. The final `RLC_RLCS_GE_FAST_CLOCK` register is incomplete in this chunk because only `FAST_CLKS_CHANGED_MASK` appears before the line boundary.

## Control Flow And State Behavior

This header has no direct control flow. It participates in runtime control flow through macro expansion: driver code reads a 32-bit register, masks/shifts fields into or out of local values, then writes the register back or interprets status. The same generated field names can be used in initialization tables, register dumps, interrupt handling, performance-counter setup, power-management sequences, and debug tooling.

The hardware state described by this chunk persists in GPU registers until changed by driver writes, firmware writes, reset, suspend/resume, virtualization context switching, or hardware events. Configuration state includes event selectors, counter modes, safe-mode commands, timer controls, clock-gating and power-gating enables, WGP masks, SPM/UTCL1/SPP settings, SRM indexed addresses, interrupt controls, and IOV perf counter addressing. Status state includes idle/busy bits, timer status, interrupt status, clock counts, write counts, error reports, GPM/RLCS status, VM-busy masks, power-gating change bits, load-balance flags, IH busy/credit state, and WGP activity.

Several groups are strobe-like or clear/ack sensitive. Safe-mode commands, timer clears, capture strobes, soft reset bits, interrupt acknowledge bits, DSM trigger, perf counter reset/clear fields, CP stat invalidation controls, SPP reset, and SRM abort/command bits should not be treated as durable ordinary configuration fields. A full-register write using stale values can accidentally retrigger, clear, or acknowledge hardware state.

Many groups are indirect or banked windows. SRM indexed address/data pairs, SERDES read/write index/data fields, SPP CAM address/data fields, PACE scratch address/data fields, and GPU IOV perf counter read/write address/data fields require correct address selection before data access. The masks are necessary but not sufficient; callers also need correct ordering and serialization around the selected index.

Virtualization-related fields are visible in the SPM pause path and GPU IOV/RLCS IOV status windows. These fields can reflect PF/VF ownership, VFID selection, per-VF counter IDs, scheduler-block state, or VM-busy state. In SR-IOV paths, stale or incorrectly selected VFID/CNT_ID fields can expose misleading counter data or disturb the wrong virtual function's accounting.

## Dependencies And Integration Points

This file must stay synchronized with `gc_10_1_0_offset.h`. The offset header defines the `mm...` register symbols and base indices; this file defines field masks and shifts for those registers. A missing or renamed field usually fails at compile time when referenced by register helper macros, while an incorrect numeric mask may compile but program the wrong hardware bits.

The main direct include site is `amdgpu/gfx_v10_0.c`, which includes this header and the matching offset header for GC 10 register programming, golden settings, register dumps, RLC firmware sequencing, clock/power handling, and debug paths. That file's register dump tables include RLC status entries such as `mmRLC_STAT`, `mmRLC_RLCS_GPM_STAT_2`, and nearby RLCS boot/load status, showing this generated namespace is part of user-visible diagnostics even when many fields are not individually hand-coded.

amdkfd v10 integration includes this header through queue, packet, MQD, and amdgpu-to-KFD support files. Those paths depend on the same GC 10 field namespace when programming compute queues, packet-manager state, and interrupt/context decoding for GFX10-family hardware.

`mxgpu_nv.c` includes the header for SR-IOV support. The GPU IOV perf counter fields and RLCS IOV status fields in this chunk are specifically relevant to virtualized GPU operation, where PF-side code may coordinate counters, scheduling blocks, command status, and per-VM busy state.

Performance tooling and debug paths integrate indirectly through the repeated perfmon/perfcounter field layout. The register blocks covered here provide event selection, mode programming, result selection, counter reset/clear, and readback selection for many GC sub-blocks. Even if a particular counter group has no high-level named helper in this tree, the generated masks are used by register access helpers, register dumps, debugfs-style tooling, or hardware-validation code that speaks the register names directly.

## Risks And Edge Cases

The primary risk is generated-header drift from the hardware specification or from the matching offset header. A wrong shift or mask can silently corrupt a neighboring field in the same 32-bit register. In this chunk that can break performance-counter selection, safe-mode sequencing, clock/power gating, WGP masks, UTCL1 error handling, SPP profiling, SRM indexed access, interrupts, or virtualization status accounting.

The chunk boundaries split logical registers. `RLC_SPM_ACCUM_MODE` is only completed here, and `RLC_RLCS_GE_FAST_CLOCK` is only started here. Any per-file summary must reconcile this report with adjacent chunks before claiming complete coverage for those registers.

Reserved masks are significant. Many registers expose large `RESERVED_MASK` regions, and code should use field helpers or read-modify-write patterns that preserve reserved bits unless the hardware programming guide explicitly says otherwise. This is especially important around power/clock controls, interrupt status registers, and firmware-visible command/status windows.

Performance-counter fields are dense and repeated. Small selector-width differences matter: for example some blocks use 9-bit selectors, others use 10-bit selectors, and mode fields occupy different high bits. Reusing a selector helper across blocks without the matching generated mask can truncate event IDs or overwrite mode bits.

Status and control bits often share nearby registers. Timer status, interrupt state, clock-capture state, power-gating change flags, load-balance flags, GPM status mirrors, and CP/SPM interrupt info require careful read/clear ordering. Tests that only check for successful writes may miss lost interrupts, stale status, or counters sampled in the wrong window.

Indirect windows are ordering-sensitive. SERDES, SRM, SPP CAM, PACE scratch, and IOV perf counter address/data pairs can produce valid-looking reads or writes against the wrong selected entry if callers race, skip barriers, or reuse a stale index. This risk is amplified in virtualization and debug tooling where multiple actors may inspect hardware state.

Power-management fields are timing-sensitive. RLC clock-gating, CGCG/CGLS ramping, memory sleep, dynamic WGP power state, deep sleep, SMU GFXCLK requests, and low-busyness controls can fail only around suspend/resume, reset, mode switches, or firmware transitions. Incorrect field definitions may surface as hangs, incomplete RLC boot, stuck busy/idle state, or intermittent power-management regressions.

## Test Signals

Build-time coverage should catch missing or renamed generated macros in GC 10 include sites such as `gfx_v10_0.c`, `gfxhub_v2_0.c`, `mxgpu_nv.c`, `sdma_v5_0.c`, and amdkfd v10 files. A useful static signal is that every field referenced by `REG_SET_FIELD`, `REG_GET_FIELD`, or SOC15 register-list macros resolves against the paired offset and sh/mask headers.

RLC firmware and reset validation should watch RLC idle/status, safe-mode completion, SMU response/message paths, GPM thread enable/reset behavior, CP DMA completion flags, GRBM soft reset behavior, and RLCS/GPM status mirrors. Regressions often appear as boot hangs, failed GPU reset, stuck safe mode, or RLC firmware not reaching expected idle states.

Power-management validation should exercise clock gating, memory sleep, WGP power-gating, dynamic PG request/status, load-balance counters, SMU GFXCLK request/status, SOC/GFX deep-sleep controls, and suspend/resume. Useful signals include no stuck busy bits, expected power-state transitions, no unexpected TC transaction errors, and stable behavior across repeated reset and runtime-PM cycles.

Performance-counter validation should program representative events across RLC, RMI, GCR, UTCL1, PA_PH, GL1A, CHA, GUS, ATC L2, and VM L2 counters. Tests should cover selector width, mode fields, counter reset/clear, result selection, SPM routing, low/high readback consistency, and counter behavior under known workloads.

SPM/SPP validation should cover SPM accumulation threshold/sample counts, pause/resume virtualization status, segment sizing, SPM interrupt status, SPM clock counts, SPP shader-profile enable masks, SSF capture thresholds, SPP inflight reads, CAM indexed access, and SPP reset. Good signals include expected sample counts, no accumulation overflow under normal programmed windows, and coherent profile readback.

Virtualization validation should exercise GPU IOV perf counter read/write address/data windows, VFID/CNT_ID selection, RLCS IOV command status, context-location size, scheduler block state, VM busy status, and IH context fields with SR-IOV enabled. Tests should verify that per-VF accounting and status are isolated and that pause/ack paths do not affect the wrong VF.

Interrupt and diagnostic tests should check CP/SPM interrupt ack/info registers, IH credit/busy state, RLC timer interrupts, CP EOF/spare interrupts, CP stat invalidation status/control, GE fast-clock change reporting, and DSM trigger behavior. Hardware register-spec cross-checks remain the strongest signal because this file is generated metadata and many errors compile cleanly while changing live hardware behavior.
