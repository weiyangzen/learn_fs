# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_sh_mask.h lines 5177-7648

## Scope

This chunk is a generated AMD GC 10.3.0 shift/mask header segment. It covers line 5177 through line 7648 and defines 1,081 `__SHIFT` macros and 1,079 `_MASK` macros across 306 visible register comments. The range begins inside the `SDMA1_RLC5_RB_CNTL` field list, completes most of the `SDMA1_RLC5`, `SDMA1_RLC6`, and `SDMA1_RLC7` register groups, then enters the `gc_grbmdec`, `gc_cpdec`, and `gc_padec` address blocks. It ends inside `PA_SC_BINNER_EVENT_CNTL_3`, before the remaining masks for that register and later PA/SC fields.

The content is declarative only. There are no C functions, structs, enums, branches, loops, allocations, locks, or direct software-side state changes. The exported surface is a set of preprocessor constants that describe hardware register bit positions and bit masks.

## Purpose

`gc_10_3_0_sh_mask.h` supplies symbolic bitfield definitions for AMDGPU, KFD, SMU, and common SOC15 code that targets GC 10.3.0-class ASIC register layouts. Consumers pair these macros with matching offsets from `gc_10_3_0_offset.h` and use helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_FIELD15`, `RREG32_SOC15`, `WREG32_SOC15`, and golden-register table helpers to program or inspect hardware without embedding raw bit positions.

This slice covers three broad hardware surfaces:

- SDMA1 RLC queue contexts 5 through 7, including ring-buffer base/pointer registers, write-pointer polling, indirect-buffer state, doorbells, context save area addresses, preemption, AQL controls, minor pointer update, and mid-command save/restore data.
- GRBM global graphics register-bus management, including busy/idle status, soft reset controls, graphics clock gating, shader-engine status, read/write error reporting, trap controls, scratch registers, fence ranges, UTCL2 invalidation range registers, and async VF violation data.
- Command-processor and primitive/raster front-end fields, including CP status/stall counters, MEC/ME controls, ring/queue thresholds, instruction pointers, command-index/data windows, VGT/WD/GE/IA controls, shader-array configuration, primitive setup/cache invalidation, PA clip/setup controls, and SC binner event routing.

## Exported API Surface

There are no callable APIs or local types. The public interface is the generated macro namespace:

- `SDMA1_RLC5_*`, `SDMA1_RLC6_*`, and `SDMA1_RLC7_*`: repeated register groups for each RLC SDMA context. Common fields include `RB_ENABLE`, `RB_SIZE`, `RB_SWAP_ENABLE`, read/write pointer offsets, writeback enable/timer/idle bits, write-pointer poll enable/frequency/idle count, IB enable/swap/switch/VMID fields, context status bits, doorbell enable/captured bits, doorbell data/error logging, outstanding read/write watermarks, CSA address fields, IB preemption, AQL packet controls, and mid-command data/control fields.
- `GRBM_*`: global graphics block management registers. Important fields include `READ_TIMEOUT`, `GUI_ACTIVE`, `CP_BUSY`, `CP_COHERENCY_BUSY`, graphics-block busy bits for PA/SC/BCI/SX/TA/DB/CB/GDS/SPI/GE, per-shader-engine busy/status fields, soft-reset bits for CP/GFX/RLC/HI/SEM/GRBM, graphics clock-enable and wait-idle timing fields, read/write error metadata, interrupt/trap controls, GFX pipe/queue selection, IH credits, power controls, UTCL2 invalidate ranges, fence ranges, and scratch register data.
- `VIOLATION_DATA_ASYNC_VF_PROG`: async virtual-function violation metadata, including VMID, client ID, source ID, write/read indicator, and data/protection/permission flags.
- `CP_*`: command-processor status and diagnostic fields for CPC, CPF, PFP, ME, CE, and MEC units. This includes busy/stalled status fields, GRBM free-count fields, privileged violation addresses, header dumps, scratch index/data access, halt hysteresis, event/de counts, instruction pointers, CSF status, MEC/ME halt controls, context status, preemption controls, ROQ/STQ/MEQ/CEQ thresholds and availability, ring-buffer pointers, write-pointer polling, command-index/data windows, and queue/IB/doorbell status registers.
- `VGT_*`, `WD_*`, `GE_*`, `IA_*`, `CC_GC_*`, `GC_USER_*`, and `GFX_PIPE_CONTROL`: primitive assembly, draw dispatch, geometry engine, input assembler, shader-array, and graphics pipe control fields. Examples include VGT cache invalidation policy, ESGS/GSVS/tessellation ring sizes, tessellation memory base, FIFO depths, vertex reuse, DMA primitive/control settings, WD QoS and UTCL1 status/control, GE status/private control, shader-array disables/configuration, and graphics pipe clock/ordering controls.
- `PA_*` and `PA_SC_BINNER_EVENT_CNTL_*`: primitive assembly clipping/setup and scan-converter binner fields. This chunk includes clipping enhancements, PA/SU busy status, SC FIFO depth, trap-screen hypervisor lock bits, forced end-of-vector maximum counters, and binner event routing fields for cache flushes, pipeline-stat/perf-counter events, streamout synchronization, thread-trace markers, context suspend, NGG/legacy pipeline enable events, and draw/pixel-shader completion.

Most complete register groups follow the generated pair pattern `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`. The exceptions are chunk-boundary artifacts: the first lines are the tail of `SDMA1_RLC5_RB_CNTL`, whose comment and earlier fields are in the prior chunk, and the last line stops after `PA_SC_BINNER_EVENT_CNTL_3__PIXEL_PIPE_STAT_DUMP_MASK`, while the remaining `PA_SC_BINNER_EVENT_CNTL_3` masks continue in the next chunk.

## Control Flow And State Behavior

This header has no local control flow. Runtime behavior appears only when callers include the generated constants and use them to build MMIO register values, decode readbacks, or populate golden-register tables.

The names in this slice describe several hardware state machines and persistent register banks:

- SDMA RLC queue contexts persist ring-buffer addresses, read/write pointers, poll addresses, doorbell offsets, VMID/privilege selection, CSA state, AQL packet geometry, and mid-command preemption data. Driver or firmware writes these registers during queue setup, reset, suspend/resume restore, or golden-register initialization; hardware mutates pointer/status/log fields as it consumes packets and receives doorbells.
- GRBM status and reset fields expose global graphics progress. AMDGPU polling paths read `GRBM_STATUS`/`GRBM_STATUS2` to decide whether graphics is idle and build `GRBM_SOFT_RESET` requests when PA/SC/CP/RLC-like blocks stay busy.
- GRBM error, trap, fence, scratch, and UTCL2 invalidation fields are stateful hardware diagnostics or control windows. Some are intended for debug/error reporting, some are scratch storage, and some affect address-range invalidation or access filtering.
- CP registers expose command-processor pipeline state, queue/ring thresholds, stalled/busy conditions, instruction pointers, privileged violation addresses, and command data windows. The associated state is maintained by CP firmware/microcode and queue-management paths, while driver code reads it for debug, hang diagnosis, reset decisions, and queue programming.
- VGT/WD/GE/IA/PA/SC fields are graphics front-end and rasterization state. Cache invalidation, ring sizes, FIFO depths, primitive type/control, shader-array config, binner event mappings, clock-gating controls, and hypervisor lock bits persist until reprogrammed, reset, or restored by firmware/golden-register logic.

Read/write semantics are not encoded by the macro format alone. Fields named `STATUS`, `BUSY`, `STALLED`, `*_COUNT`, `*_DUMP`, `*_LOG`, `READ_ERROR`, `WRITE_ERROR`, and `VIOLATION` are readback or diagnostic by naming convention, while `CNTL`, `CONTROL`, `THRESHOLD`, `BASE`, `SIZE`, `OFFSET`, `SOFT_RESET`, `PREEMPTION`, and `*_POLL_*` fields are configuration-oriented. Actual read-only, sticky, write-one-to-clear, privileged, RLC-safe, PF-owned, and reset-default behavior must be verified against the register database and the calling driver path.

## Dependencies And Integration Points

The syntactic dependency is only the C preprocessor. Semantically, these definitions are tied to the matching GC 10.3.0 offset and default headers in the same `asic_reg/gc` directory. They are also consumed through AMDGPU's SOC15 register access layer and golden-register programming infrastructure.

Important integration points in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v10_0.c`, which uses GC 10.x GRBM fields to test graphics idleness, wait for `GUI_ACTIVE` to clear, inspect `GRBM_STATUS`/`GRBM_STATUS2` busy bits, compose `GRBM_SOFT_RESET`, and program PA/SC golden registers such as `PA_SC_BINNER_EVENT_CNTL_0` and `PA_SC_BINNER_TIMEOUT_COUNTER`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v4_0.c`, whose golden-register tables program `SDMA1_RLC5_RB_RPTR_ADDR_LO`, `SDMA1_RLC5_RB_WPTR_POLL_CNTL`, and the corresponding RLC6/RLC7 registers covered by this chunk.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v10_3.c`, which includes `gc_10_3_0_offset.h` and `gc_10_3_0_sh_mask.h` for GC 10.3 KFD queue and shader-memory programming paths.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/soc15.c`, whose common golden-register write helper treats PA/SC and SH registers specially with RLC-safe writes, including `PA_SC_BINNER_EVENT_CNTL_3` and `PA_SC_ENHANCE`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/vangogh_ppt.c`, which includes the GC 10.3.0 offset and shift/mask headers for Vangogh SMU/GC register interactions.
- AMDGPU diagnostics and reset tables across SOC generations use the same GRBM and CP naming model for register dump lists, idle checks, hang analysis, and soft-reset decisions, even when exact offset macro prefixes differ between generations.

