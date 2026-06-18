# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_1_offset.h lines 2516-4992

## Scope

This chunk is the middle of a generated AMD GC 9.1 register-offset header. It contains C preprocessor constants only: each hardware register appears as an `mm...` macro whose value is the register offset within a GC address block, paired with an `mm..._BASE_IDX` macro that selects the SOC15 base-address table entry used by `SOC15_REG_OFFSET` and related AMDGPU helpers. There are no functions, structs, enums, variables, runtime branches, allocation sites, locks, or persistence code in this range.

The selected lines begin with the tail of the compute dispatch register block, then cover command processor, scheduler, shader-pipe, high-priority queue descriptor, dynamic power/debug, GDS, RAS, graphics context, and graphics user-data decoder blocks. The chunk has 2,433 `#define` lines in this line range: 1,216 register-address macros plus 1,217 base-index macros. The extra base-index macro is because the chunk starts immediately after the matching `mmCOMPUTE_STATIC_THREAD_MGMT_SE3` address macro in the previous line range.

Although the repository path is under a Ceph client mirror, this file is AMDGPU DRM hardware metadata. It is not Ceph filesystem logic and has no filesystem control flow.

## Purpose

`gc_9_1_offset.h` supplies generated register offsets for the GC 9.1 graphics IP used by Raven/Picasso/Raven2-class SOC15 AMD GPUs. Driver code combines these offsets with a hardware block id and instance id, then accesses MMIO registers through AMDGPU helper macros such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, and `WREG32_SOC15_RLC`.

This chunk describes several major register areas:

- The tail of the compute dispatch/user-data context register space: dispatch dimensions, start/restart coordinates, program address/resource registers, scratch pointers, VMID, resource limits, thread-management controls, dispatch packet address, wave restore address, and `COMPUTE_USER_DATA_0` through `_15`.
- `gc_cppdec` and `gc_cppdec2`: command processor debug, ring-buffer, queue, interrupt, doorbell, MEC/CPC/CPF/CPG, VMID, DMA, atomic, GDS, context-save, EOP, and scheduler-control offsets.
- `gc_spipdec`: SPI arbitration, weighted pipe allocation, wave limit, resource reservation, and compute wavefront context-save offsets.
- `gc_cpphqddec`: CP high-priority queue descriptor and MQD/HQD state for graphics/compute queues, including queue base, pointers, doorbells, EOP, context save, GDS state, AQL control, and error/status registers.
- `gc_didtdec` and `gc_gccacdec`: dynamic idle/droop table indirect access and GC/SE clock/power aggregation controls.
- `gc_tcpdec`: texture cache processor watchpoint, GATCL1, UTCL1, and performance-filter offsets.
- `gc_gdspdec`: global data share per-VMID base/size, GWS/OA allocation, ordered append, semaphore, context-switch count, and GDS debug/status offsets.
- `gc_rasdec`: RAS signature controls and per-pipeline signature registers for SX, DB, PA, VGT, SQ, SC, IA, SPI, TA, TD, CB, and BCI.
- `gc_gfxdec0`: context/state register offsets for DB, PA_SC, PA_CL, PA_SU, SPI, SX, CB, VGT, IA, WD, GFX/CS copy state, streamout, antialiasing, viewport, clipping, tessellation/geometry, and render-target color/depth state.
- The beginning of `gc_gfxudec`: user/control registers for CP EOP fences, streamout counters, pipe stats, scratch, append/atomic/GDS preops, semaphore/wait, coherency, and CP DMA.

## Important APIs, Types, And Macros

There are no callable APIs or C types. The public interface is the generated macro naming contract:

- `mm<REGISTER>` gives a register offset relative to the address block selected by the SOC15 base index.
- `mm<REGISTER>_BASE_IDX` gives the base index. In this chunk, registers before `gc_gfxdec0` generally use base index `0`; `gc_gfxdec0` and `gc_gfxudec` registers use base index `1`.
- Bitfield layouts are not in this file. Callers need the companion `gc_9_1_sh_mask.h` for shifts and masks when they pack or decode register values.

