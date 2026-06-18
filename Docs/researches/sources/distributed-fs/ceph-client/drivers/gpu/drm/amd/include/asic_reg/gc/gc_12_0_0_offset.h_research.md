# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_offset.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002564`: lines 1-2489, `Docs/researches/chunks/subset-b-002564_research.md`
- `subset-b-002565`: lines 2490-4978, `Docs/researches/chunks/subset-b-002565_research.md`
- `subset-b-002566`: lines 4979-7470, `Docs/researches/chunks/subset-b-002566_research.md`
- `subset-b-002567`: lines 7471-9953, `Docs/researches/chunks/subset-b-002567_research.md`
- `subset-b-002568`: lines 9954-11061, `Docs/researches/chunks/subset-b-002568_research.md`

## Chunk Research

### subset-b-002564: lines 1-2489

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_offset.h lines 1-2489

## Scope

This chunk is the opening portion of a generated AMDGPU GC 12.0.0 register-offset header. It contains preprocessor constants only: each hardware register has a `reg...` offset macro and a paired `..._BASE_IDX` macro used by SOC15 register access helpers. There are no C functions, structs, enums, global variables, allocations, locks, loops, branches, or direct MMIO operations in this range.

The requested lines contain 2,392 `#define` statements. The chunk starts with the include guard and MIT-style AMD copyright notice, then covers SDMA0, SDMA1, GRBM, CP, PA/VGT/GE/WD/IA, compute shader dispatch, RAS, and the beginning of the PF-only GC CAC/EDC/throttle block. The full source file continues past this chunk, so this document intentionally covers only lines 1-2489.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file is AMDGPU DRM hardware metadata. It is not part of Ceph filesystem logic, storage persistence, or distributed-filesystem protocol behavior.

## Purpose

`gc_12_0_0_offset.h` gives GC 12.0.0 driver code stable symbolic names for MMIO register offsets. Runtime code combines these offsets with generated shift/mask headers, generated default-value headers, and AMDGPU helper macros such as `SOC15_REG_OFFSET`, `SOC15_REG_ENTRY`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_SOC15_IP`, and `WREG32_SOC15_IP`.

The purpose of this chunk is to describe the major public register windows needed to initialize, stop, resume, inspect, and debug GC 12 graphics and SDMA hardware:

- SDMA0 and SDMA1 engine-global controls, status registers, UTCL1/cache/VM surfaces, interrupt/error reporting, timestamp/watchdog registers, and eight RLC queue templates per engine.
- SDMA hypervisor, PSP, performance-counter, performance-data, and power/clock-gating register blocks for both engines.
- GRBM control, status, trap, scratch, soft-reset, read/write error, UTCL2 invalidation, and interface-control offsets.
- CP/CPC/CPF status, stall, busy, debug, queue, threshold, read-pointer, and privilege-violation offsets.
- PA/VGT/GE/WD/IA utility/status offsets for geometry/front-end and UTCL1 behavior.
- Compute dispatch and shader-program state registers, including program addresses, dimensions, VMID, resource limits, thread management, relaunch/wave-restore, user data, and dispatch end/tunnel offsets.
- RAS signature and PF-only CAC/EDC/throttle/stall-pattern offsets.

## Important APIs, Types, And Macros

This header defines no callable APIs and no C data types. Its interface is the generated macro naming contract:

- `reg<REGISTER>` gives a register offset in the generated GC 12 address map.
- `reg<REGISTER>_BASE_IDX` selects the base-index table used by SOC15 helpers. In this chunk, public SDMA/GRBM/CP/PA/SH offsets mostly use base index `0`, while hypervisor, PSP, performance, power, and PF-only CAC/EDC offsets use base index `1`.
- `// addressBlock: ...` and `// base address: ...` comments preserve the generated hardware block boundaries and are important for humans comparing against ASIC register databases.

Important consumers visible in this tree include:

- `amdgpu/amdgpu_amdkfd_gfx_v12.c`, which includes this header and computes KFD SDMA RLC queue register bases from `regSDMA0_QUEUE0_RB_CNTL`, `regSDMA1_QUEUE0_RB_CNTL`, and the `QUEUE1 - QUEUE0` stride.
- `amdgpu/sdma_v7_0.c`, which includes this header and programs SDMA ring buffers, indirect buffers, read/write pointers, doorbells, watchdogs, UTCL1 policy, and MCU halt/reset state through these offsets.
- `amdgpu/gfx_v12_0.c`, which includes this header and polls `regGRBM_STATUS` for GC idle detection.
- `amdgpu/soc24.c`, which includes this header and exposes selected GRBM, SDMA, CP, CPC, and CPF status registers through the allowed-register/readback path.
- `amdgpu/gfxhub_v12_0.c`, `amdgpu/mes_v12_0.c`, and `amdgpu/imu_v12_0.c`, which include the same GC 12 offset namespace for generation-specific graphics, hub, MES, and microcontroller integration.

## Register Families Covered

The first large block, `gc_gfx_cpwd_sdma0_sdmadec`, starts at line 28 and maps SDMA0 public offsets. It begins with engine-wide registers such as `regSDMA0_DEC_START`, `regSDMA0_MCU_MISC_CNTL`, `regSDMA0_UCODE_REV`, timestamp, power, `CNTL`, `CACHE_CNTL`, status, freeze, watchdog, error, interrupt, scratch RAM, timestamp, queue reset, and FED/CE control registers. It then repeats an RLC queue template for `SDMA0_QUEUE0` through `SDMA0_QUEUE7`.

Each SDMA queue template includes ring-buffer control and addressing (`RB_CNTL`, `RB_BASE`, `RB_BASE_HI`, `RB_RPTR`, `RB_RPTR_HI`, `RB_WPTR`, `RB_WPTR_HI`, `RB_RPTR_ADDR_LO/HI`, `RB_WPTR_POLL_ADDR_LO/HI`), indirect-buffer state (`IB_CNTL`, `IB_RPTR`, `IB_OFFSET`, `IB_BASE_LO/HI`, `IB_SIZE`, `IB_SUB_REMAIN`), doorbell state (`DOORBELL`, `DOORBELL_LOG`, `DOORBELL_OFFSET`), context-save address, scheduling/preemption, AQL control, minor pointer update, context-switch/status registers, MQD base/control, dequeue request, and mid-command save data `MIDCMD_DATA0..10`.

The SDMA0 side blocks following the public queue window map virtualization and firmware-adjacent surfaces: `sdmahypdec` provides VM context, active function ID, virtual reset, VM control, MCU control, and instruction-cache base/control registers; `sdmapspdec` exposes `MCU_DM_FROM_RST_ADDR_OFFSET`; `sdmaperfsdec` and `sdmaperfddec` expose performance counter configuration, selection, result control, and low/high result registers; `sdmapwrdec` exposes `regGFX_ICG_SDMA0_CTRL`.

The SDMA1 blocks mirror SDMA0 with a public `sdmadec:1` window starting at `regSDMA1_DEC_START`, queue templates for `SDMA1_QUEUE0` through `SDMA1_QUEUE7`, then matching hypervisor, PSP, performance, performance-data, and power blocks. SDMA1 public queue offsets are shifted by the generated public register spacing, while some side blocks live in base-index-1 address spaces.

The `gc_gfx_cpwd_cpwd_grbmdec` block maps GRBM status/control surfaces: `GRBM_CNTL`, `SKEW_CNTL`, `STATUS`, `STATUS2`, `STATUS3`, per-shader-engine status registers, soft reset, clock enable, read/write error reporting, trap controls, chip revision, interrupt credit, UTCL2 invalidation range, invalid pipe, fence ranges, chicken bits, SA unit disable, scratch registers, and interface control. These offsets feed idle polling, register dumps, reset paths, and safe userspace-visible readback tables.

The `gc_gfx_cpwd_cpwd_cpdec` block maps CP/CPC/CPF diagnostics and command-processor queue state. It includes CPC/CPF debug control/data, status, busy and stalled stats, GRBM free counts, privilege-violation addresses, MEC/ME/PFP header dumps, scratch index/data, global CP stalled/busy/stat registers, instruction pointers, context/preemption status, RB read-pointer aliases, queue thresholds and availability, command index/data, ROQ/STQ/MEQ status, interrupt debug, and CP privilege violation addresses.

The `gc_gfx_cpwd_cpwd_padec` block maps a smaller front-end/geometry set: VGT FIFO depths, memory-controller latency control, IA and WD UTCL1 control/status registers, GE status/control, SA unit disable aliasing, graphics pipe control, and reset-debug offsets.

The `gc_gfx_cpwd_cpwd_shdec` block maps compute dispatch state. It includes dispatch dimensions, start coordinates, per-axis thread counts, pipeline/perf-counter enable, program address low/high, dispatch packet and scratch base addresses, program-resource registers, VMID, resource limits, destination/static-thread-management aliases for shader engines, restart coordinates, thread-trace enable, dispatch/threadgroup IDs, request control, accumulator/user data registers, shader checksum, dispatch interleave, relaunch/wave-restore registers, prescaled dimensions, dispatch tunnel/end, and reserved shader registers.

The final visible blocks map `regRAS_GE_SIGNATURE0` and the beginning of PF-only GC CAC/EDC/throttle controls. The CAC/EDC block includes global and per-SE CAC aggregation lower/upper counters, GFXCLK cycle aggregation counters, EDC controls and thresholds, hysteresis, GC throttle controls, EDC/PCC/power-break stall-pattern controls, and the beginning of individual stall-pattern registers.

## Control Flow

This header has no executable control flow. It affects runtime behavior when compiled C code expands these offsets into SOC15/MMIO access sequences.

For SDMA resume, `sdma_v7_0_gfx_resume_instance()` uses SDMA queue offsets from this chunk to program queue 0 for each SDMA instance. The flow reads and writes `regSDMA0_QUEUE0_RB_CNTL`, initializes RPTR/WPTR registers, writes pointer writeback and WPTR polling GPU addresses, programs ring base registers, toggles `regSDMA0_QUEUE0_MINOR_PTR_UPDATE`, configures doorbell enable and offset, sets watchdog and UTCL1 policy registers, unhalts the MCU through `regSDMA0_MCU_CNTL` on bare metal, then enables ring-buffer and indirect-buffer execution. It finishes with `amdgpu_ring_test_helper()`, so wrong offsets often appear as ring test failures or queue hangs.