At runtime these macros sit between generated register metadata and hardware-facing subsystems: SDMA queue bring-up, KFD queue management, graphics idle/reset logic, RLC/golden-register restore, command-processor diagnostics, front-end/raster setup, SR-IOV violation reporting, and power-management flows that need GC register fields.

## Risks

- Generated-header drift is the primary risk. A wrong bit position or mask can silently program the wrong SDMA queue context, GRBM reset bit, CP control field, or graphics front-end control.
- The SDMA1 RLC5/RLC6/RLC7 groups are highly repetitive. Copy-generation mistakes can affect only one queue context, producing queue-specific hangs, missed write-pointer polling, incorrect read-pointer writeback, broken doorbells, or failed preemption.
- Split address fields such as RB base, IB base, poll address, and CSA address require correct high/low masking and alignment. Bad masks can point DMA hardware at the wrong VRAM/system-memory page.
- Doorbell, AQL, and poll-control bits are externally visible to user queue submission. Incorrect enable, swap, timer, frequency, or VMID fields can cause missed submissions, stale pointers, wrong-endian pointer fetches, or privilege/VMID isolation problems.
- GRBM busy and reset masks directly affect hang detection and recovery. Misdecoded busy bits can trigger unnecessary resets or miss a stuck block; wrong `GRBM_SOFT_RESET` fields can reset the wrong sub-block or fail to recover the actual one.
- CP diagnostic and threshold fields are microcode-facing. Incorrect threshold, halt, ring, or queue availability fields can deadlock command submission or make hang dumps misleading.
- PA/SC binner event-control fields map hardware events into binner behavior. Wrong event encodings can break cache flush ordering, pipeline statistics, perf counters, thread trace, streamout synchronization, NGG/legacy pipeline switching, or draw completion signaling.
- Some registers are likely privileged, PF-owned, firmware-owned, or RLC-mediated in SR-IOV, power-management, and reset flows. Direct writes from the wrong context can be ignored, fault, or conflict with firmware state.
- The chunk starts and ends inside register groups. Merge-time validation should account for missing pairs at `SDMA1_RLC5_RB_CNTL` and `PA_SC_BINNER_EVENT_CNTL_3` as chunking artifacts, not local generation failures.

