# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_3_offset.h lines 2499-4945

## Scope

This chunk covers a generated AMD GC 9.4.3 register-offset header range. It is not executable code; its public surface is a set of preprocessor constants mapping register names to per-address-block offsets and `*_BASE_IDX` selector values used by SOC15/MMIO register access helpers.

The slice starts in the middle of the shader processor interpolator/user-data register area at `regSPI_SHADER_USER_DATA_LS_13_BASE_IDX`, continues through compute dispatch state, CP graphics/compute queue state, SPI arbitration/debug/resource-reservation state, HQD queue descriptors, TCP watch/cache controls, GDS allocation/context-switch counters, RAS signatures, and a large graphics context block. It ends just after the start of the `xcd0_gc_gfxudec` block with EOP and stream-out address registers; the adjacent chunk is needed for the rest of `gfxudec` counter definitions.

Address blocks covered in this range:

- Existing `BASE_IDX 0` shader/compute context area before the first in-range address-block comment.
- `xcd0_gc_cppdec` at base address `0xc080`.
- `xcd0_gc_cppdec2` at base address `0xc600`.
- `xcd0_gc_spipdec` at base address `0xc700`.
- `xcd0_gc_cpphqddec` at base address `0xc800`.
- `xcd0_gc_tcpdec` at base address `0xca80`.
- `xcd0_gc_gdspdec` at base address `0xcc00`.
- `xcd0_gc_rasdec` at base address `0xce00`.
- `xcd0_gc_gfxdec0` at base address `0x28000`.
- Beginning of `xcd0_gc_gfxudec` at base address `0x30000`.

## Purpose

`gc_9_4_3_offset.h` provides compile-time symbolic register offsets for AMD GC 9.4.3 graphics-core hardware. Consumers pass these symbols to macros such as `SOC15_REG_OFFSET()`, `WREG32_SOC15()`, `WREG32_SOC15_RLC()`, `RREG32_SOC15()`, and register-entry dump helpers so driver code can address hardware registers by stable names rather than literal offsets.

This chunk is centered on two hardware surfaces:

- Command, dispatch, queue, and memory-resource state for compute and graphics engines: compute dimensions/user data, CP ring buffer configuration, doorbells, interrupt state, UTCL1 errors/status, HQD/MQD queue descriptors, EOP queues, GDS/GWS/OA resources, TCP watchpoints, and RAS signature collection.
- Draw/render context state: depth-buffer state, scissor/window/viewport state, clip and user-clip-plane state, pixel-shader input mapping, blend/color target state, primitive assembly, tessellation/geometry/stream-out state, rasterization/sample state, and color-buffer render-target base/metadata addresses.

The header is generated from AMD register descriptions. Its correctness is foundational because a wrong numeric offset silently sends later driver code to the wrong MMIO/register-aperture location.

## Important API Surface

- Shader and compute context registers at lines 2499-2715 include `regSPI_SHADER_USER_DATA_LS_14` through `_31`, `regSPI_SHADER_USER_DATA_COMMON_0` through `_31`, `regCOMPUTE_DISPATCH_INITIATOR`, `regCOMPUTE_DIM_{X,Y,Z}`, `regCOMPUTE_START_{X,Y,Z}`, `regCOMPUTE_NUM_THREAD_{X,Y,Z}`, `regCOMPUTE_PGM_{LO,HI}`, `regCOMPUTE_DISPATCH_PKT_ADDR_{LO,HI}`, `regCOMPUTE_DISPATCH_SCRATCH_BASE_{LO,HI}`, `regCOMPUTE_PGM_RSRC{1,2,3}`, `regCOMPUTE_VMID`, resource/thread-management registers, restore/relaunch registers, and `regCOMPUTE_USER_DATA_0` through `_15`.
- `xcd0_gc_cppdec` at lines 2718-3079 defines CP front-end and ring state: DFY command/data registers, EOP wait timing, CPC/CPF/CPG UTCL1 controls and error status, CP virtual/error status, ring-buffer base/control/read/write pointer registers for RB0/RB1/RB2, doorbell ranges, interrupt control/status for rings and ME pipes, priority/VMID/preemption state, instruction-cache base/op controls, and ECC/EDC status.
- `xcd0_gc_cppdec2` at lines 3082-3141 defines scheduler-specific doorbell controls, doorbell clear, CPF/CPG/CPC DSM controls, EDC FUE control, graphics MQD base/control, ring status, UTCL1 status, soft reset, and CPC graphics control.
- `xcd0_gc_spipdec` at lines 3144-3263 defines SPI arbitration, per-pipe weight/percentage controls, graphics debug/trap controls, scratch address check/status, compute queue reset, per-CU resource reservation and enable registers for CUs 0-15, wavefront context-save control, and arbitration control.
- `xcd0_gc_cpphqddec` at lines 3266-3403 defines HQD/MQD queue control state: queue active/VMID/persistent state, priorities and quantum, packet-queue base/read/write pointers, read-pointer reporting address, write-pointer polling address, doorbell control, packet/IB queue controls, dequeue/offload/semaphore/message controls, atomic preops, HQ scheduler/status/control aliases, EOP queue base/control/events, context-save buffer/stack/workgroup/GDS state, error state, AQL controls, and dispatch IDs.
- `xcd0_gc_tcpdec` at lines 3406-3453 defines TCP watchpoint address/control pairs 0-3, GATCL1/TCP DSM controls, UTCL1 controls/status, and perf-counter filters.
- `xcd0_gc_gdspdec` at lines 3456-3693 defines GDS per-VMID base/size allocations for VMIDs 0-15, GWS and OA ownership per VMID, reset masks and triggers, max compute wave ID, GDS enhancement/restore/status, compute and graphics context-switch status, and per-shader-stage context-switch counters.
- `xcd0_gc_rasdec` at lines 3696-3753 defines RAS signature control/mask and signature registers for SX, DB, PA, VGT, SQ, SC, IA, SPI, TA, TD, CB, and BCI blocks.
- `xcd0_gc_gfxdec0` at lines 3756-4925 is the largest part of the chunk. It defines depth/stencil render-target state (`DB_*`), coherency destination bases, scissor/window/cliprect/viewport state (`PA_SC_*`), color and shader masks, viewport Z ranges and transforms, user clip planes, pixel-shader input control, interpolation and shader output formats, blend controls, copy-state triggers, VGT draw/DMA/event/tessellation/geometry/stream-out state, rasterization and anti-aliasing sample state, and complete color-target register groups `CB_COLOR0_*` through `CB_COLOR7_*` including base, extended base, view, info, attrib, DCC, CMASK, FMASK, clear words, and DCC base.
- The start of `xcd0_gc_gfxudec` at lines 4928-4945 defines CP EOP completion address/data/fence registers and stream-out address registers. The continuation of this block is outside this chunk.

