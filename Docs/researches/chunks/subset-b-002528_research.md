# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_sh_mask.h lines 5103-7503

## Scope

This chunk is a generated AMD GC 11.0.3 shift/mask register-header segment. It contains C preprocessor constants only: each hardware register field is represented by a `__SHIFT` value and a matching `__MASK` value used by AMDGPU register helpers to compose or decode 32-bit MMIO/indexed-register values. There are no functions, structs, enums, variables, includes, allocations, locks, callbacks, or executable branches in this range.

The selected lines start in the tail of `SDMA1_QUEUE7_CONTEXT_STATUS` masks and then cover the remaining `SDMA1_QUEUE7_*` doorbell, context-save, scheduling, AQL, preemption, and mid-command fields. The main body covers SDMA0 and SDMA1 hypervisor decode register maps, SDMA performance counter selectors/results, GRBM global graphics status/reset/error/debug registers, CP command-processor debug/status/FIFO/register-queue counters, and the first PA/VGT/IA status fields. The chunk ends after the `IA_UTCL1_STATUS_2__RETRY_DETECTED__SHIFT` macro; its corresponding masks and subsequent PA decode registers continue in the next adjacent chunk.

Although the repository path is under a `ceph-client` mirror, this file is AMDGPU DRM hardware metadata for the GC 11.0.3 graphics IP and is not Ceph filesystem code.

## Purpose

`gc_11_0_3_sh_mask.h` supplies the bit layouts for GC 11.0.3 registers. Driver code pairs these macros with register addresses from the matching `gc_11_0_3_offset.h` header and, where available, generated reset values/defaults. Consumers normally use the constants through helper macros such as `REG_SET_FIELD` and `REG_GET_FIELD` so they can program or inspect one hardware field without embedding magic bit positions.

This chunk focuses on low-level engine control and observability rather than draw-state programming:

- SDMA queue 7 state for doorbells, doorbell logging, context-save area addresses, schedule IDs and quantum, indirect-buffer preemption, write-pointer polling, AQL packet layout, minor pointer updates, ring-buffer preemption, and mid-command data restore/control.
- SDMA0 and SDMA1 hypervisor-visible register-type bitmaps that classify queue context registers, public SDMA registers, microcode/self-load controls, VM context control, virtual reset requests, F32 thread control, power/clock/debug/status registers, UTCL1/XNACK/invalidation state, GPU IOV violation logs, and queue reset/status hooks.
- SDMA0 and SDMA1 performance counter control/data windows, including performance event selection, modes, enable/clear bits, start/stop trigger fields, result selection, command operation fields, and low/high counter result registers.
- GRBM registers for global busy/clean status by graphics block, soft reset bits, clock-gating delay/idle wait controls, read/write error attribution, interrupt enablement, traps, RSMU access configuration, interrupt-handler credits, UTCL2 invalidation ranges, invalid pipe logging, fence ranges, scratch registers, and asynchronous VF violation data.
- CP registers for CPC/CPF/CP debug indices, busy/stalled/status views, GRBM free-count counters, header dumps, scratch indexed access, ring/read/write pointer state, command queue thresholds and availability, ROQ/STQ/MEQ pointer stats, command index/data access, interrupt debug status, and privilege violation address capture.
- The start of PA/VGT decode status for DMA data/request FIFO depths, draw-init FIFO depth, memory-controller timestamp resolution, and IA UTCL1 busy/fault/retry state.

## Important APIs, Types, And Macros

There are no callable APIs or C types. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position for a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the 32-bit register value.
- Register-address symbols live in the companion offset header, commonly with `mm...` names matching the register base.
- AMDGPU callers normally access these fields through `REG_SET_FIELD`, `REG_GET_FIELD`, read-modify-write MMIO helpers, debugfs/sysfs/perf counter plumbing, reset/suspend/resume code, or command-stream setup paths.

The main macro families in this slice are:

- `SDMA1_QUEUE7_*`: the last per-queue SDMA1 queue-7 context fields. Address fields such as `CSA_ADDR_LO`, `RB_WPTR_POLL_ADDR_LO`, and high-word partners describe split GPU/system addresses. Control/status fields include doorbell `ENABLE`/`CAPTURED`, doorbell-log backend error and data bits, schedule identity and quantum, `IB_PREEMPT`, AQL enable/packet/step/preempt/overlap bits, `MINOR_PTR_UPDATE`, `RB_PREEMPT`, and the `MIDCMD_DATA0..10` plus `MIDCMD_CNTL` restore state.
- `SDMA0_*` and `SDMA1_*` hypervisor decode fields: `UCODE_ADDR/DATA`, broadcast ucode windows, `UCODE_SELFLOAD_CONTROL`, VM context address/control, `ACTIVE_FCN_ID`, `VIRT_RESET_REQ`, `CONTEXT_REG_TYPE0..2`, `PUB_REG_TYPE0..3`, `VM_CNTL`, and `F32_CNTL`. The `CONTEXT_REG_TYPE*` and `PUB_REG_TYPE*` registers are bitmaps naming which SDMA queue/public registers belong to each context or public register type.
- `SDMA[01]_PERFCNT_*` and `SDMA[01]_PERFCOUNTER*`: perf selection/configuration/result macros for two SDMA performance counters and an additional perfcnt result path. These include `PERF_SEL`, `PERF_SEL_END`, `PERF_MODE`, `ENABLE`, `CLEAR`, trigger selection, `ENABLE_ANY`, `CLEAR_ALL`, and result counter low/high fields.
- `GRBM_*`: global graphics register-bus manager fields. `GRBM_STATUS*` expose busy/clean state for CP, CPF, CPC, GUI_ACTIVE, RLC, TCP, GL1/GL2, PA, TA, SX, SPI, SC, DB, CB, UTCL, SEDC, PC, PMM, and related blocks. `GRBM_SOFT_RESET` exposes reset bits for CP/RLC/UTCL2/GFX/CPF/CPC/CPG/CAC/CPAXI/EA/SDMA0/SDMA1. Error and violation registers record requester, VF/VFID/VMID, pipe/ME/queue/source IDs, address fragments, TMZ/security-write status, and sticky error bits.
- `CP_*`: command-processor observability and tuning fields. CPC/CPF status and busy/stall registers expose sub-block activity, ROQ/DC/RCIU/TCIU/cache/save-restore/MES/MEC activity, and GRBM free counts. CP global status covers stalled/busy/stat registers, ME/PFP/MEC instruction pointers, context counts, ring-buffer read pointers, write-pointer polling/delay, queue thresholds, availability counters, ROQ/STQ/MEQ stats, debug command index/data access, interrupt assertion bits, and privilege violation capture.
- `VGT_DMA_DATA_FIFO_DEPTH`, `VGT_DMA_REQ_FIFO_DEPTH`, `VGT_DRAW_INIT_FIFO_DEPTH`, `VGT_MC_LAT_CNTL`, and partial `IA_UTCL1_STATUS_2`: the opening PA decode entries for FIFO sizing, timestamp resolution, and input-assembler UTCL1 busy/fault/retry state.

## Control Flow

This header has no runtime control flow. Its only direct behavior is compile-time macro substitution.

The implied runtime flow is in AMDGPU consumers:

1. Select the GC 11.0.3 register header for the active ASIC generation.
2. Choose the matching register address from `gc_11_0_3_offset.h`.
3. Read an existing register value, prepare a debug/perf access, or construct an MMIO/command-packet write.
4. Use the `__SHIFT`/`__MASK` pairs, usually through register field helpers, to pack a field value or extract status bits.
5. Feed the resulting value into engine bring-up, SDMA queue setup, perf counter programming, GPU reset, power-management, virtualization, debug, or fault-handling logic.