Notable macro families in this slice are:

- `mmCOMPUTE_*`: dispatch initialization, dimensions, start/restart coordinates, number of threads, pipeline/perf-count enables, shader program low/high address, dispatch packet and scratch base addresses, program resources, VMID, resource limits, static thread management per shader engine, thread trace, relaunch, wave restore address, and 16 compute user-data dwords.
- `mmCP_DFY_*`, `mmCP_*_INT_*`, `mmCP_GFX_ERROR`, `mmCP_FATAL_ERROR`, `mmCP_VIRT_STATUS`, and `mmCP_AQL_SMM_STATUS`: CP debug/error/interrupt/virtualization status and indirect debug data windows.
- `mmCP_RB*`, `mmCP_ME*_PIPE*`, `mmCP_RING*`, `mmCP_EOP*`, `mmCP_MEC*`, `mmCP_CPC_*`, `mmCP_CE_*`, `mmCP_IQ_*`, and `mmCP_HQD_*`: ring-buffer setup, scheduler priority, VMID, queue pointers, packet/EOP handling, MEC/CPC control, high-priority queue descriptors, MQD state, and context save/offload state.
- `mmCP_RB_DOORBELL_CONTROL_SCH_*`, `mmCP_RB_DOORBELL_CLEAR`, `mmCP_GFX_MQD_*`, and `mmCP_RB_STATUS`: scheduler doorbell and graphics MQD state in `gc_cppdec2`.
- `mmSPI_ARB_*`, `mmSPI_WCL_PIPE_PERCENT_*`, `mmSPI_WAVE_LIMIT_*`, `mmSPI_LB_CU_MASK`, `mmSPI_RESOURCE_RESERVE_*`, and `mmSPI_COMPUTE_WF_CTX_SAVE`: shader-pipe arbitration, pipe percentage allocation, wave limits, local buffer/CU masks, resource reservation, and wavefront context-save control.
- `mmDIDT_IND_*`, `mmGC_DIDT_*`, `mmGC_CAC_*`, and `mmSE_CAC_*`: indirect DIDT access and GC/SE clock/power aggregation controls.
- `mmTCP_WATCH*`, `mmTCP_GATCL1_*`, `mmTCP_UTCL1_*`, and `mmTCP_PERFCOUNTER_FILTER*`: texture/cache watchpoints, address translation controls, UTCL1 status, and performance filtering.
- `mmGDS_VMID*_BASE`, `mmGDS_VMID*_SIZE`, `mmGDS_GWS_VMID*`, `mmGDS_OA_VMID*`, `mmGDS_*_CTXSW_CNT*`, `mmGDS_DEBUG_*`, `mmGDS_ATOM_*`, and `mmGDS_MEM_BASE`: GDS address partitioning, GWS/OA ownership, context-switch counters, debugging, atomic behavior, and memory base controls.
- `mmRAS_*_SIGNATURE*`: RAS signature control/mask and block-specific signature captures for graphics subblocks.
- `mmDB_*`: depth/stencil render control, HTILE/depth/stencil base addresses, size, clear values, shader/depth/EQAA control, preload, alpha-to-mask, and later depth surface state.
- `mmPA_SC_*`, `mmPA_CL_*`, and `mmPA_SU_*`: scissor rectangles, viewport scissor/depth ranges, raster config, screen extents, clip planes, viewport scales/offsets, clip and setup control, line/point/poly offset, AA sample locations and masks, binning, conservative rasterization, NGG, and shader control.
- `mmSPI_PS_INPUT_CNTL_*`, `mmSPI_*_FORMAT`, `mmSPI_PS_INPUT_*`, `mmSPI_TMPRING_SIZE`, and related SPI context registers: pixel shader input interpolation, shader output format, barycentric/interpolation control, temporary ring size, and shader export format state.
- `mmSX_*` and `mmCB_*`: shader export downconvert/blend optimization, blend control, target masks, DCC/CMASK/FMASK/color render-target base/view/info/attrib/clear state for color targets 0 through 7.
- `mmVGT_*`, `mmIA_*`, and `mmWD_*`: input assembly, draw initiator/event, DMA index settings, primitive id, tessellation, geometry shader rings, streamout, shader stage enable, draw payload, instance step rate, output path, and vertex reuse/deallocation controls.
- `mmCP_EOP_DONE_*`, `mmCP_NUM_PRIM_*`, `mmCP_*INVOC*`, `mmSCRATCH_*`, `mmCP_APPEND_*`, `mmCP_*ATOMIC*_PREOP_*`, `mmCP_ME_MC_*`, `mmCP_WAIT_*`, `mmCP_COHER_*`, and `mmCP_DMA_*`: graphics user-data/control offsets for fences, streamout/primitive/stat counters, scratch registers, append counters, atomic preoperation data, CP memory-controller access, semaphores, coherency, and DMA control.