For SDMA stop, `sdma_v7_0_gfx_stop()` clears `RB_ENABLE` and `IB_ENABLE` by reading and writing the queue control offsets. `sdma_v7_0_enable()` additionally halts or unhalts each SDMA MCU through the generated MCU control offset unless running as an SR-IOV VF.

For KFD SDMA diagnostics, `amdgpu_amdkfd_gfx_v12.c` treats these offsets as arithmetic anchors. It computes the SDMA engine register base from `SOC15_REG_OFFSET(SDMA0, 0, regSDMA0_QUEUE0_RB_CNTL) - regSDMA0_QUEUE0_RB_CNTL` for engine 0, a corresponding SDMA1 expression for engine 1, and a queue stride from `regSDMA0_QUEUE1_RB_CNTL - regSDMA0_QUEUE0_RB_CNTL`. It then dumps the range from `regSDMA0_QUEUE0_RB_CNTL` through `regSDMA0_QUEUE0_CONTEXT_STATUS`. This means contiguous queue spacing and equivalent queue layouts are part of the ABI between generated headers and runtime code.

For graphics idle detection, `gfx_v12_0_is_idle()` and `gfx_v12_0_wait_for_idle()` read `regGRBM_STATUS` and test the `GUI_ACTIVE` field from the matching shift/mask header. `soc24_allowed_read_registers[]` also whitelists several GRBM, SDMA status, CP, CPC, and CPF offsets from this chunk for diagnostic readback.

## State And Persistence Behavior

The macros are stateless compile-time constants. Persistent and volatile state exists only in the GPU registers selected by these offsets.

SDMA queue programming creates live hardware state that persists until queue disable, reset, suspend/resume, or MQD reload. This includes ring buffer base addresses, read/write pointers, pointer writeback locations, write-pointer polling locations, doorbell offsets, context-save addresses, scheduling/preemption state, MQD base/control state, and indirect-buffer state. KFD queue code depends on the register template to save, restore, and dump this state consistently across SDMA engines and queues.

SDMA engine-global state includes MCU halt/reset control, clock/power controls, watchdog thresholds, UTCL1 translation/cache policy, timestamp controls, EDC/error counters, violation logs, invalid-address reporting, queue reset requests, scratch RAM, and interrupt status. Some are configuration registers, some are hardware-updated status latches, and some may be firmware- or virtualization-owned depending on bare-metal versus SR-IOV mode.

GRBM and CP status registers are volatile observation points used for idle detection, hang diagnosis, allowed debug reads, and reset decisions. GRBM scratch registers and trap controls can hold driver/debug state, while GRBM read/write error and CP privilege-violation address registers preserve fault information until cleared or overwritten according to hardware rules outside this header.

Compute dispatch registers are per-dispatch or queue-selected shader state. Program addresses, user data, dimensions, VMID, resources, thread-management state, relaunch/wave-restore addresses, and dispatch IDs can change as packets execute or as queues are saved/restored. The offsets here do not encode ownership, sequencing, or clear behavior; consumers must follow generation-specific GFX/KFD/MES programming flows.

CAC/EDC/throttle registers are PF-only power and reliability control surfaces. Their state can influence throttling and stall-pattern behavior and should be considered platform-management state rather than ordinary per-queue state.

## Dependencies And Integration Points

This chunk depends on the generated GC 12.0.0 register set remaining synchronized:

- `gc_12_0_0_sh_mask.h` supplies field shifts and masks for the register names in this offset header.
- `gc_12_0_0_default.h`, where present for a register, supplies reset/default values used for comparison and initialization.
- SOC15 register helper macros interpret `reg...` offsets and `..._BASE_IDX` values to build the final MMIO address for a given IP block and instance.
- SDMA v7 code depends on SDMA0 and SDMA1 queue templates having stable relative spacing and matching field layouts where instance arithmetic is used.
- KFD GFX v12 queue dump and queue control code depends on the SDMA queue-window stride and first/last register ranges being contiguous enough for range-based dumps.
- GFX v12 idle, reset, and diagnostics depend on GRBM status/control offsets and matching field definitions.
- SOC24 allowed-register tables expose selected offsets to higher-level diagnostic users and must not include unsafe or misindexed registers.
- MES, IMU, GFXHUB, and firmware-adjacent code include this header for generation-specific register addressing, even when the direct consumer is outside this chunk.

The `BASE_IDX` values are a notable integration point. Public GC/SDMA registers in this chunk mostly use base index `0`, while hypervisor, PSP, performance, power, and PF-only CAC/EDC blocks use base index `1`. A wrong base index can direct a valid-looking register offset into the wrong MMIO aperture.

## Risks And Edge Cases

The primary risk is silent hardware misprogramming. These constants are compile-time integers; a wrong value can compile cleanly and still make the driver read or write a different register.

The SDMA queue template is especially sensitive. Runtime code computes engine bases and queue strides from `regSDMA0_QUEUE0_RB_CNTL`, `regSDMA1_QUEUE0_RB_CNTL`, and `regSDMA0_QUEUE1_RB_CNTL - regSDMA0_QUEUE0_RB_CNTL`. Any off-by-one or generation drift in those anchors can corrupt every queue register programmed through derived offsets.

Address-register pairs are high risk. Ring bases, IB bases, RPTR/WPTR writeback addresses, CSA addresses, MQD base addresses, dispatch packet addresses, scratch bases, program addresses, wave-restore addresses, privilege-violation addresses, and invalid-address logs are split across low/high registers. Incorrect low/high ordering or offset values can create GPU memory corruption, invalid DMA, missed page-fault attribution, or unrecoverable hangs.

Doorbell offsets are high risk because a valid register write can still route queue notifications to the wrong doorbell index. This affects SDMA submissions, KFD queues, SR-IOV VF behavior, and diagnostic dumps.

Status and diagnostic offsets can create misleading debugging if wrong. GRBM status, CP busy/stall stats, SDMA status, UTCL1 status, XNACK/fault registers, EDC counters, CAC counters, and RAS signatures are often used during hang and reset triage; bad offsets may hide the real fault or implicate the wrong block.

Base-index drift is subtle. Blocks that visually sit beside public SDMA or GC registers in the header may use base index `1`, not `0`. Manual edits or generator bugs that preserve the numeric offset but change `BASE_IDX` would be hard to catch without hardware register-database comparison or runtime access tests.

This file is generated hardware-description source. Manual cleanup of repeated queue templates, duplicate aliases such as `regCP_RB0_RPTR`/`regCP_RB_RPTR` or `regCOMPUTE_DESTINATION_EN_*`/`regCOMPUTE_STATIC_THREAD_MGMT_*`, reserved registers, and apparently unused side blocks is risky because out-of-tree tooling, debug dumps, firmware paths, or future workarounds may depend on the exact names.

## Test Signals

Useful validation starts with builds of AMDGPU configurations that include GC 12, SDMA v7, KFD, MES, and SOC24 support. Missing or renamed macros should fail at compile time in files such as `sdma_v7_0.c`, `amdgpu_amdkfd_gfx_v12.c`, `gfx_v12_0.c`, and `soc24.c`.

Generated-data checks should compare every offset and `BASE_IDX` in this chunk against AMD's authoritative GC 12.0.0 register database. Mechanical checks should verify that SDMA0 and SDMA1 public queue templates have the expected queue stride, that SDMA0 and SDMA1 corresponding registers have expected engine spacing, and that base-index-1 side blocks match their generated address-block comments.

Strong runtime signals include successful probe and resume on GC 12.0.0 hardware, passing `amdgpu_ring_test_helper()` for each SDMA instance, correct SDMA doorbell submissions, stable ring read/write pointer behavior, no SDMA watchdog timeouts during copy/fill workloads, and clean suspend/resume and GPU reset recovery.

KFD-specific signals include successful SDMA queue dump/load/restore on both SDMA engines, correct `hqd_sdma_dump_v12()` register counts, plausible queue register dumps from `RB_CNTL` through `CONTEXT_STATUS`, and no queue preemption or dequeue stalls caused by derived queue offsets.

Graphics-core signals include `gfx_v12_0_wait_for_idle()` returning successfully under idle workloads, accurate GRBM/CP/CPC/CPF diagnostic readbacks through SOC24 allowed registers, and register dumps that show coherent CP busy/stall, GRBM status, and per-SE status values during hangs or stress tests.

Compute and shader-dispatch signals include successful compute shader dispatches, correct user-data and program-address programming through command streams, no VMID/resource-limit misprogramming symptoms, and coherent relaunch/wave-restore behavior during preemption or debug flows.

Power/reliability signals include plausible CAC aggregation counters, EDC threshold/control behavior, no unexpected GC throttle or stall-pattern activation, and correct RAS GE signature visibility where the platform exposes these PF-only or RAS registers.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002564`. The final per-file research should merge this with later chunks for complete `gc_12_0_0_offset.h` coverage. This chunk owns the file header, the complete SDMA0 and SDMA1 public/side blocks, the early GRBM/CP/PA/SH/RAS blocks, and the beginning of the PF-only GC CAC/EDC/throttle block through `regPWRBRK_STALL_PATTERN_1_2_BASE_IDX`.

### subset-b-002565: lines 2490-4978

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

### subset-b-002566: lines 4979-7470

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_offset.h lines 4979-7470

## Scope

This chunk is a generated AMD GC 12.0.0 register-offset header segment. It contains preprocessor constants only: one `reg*` address macro and one matching `reg*_BASE_IDX` macro for each register. The requested range has 2,400 `#define` lines, representing 1,200 register offsets and 1,200 base-index constants.

