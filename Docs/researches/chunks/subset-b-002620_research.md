# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_sh_mask.h lines 12161-14705

## Scope

This chunk is a generated AMD GC 9.0 shift/mask register-header segment. It contains C preprocessor constants only: each hardware register field is represented by a `<REGISTER>__<FIELD>__SHIFT` macro and a matching `<REGISTER>__<FIELD>_MASK` macro for packing and decoding 32-bit GPU register values. There are no functions, structs, enums, variables, includes, memory allocations, locks, callbacks, or executable branches in this range.

The selected lines begin in the tail of command processor soft-disable/reset/control fields, then cover generated address blocks for `gc_spipdec`, `gc_cpphqddec`, `gc_didtdec`, `gc_gccacdec`, `gc_tcpdec`, `gc_gdspdec`, `gc_rasdec`, and the beginning of `gc_gfxdec0`. Across lines 12161-14705 the chunk defines 2,152 macros for 370 distinct register names. The dominant register families are `GDS`, `SPI`, `CP`, `DB`, `TCP`, `GC`, `PA`, and `RAS`. Although this file lives under a `ceph-client` source mirror, this path is AMDGPU DRM hardware metadata, not Ceph filesystem logic.

## Purpose

`gc_9_0_sh_mask.h` supplies bit layouts for the AMD graphics core 9.0 register set. Driver code combines these field definitions with register addresses from the matching `gc_9_0_offset.h` header and uses AMDGPU register helpers such as `REG_SET_FIELD` and `REG_GET_FIELD` to build MMIO values, command-packet payloads, queue descriptors, golden-register settings, debug reads, and status decoders.

This chunk describes several hardware areas:

- Command processor disable/reset and graphics/compute queue state: `CP_SD_CNTL`, `CP_SOFT_RESET_CNTL`, `CP_CPC_GFX_CNTL`, and a large `CP_HQD_*` block for hardware queue descriptors.
- SPI arbitration, debug/trap, wave-control, compute-queue reset, resource reservation, and compute wave context-save controls.
- DIDT/CAC/EDC power, droop, clock-gating, and indirect access registers for graphics-core power/thermal control.
- TCP cache/watchpoint, GATCL1, UTCL1, and perf-counter filter fields.
- GDS, GWS, and OA per-VMID base/size/mask allocation registers, reset masks, context-switch status/counters, and max-wave/resource state.
- RAS signature controls and signature capture registers for major GC blocks.
- Depth-buffer, stencil, PA scissor/clip/window, coherent destination, texture border-color base, and color-target mask fields in the start of `gc_gfxdec0`.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this slice. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit index of a hardware field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask, usually within a 32-bit register.
- Companion register-address macros come from `gc_9_0_offset.h`; default/reset values come from `gc_9_0_default.h` where generated.

Important macro groups in this chunk are:

