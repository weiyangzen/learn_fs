# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gca/gfx_8_1_sh_mask.h lines 1-4615

## Scope

This chunk is the opening slice of the generated AMD GFX 8.1 shift/mask register header. It contains the MIT-style AMD copyright header, include guard, and 4,590 `#define` entries through line 4615. The macro convention is the generated AMD register style:

- `REGISTER__FIELD_MASK` gives the 32-bit mask for a register field.
- `REGISTER__FIELD__SHIFT` gives the bit shift for the same field.

Within the requested range there are 644 distinct generated register names, dominated by 1,780 `CB*` color-buffer definitions and 2,629 `CP*` command-processor definitions. The range starts with complete color-buffer blend/render-target state and then moves into command processor ring, interrupt, queue, DMA, coherency, performance, and HQD/MQD queue-management state. It ends at `CP_HQD_HQ_STATUS1__STATUS_MASK`; the matching `__SHIFT` and following HQD EOP fields are outside this chunk.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU DRM hardware metadata. It does not implement Ceph or distributed filesystem logic.

## Purpose

`gfx_8_1_sh_mask.h` is a compile-time hardware ABI description for GFX 8.1-class AMD graphics blocks. Driver code uses these constants to compose, preserve, or decode fields in 32-bit MMIO registers and command processor state. The constants are intentionally declarative: they encode bit positions and masks, while runtime code supplies register offsets, values, ordering, and access methods.

This chunk covers two major hardware surfaces:

- Color Buffer (`CB`) register fields for blend constants, blend control, render-target base addresses, tile pitch/slice/view layout, color format metadata, CMASK/FMASK/DCC metadata, target masks, shader export masks, CB hardware controls, CB performance counters, clock-gating control, and CB debug buses.
- Command Processor (`CP`, `CPC`, `CPG`, `CPF`, `COHER`, `SCRATCH`) fields for ring buffers, read/write pointers, interrupts, doorbells, microcode ports, clock/power controls, MEC pipe status, performance counters, EOP/fence/stat counters, scratch and append data, atomics, semaphores, coherency, DMA, indirect buffers, stalled/busy/status diagnostics, and the beginning of HQD/MQD queue state.

## Important API Surface

There are no C functions, structs, enums, inline helpers, global variables, or callbacks in this chunk. The macro namespace is the exported API.

Important color-buffer families include:

- `CB_BLEND_RED/GREEN/BLUE/ALPHA`, `CB_COLOR_CONTROL`, and `CB_BLEND0_CONTROL` through `CB_BLEND7_CONTROL`, which describe blend constants, ROP mode, source/destination blend factors, color/alpha combine functions, separate-alpha blending, per-target blend enable, and ROP3 disable bits.
- `CB_COLOR0_BASE` through `CB_COLOR7_BASE`, `CB_COLORn_PITCH`, `CB_COLORn_SLICE`, and `CB_COLORn_VIEW`, which describe render-target base addresses and tile/slice/view bounds.
- `CB_COLORn_INFO`, which packs endian, format, number type, component swap, fast clear, compression, blend clamp/bypass, simple float, round mode, CMASK layout, blend optimization hints, FMASK compression policy, DCC enable, and CMASK address type for each MRT slot.
- `CB_COLORn_ATTRIB`, `CB_COLORn_DCC_CONTROL`, `CB_COLORn_CMASK`, `CB_COLORn_FMASK`, `CB_COLORn_CLEAR_WORD0/1`, and `CB_COLORn_DCC_BASE`, which define tiling, sample/fragment count, destination alpha forcing, DCC block sizing, key clear, color transform, lossy precision, and metadata surface base/clear state.
- `CB_TARGET_MASK` and `CB_SHADER_MASK`, which provide per-target/per-output component enables for render-target writes and shader exports.
- `CB_HW_CONTROL`, `CB_HW_CONTROL_1`, `CB_HW_CONTROL_2`, `CB_HW_CONTROL_3`, and `CB_DCC_CONFIG`, which tune or disable internal CB optimizations, cache eviction points, FIFO depths, overwrite-combiner behavior, DCC cache sizing, and documented hardware workaround bits.
- `CB_PERFCOUNTER_FILTER`, `CB_PERFCOUNTER*_SELECT`, `CB_PERFCOUNTER*_LO/HI`, `CB_CGTT_SCLK_CTRL`, and `CB_DEBUG_BUS_1` through `CB_DEBUG_BUS_22`, which expose CB profiling, clock-gating, busy, stall, compression, fragment, cache, and internal handshake status fields.