For SDMA queue state, higher-level code programs ring/doorbell/AQL/context-save/preemption fields when creating queues, restoring contexts, handling virtualization, or recovering from a fault. For GRBM and CP status, runtime flows mostly poll or snapshot bits during idle waits, hangs, debug dumps, reset decisions, interrupt handling, and performance diagnostics. For perf counters, consumers select an event/mode, clear and enable counters, optionally gate them with start/stop triggers, then read low/high result registers. This header does not define required ordering, delays, clear-on-read behavior, or reset sequences; those are encoded in AMDGPU engine code and the hardware programming guide.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe GPU register fields whose state is owned by hardware, firmware, and AMDGPU runtime programming.

SDMA queue fields are persistent queue/context state. Doorbell enable/captured state, queue scheduling IDs, context-save area addresses, write-pointer polling addresses, AQL packet controls, ring preemption state, and mid-command restore data can survive as live engine state until overwritten, context-switched, reset, or lost through power gating. Incorrect restore of these fields can resume the wrong command stream, poll the wrong write pointer, corrupt mid-command replay, or send work to the wrong queue identity.

The SDMA `CONTEXT_REG_TYPE*` and `PUB_REG_TYPE*` bitmaps are register-classification maps for hypervisor/context save and public register exposure. Their values affect which queue/public registers participate in context save/restore, virtualization handling, or decode visibility. `VIRT_RESET_REQ`, `ACTIVE_FCN_ID`, GPU IOV violation logs, VM context fields, and VF/VFID/VMID fields are especially sensitive in SR-IOV or virtualized environments because stale or misdecoded state can attribute faults or resets to the wrong function.

GRBM and CP status/error fields are primarily live hardware status or sticky diagnostic state. Busy/clean bits change as engines drain; error, invalid pipe, read/write violation, interrupt debug, and privilege violation fields may remain latched until cleared by the documented sequence. GRBM scratch registers are general full-width scratch state and may be used by firmware, driver diagnostics, or low-level bring-up code. Soft-reset and power-halt fields have direct hardware side effects and should not be treated as passive configuration.

Performance counter fields persist configured event selections, modes, and enable/clear state while counters accumulate. Counter low/high result registers must be read with the correct latching/ordering expectations from the hardware spec; this header only describes bit positions and cannot express atomicity, saturation, or clear semantics.

Reserved fields appear throughout the generated map. Callers should preserve reserved bits during read-modify-write unless a documented full-register write is required. This is particularly important for reset, virtualization, clock/power, and debug registers where undocumented bits can be ASIC- or firmware-sensitive.

## Dependencies And Integration Points

This chunk depends on the generated GC 11.0.3 register set remaining internally synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_offset.h` provides matching register addresses.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_default.h`, when present in the same generated register family, provides default/reset values for many registers.
- AMDGPU SDMA, GFX, CP, reset, power-management, virtualization/SR-IOV, KFD/compute queueing, perf counter, debugfs, and hang-dump paths rely on these bit assignments.
- Common AMDGPU register helpers provide the actual field packing/extraction and MMIO or command-packet access mechanisms.

Integration points include SDMA queue creation and teardown, context save/restore, SDMA AQL and preemption support, ring write-pointer polling, SDMA firmware/microcode load and self-load control, virtual function reset and fault attribution, SDMA and graphics idle waits, GPU reset/hang recovery, GRBM read/write error logging, CP command queue and FIFO diagnostics, CP interrupt debug handling, privilege violation reporting, per-engine performance monitoring, and early PA/VGT/IA status reporting.

## Risks And Edge Cases