- `CP_SD_CNTL`, `CP_SOFT_RESET_CNTL`, and `CP_CPC_GFX_CNTL`: enable/disable bits for CPF/CPG/CPC/RLC/SPI/WD/IA/PA/RMI/EA, compute and graphics soft-reset controls, HQD register/doorbell reset bits, and CPC queue/pipe/ME/valid selection.
- `SPI_ARB_PRIORITY`, `SPI_ARB_CYCLES_*`, `SPI_CDBG_SYS_*`, `SPI_WCL_PIPE_PERCENT_*`, `SPI_GDBG_*`, `SPI_RESET_DEBUG`, `SPI_COMPUTE_QUEUE_RESET`, `SPI_RESOURCE_RESERVE_CU_*`, `SPI_RESOURCE_RESERVE_EN_CU_*`, `SPI_COMPUTE_WF_CTX_SAVE`, and `SPI_ARB_CNTL_0`: SPI scheduling, pipe allocation, debug/trap matching, VMID stall/trap selection, compute queue reset, CU reservation masks/enables, context-save enablement, and arbitration controls.
- `CP_HQD_*`, `CP_HPD_*`, and `CP_MQD_*`: hardware queue descriptor control and status, MQD base address and processing state, VMID/VQID selection, persistent queue state, pipe/queue priority, quantum, packet queue base/read/write pointers, doorbell control, indirect buffer control, IQ timers, dequeue requests, DMA/offload controls, semaphores, HQ scheduler/status/control, EOP buffer state, context-save backing addresses/sizes, GDS resource state, UTCL1 error reporting, AQL controls, and PQ write pointers.
- `DIDT_IND_*`, `GC_CAC_*`, `GC_DIDT_*`, `GC_EDC_*`, `GC_*_DROOP_CTRL`, and `SE_CAC_*`: indirect index/data paths, current/activity counters, TDP and CAC windows, DIDT/EDC enables, reset/clock overrides, power thresholds, weightings for SQ/DB/TD/TCP/DBR, rolling droop/power status, overflow counters, and shader-engine CAC clock/indirect controls.
- `TCP_WATCH[0-3]_*`, `TCP_GATCL1_*`, `TCP_UTCL1_*`, `TCP_CNTL2`, `TCP_ATC_EDC_GATCL1_CNT`, and `TCP_PERFCOUNTER_FILTER*`: texture cache watchpoint address/mask/VMID/mode/valid fields, GATCL1 invalidation/force-miss/order/cache-size controls, UTCL1 page-size/permission/response/invalidation/client/ack/snoop behavior, low-power clock disable bits, EDC counts, and perf-counter matching/enables for buffer/flat/dimension/format/sample/opcode/cache/compression/address-mode fields.
- `GDS_VMID*_BASE`, `GDS_VMID*_SIZE`, `GDS_GWS_VMID*`, `GDS_OA_VMID*`, `GDS_GWS_RESET*`, `GDS_GWS_RESOURCE_RESET`, `GDS_COMPUTE_MAX_WAVE_ID`, `GDS_OA_RESET_MASK`, `GDS_OA_RESET`, `GDS_ENHANCE`, `GDS_OA_CGPG_RESTORE`, `GDS_*_CTXSW_STATUS`, and `GDS_*_CTXSW_CNT*`: GDS memory partitioning by VMID, global wave sync allocation, ordered-append resource masks, reset controls, compute max wave ID, context-switch watermarks/status, counter pointers, and OA clock/power-gating restore settings.
- `RAS_SIGNATURE_CONTROL`, `RAS_SIGNATURE_MASK`, and `RAS_*_SIGNATURE*`: signature collection enable/mask and full-width signature registers for SX, DB, PA, VGT, SQ, SC, IA, SPI, TA, TD, CB, and BCI blocks.
- `DB_RENDER_CONTROL`, `DB_COUNT_CONTROL`, `DB_DEPTH_VIEW`, `DB_RENDER_OVERRIDE*`, `DB_HTILE_DATA_BASE*`, `DB_DEPTH_SIZE`, `DB_*_CLEAR`, `DB_Z_INFO*`, `DB_STENCIL_INFO*`, `DB_*_READ_BASE*`, `DB_*_WRITE_BASE*`, and `DB_DFSM_CONTROL`: depth/stencil clear/copy/decompress, zpass/fail counters, slice/mip/read-only view state, HiZ/HiS/render overrides, HTILE and Z/stencil backing memory, clear values, surface format/swizzle/PRT/fault/expclear/tile settings, and punchout/overflow behavior.
- `TA_BC_BASE_ADDR*`, `COHER_DEST_BASE*`, `PA_SC_*`, `PA_SU_HARDWARE_SCREEN_OFFSET`, and `CB_TARGET_MASK`: texture border-color base addresses, coherent destination base high/low fields, viewport/window/generic clip rectangle and edge-rule fields, screen offset, and per-render-target channel write masks. The final line in this chunk stops inside the `CB_TARGET_MASK` family, so adjacent chunks are needed for the remaining masks.

## Control Flow

This header has no runtime control flow. Its only direct behavior is compile-time macro substitution.

The implied runtime flow in AMDGPU consumers is:

1. Select GC 9.0 register headers for the detected ASIC.
2. Choose a register address from `gc_9_0_offset.h`.
3. Read an existing register, prepare an indexed/debug operation, or construct a command/MMIO write value.
4. Use the `__SHIFT` and `__MASK` constants, commonly through `REG_SET_FIELD` or `REG_GET_FIELD`, to pack or extract field values.
5. Apply the value during graphics/compute queue setup, KFD queue management, GDS allocation, power/thermal programming, TLB/cache control, golden-register initialization, suspend/resume, reset/recovery, debugfs reads, perf monitoring, hang dumps, or draw/dispatch state programming.

For the `CP_HQD_*` block, runtime code typically programs MQD/HQD base addresses and queue metadata, establishes VMID and priority, configures PQ/IB/EOP buffers and doorbells, enables the queue, and later observes status/error/read-pointer fields during scheduling, preemption, dequeue, or recovery. The masks also support context-save and GDS resource handoff state used when queues are suspended or restored.

