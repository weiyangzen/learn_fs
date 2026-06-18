# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_offset.h lines 2490-4978

## Scope

This chunk is a generated AMD GC 12.0.0 register-offset header segment. It contains preprocessor constants only: each `reg*` macro names a graphics-core hardware register offset, and each paired `reg*_BASE_IDX` macro selects the SOC15 base-index slot used by AMDGPU register-address helpers.

The requested range contains 2,401 `#define reg*` entries, including both offset macros and base-index macros. The range begins mid-family at `regPWRBRK_STALL_PATTERN_3_4` and ends mid-CP-family at `regCP_MEC_GP1_LO`, so final file-level documentation must reconcile the adjacent chunks before making complete claims about the surrounding generated header.

Although this source tree is under a local `ceph-client` mirror, this file is AMDGPU DRM graphics metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

`gc_12_0_0_offset.h` supplies named register offsets for GC 12.0.0 graphics hardware. AMDGPU code pairs these macros with GC 12.0.0 shift/mask definitions and uses SOC15/MMIO helpers to read, write, or emit register addresses without hard-coding numeric offsets.

This chunk covers these main register areas:

- The tail of GC power, throttle, and current activity counter controls: EDC, DIDT, PCC, PWRBRK, throttle status, CAC weights, and CAC indirect index/data registers.
- EA SDP interface blocks for CPWD and SE paths, including VC mapping, arbitration, priority, credit/reserve, request control, error/status, backdoor credit/data controls, and SDP enable registers.
- GCR and PMM controls around PIO, target disable, command status, spare, and PMM status/control.
- GCUTCL2/GCVML2/GCVM shared physical and virtual control blocks: memory aperture programming, L2 control/status, protection-fault reporting, invalidation engines, per-context page-table bounds, bank selection, PTE cache dump, translation-assist request/response, credit-safety, walker throttle, perf and parity controls.
- CP global, ring, queue, interrupt, doorbell, firmware-program-counter, DMA-watch, graphics HQD, and UTCL1 status/error registers in the CP decoder block.
- CP HQD/HPD compute queue registers, including active/VMID/priority/quantum, base/rptr/wptr, doorbell, dequeue, EOP, IQ, MQD, semaphore, GDS, error, suspend, and context-save state.
- Graphics context registers in `gfxdec0`, including coherency destination bases, CP context IDs, VGT draw/index/tessellation/event state, and GE frontend enhancements.
- PF/VF and PF-only CP/GRBM/GCR blocks for MEC/ME controls, unmapped queue and doorbell tracking, GRBM selection, DFY data/control, HPD status, and privileged GCR/PMM controls.
- The beginning of the GFXU/RS64 command-processor area: EOP done, append/atomic, CP DMA, IB/ST/DB buffers, coherency, RLC perf counters, CP performance counters, scratch, PFP/ME/MES RS64 execution state, interrupt data, DC apertures, metadata, and initial MEC RS64 state.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, memory allocations, locks, callbacks, or executable branches in this range. The public interface is the generated macro naming contract:

- `regNAME` gives the register's encoded offset within its hardware block.
- `regNAME_BASE_IDX` gives the SOC15 base-index selector used with that offset.
- Address-block comments name the generated register block and its hardware base address, for example `gc_gfx_cpwd_gcutcl2_gcvml2vcdec` at base address `0xa210`.
- Consumers commonly combine these macros with `SOC15_REG_OFFSET`, `RREG32*`, `WREG32*`, `WREG32_FIELD*`, `RREG32_FIELD*`, register-indirect accessors, and command-stream emission helpers.
- Field packing and extraction are supplied by the matching GC 12.0.0 shift/mask header, not by this offset file.

Important register groups in this range include:

- `GC_EDC_*`, `GC_THROTTLE_STATUS`, `DIDT_*`, `PCC_*`, `PWRBRK_*`, and `GC_CAC_WEIGHT_*`: power/thermal/current estimation and throttling metadata for GC clients such as CP, EA, UTCL2, GE, PMM, SDMA, RLC, GRBM, and GL2C.
- `GC_EA_CPWD_*` and `GC_EA_SE_*`: SDP arbitration, reserve, backdoor, miscellaneous, and enable registers for EA links.
- `GCMC_VM_*`, `GCUTCL2_*`, `GCVM_L2_*`, `GCUTC_GPUVA_*`, and `GCVM_CONTEXT*`: graphics memory controller and VM/L2 controls, aperture bounds, context enablement, invalidation sem/request/ack/address ranges, page-table bases, and page-table start/end bounds.
- `CP_RB*`, `CP_ME*`, `CP_MEC*`, `CP_PFP*`, `CP_INT_*`, `CP_DOORBELL_*`, `CP_GFX_HQD_*`, `CP_DMA_WATCH*`, and `CP_*_UTCL1_*`: ring buffers, queue selection, firmware program counters, interrupts, doorbells, debug watchpoints, graphics HQD state, and CP translation/cache status.
- `CP_HQD_*`, `CP_HPD_*`, `CP_MQD_*`, and `CP_HQD_GDS_*`: compute queue descriptor and hardware queue state used by graphics/compute scheduling and KFD queue management.
- `VGT_*`, `GE_*`, `COHER_DEST_BASE*`, and `CONTEXT_RESERVED_*`: graphics frontend and context-state offsets.
- `CP_UNMAPPED_QUEUE*`, `CP_UNMAPPED_DOORBELL`, and `CP_UNMAPPED_QUEUE_BANK*`: PF/VF-visible unmapped queue and doorbell accounting.
- `CP_MES_*` and `CP_MEC_RS64_*`: MES and MEC RS64 control/status, instruction/scratch memory apertures, pending interrupt state, interrupt data payloads, and debug cache apertures.