The chunk begins mid-address-block. Lines 4979-5505 continue `gc_gfx_cpwd_cpwd_cprs64dec` from the previous chunk, covering the tail of CP MEC RS64 and graphics RS64 data-cache/aperture offsets. Lines 5506-7470 then cover complete CPWD channel, GL2, performance, power, RLC, IMU, GRBMH, PA, SQ, and early SPI/SX shader-engine address blocks. The range ends at `regSPI_LB_DATA_PERWGP_WAVE_HSGS_BASE_IDX`, before the remaining SPI low-bandwidth wave counters and later shader-engine registers that appear in the next chunk.

Although the source tree is under a local `ceph-client` mirror, this file is AMDGPU DRM graphics-core metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

`gc_12_0_0_offset.h` gives AMDGPU, KFD, MES, IMU, gfxhub, and SOC24 code symbolic addresses for GC 12.0.0 hardware registers. Driver code passes these macros to `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_FIELD15_PREREG`, ring-packet emitters, golden-register tables, and dump/debug helpers. The paired `_BASE_IDX` macros select the register base aperture used by SOC15 addressing.

This chunk focuses on these hardware areas:

- CP RS64 firmware and scheduler registers for MEC and graphics pipes, including program counters, interrupt/pending/exception state, GP registers, local/instruction/scratch apertures, data-cache base/control/operation registers, and repeated data-cache aperture windows.
- CPWD channel and cache-side control registers: `CH`, `CHA`, `CHC`, `CHI`, `GL2A`, and `GL2C` control, steering, compression, credits, status, and disable/override registers.
- CP, CPF, CPG, CPC, GE, GE1, GE2, GC-EA, GCR, CHA, CHC, GL2A, GL2C, and GRBM performance counters and selector registers.
- GDFLL, XVMIN, GRTAVFS, and RTAVFS registers used around graphics voltage/frequency and adaptive-voltage/frequency monitor/control blocks.
- RLC and RLCS control/status/programming space, including safe mode, clear-state buffer addressing, microcode RAM access, timers, power-gating and clock-gating controls, SPM/perfmon registers, save/restore machine state, GPM general/semaphore registers, UTCL1/UTCL2 error/status registers, and IMU/RLC message registers.
- PF/VF-facing RLC interrupt and scheduler registers exposed through the `pfvfdec_rlc` address block.
- PWR, PSP, CH power, and GFX IMU register blocks for IMU firmware loading, IMU/RLC RAM access, C2P message access, reset status, bootloader addresses, and IRAM/DRAM data ports.
- Shader-engine register blocks for GRBMH, PA debug/rate/safe registers, SQ/SQC/SQG/SP/LDS debug and indirect access registers, SX debug-busy registers, and early SPI debug, CU-mask, lifetime, load-balance, GDS-credit, and active-wave counters.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocations, callbacks, or executable branches in this range. The public interface is the macro naming and address contract:

- `regNAME` expands to a register offset value, such as `regCP_MEC_RS64_CNTL`, `regRLC_SAFE_MODE`, `regGFX_IMU_I_RAM_DATA`, `regSQ_IND_INDEX`, or `regSPI_WGP_WORK_PENDING`.
- `regNAME_BASE_IDX` expands to the SOC15 base-index selector. In this chunk CPWD/RLC/IMU registers primarily use base index `1`; shader-engine blocks such as GRBMH, PA, SQ, SX, and SPI primarily use base index `0`.
- Matching field layouts live in `gc_12_0_0_sh_mask.h`. Consumers combine this offset header with shift/mask macros through `REG_SET_FIELD`, `REG_GET_FIELD`, and explicit masks such as `RLC_SAFE_MODE__CMD_MASK`.
- Consumers usually reach these constants through AMDGPU register helpers rather than raw MMIO arithmetic: `SOC15_REG_OFFSET(GC, inst, regX)`, `RREG32_SOC15(GC, inst, regX)`, `WREG32_SOC15(GC, inst, regX, value)`, `WREG32_SOC15_NO_KIQ`, and ring-based write-register packets.

Important register families in this chunk include:

- `CP_MEC_*`: MEC RS64 program counter, trap/interrupt registers, MIE/MIP timer registers, GP registers, local/instruction/scratch apertures, data-cache control, and repeated `CP_MEC_DC_APERTURE0..15_{BASE,MASK,CNTL}` entries.
- `CP_GFX_RS64_*`: graphics RS64 data-cache apertures for data cache instances 0 and 1, plus exception/interrupt entries that support PFP/ME RS64 firmware data cache setup.
- `CH*`, `GL2*`, `GC_EA_*`, `GCR_*`: channel/cache/memory-fabric control, pipe steering, SDP credits/reserves/priority/enable, and performance counters.
- `RLC_*` and `RLC_RLCS_*`: the largest family in this chunk, covering core RLC enable/status, microcode data ports, SPM and perfmon, clear-state, save/restore, power and clock gating, CGCG/CGLS, SRM, GPM, UTCL error reporting, semaphore, IMU mailbox/telemetry, SDMA interrupt bridge, memory power control, and RLCS end/status registers.
- `GFX_IMU_*`: IMU C2P message access, scratch, core/reset control, RLC RAM index/address/data, bootloader address/size, and IMU IRAM/DRAM address/data ports.
- `GRBMH_*`, `PA_*`, `SQ*`, `SX_*`, `SPI_*`: shader-engine and shader-processor control/debug/status offsets, including SQ indirect read/write, watchpoint address/control registers, CU masks, WGP/work-pending status, load-balance data, and active-wave counters.

## Control Flow

This header has no runtime control flow. Its direct behavior is compile-time macro substitution.

The implied runtime flow is in AMDGPU consumers:

1. The active SOC/IP path includes `gc_12_0_0_offset.h` and the matching `gc_12_0_0_sh_mask.h`.
2. Code selects the GC instance or XCC/pipe/queue context through SOC24/GRBM selection helpers where required.
3. A register offset macro from this file and a field macro from the shift/mask header are combined to build an MMIO address or register value.
4. The driver writes or reads the register via SOC15 helpers, indirect SQ access, RLC-safe paths, KIQ/ring packets, or firmware loader loops.
5. Hardware side effects, waits, resets, cache invalidations, and firmware handshakes are implemented in the consumer code, not in this generated file.

Concrete examples from nearby consumers:

- `gfx_v12_0.c` programs MEC RS64 start addresses with `regCP_MEC_RS64_PRGRM_CNTR_START` and `_HI`, resets MEC pipes through `regCP_MEC_RS64_CNTL`, and checks `regCP_MEC_RS64_INSTR_PNTR` during compute pipe reset.
- `gfx_v12_0.c` programs PFP/ME/MEC firmware data-cache bases through `regCP_GFX_RS64_DC_BASE0_LO/HI`, `regCP_GFX_RS64_DC_BASE1_LO/HI`, `regCP_MEC_MDBASE_LO/HI`, `regCP_MEC_DC_BASE_CNTL`, and `regCP_MEC_DC_OP_CNTL`, with explicit invalidate-complete polling in the shift/mask fields.
- RLC initialization writes clear-state buffer addresses through `regRLC_CSIB_ADDR_HI`, `regRLC_CSIB_ADDR_LO`, and `regRLC_CSIB_LENGTH`; starts/stops RLC through `regRLC_CNTL`; toggles SMU handshake and clock-gating state through `regRLC_PG_CNTL`, `regRLC_CGTT_MGCG_OVERRIDE`, and `regRLC_CGCG_CGLS_CTRL`; and enters/exits safe mode with `regRLC_SAFE_MODE`.
- RLC firmware loading uses `regRLC_GPM_UCODE_ADDR/DATA`, `regRLC_LX6_IRAM_ADDR/DATA`, and `regRLC_LX6_DRAM_ADDR/DATA`.
- IMU loading and setup in `imu_v12_0.c` uses `regGFX_IMU_I_RAM_ADDR/DATA`, `regGFX_IMU_D_RAM_ADDR/DATA`, `regGFX_IMU_C2PMSG_ACCESS_CTRL0/1`, `regGFX_IMU_C2PMSG_16`, `regGFX_IMU_SCRATCH_10`, `regGFX_IMU_CORE_CTRL`, and `regGFX_IMU_GFX_RESET_CTRL`.
- SQ debug and KFD/debug paths use SQ indirect or command registers such as `regSQ_IND_INDEX`, `regSQ_IND_DATA`, and `regSQ_CMD`.

## State And Persistence Behavior

The macros themselves hold no state and persist nothing. They describe hardware-visible state whose lifetime is owned by the GPU and driver programming sequence:

- CP MEC and graphics RS64 state persists in command-processor registers and firmware data-cache aperture registers until reset, reprogrammed, context-switched, or lost across GPU reset/power events. Program-counter, trap, timer, interrupt, and GP registers may be firmware-owned while the CP is running.
- CP data-cache aperture registers define firmware-visible memory windows. Wrong base/mask/control offsets can redirect firmware loads/stores, break instruction/data cache invalidation, or expose the wrong memory region to a CP micro-engine.
- Performance counter registers are sampled or latched hardware state. Counter low/high pairs and selector registers must be programmed/read in valid order by perfmon/SPM code.
- RLC state persists across many low-power and context-save operations. Safe mode, clear-state buffer addresses, SRM enable, clock/power gating controls, SPM buffers, GPM data, semaphores, and UTCL error/status registers are mutable hardware state. Some registers are firmware ports where repeated writes stream microcode or RAM contents.
- IMU IRAM/DRAM and RLC RAM ports act as indexed firmware-memory accessors. Address/data register ordering matters, and version stamps written back to address registers are used by the driver as part of the load sequence.
- Shader-engine status/debug registers are per-SH/SE or indexed through shader-array selection. SQ watch registers and SPI CU masks are persistent debug or dispatch-affinity state until reprogrammed.

This header does not encode read-only, write-only, write-one-to-clear, latch, poll, or side-effect semantics. Those behaviors must come from the hardware programming guide, the matching shift/mask header, firmware contracts, and the surrounding AMDGPU code.

## Dependencies And Integration Points

