# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_offset.h lines 2510-4982

## Purpose

This chunk is the middle slice of the generated AMD GC 9.0 register offset header. It has no executable logic; it publishes preprocessor constants that map symbolic GC 9.0 register names to SOC15 register offsets and base-index selectors. AMDGPU code uses these `mm...` constants with register access helpers such as `SOC15_REG_OFFSET()`, `RREG32_SOC15()`, `WREG32_SOC15()`, and `WREG32_SOC15_OFFSET()` to address graphics, command-processor, GDS, RAS, and user-config/context registers on GFX9-class hardware.

The range starts in the tail of the `gc_cppdec` command-processor decoder block, then defines complete or mostly complete blocks for:

- `gc_cppdec2` at base address `0xc600`: command processor doorbell, MQD, EDC, UTCL1, and reset/control registers.
- `gc_spipdec` at base address `0xc700`: SPI arbitration, debug, wave-control, barrier, LDS, and shader-programming side registers.
- `gc_cpphqddec` at base address `0xc800`: hardware queue descriptor and queue scheduling registers.
- `gc_didtdec`, `gc_gccacdec`, `gc_tcpdec`, `gc_gdspdec`, and `gc_rasdec`: dynamic power/thermal index registers, CAC counters, texture cache processor debug/perf registers, global data share allocation registers, and RAS signature registers.
- `gc_gfxdec0` at base address `0x28000`: context-space graphics pipeline registers for DB, PA, VGT, SPI, CB, SX, CP, and related shader/primitive state.
- The first portion of `gc_gfxudec` at base address `0x30000`: user-config registers for CP events, streamout counters, scratch, indirect buffers, metadata, coherency, VGT draw state, WD buffer addresses, and early PA screen/trap registers.

Although this repository path sits under a `ceph-client` source mirror, this file is AMDGPU kernel hardware metadata. It does not implement Ceph client behavior, filesystem semantics, networking, or distributed storage persistence.

## Important APIs, Types, And Constants

There are no functions, structs, enums, typedefs, or runtime APIs in this chunk. The public interface is a large set of `#define` constants in pairs:

- `mmREGISTER_NAME`: the generated register offset value for GC 9.0.
- `mmREGISTER_NAME_BASE_IDX`: the SOC15 base index used by AMDGPU's register-offset composition macros.

This chunk contains 2,433 `#define mm...` lines: 1,216 register-offset macros and 1,217 `_BASE_IDX` selectors. The apparent one-extra base-index line is because the chunk begins at line 2510 with `mmCP_ME2_PIPE0_INT_CNTL_BASE_IDX`, while the matching `mmCP_ME2_PIPE0_INT_CNTL` offset is in the previous chunk. The chunk ends cleanly at `mmPA_SC_P3D_TRAP_SCREEN_V_BASE_IDX`; following PA trap-screen registers continue in the next chunk.

Important register groups visible here include:

- Command processor control and status, lines 2510-2675: `mmCP_ME*_PIPE*_INT_CNTL`, `mmCP_ME*_PIPE*_INT_STATUS`, `mmCP_*_PRGRM_CNTR_START`, `mmCP_*_INTR_ROUTINE_START`, `mmCP_CONTEXT_CNTL`, `mmCP_MAX_CONTEXT`, VMID reset/preempt/status registers, CPC interrupt status/context registers, doorbell scheduler controls `mmCP_RB_DOORBELL_CONTROL_SCH_0` through `_7`, `mmCP_RB_DOORBELL_CLEAR`, EDC counters, GFX MQD base/control registers, ring-buffer status, UTCL1 status registers, and soft reset/control registers.
- SPI block, lines 2681-2799: `mmSPI_ARB_*`, `mmSPI_CDBG_SYS_*`, wave-control percentages, WGP per-wave debug registers, debug-busy controls, shader/user data debug selectors, PS input debug, wave halt/resume controls, barrier debug, LDS debug and perf controls, `mmSPI_RESOURCE_RESERVE_*`, `mmSPI_SHADER_PGM_RSRC3_*`, and SPI arbiter controls.
- HQD block, lines 2805-2933: `mmCP_HQD_GFX_CONTROL`, `mmCP_MQD_BASE_ADDR`, `mmCP_MQD_CONTROL`, `mmCP_HQD_ACTIVE`, `mmCP_HQD_VMID`, priority/quantum registers, persistent state, PQ base/read/write pointer and doorbell controls, IB base/size/control registers, GDS resource registers, EOP base and control, dequeue/request/status, semaphore and message type registers, and `mmCP_HQD_PQ_WPTR_HI`.
- Power and counter side blocks, lines 2939-3037: DIDT indirect index/data registers; GC/SE CAC control and readout registers; TCP watch, address config, invalidation, EDC, status, UTCL1 status, ATC, performance-counter, and perf-filter registers.
- GDS block, lines 3043-3277: per-VMID GDS base and size registers for VMID0 through VMID15, GWS/OA allocation registers for VMID0 through VMID15, ordered append index/read pointers, GDS debug/EDC controls, context switch state/save/restore registers, partition-size controls, and GS context switch counters.
- RAS block, lines 3283-3337: `mmRAS_SIGNATURE_CONTROL`, `mmRAS_SIGNATURE_MASK`, and signatures for SX, DB, PA, VGT, SQ, SC, SPI, TA, TCP, and TCP stalls.
- Graphics context block `gc_gfxdec0`, lines 3343-4529: depth buffer and stencil state, PA scissor/window/viewport/clipping/raster state, CB target/mask/blend/color target state, SPI PS input and shader output format state, SX blend optimization state, VGT primitive/tessellation/streamout state, CP VMID/perf context state, and `mmCB_COLOR0_*` through `mmCB_COLOR7_*` render-target layout and DCC registers.
- User-config block `gc_gfxudec`, lines 4535-4981: CP EOP completion/fence addresses, streamout counters and controls, primitive/sample/query counters, scratch registers, atomic preop and GDS atomic preop registers, CP DMA/ME source/destination/address registers, indirect-buffer base/size registers, metadata base addresses, indirect draw/dispatch addresses, index buffer address/type, GDS backup addresses, coherency registers, RLC performance counters, `mmGRBM_GFX_INDEX`, immediate draw VGT state, WD buffer base registers, and early PA line stipple/screen/trap-screen registers.

All numeric offsets are untyped integer constants. The `_BASE_IDX` values are significant: the first blocks in this chunk use base index `0`, while `gc_gfxdec0` and `gc_gfxudec` use base index `1`. Consumers must preserve that pairing when building SOC15 register addresses.

## Control Flow

This header has no runtime control flow. Its effect is entirely compile-time name substitution.

The usual consumer flow is:

1. AMDGPU selects a GFX9 ASIC path and includes `gc/gc_9_0_offset.h` along with companion shift/mask/default headers such as `gc_9_0_sh_mask.h` and `gc_9_0_default.h`.
2. Driver code names a register by its `mm...` macro instead of hard-coding an offset.
3. Register helpers combine the GC IP block, instance id, register offset, base index, and optional register-array displacement into a MMIO address.
4. The driver reads status registers, writes configuration registers, polls completion bits, or emits register programming into command streams depending on the register's hardware role.

This chunk's constants participate in several common control paths:

- Queue bring-up and teardown: HQD/MQD/PQ/IB/doorbell registers are programmed to bind queues, ring buffers, VMIDs, doorbell routing, EOP state, and queue priorities.
- Graphics context programming: context registers in `gc_gfxdec0` are loaded as part of graphics pipeline state and can be saved/restored by context switching or emitted through command streams.
- Draw and dispatch execution: user-config registers in `gc_gfxudec` describe index buffers, indirect draw/dispatch buffers, primitive counts, streamout counters, coherency ranges, and EOP completion behavior.
- Diagnostics and error handling: status, EDC, RAS signature, debug, perf-counter, trap-screen, and wave-control registers are read or written by debug, hang analysis, reset, interrupt, and validation paths.
- Resource partitioning: GDS, GWS, and OA VMID registers define per-VMID hardware resource ownership and are updated when queues or processes receive or release GDS-backed resources.

The file itself does not encode ordering. Correct ordering lives in AMDGPU code and hardware programming guides. For example, HQD registers must be programmed in queue-setup order, DB/CB/PA/VGT state must be synchronized with command submission, and interrupt/status registers must be sampled or cleared according to their register semantics.

## State And Persistence Behavior

The header stores no state and persists nothing. It describes state that lives in GPU registers.

State represented by this chunk includes:

- Command-processor state: pipe interrupt enables/status, micro-engine program-counter start addresses, interrupt routine starts, context limits, VMID reset/preempt/status, doorbell routing, MQD base addresses, ring status, soft reset, and CPC/CPF/CPG EDC and UTCL1 status.
- Queue state: HQD active/VMID/persistent-state fields, priority and quantum, queue base/read/write pointers, doorbell controls, IB state, dequeue request/status, semaphore/message registers, and EOP base/size controls.
- GDS resource state: per-VMID GDS base/size, per-VMID GWS and ordered-append resources, append/consume pointers, GDS debug/counter state, context-save/restore state, and partition sizing.
- Graphics pipeline context state: depth/stencil buffer addresses and controls, viewport/scissor and clip/raster settings, shader input/output formats, blend/downconvert state, VGT primitive/tessellation/streamout controls, CB render-target base/attributes/DCC state, and DB/PA/CB/SPI/SX/VGT status-relevant controls.
- User-config state: EOP completion destinations, fence data, streamout counters, shader query counters, scratch registers, CP atomic and DMA operands, indirect buffer and metadata addresses, index-buffer state, coherency ranges, RLC performance counters, GRBM indexing, WD buffer addresses, and line-stipple/trap-screen controls.
- Reliability and diagnostics state: RAS signature registers, EDC counters, TCP/SPI debug controls, performance-counter selectors, and status registers.

Persistence depends on the register family. Context registers can be part of GPU context state and may be saved/restored across preemption or queue switches. Queue descriptor and doorbell state persists until the driver destroys the queue, resets the GPU, reinitializes the engine, or suspend/resume reprograms it. Status, counter, interrupt, and debug registers are transient and may be clear-on-read, write-one-to-clear, monotonically counting, or reset by block reset depending on the underlying hardware definition. Resource allocation registers such as GDS VMID ranges persist as hardware state until explicitly reprogrammed or reset.

The constants are part of a source-level ABI between generated AMD register descriptions and driver code. Renaming a macro or changing an offset can break builds or silently redirect MMIO accesses if the change compiles through another similarly named symbol.

## Dependencies And Integration Points

This generated header depends on AMD's GC 9.0 register database. The offsets are meaningful only with the rest of the AMDGPU SOC15 register infrastructure and the companion generated headers in the same `asic_reg/gc` tree:

- `gc_9_0_sh_mask.h` for field shifts and masks.
- `gc_9_0_default.h` for default register values.
- Related GC 9.x offset headers such as `gc_9_1_offset.h` and `gc_9_2_1_offset.h`, which show the same register-map pattern for later GFX9 variants.
- SOC15 register access macros that combine `GC`, instance ids, `mm...` offsets, and `_BASE_IDX` values into MMIO addresses.

Observed include and consumer points in this repository include `amdgpu/gfx_v9_0.c`, `amdgpu/amdgpu_amdkfd_gfx_v9.c`, `amdgpu/amdkfd/kfd_mqd_manager_v9.c`, `amdgpu/gfxhub_v1_0.c`, `amdgpu/soc15.c`, `amdgpu/mxgpu_ai.c`, PSP setup files, and PowerPlay's `vega10_inc.h`. The GDS VMID macros from this chunk are used directly in `gfx_v9_0.c` to reset and program per-VMID GDS ranges, and related GFX10 code uses analogous generated offsets for the same programming pattern.

Important integration areas are:

- AMDGPU graphics ring and compute queue initialization, especially MQD/HQD/PQ/doorbell/EOP programming.
- AMD KFD queue management, where per-process queues, VMIDs, GDS resources, and doorbells must match hardware queue descriptors.
- Graphics pipeline state emission and context management, where DB, PA, SPI, VGT, CB, and SX context registers are addressed by command packets or direct register writes.
- Reset and hang recovery, where status, RAS, EDC, debug, and queue registers are read to determine engine state and then reinitialized.
- Performance and diagnostics paths, including SPI/TCP debug, RLC counters, streamout counters, query counters, and RAS signature collection.
- Virtualization/SR-IOV-sensitive code paths, where VMID, queue, doorbell, and GDS resource registers must not leak or corrupt another virtual function's state.

## Risks And Edge Cases

The main risk is silent hardware misaddressing. These constants are plain C preprocessor values, so the compiler cannot distinguish a CP queue register from a CB color target register or a base-index mismatch.

High-risk areas include:

- Chunk boundary split: line 2510 contains only `mmCP_ME2_PIPE0_INT_CNTL_BASE_IDX`; the offset macro is in the previous chunk. The next chunk continues the user-config graphics block after line 4982. The final merged report should avoid treating this slice as a complete standalone register map.
- Base-index correctness: many registers in early blocks have `_BASE_IDX 0`, while context/user-config registers have `_BASE_IDX 1`. A wrong base index can produce a valid-looking but incorrect MMIO address.
- Queue programming: HQD, MQD, PQ, IB, doorbell, EOP, and VMID registers are tightly sequenced. Wrong offsets or array assumptions can make queues fail to start, read/write the wrong ring, lose interrupts, or signal completion to the wrong address.
- GDS allocation: per-VMID GDS/GWS/OA registers are repetitive. Off-by-two, wrong-VMID, or wrong base/size programming can leak global data share resources between processes or make shaders access unavailable GDS.
- Context-state corruption: DB, PA, SPI, VGT, CB, SX, and CP context registers are dense and highly order-sensitive. A single wrong address can cause rendering corruption, hangs, invalid depth/stencil behavior, bad viewport/scissor state, streamout failures, wrong color targets, or broken DCC/compression metadata.
- Interrupt and status handling: CP pipe interrupt controls/status, CPC status, EOP completion, queue dequeue status, and debug/status registers have hardware-specific clear and polling semantics not expressed in this offset header.
- Debug/perf/RAS registers: RAS signatures, EDC counters, SPI/TCP debug controls, and perf filters may be side-effectful or require block-idle conditions. Address mistakes can hide reliability issues or interfere with live workloads.
- Cross-generation drift: GC 9.0 offsets differ from GCA/GFX6-8 and GFX10 generated headers. Reusing constants across ASIC families can compile if names overlap but address the wrong register map.

## Test Signals

Useful validation signals are primarily build, generated-data comparison, and hardware behavior tests:

- Kernel build coverage for all GFX9 AMDGPU and KFD files that include `gc_9_0_offset.h`; missing or renamed macros should fail compilation.
- Generated-header comparison against AMD's authoritative GC 9.0 register database, checking every offset and `_BASE_IDX` pair in lines 2510-4982.
- Static checks that every `mm...` register macro has a matching `_BASE_IDX`, with known exceptions for chunk boundaries during chunk research.
- Queue bring-up tests for graphics and compute rings, including MQD/HQD setup, doorbell writes, EOP fence signaling, indirect buffers, preemption/dequeue, and VMID assignment.
- KFD workload tests that exercise multiple processes/VMIDs, per-VMID GDS/GWS/OA allocation, queue priorities, and doorbell routing.
- Graphics rendering tests covering depth/stencil, scissor/viewport, primitive topology, tessellation, streamout, blend/downconvert, multiple render targets, DCC, and color target base/address handling.
- Indirect draw/dispatch and index-buffer tests that use `CP_DRAW_INDX_INDR_ADDR`, `CP_DISPATCH_INDR_ADDR`, `CP_INDEX_BASE_ADDR`, `CP_INDEX_TYPE`, and related user-config registers.
- Reset, suspend/resume, and GPU hang recovery tests that verify CP/HQD/GDS/context registers are restored and status/debug registers remain usable after reinitialization.
- RAS/EDC/debug/perf validation that reads signature/counter/status registers and confirms expected interrupt or diagnostic behavior without MMIO faults.
- Cross-ASIC regression tests that verify GFX9 code uses `gc_9_0_offset.h` while GFX10 and older GCA paths use their own generated offsets.

Symptoms of incorrect constants include failed ring initialization, KFD queue launch failures, missed or misdirected doorbell/EOP interrupts, GPU page faults, hangs during draws or dispatches, corrupted rendering, broken streamout/query counters, invalid GDS isolation, failed reset recovery, or misleading RAS/performance diagnostics.

## Cross-Chunk Notes

This is chunk 2 of 3 for `gc_9_0_offset.h`. The previous chunk contains the file prologue, include guard, early GRBM/CP/SQ/GDS/TCP/TA/DB/CB/SX/PA/GL1 registers, and the beginning of the `gc_cppdec` block. This chunk starts mid-pair with a `_BASE_IDX` from that CP block, then covers the main middle register-map blocks. The next chunk completes later `gc_gfxudec` registers, SQ thread trace, SQC, TA, DB occlusion counters, and the remaining tail of the header including the include guard close. The merge lane should synthesize the final per-file report from all three chunks and treat this document as a chunk-local view, not a complete standalone description of the header.