## Control Flow

This header has no runtime control flow. Its direct behavior is compile-time macro substitution.

The implied runtime flow is in AMDGPU and KFD consumers:

1. Select the GC 12.0.0 register-definition headers for the active ASIC.
2. Use an offset macro from this file and, when field-level programming is needed, a matching shift/mask macro from the GC 12.0.0 mask header.
3. Compose or decode register values through AMDGPU register helpers.
4. Access the hardware through MMIO, indexed-register paths, RLC-safe accessors, firmware-mediated paths, or command packets.
5. Poll or validate status registers where the higher-level driver sequence requires acknowledgement, queue state transitions, TLB invalidation completion, interrupt delivery, or fault capture.

For VM state, driver code typically programs apertures and per-VMID context/page-table registers, issues GCVM invalidation requests, waits for matching acknowledgement registers, and handles protection-fault status. For CP queue state, initialization paths program ring/HQD/MQD/doorbell/EOP registers and scheduling paths request dequeue, suspend, resume, or reset. For RS64/MES state, firmware setup and diagnostics use the control, interrupt, program-counter, scratch, and aperture registers named here; this file only supplies the offsets.

The generated header does not encode sequencing, side-effect, access-width, W1C, clear-on-read, privilege, or polling rules. Those semantics come from the hardware programming guide and the AMDGPU code that uses these macros.

## State And Persistence Behavior

The macros themselves hold no runtime state and persist nothing. They describe hardware-visible state:

- EDC/DIDT/PCC/PWRBRK/CAC registers are power-management and telemetry state. Some registers configure thresholds, stall patterns, weights, and monitors; others report counters, overflow, hysteresis, throttle, or rolling-power status.
- EA SDP registers configure arbitration, priority, credit, reserve, and enable state for hardware links. Misprogramming can affect request flow, backpressure, or error visibility.
- GCVM/GCMC/GCUTCL2/GCVML2 registers describe memory apertures, L2 behavior, translation-assist state, fault capture, invalidate-engine semaphores/requests/acks, and per-context page-table boundaries. Much of this state must be rebuilt across GPU reset, suspend/resume, VM reinitialization, or SR-IOV function reset.
- CP ring, doorbell, HQD, MQD, GDS, EOP, and interrupt registers are live queue-management state. Some are software-programmed, some are hardware-updated as rings execute, and some are latched status/error/fault registers.
- PF/VF and PF-only registers partition visibility and control between virtual functions and privileged physical-function code. The `BASE_IDX` values are part of how common SOC15 helpers target the correct register aperture.
- Graphics context registers such as VGT, GE, coherency destination, and context ID state persist until replaced by context restore, command stream emission, reset, or power-management reprogramming.
- RS64/MES/MEC registers describe firmware execution, instruction pointers, interrupt vectors/data, scratch/instruction apertures, timer compare, debug cache apertures, and metadata. They are sensitive to firmware load/reset sequencing.

Because this header is offset-only, it cannot tell whether a register is read-only, write-only, write-one-to-clear, indexed, privileged, shadowed, saved/restored, or safe for read-modify-write. Consumers must rely on the corresponding driver sequence and field definitions.

## Dependencies And Integration Points

This header depends on synchronization with AMD's authoritative GC 12.0.0 register database and with companion generated headers in the same directory, especially the GC 12.0.0 shift/mask header that defines the bit layouts for these offsets.

Primary integration points are:

- AMDGPU ASIC-specific initialization code for GC 12.0.0, which includes this header to select register addresses for the active hardware generation.
- Common AMDGPU SOC15 register helpers, which combine `reg*` offsets and `reg*_BASE_IDX` selectors into MMIO addresses.
- GFXHUB/VM code that uses `GCMC_VM_*`, `GCVM_L2_*`, `GCVM_CONTEXT*`, and invalidation engine offsets to initialize GPU virtual memory and handle faults.
- CP/GFX scheduling and ring code that uses `CP_RB*`, `CP_ME*`, `CP_MEC*`, `CP_HQD*`, `CP_GFX_HQD*`, `CP_MQD*`, doorbell, EOP, and interrupt offsets.
- KFD compute-queue and debug paths that depend on HQD/MQD/GDS/watchpoint-related CP offsets when programming user-mode compute queues.
- MES/RS64 firmware setup and diagnostics that use `CP_MES_*` and `CP_MEC_RS64_*` offsets.
- SR-IOV and virtualization paths that care about PF/VF-visible `CP_UNMAPPED_QUEUE*`, PF-only CP/HPD/GCR offsets, and base-index selection.
- Power, throttling, and telemetry paths that read or program EDC, DIDT, PWRBRK, PCC, CAC, perf-counter, and throttle-status offsets.