The immediate dependency is `gc_12_0_0_sh_mask.h`, which provides the field definitions used with these offsets. The offset values also depend on AMD's generated GC 12.0.0 register database and must stay synchronized with other GC 12.0.0 generated headers, defaults, firmware interfaces, and SOC24 IP discovery data.

Observed integration points in this tree include:

- `drivers/gpu/drm/amd/amdgpu/gfx_v12_0.c`, the main GFX 12 implementation. It consumes many registers from this chunk for CP firmware loading, MEC compute enable/reset, RLC startup, RLC safe mode, clock/power gating, clear-state buffer programming, SQ indirect reads, interrupt registers, pipe reset diagnostics, and golden settings.
- `drivers/gpu/drm/amd/amdgpu/mes_v12_0.c`, which includes this header for MES queue scheduler interaction and register access.
- `drivers/gpu/drm/amd/amdgpu/imu_v12_0.c`, which uses the GFX IMU and several golden-register offsets in this range.
- `drivers/gpu/drm/amd/amdgpu/gfxhub_v12_0.c`, `sdma_v7_0.c`, and `soc24.c`, which include the same generated GC 12.0.0 register headers for hub setup, SDMA/SOC-level integration, and register initialization.
- `drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v12.c`, `drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_v12.c`, and `drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_v12.c`, which rely on the same GC 12.0.0 register definitions for KFD compute queues, MQDs, and scheduler/debug behavior.
- Firmware blobs and firmware headers for MEC, PFP, ME, RLC, MES, and IMU, whose load/start/status sequences depend on these register addresses matching the hardware.

## Risks And Edge Cases

- Generated-header drift is the primary risk. A wrong offset or base index compiles cleanly but sends MMIO to the wrong register or aperture.
- This chunk starts and ends inside larger generated structures. The previous chunk owns the beginning of `gc_gfx_cpwd_cpwd_cprs64dec`, including early CP MEC RS64 definitions; the next chunk completes the SPI family. File-level research should merge those artificial boundaries before making complete claims about the whole address block.
- `_BASE_IDX` mistakes are as damaging as bad offsets. Most CPWD/RLC/IMU registers in this chunk use base index `1`, while shader-engine blocks use base index `0`; mixing them can address the wrong MMIO base even when the numeric offset is correct.
- CP RS64 data-cache and firmware-start registers are boot-critical. Bad `CP_MEC_*` or `CP_GFX_RS64_*` offsets can cause firmware load failure, cache invalidation timeouts, stuck MEC/PFP/ME pipes, bad ring tests, or unrecoverable GPU resets.
- Repeated data-cache aperture and performance-counter families are copy-sensitive. A single off-by-one in `APERTURE0..15` or counter low/high/select pairs may only fail under a specific pipe, aperture, or counter slot.
- RLC safe mode, SRM, SPM, and power/clock-gating registers have strict ordering and side effects. Wrong offsets can leave RLC enabled when it should be quiesced, make safe-mode polling time out, corrupt clear-state restore, or break GFXOFF/SMU handshake behavior.
- Firmware-memory data ports such as `RLC_*_UCODE_DATA`, `RLC_LX6_*_DATA`, and `GFX_IMU_*_RAM_DATA` are sequential access points. Misaddressing the data or address register can silently load corrupt microcode.
- PF/VF and SR-IOV-sensitive registers such as the RLC PF/VF block and KIQ/no-KIQ paths can behave differently in virtualized environments. A register that works on bare metal may be trapped, virtualized, or inaccessible in a VF.
- SQ/SPI/PA debug and watch registers may be per-SE/per-SH, selected by GRBM/SRBM state, or indirect. Wrong offsets or missing selection can produce misleading dumps rather than immediate failures.
- Performance and power registers often produce subtle regressions. Errors in GDFLL/GRTAVFS/RTAVFS, clock-gating, CU-mask, or SPI lifetime/load-balance registers may show up as clocks, residency, dispatch fairness, or perf-counter anomalies rather than a hard fault.

## Test Signals

Useful validation should combine generated-data checks, build coverage, and runtime hardware tests:

- Build AMDGPU with GFX 12, SOC24, MES, KFD, IMU, SDMA, and gfxhub support enabled. Missing or renamed macros should surface in the include users listed above.
- Mechanically compare lines 4979-7470 against AMD's authoritative GC 12.0.0 register database. Check that each non-`BASE_IDX` register has exactly one matching `_BASE_IDX`, and that the base index matches the address block's expected aperture.
- Run structural checks for repeated families: `CP_MEC_DC_APERTURE0..15`, `CP_GFX_RS64_DC_APERTURE0..15` for both cache instances, perfcounter low/high/select pairs, `RLC_SPM_*`, `RLC_SRM_INDEX_CNTL_ADDR/DATA_0..7`, `RLC_SEMAPHORE_0..3`, `SQ_WATCH0..3`, and `SPI_CONFIG_CU_MASK_*`.
- Boot on GC 12.0.0 hardware and watch for successful RLC, MEC, PFP, ME, MES, and IMU firmware load messages. Failure signals include RLC autoload timeout, instruction/data cache invalidation timeout, IMU start timeout, and failed ring tests.
- Exercise graphics and compute ring initialization, queue submission, preemption/reset, and recovery. Relevant signals are stuck CP/MEC pipe resets, nonzero CP/MEC instruction-pointer deltas after reset, KIQ readiness failures, and MES legacy queue reset fallback.
- Exercise RLC safe-mode entry/exit, clear-state buffer programming, GFXOFF/power-gating transitions, clock-gating toggles, SPM perfmon, and SRM save/restore. Watch for safe-mode polling timeouts, bad clear-state restore, SPM VMID programming failures, or GFXOFF residency regressions.
- Validate IMU firmware loading and IMU-driven power-up paths. Check C2P access control, IMU reset-status polling, IRAM/DRAM loading, and any APU-specific `amdgpu_dpm_set_gfx_power_up_by_imu` behavior.
- Run SQ/SPI debug tests: SQ indirect register reads, shader debugger/watchpoint use, SPI CU mask and WGP work-pending status reads, and active-wave/lifetime counter collection.
- Run performance-counter and profiling workloads using CP, CPF/CPC/CPG, GE, GC-EA, GCR, CHA/CHC, GL2A/GL2C, GRBM, RLC, SQ, SX, and SPI counters. Expected signals are stable counter reads, sane low/high composition, and no selector aliasing.
- Run SR-IOV VF and bare-metal coverage where available, especially around no-KIQ RLC SPM access, RLC PF/VF interrupt/status registers, MES queue management, and trapped register writes.

## Cross-Chunk Notes

The previous chunk contains the start of `gc_gfx_cpwd_cpwd_cprs64dec`; this chunk starts at `regCP_MEC_GP1_LO_BASE_IDX` after `regCP_MEC_GP1_LO` was defined on the prior line. The next chunk begins immediately after `regSPI_LB_DATA_PERWGP_WAVE_HSGS_BASE_IDX` and should complete the SPI low-bandwidth per-WGP wave counters and remaining shader-engine register offsets. The final per-file document should reconcile these chunk boundaries before describing complete CP RS64 or SPI register families.

### subset-b-002567: lines 7471-9953

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_offset.h lines 7471-9953

## Chunk Scope

This chunk is a generated AMD GC 12.0.0 register offset header segment. It contains C preprocessor constants only: each visible register macro maps a symbolic `reg...` name to a 32-bit register offset value, and each companion `reg..._BASE_IDX` macro maps that register to a SOC15 base-index selector. There are no functions, structs, enums, callbacks, locks, allocations, branches, or software-owned storage declarations in this range.

The range contains 2,403 `#define` lines: 1,202 register offset definitions and 1,201 `_BASE_IDX` definitions. The count is intentionally uneven because the chunk ends at `regSQG_PERFCOUNTER7_LO`; its companion `regSQG_PERFCOUNTER7_LO_BASE_IDX` is on the next source line outside this work item. The chunk also begins inside an existing SPI address block from the previous chunk before the first local address-block marker.

Visible address-block markers in this slice cover these GC graphics/shader-engine register regions:

- Tail of a preceding SPI block: live wave counters, debug reads, trap-screen pointers, and crawler configuration.
- `gc_gfx_se_gfx_se_tpdec` at `0x9400`: TD/TA control, status, power, DSM, and scratch registers.
- `gc_gfx_se_gfx_se_rbdec` at `0x9800`: DB/CB/GB backend debug, FIFO, arbitration, memory, backend map, and cache-control registers.
- `gc_gfx_se_gfx_se_spipdec2` at `0x9c80`: SPI PQEV and export-throttle controls.
- `gc_gfx_se_rmi_gfx_se_rmidec` at `0x2e200`: RMI request-interface control, status, scoreboard, xbar, UTCL1, formatter, clock, CID-map, spare, and redundancy registers.
- `gc_gfx_se_gfx_se_utcl1dec` at `0x9fb0`: GCR PIO and PMM controls/status.
- `gc_gfx_se_gfx_se_shdec` at `0xb000`: shader program addresses/resources/user data for PS/GS/VS/HS, SQ configuration controls, shader trap/debug, and SQC performance-snapshot registers.
- `gc_gfx_se_gfx_se_spipdec` at `0xc700`: SPI interpolation, thread-grouping, LDS, barycentric, and attribute-ring controls.
- `gc_gfx_se_gfx_se_tcpdec` at `0xca80`: TCP UTCL1 control/status, debug, cache, address/config, and invalidation-related registers.
- `gc_gfx_se_gfx_se_rasdec` at `0xce00`: GL1/SPI/SQ/SQC/TCP/TD/TA RAS and EDC count/control registers.
- `gc_gfx_se_gfx_se_gfxdec0` at `0x28000`: the largest block in this chunk, covering DB render/depth/stencil state, PA/SC viewport and rasterizer state, VGT and GE geometry state, CB color-buffer state, blend state, SX controls, depth/color base addresses, DB/CB clear words, clip/viewport transforms, and indexed multi-slot state families.
- `gc_gfx_se_gfx_se_pfvf_padec` at `0x2a500`: PF/VF-accessible PA/SC screen, trap-screen, binning, primitive-filter, and sample-pattern registers.
- `gc_gfx_se_gfx_se_pfvf_sqdec` at `0x2a780`: PF/VF-accessible SQ counters, watermarks, ring sizes, and WGP reserved-resource registers.
- `gc_gfx_se_gfx_se_pfonly_spidec`, `pfonly_utcl1dec`, `pfonly_tcpdec`, and `pfonly2_spidec`: PF-only SPI, UTCL1, TCP, and per-CU resource-reservation controls.
- `gc_gfx_se_gfx_se_gfxudec` at `0x30000`: user/config-like GE/VGT/PA/SC/SQ/SQC/TA/DB/SPI/CB/SX state, shader engine metrics, and debug state.
- `gc_gfx_se_gfx_se_gl1dec` at `0x33400`: GL1C/GL1A/GL1X/GL1I/GL1XC cache invalidation, status, control, event, and debug registers.
- `gc_gfx_se_gfx_se_pfonly_secacdec` at `0x33a00`: SE CAC control/status, accumulator, and block-weight registers.
- `gc_gfx_se_gfx_se_perfddec` at `0x34000`: GE2, GRBMH, PA_SU, PA_SC, SPI, PC, SQ, and SQG performance counter data registers.