There are no C types, structs, enums, functions, or inline helpers in this range. Each logical register usually has two macros: `regNAME` for the offset and `regNAME_BASE_IDX` for the register base selector. Most queue/control registers in the earlier blocks use `BASE_IDX 0`; the `gfxdec0` and initial `gfxudec` registers use `BASE_IDX 1`.

## Control Flow

This header has no runtime control flow. Runtime behavior is created by callers that choose a register symbol, combine it with a GC instance, and perform a read or write through AMDGPU register accessors. Typical flows are:

1. Initialization or resume code programs CP rings, doorbells, HQD queues, MQD pointers, SPI scheduling, GDS resources, and render context defaults using the symbolic offsets.
2. Command submission and queue-management paths update ring write pointers, HQD active/dequeue state, packet-queue bases, read-pointer report addresses, doorbell controls, and EOP queues.
3. Graphics command emission or context restore writes draw/render state registers such as DB, PA, VGT, SPI, and CB registers before draws.
4. Diagnostics, RAS, KFD, and reset paths read status, error, signature, queue, context-switch, and watchpoint registers to decide whether hardware is idle, occupied, faulted, or recoverable.

In the local tree, `gfx_v9_4_3.c` includes this header and programs HQD registers with `WREG32_SOC15_RLC(GC, GET_INST(GC, xcc_id), regCP_HQD_..., ...)`, including EOP base/control, PQ base, PQ control, report/poll addresses, and active/dequeue state. `amdgpu_amdkfd_gfx_v11.c` has the same register-family pattern for queue occupancy checks: it reads `regCP_HQD_ACTIVE`, then compares `regCP_HQD_PQ_BASE` and `regCP_HQD_PQ_BASE_HI` against a queue address. Newer `gfx_v11_0.c`, `gfx_v12_0.c`, `gfx_v12_1.c`, and MES paths use equivalent symbols from their generation-specific headers, showing the integration pattern this GC 9.4.3 header supports.

## State and Persistence

The macros are stateless compile-time constants. The hardware registers they name are persistent GPU state until changed by firmware, command processor packets, direct MMIO writes, context save/restore, power management, GPU reset, or suspend/resume.

Queue and dispatch state is persistent and safety-critical. CP ring bases, write/read pointers, doorbell ranges, HQD/MQD bases, EOP queue pointers, VMID fields, and AQL dispatch IDs represent live scheduling state for graphics and compute queues. Incorrect persistence can make a ring appear occupied, redirect queue fetches, lose completion notifications, or corrupt command processing.

Graphics context state is also persistent across command buffers according to the GPU context model. DB/CB/PA/VGT/SPI registers describe the current render target addresses and metadata, viewport/scissor/clip state, shader input routing, primitive topology, tessellation, stream-out, depth/stencil policy, color blending, and sample locations. A stale or misprogrammed register can affect later draws until overwritten or context-restored.

GDS/GWS/OA allocations are per-VMID resource partitioning state. Their base/size/ownership registers decide how shader queues see global data share and synchronization resources. GDS context-switch counters and status registers are diagnostic/persistence signals around context save/restore.

RAS signature registers are diagnostic accumulation/state registers for hardware error-signature collection. TCP watch registers persist as data-watch/debug controls. SPI resource reservation registers persist CU reservation policy that can constrain queue execution until cleared.

## Dependencies and Integration Points