Several offset aliases intentionally point to the same numeric address, such as `mmCP_RB0_BASE`/`mmCP_RB_BASE`, `mmCP_RINGID`/`mmCP_PIPEID`, `mmCP_HQD_DMA_OFFLOAD`/`mmCP_HQD_OFFLOAD`, `mmCP_HQD_HQ_SCHEDULER0`/`mmCP_HQD_HQ_STATUS0`, and ME-specific aliases for atomic/GDS preop registers. Consumers must treat these as hardware naming aliases, not duplicate storage in this header.

## Control Flow

This header has no runtime control flow. Its only direct behavior is compile-time macro substitution.

The implied runtime flow in AMDGPU consumers is:

1. Detect a GC 9.1 ASIC and select the appropriate generated register headers.
2. Use an `mm...` offset macro, a GC hardware block id, and an instance id to compute an MMIO address.
3. Read, write, or packetize that register address through AMDGPU register helpers.
4. Use companion `gc_9_1_sh_mask.h` field macros when a caller must preserve or update specific bits.
5. Rely on golden-register programming, graphics/compute queue setup, PSP/firmware initialization, reset/recovery, KFD queue management, debugfs, or hang-dump paths to sequence those accesses.

For compute dispatch and HQD/MQD state, runtime code writes queue bases, read/write pointers, doorbell controls, VMID, EOP buffers, context-save addresses, queue priorities, and resource descriptors before activating a queue. Later status paths read the same offsets to locate queues, compare queue bases, drain/offload queues, or diagnose hangs.

For `gc_gfxdec0`, state is programmed by command streams and driver initialization as graphics pipeline context. Draw setup writes viewport/scissor/depth/color/blend/shader/VGT/streamout registers in packet order. The header does not encode ordering requirements, register shadowing, context-roll behavior, RLC interactions, cache flushes, or which registers are context-saved.

For `gc_gfxudec`, EOP/fence, primitive counter, scratch, append, atomic, semaphore, coherency, and CP DMA registers are used by command processor packet execution and synchronization paths. These registers often interact with GPU memory addresses, command stream fences, streamout counters, and wait/reg-mem operations, but this file supplies only offsets.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe stateful GPU registers whose values are owned by hardware, firmware, command submission, and AMDGPU initialization/recovery code.

Compute and HQD/MQD registers are queue and dispatch state. Queue base addresses, VMID, PQ/IB/EOP pointers, doorbells, context-save buffers, GDS resource state, user-data registers, and active/dequeue bits persist until the queue is destroyed, reset, preempted, offloaded, or reprogrammed. Incorrect offsets can activate the wrong queue, corrupt ring pointers, lose EOP events, break KFD queue lookup, or point context save/restore at the wrong memory.