- Generated-header drift is the dominant risk. A wrong shift or mask compiles cleanly but can write the wrong hardware bits or decode misleading diagnostics.
- This chunk starts and ends mid-family. It begins with only the last visible `SDMA1_QUEUE7_CONTEXT_STATUS` masks and ends before the masks for `IA_UTCL1_STATUS_2`; file-level conclusions must be merged with adjacent chunks.
- SDMA0 and SDMA1 macro families are nearly symmetric. Generator or copy/paste mistakes can affect one engine only, producing asymmetric queue failures, perf counter readings, or reset behavior.
- Address fields often omit low alignment bits, such as low address words shifted by two bits. Treating these as raw byte addresses can program plausible but wrong addresses for context-save areas, write-pointer polling, VM context state, or trap/error addresses.
- Reset and halt fields have side effects. Misusing `GRBM_SOFT_RESET`, `GRBM_PWR_CNTL2`, `SDMA*_F32_CNTL`, `SDMA*_VIRT_RESET_REQ`, or queue reset hooks can hang the GPU or lose active work.
- Virtualization and security attribution fields are high risk: VF/VFID/VMID/SSRCID/TMZ/security-write bits must be decoded exactly for fault isolation, SR-IOV reset, and security logging.
- Busy/clean/status bits are volatile. Polling code must account for transitions, hardware blocks that may be clock-gated, and sticky error bits that require explicit clearing.
- Counter high/low result registers can be race-prone if read without the documented latching sequence. The shift/mask header cannot describe atomic snapshot requirements.
- Reserved masks are included in many bitmap registers. Full-register writes that do not preserve reserved bits may change undocumented engine behavior.
- CP threshold and availability fields are tightly coupled to command processor queue sizing. Incorrect field widths can make queue diagnostics or tuning appear valid while hiding near-full or stalled conditions.

## Test Signals

Useful validation is primarily generated-data consistency, build coverage, and hardware/runtime diagnostics:

- Kernel build coverage for AMDGPU files that include `gc_11_0_3_sh_mask.h`, especially GC 11.0.3 SDMA, GFX, CP, reset, virtualization, KFD, debug, and perf counter paths.
- Mechanical comparison against AMD's authoritative GC 11.0.3 register database to confirm every `__SHIFT` and `__MASK` value in this slice.
- Cross-checks that all registers in this chunk have matching address macros in `gc_11_0_3_offset.h` and expected defaults in the matching default header where generated.
- Static mask/shift sanity checks: masks should align with shifts, full-width data fields should use `0xFFFFFFFFL`, SDMA0/SDMA1 mirrored families should remain structurally aligned, and bitmap fields should not overlap unless documented.
- SDMA queue tests covering doorbell programming, write-pointer polling, AQL packet execution, preemption, context save/restore, queue reset, and mid-command restore after suspend/resume or GPU reset.
- SR-IOV or virtualization tests that trigger virtual reset requests and validate VF/VFID/VMID/SSRCID fault attribution for SDMA, GRBM, and CP paths.
- Perf counter tests that select SDMA events, clear/enable/disable counters, read low/high results, and compare monotonicity or expected activity under controlled DMA workloads.
- Hang/debug dump tests that verify GRBM busy/clean bits, read/write error registers, invalid-pipe logs, CP busy/stalled/status fields, ring/ROQ/STQ/MEQ pointers, and CP interrupt debug bits are decoded coherently.
- Reset and idle-wait tests that exercise `GRBM_STATUS*`, `GRBM_SOFT_RESET`, clock/idle wait fields, CP/SDMA reset bits, and post-reset register restore.
- Runtime warning signals include SDMA queue hangs, lost doorbell updates, wrong queue preemption, bad AQL dispatch, misleading perf counters, failed idle waits, incorrect fault attribution, unexpected privilege/security violation reports, GPU reset loops, or CP/GRBM debug dumps with impossible busy/clean combinations.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002528`. It covers lines 5103-7503 of `gc_11_0_3_sh_mask.h`. The final per-file research should merge this with adjacent chunks to complete the partial `SDMA1_QUEUE7_CONTEXT_STATUS` and `IA_UTCL1_STATUS_2` families and to place these SDMA/GRBM/CP/PA status definitions in the full GC 11.0.3 register map.