Important command-processor families include:

- `CP_DFY_*` data/address/command/status fields for the DFY block, including policy, memory type, LFSR reset, mode, enable, address, data lanes, offset, size, busy, and pending-tag state.
- `CP_RB*` and `CP_RB*_CNTL` fields for graphics ring buffer base, high address, buffer/block sizing, memory type, byte swap, minimum availability, cache policy, no-update mode, and read-pointer writeback enable.
- `CP_RB*_RPTR_ADDR*`, `CP_RB*_WPTR`, `CP_RB_WPTR_POLL_ADDR*`, `CP_RB_DOORBELL_CONTROL`, and doorbell range fields, which connect software ring pointers and doorbells to CP scheduling.
- `CP_INT_CNTL`, `CP_INT_CNTL_RING0/1/2`, `CP_INT_STATUS`, `CP_INT_STATUS_RING0/1/2`, `CPC_INT_CNTL`, `CP_MEx_PIPEn_INT_CNTL`, and matching status/debug families. These define interrupt enables/status for VM doorbells, ECC, wait-reg-mem timeouts, context busy/empty, gfx idle, privileged instruction/register access, opcode errors, timestamps, reserved-bit errors, dequeue requests, query status, and SUA violations.
- `CP_DEVICE_ID`, priority counters, pipe priorities, VMID, endian, microcode address/data ports, clock-gating controls, power controls, memory sleep controls, ECC first-occurrence fields, and write-pointer polling controls.
- `CP_CPC_STATUS`, `CP_CPC_BUSY_STAT`, `CP_CPF_STATUS`, `CP_CPF_BUSY_STAT`, `CP_STALLED_STAT*`, `CP_BUSY_STAT`, `CP_STAT`, `CP_CNTX_STAT`, and related free-count/header-dump fields. These are diagnostic fields for CP/CPC/CPF/MEC state machines, busy sources, stalls, queue availability, and command fetch state.
- `CP_CE/PFP/ME/MEC*_PRGRM_CNTR_START` and interrupt routine start fields, context control, wait timers, VMID reset/preempt/status, instruction cache base/control fields, and MEC halt/step/reset controls.
- `CPG_PERFCOUNTER*`, `CPC_PERFCOUNTER*`, and `CPF_PERFCOUNTER*` selector/data fields for command processor performance monitoring.
- `CP_EOP_DONE_*`, stream-out, primitive count, pipe stats, scratch registers, append/fence registers, atomic pre-operation registers, CP memory read/write address/data registers, semaphore wait/signal fields, and wait-reg-mem timeout fields.
- `CP_COHER_CNTL`, `CP_COHER_*`, and `COHER_DEST_BASE*`, which describe cache/coherency action bits for TC, TCL1, CB, DB, shader caches, destination-base windows, coherency size/base, and coherency status.
- `CP_DMA_ME_*`, `CP_DMA_PFP_*`, `CP_DMA_CNTL`, and `CP_DMA_READ_TAGS`, which describe CP DMA source/destination addresses, memory type, ATC/cache policy, source/destination selection, byte count, endian swap, address increment controls, raw wait, FIFO status, and read-tag validity.
- `CP_PFP_IB_CONTROL`, `CP_PFP_LOAD_CONTROL`, IB/RB/CE offsets, IB base/buffer-size fields, metadata bases, indirect draw/dispatch bases, index base/type, GDS backup base, sample status, ROQ/STQ/MEQ/CEQ thresholds and availability, and command index/data fields.
- `CP_HPD_*`, `CP_MQD_BASE_ADDR*`, `CP_HQD_ACTIVE`, `CP_HQD_VMID`, `CP_HQD_PERSISTENT_STATE`, `CP_HQD_PQ_*`, `CP_HQD_IB_*`, `CP_HQD_IQ_TIMER`, dequeue/offload/semaphore/message fields, HQD atomic preops, and the first HQ scheduler/status/control fields. These are queue and memory queue descriptor fields used by compute/graphics queue management.