Although the repository path includes `ceph-client`, this file is AMDGPU hardware metadata, not Ceph filesystem logic.

## Purpose

`gc_12_0_0_offset.h` supplies symbolic register offsets for AMD GC 12.0.0 graphics-core programming. Consumers combine these offsets with SOC15 register helpers such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_SOC15_OFFSET`, and `WREG32_SOC15_OFFSET`. The companion `gc_12_0_0_sh_mask.h` file supplies bit shifts and masks for fields inside the registers named here.

This slice focuses on shader-engine and graphics-pipeline register addressability:

- Shader processor input (`SPI`) state for shader program pointers, resource descriptors, user data, accumulators, trap-screen state, LDS/thread-grouping controls, interpolation and attribute-ring configuration, live wave counts, and SPI performance counters.
- Shader queue (`SQ`) and shader cache (`SQC`) controls for config, status, counters, wave/dispatch behavior, trap/debug state, thread trace user data, reserved resources, and performance data.
- Texture/data path blocks (`TA`, `TD`, `TCP`, `UTCL1`, `GL1*`) for texture address/data controls, cache invalidation/status, UTCL1 request/fault paths, compression/arbitration, GL1 cache events, and debug access.
- Render backend blocks (`DB`, `CB`, `GB`, `SX`) for depth/stencil/color render state, backend maps, framebuffer/depth buffer base addresses, blend state, cache-control/debug, occlusion counters, and backend disable/topology registers.
- Primitive assembly, scan conversion, and geometry blocks (`PA`, `SC`, `VGT`, `GE`, `PC`) for viewport, scissor, clipping, rasterization, binning, screen extents, primitive rings, transform feedback, tessellation/offchip parameters, line stipple, sample pattern, primitive filtering, and performance counters.
- Request-interface and reliability blocks (`RMI`, `RAS`, `SE_CAC`) for request routing/status, scoreboard/xbar state, UTCL1 interaction, RAS/EDC counters, and shader-engine current/activity accounting.
- SR-IOV split ownership blocks: `PFVF` regions expose selected state to both physical and virtual functions, while `PFONLY` regions name privileged controls that should normally remain PF/firmware owned.

The header is part of the hardware ABI between AMDGPU driver code, generated register databases, firmware/golden-register programming, and the GC 12 silicon register map. It does not describe policy by itself; it gives the exact numeric offsets that policy code uses when it programs the GPU.

## Important APIs, Types, And Macros

There are no callable APIs or local types. The exported interface is the generated macro namespace.

Key macro families in this chunk:

- SPI debug, trap, and wave-observation registers: `regSPI_LB_DATA_PERWGP_WAVE_PS`, `regSPI_LB_DATA_PERWGP_WAVE_CS`, `regSPI_WF_ACTIVE_COUNT_GFX`, `regSPI_WF_ACTIVE_COUNT_HPG`, `regSPIS_DEBUG_READ`, `regBCI_DEBUG_READ`, `regSPI_P0_TRAP_SCREEN_*`, `regSPI_P1_TRAP_SCREEN_*`, `regSPI_GFX_CRAWLER_CONFIG`, and `regSPI_CS_CRAWLER_CONFIG`.
- TD/TA controls: `regTD_CNTL`, `regTD_STATUS`, `regTD_POWER_CNTL`, `regTD_DSM_CNTL*`, `regTA_CNTL`, `regTA_CNTL_AUX`, `regTA_CNTL2`, `regTA_STATUS`, and scratch registers.
- DB/CB/GB backend controls in `rbdec`: `regDB_DEBUG*`, `regDB_CREDIT_LIMIT`, `regDB_WATERMARKS`, `regDB_FIFO_DEPTH*`, `regDB_RING_CONTROL`, `regDB_EXCEPTION_CONTROL`, `regDB_MEM_CONFIG`, `regDB_ARB_CONFIG`, `regDB_DFD_INDIRECT_*`, `regDB_FGCG_*`, `regCC_RB_BACKEND_DISABLE`, `regGB_ADDR_CONFIG`, `regGB_BACKEND_MAP`, `regGB_GPU_ID`, and `regCB_HW_CONTROL*`.
- RMI controls/status: `regRMI_GENERAL_CNTL*`, `regRMI_GENERAL_STATUS`, `regRMI_SUBBLOCK_STATUS*`, `regRMI_XBAR_CONFIG`, `regRMI_DEMUX_CNTL`, `regRMI_UTCL1_CNTL*`, `regRMI_UTC_UNIT_CONFIG`, `regRMI_TCIW_FORMATTER*`, `regRMI_SCOREBOARD_*`, `regRMI_XBAR_ARBITER_CONFIG*`, `regRMI_CLOCK_CNTRL`, `regRMI_UTCL1_STATUS`, `regRMI_RB_GLX_CID_MAP`, `regRMI_XNACK_DEBUG`, `regRMI_SPARE*`, and `regCC_RMI_REDUNDANCY`.
- UTCL1/GCR/PMM registers: `regGCR_PIO_CNTL`, `regGCR_PIO_DATA`, `regPMM_CNTL`, `regPMM_STATUS`, `regGCR_PIO_INDEX`, and `regGCR_PIO_DATA_2`.
- Shader program and user-data register families: `regSPI_SHADER_PGM_*_PS`, `regSPI_SHADER_USER_DATA_PS_0` through `_31`, `regSPI_SHADER_USER_ACCUM_PS_*`, GS/ES program and user-data registers, VS program and user-data registers, HS program and user-data registers, shader checksums, and shader request/output config registers.
- SQ and SQC controls: `regSQ_CONFIG`, `regSQ_PERFCOUNTER_CTRL`, `regSQG_CONFIG`, `regSQ_THREAD_TRACE_*`, `regSQ_WAVE_*`, `regSQ_DEBUG_*`, `regSQ_WAVE_STATUS`, `regSQ_CMD`, `regSQ_IND_*`, `regSQC_CONFIG`, `regSQC_CACHES`, and SQC performance-snapshot registers.
- SPI pipeline controls: `regSPI_PS_INPUT_*`, `regSPI_BARYC_CNTL`, `regSPI_TMPRING_SIZE`, `regSPI_GDBG_*`, `regSPI_SHADER_LATE_ALLOC_*`, `regSPI_SHADER_PGM_RSRC4_*`, `regSPI_CONFIG_CNTL*`, `regSPI_GS_THROTTLE_CNTL*`, `regSPI_ATTRIBUTE_RING_*`, `regSPI_PS_INPUT_CNTL_0` through `_31`, and `regSPI_SHADER_COL_FORMAT`.
- TCP registers: `regTCP_UTCL1_CNTL`, `regTCP_UTCL1_STATUS`, `regTCP_DEBUG`, `regTCP_CHAN_STEER_*`, `regTCP_CNTL`, `regTCP_ADDR_CONFIG`, `regTCP_INVALIDATE`, `regTCP_STATUS`, `regTCP_CNTL2`, `regTCP_CREDIT`, `regTCP_COMPRESSION_CNTL`, and `regTCP_ARB`.
- RAS/EDC registers: `regGL1_EDC_CNT`, `regSPI_EDC_CNT`, `regSQ_EDC_CNT*`, `regSQC_EDC_*`, `regTCP_EDC_CNT*`, `regTD_EDC_CNT`, `regTA_EDC_CNT`, `regGE_EDC_CNT`, `regGL1_EDC_MODE`, `regSPI_EDC_MODE`, `regSQ_EDC_MODE`, `regTCP_EDC_MODE`, and related parity/control entries.
- `gfxdec0` render state families: `regDB_RENDER_CONTROL`, `regDB_DEPTH_VIEW*`, `regDB_RENDER_OVERRIDE*`, `regDB_DEPTH_SIZE_XY`, `regDB_Z_INFO`, `regDB_STENCIL_INFO`, DB read/write base registers, `regDB_DEPTH_CONTROL`, `regDB_STENCIL_CONTROL`, `regDB_EQAA`, `regDB_ALPHA_TO_MASK`, `regPA_SC_VPORT_*`, `regPA_CL_*`, `regVGT_*`, `regGE_*`, `regPA_SU_*`, `regPA_SC_*`, `regCB_COLOR*`, `regCB_BLEND*`, `regSX_*`, `regDB_HTILE_*`, `regCB_DCC_*`, and repeated viewport/scissor/window/clip color families.
- PF/VF and PF-only control families: `regPA_SC_SCREEN_EXTENT_*`, `regPA_SC_*_TRAP_SCREEN_*`, `regPA_SC_BINNER_*`, `regPA_SC_PRIM_FILTER_*`, `regSQ_WGP_*`, `regSQ_PERF_SNAPSHOT_*`, `regUTCL1_*`, `regTCP_*`, and `regSPI_RESOURCE_RESERVE_*`.
- GL1 cache controls: `regGL1C_GL1C_ADDR_MATCH_MASK`, `regGL1C_CNTL`, `regGL1C_STATUS`, `regGL1C_CTRL*`, `regGL1A_*`, `regGL1X_*`, `regGL1I_*`, `regGL1XC_*`, and `regGL1C_DEBUG`.
- Shader-engine CAC registers: `regSE_CAC_CNTL`, `regSE_CAC_STATUS`, `regSE_CAC_ACC_*`, `regSE_CAC_WEIGHT_*`, `regSE_CAC_IND_INDEX`, and `regSE_CAC_IND_DATA`.
- Performance data registers: `regGE2_SE_PERFCOUNTER*_LO/HI`, `regGRBMH_PERFCOUNTER*_LO/HI`, `regPA_SU_PERFCOUNTER*_LO/HI`, `regPA_SC_PERFCOUNTER*_LO/HI`, `regSPI_PERFCOUNTER*_LO/HI`, `regPC_PERFCOUNTER*_LO/HI`, `regSQ_PERFCOUNTER*_LO`, and `regSQG_PERFCOUNTER*_LO/HI`.

The `_BASE_IDX` values are part of the interface. In this chunk, early shader-engine block registers use base index `0`, while later large per-block/user/config/performance regions use base index `1`. SOC15 helper macros depend on that base index to compute the correct MMIO address for the selected GC instance.

## Control Flow

This header has no software control flow. Runtime sequencing lives in the AMDGPU and AMDKFD code that includes the generated register headers.

Observed direct GC 12 include users in this tree include:

- `drivers/gpu/drm/amd/amdgpu/gfx_v12_0.c`
- `drivers/gpu/drm/amd/amdgpu/gfxhub_v12_0.c`
- `drivers/gpu/drm/amd/amdgpu/gfxhub_v12_1.c`
- `drivers/gpu/drm/amd/amdgpu/mes_v12_0.c`
- `drivers/gpu/drm/amd/amdgpu/imu_v12_0.c`
- `drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v12.c`
- `drivers/gpu/drm/amd/amdgpu/soc24.c`
- `drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_v12.c`
- `drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_v12.c`

In those consumers, offset macros from this file are passed to SOC15 accessors and register-list helpers. Typical runtime flows that rely on this address metadata are:

- GFX bring-up and reset paths load GC 12 firmware, initialize RLC/CP/MEC/MES-related state, program golden registers, and access GC registers through `RREG32_SOC15`/`WREG32_SOC15`.
- Graphics command stream submission programs context registers that correspond to many `gfxdec0`, `gfxudec`, shader, DB/CB, PA/SC, VGT, SPI, and SQ offsets in this chunk.
- KFD and MES queue-management paths use GC 12 shader and queue register definitions, via the same generated namespace, to build and manage compute queues and MQDs.
- VM hub paths mostly use other regions of `gc_12_0_0_offset.h`, but they share the same offset/header scheme and base-index semantics.
- IMU/RLC golden-register programming references some offsets in this chunk directly; for example `imu_v12_0.c` programs `regRMI_GENERAL_CNTL` golden values.
- Performance-monitoring and diagnostics read the per-block performance counter data registers here after selection/configuration registers, some of which are in adjacent chunks.

The header does not encode ordering requirements. For example, it names render, cache, trap, invalidation, and performance-counter registers, but it does not say when to quiesce the GPU, which domains must be powered, whether a write is packet-only versus MMIO-safe, whether a register is read-only or write-one-to-clear, or which PF/VF entity is allowed to touch it.

## State And Persistence Behavior

The file persists no software state. It names hardware registers whose state persists according to GPU block lifetime: until explicit driver/firmware rewrite, command-stream context switch, golden-register restore, graphics reset, full GPU reset, power-gating loss, suspend/resume restore, or SR-IOV PF/VF ownership rules.

Important hardware state represented by this chunk includes:

- Shader program state: program base addresses, resource words, user-data SGPR mappings, checksums, request controls, late allocation, and shader accumulators for PS/GS/VS/HS.
- Graphics render context: depth/stencil/color buffer metadata, render overrides, viewport/scissor/window state, clip and guard-band state, primitive/rasterizer controls, blend controls, clear values, tile/compression metadata addresses, sample locations, binning and primitive filtering, and trap-screen windows.
- Cache and data-path state: TCP/GL1/UTCL1 invalidation/status/debug controls, texture address/data path controls, GL1 cache event controls, compression controls, and address configuration.
- Backend topology and routing: GB address/backend map registers, CB/DB hardware controls, backend disable state, RMI demux/xbar/scoreboard/status, and CID mapping.
- Reliability and accounting state: RAS/EDC counters, EDC modes, SE CAC accumulators and weights, SQ/SQC/TCP/SPI/TA/TD counters, and block-specific performance counters.
- Debug and trace state: SQ thread-trace user data, SQ wave/debug registers, SPI crawler/trap-screen registers, indirect debug selectors/data, and live wave counters.
- SR-IOV partitioned state: PF/VF-accessible state in `pfvf_*` blocks, plus privileged PF-only controls for SPI, UTCL1, TCP, and SE CAC.

Because this header only supplies offsets, it does not distinguish context-switched command-stream state from static golden registers or live status counters. Consumers must preserve those distinctions. Whole-register writes to status/debug/cache/control registers are especially sensitive because reserved bits, sticky status bits, self-clearing request bits, and firmware-owned fields are not marked in this file.

## Dependencies And Integration Points

The closest generated companion is `gc_12_0_0_sh_mask.h`, which defines bitfield shift/mask macros for the registers named here. Other generated companions in the same `asic_reg/gc` directory provide default values and additional register generations. Consumers depend on the spelling and numeric offsets in this file matching the GC 12.0.0 register database exactly.

Primary integration points:

- SOC15 register access: `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_SOC15_OFFSET`, `WREG32_SOC15_OFFSET`, and field helpers combine these `reg...` offsets with the GC hardware instance and base-index data.
- GFX v12 core driver: command processor, RLC, graphics-ring, shader-engine, golden-register, hang/reset, and debug paths include this header as part of the GC 12 register ABI.
- MES v12 and KFD v12: compute scheduling, MQD setup, queue management, and debug paths include the GC 12 masks and offsets to describe hardware queue/shader state.
- IMU/RLC initialization: golden-register tables can write offsets from this chunk, including RMI controls, during firmware-assisted setup.
- Graphics user-mode driver command streams: many `gfxdec0`/`gfxudec` registers are context or user/config registers normally written by packets generated outside the kernel, while the kernel still needs correct symbolic names for validation, debugging, reset dumps, and golden state.
- Performance and profiling: per-block `*_PERFCOUNTER*_LO/HI` registers integrate with the perf counter selection/control registers in adjacent chunks and with profiling tools that sample shader-engine counters.
- SR-IOV: `PFVF` and `PFONLY` address blocks make ownership explicit at the register-map level. Kernel code must honor PF/VF restrictions when adding direct MMIO programming.

The macros are syntactically just C preprocessor constants, so accidental cross-generation inclusion can still compile. The semantic dependency is the GC generation: using GC 12.0.0 offsets with another GC version's masks, defaults, or hardware can silently address the wrong register.

## Risks And Maintenance Notes

- Generated offset drift is high impact. A single wrong numeric offset can program an unrelated hardware register while compiling cleanly.
- The chunk boundaries are artificial. The start is the tail of a prior SPI block, and the end omits the `_BASE_IDX` for `regSQG_PERFCOUNTER7_LO`; the final per-file report must reconcile adjacent chunks before treating these families as complete.
- `_BASE_IDX` values are part of address calculation. Changing base index `0` versus `1` is as dangerous as changing the offset itself.
- This slice mixes live status, debug, command/context state, cache invalidation controls, trap controls, and performance counters. The header does not mark access direction, side effects, volatility, privilege, or synchronization requirements.
- Render state families are large and repetitive. Off-by-one errors in indexed families such as viewport transforms, scissor windows, CB color targets, blend controls, PS input controls, resource-reserve registers, or performance counters can produce slot-specific rendering or profiling failures.
- PF-only and PF/VF blocks need careful ownership checks under SR-IOV. A register name being available in the header does not imply that VF code may write it.
- Performance counter data registers in this chunk are only the data side of a larger mechanism. Selection, enable, freeze, and counter-reset controls are partly outside this range, so validation must include adjacent chunks.
- RAS/EDC and SE CAC registers are often tied to reliability, telemetry, and power/activity accounting. Uncoordinated writes can hide errors, perturb accounting, or conflict with firmware.
- Many `gfxdec0`/`gfxudec` registers are normally packet-programmed context state. Direct MMIO writes from kernel paths can race command submission unless the GPU is idle, reset, or otherwise synchronized.
- Debug/trap/thread-trace registers may expose or alter per-wave execution state. Reads and writes should be limited to debug flows that understand wave selection and trap-screen sequencing.

## Test Signals

Useful validation is mostly generated-data, build-time, and hardware-integration oriented:

- Preprocess/compile GC 12 paths that include `gc_12_0_0_offset.h` and `gc_12_0_0_sh_mask.h`: `gfx_v12_0.c`, `gfxhub_v12_0.c`, `gfxhub_v12_1.c`, `mes_v12_0.c`, `imu_v12_0.c`, `amdgpu_amdkfd_gfx_v12.c`, KFD v12 queue/MQD managers, and `soc24.c`.
- Static checks that every register offset in the full generated file has exactly one `_BASE_IDX` companion, with explicit chunk-boundary exceptions only during chunk-level research.
- Cross-check offset/header generation against the authoritative GC 12.0.0 register database, especially base-index transitions at address-block boundaries and repeated indexed families.
- Boot and resume GC 12.0.0 hardware with golden-register programming enabled; verify no register access faults, no early GPU hangs, and expected IMU/RLC programming of entries such as `regRMI_GENERAL_CNTL`.
- Run graphics workloads that exercise DB/CB/PA/SC/VGT/GE/SPI/SQ state: depth/stencil, blending, MSAA/EQAA, scissor/viewport arrays, tessellation, geometry shaders, transform feedback, primitive filtering, binning, and color/depth compression.
- Run compute/KFD/MES workloads that exercise SQ/SPI queue and shader-state programming, including context switches, preemption, queue teardown, and reset recovery.
- Validate cache and invalidation behavior with texture-heavy, render-to-texture, VRAM/system-memory, compression, and VM pressure workloads; watch for stale data, corruption, or hangs around TCP/GL1/UTCL1 controls.
- Exercise SR-IOV PF and VF configurations to confirm PF-only registers are not accessed from VF paths and PF/VF shared registers behave as expected.
- Run RAS/EDC injection or fault-observation tests where available, confirming GL1/SPI/SQ/SQC/TCP/TD/TA counters and modes report expected events.
- Sample performance counters for GE2, GRBMH, PA_SU, PA_SC, SPI, PC, SQ, and SQG while running known workloads; verify low/high pairing, freeze/reset sequencing, and counter selection from adjacent chunks.
- Use debugfs or driver register-dump paths during idle/reset/debug scenarios to ensure debug, trap, thread-trace, and indirect-data registers can be read without side effects outside the intended diagnostic windows.

## Chunk Notes For Merge

This document is source-tree aligned and covers only lines 7471-9953 of `gc_12_0_0_offset.h`. Adjacent chunks should provide the preceding SPI block context before `regSPI_LB_DATA_PERWGP_WAVE_PS` and the continuation after `regSQG_PERFCOUNTER7_LO`, beginning with its missing `_BASE_IDX` and the rest of the SQG/performance-counter region. The final per-file report should treat `gc_12_0_0_offset.h` as generated GC 12.0.0 register-address metadata consumed by AMDGPU GFX, VM hub, MES, KFD, IMU/RLC, debug, SR-IOV, and performance-monitoring paths.

### subset-b-002568: lines 9954-11061

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_offset.h lines 9954-11061

## Scope

This chunk is the final segment of the generated AMD GC 12.0.0 register offset header. It contains C preprocessor constants only: `reg...` macros define MMIO/register offsets, matching `reg..._BASE_IDX` macros define the SOC15 register base index, and `ix...` macros define offsets inside indirect/indexed register spaces. There are no functions, structs, enums, variables, includes, allocations, locks, callbacks, or executable branches in this range.

The slice starts mid-family with `regSQG_PERFCOUNTER7_LO_BASE_IDX`, whose matching `regSQG_PERFCOUNTER7_LO` definition is in the previous adjacent chunk. It then completes graphics/shader-engine performance counter result registers, provides performance counter selection/control registers for the per-SE performance decoder, maps clock-gating/power-management registers, lists user/harvest/remap/security registers, and finishes with several indexed register blocks: GC CAC, RTAVFS, DBGU GFX ports, shader queue debug/wave state, and SE CAC. The chunk ends with the header's `#endif`, so this is the terminal chunk for `gc_12_0_0_offset.h`.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU DRM hardware metadata for AMD graphics IP and is unrelated to Ceph filesystem client behavior.