For SPI and TCP debug/status/control fields, consumers sequence selectors and enable bits around live hardware. Trap/debug masks, VMID filters, resource reservation registers, and perf-counter filters persist as programmed policy, while busy/fault/retry/PRT/status fields can change asynchronously with GPU execution.

For DIDT/CAC/EDC, initialization and power-management code programs thresholds, windows, weights, and clock overrides. Status and overflow fields are then sampled to determine throttle/droop behavior. The indirect index/data registers imply ordered index-then-data accesses; the header does not encode that sequencing.

For GDS/GWS/OA, queue and KFD paths program per-VMID allocations and reset masks. Context-switch counters/status fields are read or restored around queue switches. Incorrect sequencing can expose one VMID's GDS/GWS/OA resources to another or leave resources allocated after reset.

For DB/PA/CB start-of-gfxdec state, draw setup paths program depth/stencil surfaces, clear values, scissor/clip/window rules, coherent destination bases, and target write masks before rasterization and export. These fields become persistent graphics pipeline state until the next command stream changes them or the GPU is reset.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe stateful GPU registers whose values are owned by hardware, firmware, command submission, and AMDGPU initialization/recovery code.

Queue and command-processor fields are persistent queue state. Base addresses, high-address halves, read/write pointers, doorbell offsets, EOP buffers, context-save backing stores, priorities, VMIDs, and cache policies must stay coherent with MQD memory and command processor expectations. Status/error bits such as UTCL1 faults, queue idle, pending semaphore, dequeue state, and doorbell hit are live or sticky hardware state and may require hardware-specific clearing outside this header.

SPI resource reservation, trap, debug, wave context-save, and compute reset bits can affect wave scheduling and debug behavior across queues. Some fields are selector/configuration state; others trigger reset or dequeue behavior when written. The header only gives bit positions, not side-effect semantics.

DIDT/CAC/EDC fields persist as power/thermal policy. Bad windows, weights, thresholds, or clock overrides can cause excessive throttling, disabled protection, power/performance regressions, or hard-to-debug hangs under load.

TCP and UTCL1 fields persist as cache/TLB policy. Invalidation toggles, force-miss/snoop/order controls, page-size defaults, fault response modes, and cache-size/fifo reductions affect memory-system coherency and performance. Watchpoint registers are debug state keyed by address, mask, VMID, ATC, mode, and valid bits.

GDS/GWS/OA fields persist as per-VMID resource allocation and reset state. Context-switch counters and status fields expose transient save/restore state, while base/size/mask registers define the hardware-visible resource partitioning for queues.

RAS signature registers expose captured diagnostic state. The full-width signature fields should be treated as hardware-generated values, while `RAS_SIGNATURE_CONTROL` and `RAS_SIGNATURE_MASK` alter what is captured.

DB/PA/CB fields persist as graphics pipeline state. Surface base addresses, formats, swizzle modes, PRT/fault behavior, clear/decompress/copy controls, scissor rectangles, clip rules, and target masks must match the command stream and memory layout. Several DB fields can also preserve or invalidate compression metadata and hierarchical depth/stencil state.

## Dependencies And Integration Points

