# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_sh_mask.h lines 24721-27318

## Scope

This chunk is part of AMD's generated GC 11.0.0 register shift/mask header. It contains C preprocessor constants only: each hardware register field is represented by a `__SHIFT` value and a matching `_MASK` value used by AMDGPU register helpers to pack or decode 32-bit MMIO and command-stream register values. There are no functions, structs, enums, variables, includes, memory allocations, locks, callbacks, or executable branches in this range.

The requested range contains 2,598 lines, 2,131 `#define` statements, and 445 generated comment lines. It starts mid-register at the `CP_DEBUG_2` mask definitions; the corresponding `CP_DEBUG_2` shift macros are in the previous chunk. It then covers complete register families across queue debug, dynamic power/throttle accounting, SPI/TCP/GDS/UTCL1/GCR controls, CAC/EDC weighting, CU resource reservation, user/config CP registers, draw statistics, scratch/atomic/DMA/semaphore controls, graphics coherency, RLC performance counters, GRBM indexing, and the first VGT/GE draw-state registers. It ends at the `//PA_SC_SCREEN_EXTENT_MIN_0` marker before that register's field macros, which belong to the next adjacent chunk.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU DRM hardware metadata for GC 11.0.0 graphics IP. It is not Ceph filesystem code.

## Purpose

`gc_11_0_0_sh_mask.h` supplies symbolic bit layouts for GC 11.0.0 hardware registers. Driver code combines these macros with register offsets from `gc_11_0_0_offset.h` and helper macros such as `REG_SET_FIELD` and `REG_GET_FIELD` so it can manipulate named fields without hard-coded bit positions.

This chunk focuses on several hardware domains:

- Command processor and queue/debug controls: `CP_DEBUG_2`, `CP_FETCHER_SOURCE`, HPD queue offset/status registers, CP append/fence/atomic/semaphore/DMA registers, PFP indirect-buffer/load controls, scratch access, EOP-done event/data controls, draw/dispatch/index indirect addresses, sample status, and ME coherency controls.
- DIDT, EDC, CAC, PCC, PWRBRK, and throttle accounting: global and per-shader-engine counter aggregation, rolling power delta, dynamic thresholds, hysteresis, stretch counters, throttle controls/status, clock monitor control, and many generated weight registers used by power estimation and throttling logic.
- SPI and shader front-end state: wave debug stall controls, trap configuration, export arbitration weights, feature controls, shader resource limit controls, compute wavefront context-save status, and per-CU resource reservation and enable masks.
- Texture/cache/memory front-end blocks: TCP invalidate/status/control/debug-index/data registers, GDS enhance and OA restore controls, UTCL1 controls, FIFO sizing, GCRD target disable and credit-safe fields, and GCR command/status/general controls.
- Graphics user/config state: CP pipe-stat address and performance counters, scratch registers and atomic operations, DMA command descriptors, IB2/ST buffer state, DB base/buffer fields, GDS backup address, RLC GPM performance counters, GRBM instance selection, primitive/index type, VGT/GE draw setup, tessellation factor ring/base fields, GE grouping, stereo, user VGPRs, fast GS launch dimensions, GS output primitive type, and line stipple state.

## Important APIs, Types, And Macros

There are no callable APIs or C types. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit position for a hardware field.
- `<REGISTER>__<FIELD>_MASK` gives the 32-bit mask for the same field.
- `// addressBlock: ...` comments identify the generated hardware register block for following register comments.
- `//<REGISTER>` comments mark register groups that correspond to address macros in the companion offset header.

The major generated address blocks and register families in this slice are:

- `gc_pfonly_cpdec` tail: `CP_DEBUG_2` masks and `CP_FETCHER_SOURCE`.
- `gc_pfonly_cpphqddec`: `CP_HPD_MES_ROQ_OFFSETS`, `CP_HPD_ROQ_OFFSETS`, and `CP_HPD_STATUS0` queue state, mapped-queue, availability, pending-transfer, offload-check, freeze, and force fields.
- `gc_pfonly_didtdec`: DIDT indirect index/data and EDC controls, throttle controls, thresholds, stall patterns, status, overflow, and rolling-power-delta fields.
- `gc_pfonly_spidec`: SPI graphics debug wave stall/trap fields, arbitration controls, shader resource limit controls, and compute wavefront context-save status fields.
- `gc_pfonly_tcpdec`: TCP invalidation, status, control, and debug index/data fields.
- `gc_pfonly_gdsdec`: GDS enhance and OA clock/power-gating restore fields.
- `gc_pfonly_utcl1dec`: UTCL1 control, invalidation disable, FIFO sizing, per-SA GCRD target disable, and credit-safe fields.
- `gc_pfonly_pmmdec`: GCR general control, command/status, spare, and PMM control fields.
- `gc_sedcdec`: SEDC GL1/GL2 override controls.
- `gc_pfonly_gccacdec`: the largest portion of this chunk, covering GC/SE CAC aggregation counters, EDC/throttle controls and status, stall-pattern controls for EDC/PCC/PWRBRK/DIDT, hysteresis/performance counters, many `GC_CAC_WEIGHT_*` and `SE_CAC_WEIGHT_*` registers, clock monitor control, and indirect CAC index/data accessors.
- `gc_pfonly2_spidec`: `SPI_RESOURCE_RESERVE_CU_0` through `_15` and `SPI_RESOURCE_RESERVE_EN_CU_0` through `_15`, giving per-CU VGPR/SGPR/LDS/thread-group reservation and enable fields.
- `gc_gfxudec`: user/config graphics registers, including CP event/fence/stat counters, scratch/atomic append state, CP DMA descriptors, semaphore waits/signals, IB2/ST buffers, EOP done controls, draw/dispatch/index indirect addresses, ME coherency, RLC performance counters, GRBM indexing, VGT primitive/index/count/state registers, and GE grouping/user/stereo/resource controls.

Representative high-risk field groups include address fragments such as `*_ADDR_LO`, `*_ADDR_HI`, `*_BASE`, `*_BASE_HI`, `*_BASE_256B`, and `*_HI_256B`; command/control bits such as `ENABLE`, `RESET`, `STALL`, `FORCE`, `FREEZE`, `WAIT`, `EXEC_COUNT`, `DISABLE_*`, and `AUTO_INCR`; status/counter fields such as `BUSY`, `IDLE`, `STATUS`, `COUNT`, `OVERFLOW`, `PEND_TXFER`, and `THROTTLE_LEVEL`; and reserved fields that callers must not treat as portable feature bits.

## Control Flow

This header has no runtime control flow. Its direct behavior is compile-time macro substitution.

The implied runtime flow in AMDGPU consumers is:

1. Select the GC 11.0.0 register header for the active ASIC/IP version.
2. Choose the matching register offset from `gc_11_0_0_offset.h`.
3. Use a `__SHIFT`/`_MASK` pair directly, or through `REG_SET_FIELD`/`REG_GET_FIELD`, to compose or decode a 32-bit register value.
4. Read, write, poll, or emit that value through AMDGPU MMIO helpers or PM4 command packets.
5. Let the underlying CP, SPI, TCP, GDS, UTCL1, GCR, CAC/EDC, RLC, GRBM, VGT, or GE hardware block act on the programmed bits or report status through them.

The runtime sequencing is owned by the surrounding driver and firmware-facing paths, not by this generated header. For example, CP DMA command registers need correct source/destination address and command programming before execution; semaphore wait/signal registers need ordering against producer and consumer queues; coherency registers need pairing with cache management and command submission rules; CAC/EDC throttle registers need power-management sequencing; and VGT/GE draw-state registers need coherent draw-packet setup. This file describes bit positions only and does not encode waits, flushes, write-one-to-clear behavior, read side effects, or reset ordering.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe hardware register state that is volatile, generation-specific, and controlled by AMDGPU driver code, firmware, command processors, and the GPU itself.