## Purpose

`gc_12_0_0_offset.h` is the address half of the generated GC 12.0.0 register interface. AMDGPU code combines these symbols with matching shift/mask/default headers and register access helpers to read, write, poll, and program graphics-core hardware registers without hard-coded numeric offsets in driver logic.

This chunk specifically describes:

- Performance counter result registers for shader and render blocks, including `SX`, `TA`, `TD`, `TCP`, `GL1C`, `GL1XC`, `CB`, `DB`, `RMI`, `PA_PH`, `UTCL1`, `GL1A`, and `GL1XA` counter low/high pairs.
- Per-shader-engine performance counter control/select registers under `gc_gfx_se_gfx_se_perfsdec`, including `GE2_SE`, `GRBMH`, `PA_SU`, `PA_SC`, `SPI`, `PC`, `SQ`, `SQG`, `SX`, `TA`, `TD`, `TCP`, `GL1C`, `GL1XC`, `CB`, `DB`, `RMI`, `PA_PH`, `UTCL1`, `GL1A`, and `GL1XA`.
- Shader queue thread-trace registers, including buffer sizes, buffer base addresses, trace control/masks, write pointer, halt/status, poweroff restore, draw/marker counters, dropped packet counter, and finish debug status.
- Graphics clock-gating/power registers under `gc_gfx_se_gfx_se_pwrdec`, `gc_gfx_se_gfx_sc_pwrdec`, and `gc_gfx_se_gfx_se_gl1_pwrdec`, covering SPI, PC, BCI, VGT, GS/NGG, PA, SQ/SQG, SX, TA/TD, DB, CB, RMI, SE CAC, PH, TCP, LDS, UTCL1, GRBMH, SC, GL1C, GL1XC, GL1A, and GL1XA controls.
- Hypervisor/user-topology registers under `gc_gfx_se_gfx_se_hypdec` and related GRBMH/GRBM blocks, including GL1 pipe steering, user shader-array configuration, WGP/RB/RMI disable or redundancy state, shader-rate configuration aliases, and shader-engine/remap controls.
- Security and indirect-register spaces, including `UTCL1_SECURITY`, `ixGC_CAC_*`, `ixRTAVFS_REG0..194`, `ixPACKER_CONTROL`, `ixSQ_*` wave/debug registers, and `ixSE_CAC_*`.