This chunk depends on the generated GC 9.0 register set remaining synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_offset.h` provides matching register addresses.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_default.h` provides reset/default values for related registers where generated.
- Common AMDGPU helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32*`, `WREG32*`, `SOC15_REG_OFFSET`, indirect register helpers, and golden-register programming tables consume these field definitions.
- Runtime integration includes AMDGPU GFX 9 initialization, compute ring and KFD queue setup, MQD/HQD management, graphics and compute preemption, doorbell programming, VMID/TLB fault handling, GDS allocation, RAS diagnostics, power management, perf counters, debugfs/hang dumps, and draw-state emission.

The queue fields integrate with MES/KFD and kernel queue scheduling paths that create MQDs, map doorbells, program HQDs, and recover stuck queues. The TCP/UTCL1 fields integrate with GPUVM fault handling, cache invalidation, memory attribute policy, and performance monitoring. The GDS/GWS/OA fields integrate with KFD resource allocation and context switching. The DB/PA/CB fields integrate with graphics command emission and render-backend/depth-buffer programming.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong shift or mask compiles successfully but writes the wrong hardware bits or decodes status incorrectly.
- This chunk starts after the first `CP_SD_CNTL` field and ends mid-`CB_TARGET_MASK`; adjacent chunks are required for complete family context.
- Similar repeated families are not interchangeable. `SPI_RESOURCE_RESERVE_CU_*`, `GDS_VMID*`, `GDS_GWS_VMID*`, `GDS_OA_VMID*`, `TCP_WATCH*`, and per-stage GDS context-switch counters follow patterns but still encode distinct hardware registers.
- Full-width address/data masks do not imply arbitrary values are valid. Many address fields have alignment, aperture, high/low split, VMID, cache policy, or command-packet ordering constraints outside this header.
- Doorbell, queue pointer, EOP, and context-save fields can corrupt scheduling state if programmed while a queue is active or if the MQD/HQD memory image disagrees with the hardware registers.
- Reset and dequeue fields can have write-triggered side effects. The macros do not identify write-one-to-clear, sticky, clear-on-read, or self-clearing behavior.
- UTCL1/TCP invalidation and fault-response fields are coherency-sensitive. Misprogramming can produce stale memory, spurious GPUVM faults, PRT/retry anomalies, or performance collapse.
- DIDT/CAC/EDC controls affect power safety and throttling. Incorrect thresholds or disabled enables may only fail under high-power workloads.
- GDS/GWS/OA partitioning mistakes can cause inter-VMID resource leakage, failed queue launches, deadlocks around ordered append/global wave sync, or stale allocation state after reset.
- DB render override, compression, expclear, PRT, swizzle, and base-address fields can cause rendering corruption rather than immediate crashes.
- RAS signature values are diagnostic and may be volatile or capture-window dependent; tests should not assume stable values without controlling the input mask and workload.

## Test Signals

Useful validation is mostly generated-data consistency, build coverage, and hardware runtime behavior:

- Kernel build coverage for AMDGPU files that include `gc_9_0_sh_mask.h`, especially GFX 9 queue, KFD, GPUVM, GDS, RAS, power-management, perf-counter, reset, and graphics draw-state paths.
- Mechanical comparison against AMD's authoritative GC 9.0 register database to confirm every `__SHIFT` and `__MASK` in lines 12161-14705.
- Cross-checks that every register family in this chunk has matching address macros in `gc_9_0_offset.h` and expected reset/default entries in `gc_9_0_default.h` where generated.
- Static mask/shift sanity checks: masks align with shifts, fields do not overlap unexpectedly, repeated VMID/watchpoint/context-counter families stay internally consistent, full-width fields use `0xFFFFFFFFL`, and high/low address halves have expected widths.
- Queue bring-up tests for CP HQD/MQD/PQ/IB/EOP/doorbell programming, including KFD compute queues, graphics queues, dequeue/preemption, context save/restore, and GPU reset recovery.
- Fault and diagnostic tests that exercise `CP_HPD_UTCL1_ERROR`, `CP_HQD_ERROR`, TCP/UTCL1 fault/retry/PRT status, and RAS signature capture under controlled workloads.
- SPI scheduling/debug tests that validate arbitration fields, compute queue reset, CU resource reservation, trap masks, wave context-save behavior, and debug selector reads.
- Power and throttling tests for CAC/DIDT/EDC programming under sustained graphics/compute workloads, checking throttle levels, droop status, overflow counters, and clock override recovery across suspend/resume.
- GDS/GWS/OA tests covering per-VMID base/size/mask allocation, ordered append/global wave sync resources, reset masks, max wave ID, and context-switch counters.
- TCP/cache tests covering watchpoints, GATCL1/UTCL1 invalidation, forced miss/snoop/order controls, page-size defaults, perf-counter filters, and memory-coherency stress.
- Graphics rendering tests covering depth/stencil clear/copy/decompress, HTILE, depth bounds, expclear, PRT/fault behavior, scissor/clip/window rules, coherent destination bases, and color target masks.
- Runtime warning signals include stuck queues, doorbell hits not advancing write pointers, HQD UTCL1 errors, stale or leaked GDS resources, unexpected throttling, TCP fault/retry/PRT spikes, corrupted depth/stencil output, and repeated GPU resets.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002620`. It covers lines 12161-14705 of `gc_9_0_sh_mask.h`. The final per-file research should merge this with adjacent chunks to restore the beginning of the `CP_SD_CNTL` family before line 12161 and the remaining `CB_TARGET_MASK`/following `gc_gfxdec0` fields after line 14705.