`gc_cppdec` and `gc_cppdec2` CP registers include live status/error/interrupt state and persistent scheduler/ring policy. Ring buffer base/control/pointer registers, doorbell clear/control registers, MEC/CPC controls, and CP DMA/coherency controls must be programmed in hardware-defined sequences. Status and error registers may be volatile, sticky, write-one-to-clear, or latched by hardware behavior not represented in this header.

SPI, TCP, GDS, DIDT/CAC, and RAS registers mix persistent policy with volatile telemetry. Arbitration percentages, wave limits, resource masks, texture/cache controls, GDS VMID partitioning, clock/power aggregation, and RAS signature masks persist across workloads until reset or reprogramming. Watchpoint, status, signature, context-switch counter, and debug registers reflect live hardware state and can change while the GPU is running.

Graphics context registers in `gc_gfxdec0` are persistent per-context draw state. Depth/stencil/color surface bases, viewport/scissor arrays, blend state, shader input/output formats, streamout setup, VGT tessellation/geometry state, and AA sample locations must match the command stream, compiled shaders, and framebuffer layout. A wrong offset or base index can cause silent rendering corruption, memory writes to the wrong surface, bad compression metadata, or GPU hangs rather than a straightforward build failure.

The `BASE_IDX` values are part of the state-addressing contract. Confusing base index `0` decoder registers with base index `1` context/user registers changes the computed MMIO base and can target unrelated hardware.

## Dependencies And Integration Points