## Important APIs, Types, And Macros

There are no callable APIs or C types. The public interface is the generated macro contract:

- `regNAME` gives the register offset used with AMDGPU SOC15/MMIO register helpers or command-packet register programming.
- `regNAME_BASE_IDX` gives the SOC15 base index. Every `reg..._BASE_IDX` visible in this chunk is `1`, indicating these registers belong to the second base aperture for the GC 12.0.0 generated address map.
- `ixNAME` gives an offset within an indirect/indexed register space rather than a normal `reg...` MMIO offset. Callers must use the matching indirect access path for the block, not a plain MMIO access using the numeric value alone.

Important macro families in this chunk include:

- Counter result pairs: `regSX_PERFCOUNTER0..3_{LO,HI}`, `regTA_PERFCOUNTER0..1_{LO,HI}`, `regTD_PERFCOUNTER0..1_{LO,HI}`, `regTCP_PERFCOUNTER0..3_{LO,HI}`, `regGL1C_PERFCOUNTER0..3_{LO,HI}`, `regGL1XC_PERFCOUNTER0..3_{LO,HI}`, `regCB_PERFCOUNTER0..3_{LO,HI}`, `regDB_PERFCOUNTER0..3_{LO,HI}`, `regRMI_PERFCOUNTER0..3_{LO,HI}`, `regPA_PH_PERFCOUNTER0..7_{LO,HI}`, `regUTCL1_PERFCOUNTER0..3_{LO,HI}`, `regGL1A_PERFCOUNTER0..3_{LO,HI}`, and `regGL1XA_PERFCOUNTER0..3_{LO,HI}`.
- Counter selection/control: `regGE2_SE_PERFCOUNTER*_SELECT*`, `regGRBMH_PERFCOUNTER*_SELECT`, `regPA_SU_PERFCOUNTER*_SELECT*`, `regPA_SC_PERFCOUNTER*_SELECT*`, `regSPI_PERFCOUNTER*_SELECT*`, `regPC_PERFCOUNTER*_SELECT*`, `regSQ_PERFCOUNTER0..15_SELECT`, `regSQG_PERFCOUNTER*_SELECT`, `regSQG_PERFCOUNTER_CTRL*`, `regSQ_PERFCOUNTER_CTRL*`, and block-local select/filter/control registers for SX, TA, TD, TCP, GL1C/GL1XC, CB, DB, RMI, PA_PH, UTCL1, GL1A, and GL1XA.
- Thread trace: `regSQ_THREAD_TRACE_BUF0_*`, `regSQ_THREAD_TRACE_BUF1_*`, `regSQ_THREAD_TRACE_CTRL`, `regSQ_THREAD_TRACE_MASK`, `regSQ_THREAD_TRACE_TOKEN_MASK`, `regSQ_THREAD_TRACE_WPTR`, `regSQ_THREAD_TRACE_HALT`, `regSQ_THREAD_TRACE_STATUS*`, counter registers for GFX/HP3D draw and marker events, dropped counter, and finish debug.
- Clock gating and power: `regGFX_ICG_*`, `regCGTT_*_CLK_CTRL*`, `regCGTX_SPI_DEBUG_CLK_CTRL`, `regSQ_*_CLK_CTRL`, `regICG_*_CLK_CTRL`, `regDB_CGTT_CLK_CTRL_0`, and GL1 medium-grain clock-gating override registers.
- Topology, harvest, remap, and security: `regGL1_PIPE_STEER`, `regGL1X_PIPE_STEER`, `regGC_USER_SHADER_ARRAY_CONFIG`, `regGRBMH_GC_USER_SA_UNIT_DISABLE`, `regGC_USER_SA_UNIT_DISABLE_1`, `regGC_USER_RB_BACKEND_DISABLE`, `regGC_USER_RMI_REDUNDANCY`, `regGC_USER_SHADER_RATE_CONFIG`, `regGRBMH_WGP_SA*_REMAP_CNTL`, `regGRBMH_RB_SA*_REMAP_CNTL`, `regGRBMH_GRBM_SA_REMAP_CNTL`, and `regUTCL1_SECURITY`.
- Indirect blocks: `ixGC_CAC_ID`, `ixGC_CAC_CNTL`, many `ixGC_CAC_ACC_*` accumulator sources, stall/power-break lookup registers, fixed-pattern counters, hardware LUT update status registers, `ixRTAVFS_REG0..194`, `ixPACKER_CONTROL`, shader queue debug/wave state registers such as `ixSQ_WAVE_STATUS`, `ixSQ_WAVE_PC_{LO,HI}`, `ixSQ_WAVE_TTMP0..15`, and `ixSE_CAC_ID/CNTL`.

## Control Flow

This header has no runtime control flow. It contributes compile-time macro substitution only.