State represented in this chunk includes:

- Queue and command-processor state: HPD queue availability/state, append/fence counters, scratch register storage, atomic pre-operation data, semaphore addresses, CP DMA descriptors, IB2/ST buffer pointers and sizes, EOP done event/data context, draw/dispatch/index indirect addresses, sample status, and ME coherency ranges.
- Power and throttle state: DIDT/EDC controls, rolling power deltas, dynamic thresholds, stretch counters, CAC aggregate windows and GFXCLK-cycle counters, per-block CAC weights, PCC/PWRBRK/DIDT stall patterns, throttle status, overflow counters, and EDC hysteresis state.
- Debug and status state: SPI trap and wave-stall controls, TCP status and debug data, GCR command/status, GDS restore fields, RLC GPM performance counters, GRBM graphics instance selection, and CP pipe-stat/performance counters.
- Draw and geometry state: primitive and index type, vertex index bounds and offsets, number of indices/instances, tessellation-factor ring and memory base, HS offchip parameters, GE grouping and stereo controls, user VGPR data/enables, fast GS launch dimensions, GS output primitive type, and line stipple state.

Persistence depends on the hardware block. Some fields are context or queue state that persists until rewritten, context-switched, or restored after reset. Some are live status snapshots or counters. Some registers are command-like or side-effecting, especially DMA, semaphore, EOP, atomic, and append-related registers. Some power-management fields may be initialized from golden settings or firmware-managed sequences and then preserved across normal operation until power-gating, reset, suspend/resume, or reinitialization.

The header does not distinguish read-only, write-only, sticky, clear-on-read, write-one-to-clear, pulse, or reserved fields. Consumers must rely on hardware documentation and established AMDGPU programming sequences. Reserved and generation-specific bits should generally be preserved during read-modify-write unless a documented full-register value is being emitted.

## Dependencies And Integration Points

This chunk must remain synchronized with the GC 11.0.0 generated register set:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_offset.h` supplies matching `mm*` register addresses.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_default.h` supplies generated default/reset values where present.
- AMDGPU GC 11 driver code, KFD integration, power-management code, reset/suspend/resume paths, debug tooling, and firmware-facing command paths rely on these field names matching the register database.
- Neighbor generation headers such as `gc_10_3_0_sh_mask.h`, `gc_10_1_0_sh_mask.h`, and other GC 11 variants expose similar families with generation-specific field layouts. Mixing a GC 11.0.0 mask with another generation's offset may compile but program the wrong hardware bits.

Functional integration points include CP queue management, CP DMA packet execution, semaphore/fence/EOP signaling, scratch and atomic operations, shader wave debug and trap controls, texture/cache invalidation and status collection, GDS restore behavior, UTCL1/GCR controls, CAC/EDC/PCC/PWRBRK power throttling, RLC performance monitoring, GRBM instance targeting, primitive assembly, indexed/indirect draw setup, tessellation-factor storage, geometry engine grouping, stereo routing, user VGPR handoff, and line stipple state.

Because these are untyped preprocessor macros, integration relies on exact token spelling. A consumer using `REG_SET_FIELD(value, CP_ME_COHER_CNTL, DB_DEST_BASE_ENA, x)` depends on the existence and correctness of both `CP_ME_COHER_CNTL__DB_DEST_BASE_ENA__SHIFT` and `CP_ME_COHER_CNTL__DB_DEST_BASE_ENA_MASK`.

## Risks And Edge Cases