## Control Flow

The header has no executable control flow. Its only compile-time flow is C preprocessor inclusion guarded by `GFX_8_1_SH_MASK_H`.

The implied runtime flow in consumers is:

1. ASIC-specific driver code includes this generated shift/mask header and the matching register address/value definitions used by that code path.
2. A caller selects a register, often through generated `reg*` symbols, packet definitions, or a ring/MMIO register table.
3. The caller uses helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, direct mask/shift operations, SOC15-style MMIO helpers, or command packet emission to pack or decode a register value.
4. Hardware state is written, read, polled, or interpreted by AMDGPU/KFD queue, graphics, interrupt, profiling, debug, or reset logic.

Loops and branching are therefore outside this file. Repeated families such as `CB_COLOR0..7`, `CB_BLEND0..7`, `CP_RB0..2`, `CP_ME1/ME2_PIPE0..3`, and `CP_HQD_*` imply indexed driver logic, but this chunk only provides the bit layout each iteration would use.

## State And Persistence Behavior

The macros themselves are stateless compile-time constants. The state they describe is persistent hardware state until changed by command submission, MMIO writes, firmware, context save/restore, power management, reset, or hardware progress.

CB render-target fields are graphics context state. Surface base addresses, tile dimensions, view ranges, formats, compression flags, CMASK/FMASK/DCC metadata bases, clear words, target masks, shader masks, and blend controls can persist across draws in a context until the command stream or context restore changes them. Incorrect fields can corrupt render-target memory or produce valid-looking but wrong pixels.

CB hardware-control, DCC, debug, clock-gating, and performance-counter fields are lower-level configuration or observation state. Some values tune internal FIFOs, cache tags, overwrite combiners, and workarounds. Debug bus and performance counter registers reflect live hardware conditions and may change while being sampled.

CP ring and queue fields represent active command-submission state: ring base addresses, read/write pointers, doorbell range/control, pointer polling, queue priorities, VMID assignment, HQD active state, PQ/IB/IQ pointers, dequeue requests, and persistent-state bits. These values affect which command buffers hardware consumes and which VMID/queue owns execution.

CP interrupt, status, stalled, busy, and ECC fields describe hardware-reported state. Some bits may be sticky, write-one-to-clear, latched, or read-clear according to the hardware spec, but that access policy is not encoded in this header.

Coherency, semaphore, DMA, EOP, append, atomic, scratch, and indirect-buffer fields describe command processor side effects and synchronization surfaces. Values can point at GPU memory, trigger cache actions, report fence/completion data, control waits, or drive CP DMA transfers. Ordering, alignment, and timeout rules are properties of the consuming code and hardware, not the macro definitions.

## Dependencies And Integration Points

This file depends syntactically only on the C preprocessor. Semantically, it depends on AMD's generated GFX 8.1 register database and must remain synchronized with the corresponding register address and enum/value definitions. In this source tree the immediate sibling `gfx_8_1_enum.h` provides generated field values, while this header provides bit masks and shifts.

A direct include search in the current mirror found only the header itself, so this specific GFX 8.1 `gca` header may be retained generated inventory rather than an actively included path in the mirrored kernel subset. The macro names still match the standard AMDGPU/KFD register-helper pattern used throughout nearby ASIC generations.

Integration points for the macro contract include:

- AMDGPU register helper macros such as `REG_SET_FIELD` and `REG_GET_FIELD`, which rely on the `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT` naming convention.
- MMIO and command-submission paths that write registers or packet payloads for CB render state, CP ring setup, interrupt enables, queue descriptors, coherency actions, EOP/fence reporting, and DMA/semaphore commands.
- KFD/MQD queue-management code patterns that populate `cp_hqd_pq_control`, HQD VMID, PQ/IB bases, doorbell controls, and persistent-state fields using the same CP_HQD macro families in VI and later ASIC managers.
- Profiling and debug paths that select and sample CB/CP/CPC/CPG/CPF performance counters, stalled/busy/status fields, debug bus outputs, and header dumps.
- Reset, suspend/resume, firmware, and bring-up paths that must restore or reinitialize ring buffers, microcode ports, CP power/clock settings, interrupt masks, VMID state, and queue descriptors.