## Risks And Edge Cases

- Generated-header drift is the primary risk. An incorrect numeric offset or base index compiles cleanly but can address the wrong hardware register.
- The chunk boundaries are artificial. This range starts after the first PWRBRK stall-pattern register and stops at the first part of a MEC GP register sequence, so adjacent chunks are needed for full family coverage.
- `BASE_IDX` mismatches are as dangerous as offset mismatches. The same encoded offset can mean a different physical register if the SOC15 base slot is wrong.
- Repeated register families are copy-sensitive: `GCVM_CONTEXT0` through `GCVM_CONTEXT15`, invalidate engines 0 through 17, unmapped queues 0 through 63, `CP_MES_DC_APERTURE0` through `15`, and ring/HQD aliases must preserve exact stride and naming.
- Some macros intentionally alias the same offset with multiple names, such as `CP_RB0_*` and `CP_RB_*`, `CP_RING*` and `CP_ME0_PIPE*`, `CP_APPEND_DATA` and `CP_APPEND_DATA_LO`, or HPD/MES ROQ names. Mechanical deduplication would lose compatibility with consumers.
- VM and fault registers are security-sensitive. Wrong aperture, context, page-table, invalidation, or protection-fault offsets can cause address-translation failures, stale TLB entries, incorrect fault attribution, or cross-VMID isolation bugs.
- CP/HQD/MQD offsets are queue-liveness sensitive. Wrong active, VMID, base, rptr/wptr, doorbell, dequeue, EOP, semaphore, GDS, or error offsets can cause queue hangs, missed completions, broken preemption, or failed GPU reset recovery.
- PF/VF and PF-only register placement affects virtualization boundaries. Exposing or programming the wrong register through a VF path can create isolation or reliability failures.
- Power/throttle/CAC offsets can produce performance and thermal regressions rather than immediate functional failures, especially under mixed graphics/compute load.
- Status and error registers may be latched, clear-on-read, write-one-to-clear, or access-sensitive. The offset header does not represent those access semantics.

## Test Signals

Useful validation should combine generated-data checks, compile coverage, and hardware/runtime tests:

- Build AMDGPU with GC 12.0.0 support and KFD enabled. Missing, renamed, or malformed macros should surface in ASIC-specific include users and common register-helper call sites.
- Mechanically compare this range against AMD's authoritative GC 12.0.0 register database. Check both offset values and `_BASE_IDX` values.
- Cross-check complete register families for stride consistency: GCVM contexts, invalidation engines, page-table base/start/end registers, unmapped queues, CP DMA watch slots, HQD/MQD blocks, MES interrupt data, and MES DC aperture slots.
- Verify intentional aliases map to the same offsets where expected and are not accidentally collapsed or renamed.
- Run VM stress tests with many VMIDs, page-table updates, TLB invalidations, dummy/protection faults, and suspend/resume or GPU reset. Relevant signals include correct invalidate acknowledgements, correct fault addresses/status, and no stale translations.
- Run KFD compute queue creation, teardown, preemption, suspend/resume, and multi-process workloads. Watch for stuck HQDs, dequeue timeouts, CP_HQD error bits, EOP pointer mismatches, and reset recovery failures.
- Exercise graphics rings, CP DMA, indirect buffers, doorbells, append/atomic paths, and coherency flushes. Relevant signals include ring progress, correct fences, no CP fatal errors, and expected interrupt status.
- Exercise SR-IOV/PF-VF scenarios where available, especially unmapped queue accounting and PF-only register access restrictions.
- Run MES/RS64 firmware initialization and queue scheduling diagnostics. Watch for pending interrupts, RS64 exception status, program-counter anomalies, scratch/instruction aperture failures, and metadata setup errors.
- Run power/thermal/performance telemetry tests that read EDC/DIDT/PWRBRK/PCC/CAC counters and throttle status under load. Look for plausible counter movement and no unexpected throttling or overflow behavior.

## Cross-Chunk Notes

The previous chunk owns the beginning of the GC power-management/CAC block, including earlier EDC/PCC/PWRBRK stall-pattern registers. This chunk begins at `regPWRBRK_STALL_PATTERN_3_4`, carries through EA, GCR, GCVM/GCUTCL2/GCVML2, CP, HQD, PF/VF, GFXU, MES, and RS64 register-offset groups, and stops at `regCP_MEC_GP1_LO`. The next chunk should complete the surrounding MEC RS64 general-purpose register sequence and any remaining GC 12.0.0 offset definitions.