## Test Signals

Useful validation is mostly build-time, generated-data, and hardware-integration oriented:

- Compile or preprocess AMDGPU, KFD, SMU, and SOC15 paths that include `gc_10_3_0_offset.h`, `gc_10_3_0_sh_mask.h`, and the matching default header.
- Run generated-header consistency checks over the full file: every complete register field should have matching `__SHIFT` and `_MASK` definitions, with explicit boundary exceptions for this chunk's partial `SDMA1_RLC5_RB_CNTL` start and `PA_SC_BINNER_EVENT_CNTL_3` end.
- Cross-check register names and field widths against the GC 10.3.0 register database and offset header, especially repeated SDMA1 RLC context spacing and GRBM/CP/PA address-block transitions at lines 5774, 6252, and 7105.
- SDMA validation on GC 10.3.0-class hardware: initialize RLC5/RLC6/RLC7 queues, submit ring and indirect-buffer work, exercise doorbells and write-pointer polling, verify read-pointer writeback, test AQL mode when enabled, and validate preemption/context-save behavior.
- Graphics idle/reset testing: submit graphics and compute workloads, verify `GRBM_STATUS`/`GRBM_STATUS2` polling, force hang/reset paths, and confirm `GRBM_SOFT_RESET` recovery selects the intended sub-blocks.
- CP diagnostics: capture register dumps during normal operation and induced hangs, confirm busy/stall/header/instruction-pointer fields decode coherently, and check privileged violation addresses for expected values during negative tests.
- Front-end/raster tests: draw workloads that exercise VGT cache invalidation, tessellation/geometry ring sizing, WD/GE/IA status, shader-array configuration, PA clipping/setup, SC binner event routing, pipeline stats, perf counters, and thread trace markers.
- Suspend/resume, GPU reset, SR-IOV VF/PF, and firmware restore tests that ensure SDMA, GRBM, CP, and PA/SC state is restored by the correct owner and that RLC-safe writes are used where required.

## Chunk Notes For Merge

This document is intentionally source-tree aligned and covers only lines 5177-7648 of `gc_10_3_0_sh_mask.h`. Earlier chunks should cover the start of `SDMA1_RLC5_RB_CNTL` and RLC0 through RLC4 definitions. Later chunks should complete `PA_SC_BINNER_EVENT_CNTL_3`, continue PA/SC binner performance and enhancement fields, and cover the remaining GC 10.3.0 register groups. The final per-file report should treat the whole header as generated GC 10.3.0 hardware bitfield metadata used by AMDGPU/KFD/SMU register programming paths, not as handwritten executable driver logic.