- The range begins mid-register. This chunk contains only the `CP_DEBUG_2` mask lines; the corresponding shift lines and register comment are owned by the previous chunk.
- The range ends at a register marker. `PA_SC_SCREEN_EXTENT_MIN_0` has no field macros in this chunk; its `X`/`Y` shift and mask definitions are in the next chunk.
- Generated-header drift is the dominant risk. A wrong shift or mask compiles cleanly but programs or decodes the wrong hardware bits, causing hangs, lost fences, bad status reporting, broken throttling, corrupted draws, or performance regressions.
- Address fields often encode high/low halves or hardware-aligned units, such as 256-byte base units. Treating these as raw byte addresses or failing to preserve high bits can target the wrong GPU memory.
- CP DMA, semaphore, append, atomic, EOP, and indirect draw registers are sequencing-sensitive. Misordered writes or incorrect field packing can trigger work early, wait forever, corrupt command-visible memory, or signal the wrong fence.
- CAC/EDC/PCC/PWRBRK/DIDT fields affect power estimation and throttling. Incorrect weights, thresholds, hysteresis, stall patterns, or overflow handling can create silent performance cliffs, unstable throttling, or thermal/power-limit behavior that only appears under specific workloads.
- Repeated families invite generator or copy errors. Per-SE CAC counters and weights, per-CU SPI resource reservation registers, and repeated CP counter/address pairs should remain structurally consistent where hardware requires it.
- Debug/status fields can be volatile or latch side effects. Driver diagnostics should avoid assuming that every status field is stable across reads or safe to write through a generic read-modify-write path.
- Reserved fields appear throughout this generated map. Full-register writes that do not preserve undocumented bits can break generation-specific behavior.
- The file does not encode hardware access permissions. Some fields may be privileged, PF-only, debug-only, read-only, or firmware-owned even though the macros are available to all C consumers that include the header.

## Test Signals

Useful validation is mostly build coverage, generated-data consistency checks, and hardware runtime coverage:

- Build AMDGPU and KFD configurations that include GC 11.0.0 support. Missing or renamed macros should surface in graphics, compute, reset, power-management, debug, and command-submission code.
- Mechanically compare this range against AMD's authoritative GC 11.0.0 register database and verify that every register in the chunk has matching offsets in `gc_11_0_0_offset.h` and defaults in `gc_11_0_0_default.h` where generated.
- Run static mask sanity checks: masks should align with their shifts, full-width data fields should use `0xFFFFFFFFL`, high/low address pairs should have expected widths, repeated per-SE/per-CU/per-counter groups should be consistent, and reserved masks should not be consumed as feature flags.
- Exercise CP DMA copy/fill paths, semaphore wait/signal paths, EOP fence signaling, scratch/atomic operations, append buffers, indirect draw/dispatch/index addresses, and ME coherency programming on GC 11 hardware.
- Exercise power and throttling workloads that stress EDC/CAC/PCC/PWRBRK/DIDT controls and watch for unexpected throttle levels, overflow counters, unstable clocks, performance regressions, or thermal/power-limit anomalies.
- Test graphics workloads covering indexed and indirect draws, primitive type/index type changes, tessellation, GS/fast-launch paths, stereo state, line stipple, multi-instance draws, and geometry-engine subgroup controls.
- Inspect debugfs/register dumps for decoded HPD queue status, SPI trap/wave controls, TCP status, GCR status, CAC/EDC counters, RLC GPM counters, GRBM index selection, CP pipe stats, VGT counters, and GE controls. Known-good dumps should decode consistently with hardware documentation.
- Stress suspend/resume, GPU reset, runtime power management, queue teardown/restart, and hang recovery paths. Warning signals include CP/ME/PFP timeouts, bad fence completion, semaphore waits that never resolve, corrupted output buffers, false idle detection, bad performance-counter values, and workload-specific rendering corruption.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002514`. The final per-file report for `gc_11_0_0_sh_mask.h` should merge this with adjacent chunks before making whole-file statements.

The previous chunk owns the beginning of `CP_DEBUG_2`, including its register comment and shift macros. This chunk resumes with `CP_DEBUG_2` masks and then covers complete generated families through `PA_SC_LINE_STIPPLE_STATE`. The next chunk owns the field definitions for `PA_SC_SCREEN_EXTENT_MIN_0` and subsequent rasterizer/screen-extent registers.