## Risks And Edge Cases

- Bitfield drift is the central risk. A wrong mask or shift compiles normally but can program unrelated hardware bits, causing rendering corruption, queue hangs, lost interrupts, bad cache coherency, or misleading diagnostics.
- This chunk is boundary-partial. It includes the include guard as a `#define`, and it ends with only `CP_HQD_HQ_STATUS1__STATUS_MASK`; the matching shift and later HQD EOP fields are in the next chunk.
- Repeated register families are vulnerable to one-slot copy or generation errors. CB slots 0-7, blend controls 0-7, ME pipe interrupt blocks, ring buffer variants, and HQD queue fields can fail only on specific targets or queues.
- Address fields often encode aligned addresses, not raw byte pointers. Examples include 256-byte color/DCC/CMASK/FMASK bases, 4-byte or 8-byte-aligned CP pointer/report addresses, and high/low address splits. Consumers must preserve required alignment and high bits.
- Reserved and workaround-style fields such as `CHICKEN_BITS`, `RESERVED`, `OBSOLETE`, `RSV_*`, and generated typo-compatible names must not be cleaned up casually. Renaming a generated macro can break consumers even when the name looks wrong.
- CP coherency, DMA, semaphore, EOP, and wait fields are sequencing-sensitive. This header does not encode required fences, polling loops, timeout policy, cache flush ordering, or engine ownership.
- Status and control fields are interleaved in the same namespace. Debug/status names may be passive reads, while reset, halt, step, dequeue, offload, interrupt-enable, cache-action, or DMA command bits can have side effects.
- Low/high counter pairs and live status registers can race hardware updates. The header gives field positions only; coherent sampling requires caller-side latching or retry logic.

## Test And Validation Signals

- Build coverage should compile any active AMDGPU/KFD paths that include the GFX 8.1 generated headers or use same-generation generated macro names. Missing or renamed macros should fail at compile time.
- Generated-data validation should compare all line 1-4615 definitions with AMD's authoritative GFX 8.1 register database, including mask/shift pairing, mask alignment to shift, and repeated-family completeness.
- Boundary validation should verify that `CP_HQD_HQ_STATUS1__STATUS_MASK` is intentionally unpaired in this chunk and paired by the following chunk before final per-file reconciliation.
- Graphics runtime testing should cover multi-render-target blending, ROP modes, color write masks, shader export masks, fast clears, DCC, CMASK/FMASK, MSAA sample/fragment layouts, mip/slice views, and context restore.
- CP runtime testing should cover ring initialization, read/write pointer reporting, doorbell writes, interrupt enable/status paths, privileged/opcode error handling, VMID reset/preempt, MEC pipe scheduling, and queue priority behavior.
- Synchronization and memory tests should exercise CP coherency packets, EOP fence writes, append/fence registers, wait-reg-mem, signal/wait semaphores, atomics, and CP DMA transfers while watching for hangs, stale data, or timeout interrupts.
- Profiling/debug validation should program CB and CP/CPC/CPG/CPF performance counters, read low/high counter pairs, inspect stalled/busy/status registers, and compare results against known workloads or hardware traces.
- Power-management and recovery tests should cover suspend/resume, GPU reset, CP microcode reload, clock/power gating, memory sleep controls, and queue teardown/restart, because many fields in this chunk persist until explicitly restored.

## Cross-Chunk Notes

This first chunk starts at the beginning of `gfx_8_1_sh_mask.h` and contains complete CB render-target state plus a large but not complete CP block. The next chunk should continue at `CP_HQD_HQ_STATUS1__STATUS__SHIFT` and then cover the remaining HQD EOP/queue-management definitions. The merge lane should join these artificial chunk boundaries before making any final statement about complete HQD/MQD coverage for the full source file.