This chunk depends on the generated GC 9.1 register set remaining internally synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_1_sh_mask.h` provides matching field shifts and masks for the offsets in this header.
- AMDGPU SOC15 register helpers consume the `mm...` and `mm..._BASE_IDX` macros, including `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_RLC`, and register-table helpers such as `SOC15_REG_ENTRY_STR`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v10_0.c` includes this exact offset header for GC 9.1 PSP-related code and GC IP version checks.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_0.c` contains GC 9.1 golden settings and uses representative macros from this chunk, such as `mmCP_HQD_PQ_BASE` and `mmDB_RENDER_CONTROL`, through SOC15 register helpers.
- AMDKFD interop paths for GFX9 queue management use HQD offsets such as `mmCP_HQD_PQ_BASE`, `mmCP_HQD_PQ_BASE_HI`, pointer registers, and active/dequeue controls to locate, inspect, and manage hardware queues.
- Powerplay test/power-virus headers in this tree also use HQD queue macros from this family in register programming tables.

Integration points include PSP initialization for GC 9.1 devices, GFX9 golden-register programming, graphics ring and compute queue setup, KFD queue discovery/preemption, RLC-safe register writes, hang diagnostics, debugfs dumps, suspend/resume and GPU reset recovery, render/depth/color state setup, streamout and primitive statistics, command-processor fences, CP DMA/coherency sequences, GDS partitioning, RAS signature capture, and shader-pipe arbitration/resource policy.

## Risks And Edge Cases

- Generated-header drift is the dominant risk. An incorrect offset or base index compiles cleanly but reads or writes the wrong hardware register.
- The chunk starts mid-family. The matching address macro for `mmCOMPUTE_STATIC_THREAD_MGMT_SE3_BASE_IDX` is in the prior chunk, so the final per-file report must merge adjacent chunks to avoid treating this first line as a standalone register.
- The chunk ends at `mmCP_DMA_ME_COMMAND` inside `gc_gfxudec`; the remaining graphics user decoder registers are in the next chunk.
- Numeric aliases are intentional but easy to misread. Alias pairs with the same offset may reflect old/new names, ME-specific names, or scheduler/register-block naming differences. Replacing one name with another without checking the intended hardware path can make later code harder to audit.
- Similar repeated families are not interchangeable. Registers for color targets 0 through 7, viewport/scissor slots 0 through 15, GDS VMIDs, queue rings, streamout buffers, and CP primitive counters follow patterns but have distinct offsets and ordering.
- Address split registers (`*_LO`, `*_HI`, `*_BASE`, `*_BASE_HI`, `*_ADDR_LO`, `*_ADDR_HI`) have alignment and address-unit constraints outside this header. Correct offsets do not guarantee correct address packing.
- Queue-management registers have side effects. Writes to active, dequeue, offload, doorbell, pointer, semaphore, and EOP registers can start, stop, or drain real GPU work.
- Debug, status, RAS signature, and counter registers may be volatile, sticky, clear-on-read, write-one-to-clear, or latch on selector writes. This header does not distinguish those behaviors.
- Full-register writes to context registers risk clobbering reserved bits if callers do not use field masks and read-modify-write sequences where required.
- `BASE_IDX` mistakes are high impact. `gc_gfxdec0` and `gc_gfxudec` use base index `1`, while earlier decoder blocks use base index `0`; mixing these can produce valid-looking but wrong SOC15 addresses.
- Render-target and depth/stencil offsets are tied to compression metadata such as DCC, CMASK, FMASK, HTILE, and depth/stencil bases. Wrong offsets can create memory corruption or rendering defects that only appear with MSAA, compression, or multi-render-target workloads.
- GDS, GWS, OA, semaphore, append, and atomic preop registers affect cross-wave or cross-queue synchronization. Incorrect programming can hang workloads or produce nondeterministic data races.

## Test Signals

Useful validation is mostly generated-data consistency, build coverage, and hardware/runtime behavior:

- Kernel build coverage for AMDGPU files that include or indirectly depend on `gc_9_1_offset.h`, especially `psp_v10_0.c`, `gfx_v9_0.c`, GFX9 KFD queue-management paths, power-management register tables, and SOC15 register helpers.
- Mechanical comparison against AMD's authoritative GC 9.1 register database to confirm every `mm...` offset and `mm..._BASE_IDX` value in this slice.
- Cross-checks that register names in this offset chunk have matching field definitions in `gc_9_1_sh_mask.h` when bitfields are expected.
- Static consistency checks for repeated families: every register macro should have a paired `_BASE_IDX`, except for chunk-boundary split cases; color target, viewport, streamout, GDS VMID, CP counter, scratch, and user-data sequences should be monotonic where the hardware table says they are.
- Bring-up tests on GC 9.1 hardware that exercise PSP initialization, golden-register programming, graphics ring setup, and compute queue creation/destruction without MMIO faults or unexpected GPU resets.
- KFD queue tests that create queues, compare `CP_HQD_PQ_BASE`/`HI`, update doorbells and pointers, trigger dequeue/offload paths, and verify EOP/context-save behavior.
- Render tests covering depth/stencil, HTILE, DCC/CMASK/FMASK, MRT color targets 0 through 7, blending, viewport/scissor arrays, clipping, AA sample locations, streamout, primitive counters, tessellation, and geometry shader paths.
- Compute dispatch tests that exercise `COMPUTE_*` dimensions, program resource registers, scratch, user-data windows, static thread management, wave restore, and relaunch paths.
- Synchronization tests for EOP fences, scratch registers, append counters, CP atomic/GDS preoperations, semaphores, `WAIT_REG_MEM`, coherency registers, and CP DMA.
- Debug and recovery tests that read CP error/status, RAS signatures, SPI/TCP/GDS status, primitive/invocation counters, and hang-dump register tables during controlled workloads.
- Runtime warning signals include bad queue base comparisons, stuck HQD active/dequeue state, missing EOP fences, invalid VMID usage, CP fatal/GFX errors, RAS signature anomalies, bad primitive/invocation counts, rendering corruption, KFD queue hangs, or repeated GPU reset after golden-register programming.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002629`. It covers lines 2516-4992 of `gc_9_1_offset.h`. The final per-file research should merge this with adjacent chunks to include the full compute block before line 2516 and the remainder of `gc_gfxudec` plus later register blocks after line 4992.