The implied driver flow is in AMDGPU consumers:

1. Select the GC 12.0.0 register header set for the active ASIC/IP version.
2. Use a `reg...` offset with the correct SOC15 base index for direct register reads, writes, read-modify-write operations, polling, or command-stream programming.
3. Use an `ix...` offset only through the owning indexed-register accessor, after programming the appropriate indirect address/data registers or block-specific debug window.
4. Pair offsets from this file with bit definitions from the matching GC 12.0.0 shift/mask header when composing field values or decoding register contents.
5. Apply hardware-specific ordering outside this header: counter event selection before enable/readback, thread-trace buffer setup before capture, clock-gating writes during safe power-management windows, and topology/security/remap writes only during initialization or privileged transitions.

For performance counters, the usual flow is to program `*_SELECT` and control registers, clear or arm counters through the owning block, run a workload, then read `*_LO` and `*_HI` result registers with the hardware's required latching or snapshot sequence. For thread tracing, software programs buffer base/size registers, masks and token filters, enables capture, polls/halt/status registers, and consumes buffer data using the write pointer. For power and topology registers, initialization, reset, suspend/resume, or virtualization paths write configuration registers after firmware and fuse/harvest policy have established legal values.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe GPU register addresses whose contents are owned by hardware, firmware, and AMDGPU runtime code.

Performance counter selector/control registers persist as profiling configuration until changed, reset, or power-gated. Result low/high registers expose hardware accumulation state. Because 64-bit counters are split across low/high 32-bit registers, readers may need a documented snapshot or high-low-high pattern to avoid torn samples; this header does not express atomicity.

Thread trace buffer size/base/control/mask registers are active debug state. Buffer base low/high fields identify memory used by trace capture, and stale or wrong addresses can corrupt memory or make diagnostics misleading. Trace status and dropped/finish counters are live hardware state and may be sticky or require defined clear sequencing in the consumer path.

Clock-gating and power control registers are durable hardware configuration across normal engine operation and can affect clock domains, idle behavior, power savings, and debug visibility. They should be written only by initialization, power-management, reset, or firmware-coordinated code that knows which domains are safe to gate. Full-register writes must preserve reserved bits unless the hardware specification says otherwise.

Topology, harvest, pipe-steering, user shader-array, shader-rate, RMI redundancy, RB disable, and remap registers describe active hardware layout. Bad programming can expose disabled units, hide valid units, steer traffic incorrectly, or attribute per-SE/per-SA work to the wrong physical block. These registers are especially sensitive around virtualization, SKU harvesting, reset recovery, and diagnostics.

`regUTCL1_SECURITY` and the CAC/RTAVFS/SQ indexed spaces are not ordinary passive constants. Security state, clock/activity counters, adaptive voltage/frequency indexed registers, and wave debug state can be privileged, sticky, command-like, or transient. The indirect `ix...` offsets persist only as addresses in the indexed namespace; the actual state and sequencing live in the hardware block and its driver/firmware owner.

## Dependencies And Integration Points

This chunk depends on the generated GC 12.0.0 register family remaining synchronized:

- `gc_12_0_0_sh_mask.h` supplies field shifts and masks for the register names addressed here.
- `gc_12_0_0_default.h`, when present in the same generated family, supplies reset/default values for some registers.
- AMDGPU SOC15 register helpers consume `reg...` offsets and `reg..._BASE_IDX` values for direct MMIO access.
- AMDGPU indirect-register helpers consume `ix...` offsets for CAC, RTAVFS, DBGU, SQ wave/debug, and SE CAC register spaces.
- GFX, CP, RLC, KFD/compute, perf counter, debugfs, GPU reset, suspend/resume, power-management, SR-IOV/virtualization, and hang-dump paths rely on this address map indirectly.

Important integration points include hardware performance monitoring, shader-engine perf event programming, thread-trace capture, graphics clock gating, shader/texture/cache/render-backend power controls, GL1 pipe steering, harvested-unit exposure, shader-array and render-backend disable masks, remap controls used for topology repair or virtualization, UTCL1 security setup, CAC accumulator access, RTAVFS indexed tuning/status, packer debug control, and shader wave inspection.

Because this is an offset header, most correctness is relational. A `reg...` value must match the hardware register database, the same symbol's masks in `gc_12_0_0_sh_mask.h`, the base index used by the SOC15 tables, and any generated default. An `ix...` value must match the indexed aperture selected by the accessor; using an indexed offset through a direct MMIO path or using a direct `reg...` offset as an index would target the wrong state.

## Risks And Edge Cases

- Generated-header drift is the primary risk. A wrong numeric offset or base index compiles cleanly but sends driver writes to the wrong register.
- The chunk begins mid-family at `regSQG_PERFCOUNTER7_LO_BASE_IDX`; the matching low-register offset is in the previous chunk. Merge logic must combine adjacent chunks before drawing whole-file conclusions about SQG counters.
- Counter families are highly repetitive but not perfectly uniform. Some blocks have select1 registers, filters, control registers, or fewer counters. Assuming symmetry across SQ, SQG, SPI, TCP, PA, CB, DB, RMI, GL1, and UTCL1 can miss real hardware differences.
- Split low/high counter and address-like registers are easy to read or write incorrectly. The header names identify pairs but do not provide latching, ordering, alignment, or overflow rules.
- `regCP_PERFMON_CNTL_1` aliases the same offset as `regGRBMH_CP_PERFMON_CNTL` in this chunk. Callers and reviewers must recognize alias names can exist for the same hardware location.
- Similar aliasing appears in topology/user registers, such as `regGRBMH_GC_USER_SA_UNIT_DISABLE` with `regGC_USER_SA_UNIT_DISABLE_1`, and `regGC_USER_SHADER_RATE_CONFIG` with `_1`. Alias drift can confuse diagnostics if one name is updated without the other in generated sources.
- Clock-gating and power registers have side effects. Accidental full-register writes, use outside safe windows, or preserving the wrong reserved bits can produce intermittent hangs, bad power state, or lost debug visibility.
- Harvest, remap, pipe-steering, RB disable, RMI redundancy, and shader-rate registers can affect hardware topology and isolation. Incorrect values may only fail on specific SKUs, shader-engine counts, harvested configurations, or SR-IOV partitions.
- `ix...` symbols look like simple offsets but require the correct indirect access mechanism. Misrouting an indexed access can read stale data, write a control register in a different aperture, or silently report meaningless debug state.
- RTAVFS and CAC indexed registers represent adaptive power/clock or counter/accumulator state. They may have firmware ownership or handshake requirements not captured by this offset-only header.
- Wave debug registers such as PC, EXEC, TTMP, trap, scratch, allocation, and status are context-sensitive. Reading them without selecting the intended wave/SIMD/SE context can produce misleading hang or shader-debug evidence.
- Security and virtualization-sensitive registers, especially `UTCL1_SECURITY` and topology/remap controls, should be considered privileged integration points even though the header itself has no access-control logic.

## Test Signals

Useful validation is mostly generated-data consistency plus hardware/runtime behavior:

- Build coverage for AMDGPU files that include the GC 12.0.0 register headers, especially GFX 12 initialization, KFD/compute, perf counter, thread trace, debugfs, reset, virtualization, and power-management paths.
- Mechanical comparison against AMD's authoritative GC 12.0.0 register database to verify every `reg...` offset, every `reg..._BASE_IDX`, every alias, and every `ix...` offset in lines 9954-11061.
- Cross-header checks that register names in this offset chunk have matching field masks in `gc_12_0_0_sh_mask.h` where the register is field-addressable, and matching defaults in the generated default header where expected.
- Static consistency checks for repeated families: low/high counter pairs should be adjacent where documented, select/control families should preserve expected stride patterns, aliases should share identical offsets, and all direct registers in this chunk should keep base index `1`.
- Perf counter tests that select events for SX, TA, TD, TCP, GL1C/GL1XC, CB, DB, RMI, PA_PH, UTCL1, GL1A/GL1XA, SQ/SQG, SPI, PC, GE2_SE, PA_SU, and PA_SC blocks, run controlled workloads, and verify nonzero or monotonic low/high results.
- Counter readback tests that stress 64-bit low/high read ordering and compare snapshot behavior against expected overflow/latch semantics.
- Thread-trace tests that program SQ trace buffers and masks, capture wave execution, verify write-pointer/status/dropped counters, and decode expected draw or marker events.
- Power-management tests that exercise suspend/resume, reset, clock-gating enablement, and idle transitions while monitoring SPI, SQ, SX, TCP, GL1, DB, CB, RMI, PH, UTCL1, and GRBMH clock-control state.
- Topology and harvest tests across SKUs or emulated fuse configurations to validate GL1/GL1X pipe steering, shader-array config, WGP/RB/RMI disable or remap registers, and shader-rate aliases.
- Virtualization/SR-IOV tests that verify remap, disable, redundancy, and security-related registers are accessible only through intended PF/VF or firmware-owned paths and decode to the expected partition topology.
- Indirect access tests for GC CAC, SE CAC, RTAVFS, DBGU packer control, and SQ wave/debug registers, ensuring the correct index/data window is selected before using each `ix...` offset.
- Hang-dump and shader-debug tests that select a known wave context and confirm `ixSQ_WAVE_*`, PC, EXEC, TTMP, trap, scratch, allocation, and shader-cycle registers decode coherently.
- Runtime warning signals include zero or nonsensical perf counters under active workloads, GPU hangs after clock-gating changes, failed thread trace capture, wrong harvested-unit exposure, invalid shader-engine remap, unexpected UTCL1/security behavior, misleading wave debug dumps, or register read/write traces that touch offsets adjacent to but not equal to the generated values.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002568`. It covers lines 9954-11061 of `gc_12_0_0_offset.h`, the final chunk of that file. The final per-file report should merge it with chunks `subset-b-002564` through `subset-b-002567` so the complete GC 12.0.0 offset map includes earlier SDMA, GFX, VM, CP, RLC, shader, and performance-counter definitions, plus the SQG counter low offset that immediately precedes this slice.
