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