- Depends on AMD's generated GC 9.4.3 register database. This offset header must stay synchronized with companion generated headers for GC 9.4.3 bit masks, defaults, and any packet/register programming tables.
- Integrated through AMDGPU SOC15 address helpers and direct register access macros. The numeric offset is only meaningful when paired with the correct hardware IP block (`GC`), instance/XCC selection, and `BASE_IDX`.
- Used by GC 9.4.3-specific graphics code such as `amdgpu/gfx_v9_4_3.c` and KFD integration such as `amdgpu_amdkfd_gc_9_4_3.c`, with nearby architecture versions following the same register names for debug tables, ring setup, HQD programming, and queue occupancy logic.
- The CP/HQD/MQD macros integrate with KFD and MES concepts: MQD memory contents are copied into hardware queue descriptors, doorbells notify the command processor, and polling/report addresses live in GPU-visible memory.
- The DB/CB/PA/VGT/SPI graphics context macros integrate with PM4 packet emission and context image layout. They are not usually written by arbitrary kernel code one by one during normal draws, but they define the register names used by packets, dumps, and restore paths.
- RAS signature macros integrate with GPU reliability/error-detection paths; TCP watch and UTCL1 status/error registers integrate with debug/fault diagnostics.

## Risks

- Offset drift is the primary risk. If a generated value or `BASE_IDX` is wrong, a valid-looking `WREG32_SOC15*` call targets the wrong register or wrong aperture. This can cause silent queue corruption, hangs, bad render output, or misleading diagnostics.
- The chunk boundaries are partial. The first line is only the base-index macro for `regSPI_SHADER_USER_DATA_LS_13`, whose offset appears before this chunk. The final `gfxudec` block continues after `regCP_STREAM_OUT_ADDR_HI`; merge tooling must not treat the block as complete from this document alone.
- Alias-like duplicate offsets are intentional but hazardous for manual review. Examples include `regCP_RB0_BASE` and `regCP_RB_BASE`, `regCP_ME0_PIPE*_PRIORITY` and `regCP_RING*_PRIORITY`, `regCP_HQD_DMA_OFFLOAD` and `regCP_HQD_OFFLOAD`, `regCP_HQD_HQ_SCHEDULER*`/status/control aliases, and `regCP_PIPEID`/`regCP_RINGID`. A caller must use the semantic alias appropriate to the engine path being maintained.
- Queue-management registers are high-risk. Bad HQD base, PQ control, doorbell control, report/poll address, EOP base, active/dequeue, or VMID programming can leave compute queues stuck, falsely occupied, or writing completion data to the wrong memory.
- Render-target address and metadata registers are high-risk. `CB_COLOR*_BASE`, `*_BASE_EXT`, `*_DCC_BASE`, `*_CMASK`, and `*_FMASK` fields affect GPU memory access. Incorrect offsets or writes can produce memory corruption or invalid compression metadata access.
- GDS/GWS/OA per-VMID registers repeat over VMID 0-15, creating copy/paste and loop-index hazards. A one-off error changes another VMID's resource allocation.
- `BASE_IDX` mismatch is subtle. Early CP/SPI/HQD/TCP/GDS/RAS registers use base index 0, while graphics context and the initial `gfxudec` registers use base index 1. Incorrect table generation or manual macro selection can address the wrong base.
- This header has no reserved-bit, sequencing, range, or locking enforcement. Consumers must preserve hardware-required write ordering and use the correct accessor variant, especially RLC-safe writes during queue setup.

## Test Signals

- Build coverage: compiling AMDGPU with GC 9.4.3 support catches missing symbols, malformed macros, duplicate definitions that break preprocessing, and include-order issues.
- Generated-header validation: compare lines 2499-4945 against the AMD GC 9.4.3 register source/spec and companion `*_sh_mask.h`/default headers, checking every `reg*` offset and `*_BASE_IDX`.
- Register-access smoke tests on GC 9.4.3 hardware: boot, suspend/resume, GPU reset, and ring initialization should complete without MMIO faults, register-restore warnings, or command-processor timeouts.
- Queue tests: run KFD/compute workloads that create, destroy, preempt, and resume queues. Watch `regCP_HQD_ACTIVE`, PQ base/high, doorbells, EOP write pointers, and dequeue behavior for hangs or false occupancy.
- Graphics tests: run draw workloads covering depth/stencil, multiple render targets, DCC/CMASK/FMASK, viewport/scissor arrays, tessellation/geometry, stream-out, MSAA sample positions, and primitive restart. Failures often indicate DB/CB/PA/VGT/SPI offset or context-restore mistakes.
- RAS/debug tests: read RAS signatures, TCP watch/status, UTCL1 status/error, CP/CPC/CPF/CPG error status, and GDS context-switch counters through debug or recovery paths and compare against known-good dumps.
- Cross-generation sanity: because GC 9.4.2 and GC 9.4.3 share many CP/HQD and CB offsets while GC 11/12 use different generated offsets for several blocks, tests should ensure the GC 9.4.3 device selects `gc_9_4_3_offset.h` rather than a neighboring generation's header.
