# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_offset.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002612`: lines 1-2509, `Docs/researches/chunks/subset-b-002612_research.md`
- `subset-b-002613`: lines 2510-4982, `Docs/researches/chunks/subset-b-002613_research.md`
- `subset-b-002614`: lines 4983-7279, `Docs/researches/chunks/subset-b-002614_research.md`

## Chunk Research

### subset-b-002612: lines 1-2509

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_offset.h lines 1-2509

## Scope

This chunk is the first segment of the generated AMD GC 9.0 register offset header. It contains the MIT license, the `_gc_9_0_OFFSET_HEADER` include guard, and C preprocessor constants mapping GC 9.0 hardware register names to register offsets. Each visible register offset is paired with a `<REGISTER>_BASE_IDX` macro, almost always `0`, for use by SOC15 register-address construction helpers.

The selected range covers 1,210 non-`_BASE_IDX` register offset macros from `0x0000` through `0x1089`. It starts with top-level SQ debug status aliases before the first address-block comment, then spans these address blocks: `gc_grbmdec`, `gc_cpdec`, `gc_padec`, `gc_sqdec`, `gc_shsdec`, `gc_tpdec`, `gc_gdsdec`, `gc_rbdec`, `gc_ea_gceadec2`, `gc_rmi_rmidec`, `gc_utcl2_atcl2dec`, `gc_utcl2_vml2pfdec`, `gc_utcl2_vml2vcdec`, `gc_utcl2_vmsharedpfdec`, `gc_utcl2_vmsharedvcdec`, `gc_tcdec`, `gc_shdec`, and the start of `gc_cppdec`. The chunk ends mid-`gc_cppdec` at `mmCP_ME2_PIPE0_INT_CNTL`; later CP interrupt/status and ring-management macros continue in the next chunk.

Although the repository path is under a `ceph-client` mirror, this file is AMDGPU DRM hardware metadata, not distributed filesystem logic.

## Purpose

`gc_9_0_offset.h` provides the register-address side of the GC 9.0 hardware definition. Driver code uses these `mm...` macros to form MMIO addresses, indexed-register offsets, and PM4 packet payloads for graphics, compute, memory-translation, cache, render-backend, and command-processor programming. Companion generated headers provide field masks/shifts and defaults; this file only identifies where each register lives.

This chunk covers the early GC 9.0 control surface:

- GRBM global control, status, soft reset, trap, scratch, power, read/write-error, RSMU, UTCL2 invalidation range, and shader-engine status registers.
- CP/CPC/CPF command-processor status, queue availability, ring-buffer pointers, instruction pointers, preemption/status counters, queue thresholds, and debug/stat registers.
- PA/VGT/WD front-end and rasterization-related controls, cache invalidation, primitive/shader-array configuration, DMA state, binner/performance controls, FIFO sizing, and UTCL1 status.
- SQ/SQC shader-core configuration, LDS/shared-memory settings, exception/debug controls, instruction/data-cache controls, thread trace words, EDC counters, resource descriptor words, scratch words, and UTCL1 controls.
- SPI/SX shader interpolator/export state, wave lifetime counters, CU masks, load-balancer data, trap-screen addresses, GDS credits, and shader-array debug state.
- Texture/TA/TD, GDS, DB/CB/GB render backend, RMI, ATC L2, VM L2, VM context, shared aperture, TCP/TCI/TCC/TCA cache, graphics shader-stage, compute dispatch, and start-of-CP ring/doorbell/interrupt registers.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or runtime variables in this chunk. Its public interface is the generated macro contract:

- `mm<REGISTER>` expands to a numeric GC 9.0 register offset.
- `mm<REGISTER>_BASE_IDX` identifies the SOC15 base index used by helpers that combine an IP block, instance, and register offset.
- Address-block comments preserve the generating register database's block names and base addresses. They are useful when reconciling offsets with hardware manuals or other generated IP-version headers.
- Several aliases intentionally map different legacy or semantic names to the same offset. Examples in this chunk include `mmCP_RB_RPTR` and `mmCP_RB0_RPTR`, `mmCP_RB_BASE` and `mmCP_RB0_BASE`, `mmCP_RING_PRIORITY_CNTS` and `mmCP_ME0_PIPE_PRIORITY_CNTS`, plus many thread-trace word aliases at `0x03b0` and `0x03b1`.

Typical consumers include `gfx_v9_0.c`, `soc15.c`, `gfxhub_v1_0.c`, PSP setup files, KFD GC 9 code, virtualization support, and power-management include paths. The macros are commonly passed to `SOC15_REG_OFFSET`, `SOC15_REG_ENTRY`, `SOC15_REG_ENTRY_STR`, `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_GOLDEN_VALUE`, and PM4 packet emission code.

## Control Flow

The header has no runtime control flow. Its behavior is compile-time macro substitution.

The implied runtime flow in AMDGPU is:

1. Select GC 9.0 register headers for an ASIC using that graphics IP version.
2. Use an `mm...` macro and its base index to build a concrete register address for MMIO, indexed access, or command-stream programming.
3. Combine the address macro with field masks/shifts from the matching `gc_9_0_sh_mask.h` header when modifying individual fields.
4. Read, write, poll, or emit the register as part of device initialization, ring setup, VM setup, graphics/compute dispatch, interrupt handling, reset, suspend/resume, debug dumps, or KFD queue management.

The file itself does not encode sequencing requirements. For example, programming VM invalidation request/ack registers, CP ring base/write-pointer registers, cache invalidation registers, or shader program addresses requires ordering, waits, and field packing supplied by driver code and the hardware programming model.

## State And Persistence Behavior

The macros are stateless and persist nothing. The hardware registers they identify are stateful, and their lifetime depends on the block:

- GRBM, GB, DB, CB, TC, ATC, RMI, and power/clock registers represent global or per-IP hardware state normally initialized at device bring-up and restored after reset or power transitions.
- CP ring-buffer, doorbell, interrupt, VMID, priority, and active-status registers bind driver-managed ring objects and doorbell ranges to hardware queue execution. Stale values can redirect command fetching or break interrupt delivery.
- VM context and VM invalidation registers persist address-space configuration, page-table ranges, fault reporting, invalidate request/ack state, and shared aperture settings. These must stay synchronized with GPUVM and KFD memory-management state.
- Shader-stage and compute registers describe program addresses, resource limits, user-data registers, thread geometry, scratch dispatch addresses, and wave restore state. These are context or dispatch state and may be emitted through command streams rather than simple MMIO writes.
- Debug, EDC/ECC, trap, performance, and status registers may be read-only, sticky, clear-on-write, write-one-to-clear, or diagnostic-only depending on the specific register. This header does not identify those access semantics.

Because offsets are raw hardware contract data, incorrect persistence handling is usually a consumer bug rather than a header behavior. Still, a wrong offset in this file can make otherwise correct save/restore or polling code operate on the wrong register.

## Dependencies And Integration Points

This chunk depends on the rest of the GC 9.0 generated register set staying consistent:

- `gc_9_0_sh_mask.h` supplies bit fields for the same register names.
- `gc_9_0_default.h`, where present, supplies default values for many of the same registers.
- SOC15 register helpers translate `(IP block, instance, base index, offset)` into actual MMIO addresses.
- PM4 packet builders use these offsets when emitting SET registers or command processor setup packets.
- AMDGPU ring, VM, GFX, CP, PSP, KFD, virtualization, reset, debugfs, and power-management code all assume these offsets match the hardware database.

Integration points visible from repository searches include GC 9 includes in `gfx_v9_0.c`, `soc15.c`, `gfxhub_v1_0.c`, PSP v3/v11/v12 files, KFD GC 9 MQD management, SR-IOV/MxGPU support, Arcturus KFD code, and Vega powerplay includes. Common direct uses include GRBM status polling, `GB_ADDR_CONFIG` golden settings and reads, CP ring base/pointer setup, compute shader PM4 test packets, VM context programming, and debug register lists.

## Risks And Edge Cases

- Generated-header drift is the main risk. A single wrong offset can compile cleanly but cause MMIO writes or PM4 packets to touch unrelated hardware state, leading to GPU hangs, bad page faults, corrupted render/compute output, or broken interrupts.
- The chunk contains many repeated register families: VM contexts 0-15, invalidation engines 0-17, shader user-data slots, CP rings 0-2, compute user-data slots, tile modes, and wave lifetime/status counters. Off-by-one generator errors in these sequences can affect only one queue, VM context, shader stage, or engine.
- Aliased macros are intentional compatibility and naming surfaces. Removing or "deduplicating" aliases such as `mmCP_RB_BASE`, `mmCP_RB0_BASE`, `mmCP_RING0_PRIORITY`, or thread-trace word aliases can break consumers that use a different naming convention for the same offset.
- The chunk ends in the middle of the `gc_cppdec` address block. Final per-file research must merge adjacent chunks to capture the complete CP interrupt/status and ring-control register family.
- The `_BASE_IDX` value is part of the SOC15 address contract. Assuming all future or adjacent headers use the same base index can break multi-base IP blocks, even though this range mostly uses `0`.
- Register names alone do not communicate access permissions, reset values, reserved-bit policy, or whether read-modify-write is safe. Consumers need the matching field/default headers and hardware programming rules.
- VM, ATC/TCC/TCP cache, and invalidation registers are ordering-sensitive. Correct offsets are necessary but not sufficient; callers must still issue required waits, flushes, acknowledgements, and range programming.
- CP ring and doorbell registers carry GPU addresses, queue ownership, and interrupt routing. Width, alignment, and high/low register pairing mistakes around these offsets can cause command fetch from the wrong memory or missed fence completion.

## Test Signals

Useful validation is mostly generated-data consistency, build coverage, and hardware exercise:

- Kernel build coverage for AMDGPU and KFD code paths that include `gc_9_0_offset.h`, especially `gfx_v9_0.c`, `gfxhub_v1_0.c`, `soc15.c`, PSP setup, and KFD MQD management.
- Mechanical comparison against AMD's authoritative GC 9.0 register database for every `mm...` offset and `_BASE_IDX` pair in lines 1-2509.
- Cross-checks that registers in this chunk have matching shift/mask definitions and defaults where those companion headers generate them.
- Static checks for repeated families: VM context ranges, VM invalidate engine request/ack/address ranges, CP ring aliases, shader user-data sequences, compute dispatch registers, tile-mode arrays, and thread-trace aliases.
- Runtime smoke tests that initialize GC 9 hardware, submit graphics and compute rings, program CP ring buffers and doorbells, dispatch compute shaders, reset the GPU, suspend/resume, and poll GRBM idle/status registers.
- GPUVM and KFD tests that exercise VM context setup, page-table base/start/end ranges, invalidate request/ack handling, dummy/protection fault reporting, PASID/VMID state, and shared aperture registers.
- Rendering and compute correctness tests that cover shader program address programming, user-data upload, scratch/tmp ring setup, TC/TCC cache invalidation, render-backend configuration, GDS, and EDC/ECC reporting paths.
- Diagnostic signals include hangs during ring bring-up, GRBM never-idle polling, failed VM invalidation acknowledgements, page faults with implausible addresses, missing CP interrupts, broken doorbells, bad shader dispatch packets, or failures isolated to one VM context, invalidation engine, ring, or shader stage.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002612`. It covers lines 1-2509 of `gc_9_0_offset.h`; the final per-file document should merge it with following chunks to complete `gc_cppdec` and the remaining GC 9.0 register address space.

### subset-b-002613: lines 2510-4982

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

### subset-b-002614: lines 4983-7279

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_offset.h lines 4983-7279

## Scope

This chunk is the final slice of AMD's generated GC 9.0 register-offset header. It starts in the tail of the main graphics MMIO offset namespace, spans multiple explicit address blocks, defines several indirect-register namespaces, and closes the `_gc_9_0_OFFSET_HEADER` guard.

The file is hardware metadata for AMDGPU GC 9.x devices. It contains preprocessor constants only; there are no functions, structs, variables, allocations, locks, or executable branches in these lines. Runtime behavior comes from AMDGPU and power-management consumers that use these constants with SOC15 MMIO helpers or indirect-register accessors.

## Purpose

The purpose of this range is to publish the numeric register addresses and indirect indices needed by GC 9 driver code for graphics debug, performance monitoring, power management, virtualization, and low-level diagnostics.

The main covered areas are:

- Tail graphics-context offsets for PA/SC trap-screen counters, SQ thread tracing, SQC cache controls, TA buffer base, DB occlusion/Z-pass counters, GDS read/write/atomic windows, GWS/OA state, and SPI configuration.
- `gc_perfddec` at base `0x34000`, covering many block-level performance counter low/high data registers and matching select/control registers for CPG, CPC, CPF, GRBM, WD, IA, VGT, PA, SPI, SQ, SX, GDS, TA, TD, TCP, TCC, TCA, CB, DB, RLC, and RMI.
- UTCL2/ATCL2 and VM L2 performance counter blocks for counter result and selection programming.
- `gc_rlcpdec` at base `0x3b000`, covering RLC control/status, safe mode, GPM timers and scratch space, power-gating/load-balance controls, SPM controls, SRM command windows, SMU/RLC command mailboxes, UTCL1/UTCL2 error/status registers, semaphores, and prewalker controls.
- `gc_pwrdec` and `gc_ea_pwrdec` at base `0x3c000`, covering CGTS per-CU power controls and CGTT clock-gating controls for major GC blocks.
- `gc_utcl2_vmsharedhvdec` and `gc_hypdec`, covering SR-IOV/hypervisor VM aperture, MARC, retry-fault, VF, CP, KIQ, SDMA, scratch, reset, interrupt, and RLC/SMU response registers.
- Indirect `gccacind`, `secacind`, `sqind`, and `didtind` namespaces for GC CAC weights/accumulators/overrides, SE CAC control, SQ wave debug state, and DIDT/EDC throttle tuning.

## Important APIs, Types, And Macros

The exported interface is a set of untyped C preprocessor constants. `mm*` names are SOC15 GC register offsets paired with `_BASE_IDX` macros, almost all using base index `1` in this range. `ix*` names are indirect register indices and do not have `_BASE_IDX` companions.

Important macro families include:

- Trap, shader trace, and render counters: `mmPA_SC_*TRAP_SCREEN_*`, `mmSQ_THREAD_TRACE_*`, `mmDB_OCCLUSION_COUNT*_LOW/HI`, and `mmDB_ZPASS_COUNT_LOW/HI`.
- GDS/GWS/OA control windows: `mmGDS_RD_*`, `mmGDS_WR_*`, `mmGDS_ATOM_*`, `mmGDS_GWS_RESOURCE*`, and `mmGDS_OA_*`.
- Performance data registers: `mm*_PERFCOUNTER*_LO/HI` for CP, front-end, geometry, shader, texture, cache, color/depth, RLC, and memory-interface blocks.
- Performance selection/control registers: `mm*_PERFCOUNTER*_SELECT`, `mm*_PERFCOUNTER*_SELECT1`, `mm*_PERFCOUNTER_CTRL`, `mmGRBM_PERFCOUNTER_SELECT`, `mmCP_PERFMON_CNTL`, and `mmRLC_GPU_IOV_PERF_CNT_*`.
- Streaming performance monitor state: `mmRLC_SPM_PERFMON_CNTL`, ring base/size/segment registers, mux-select address/data pairs, per-block sample-delay registers, `mmRLC_SPM_RING_RDPTR`, and `mmRLC_SPM_MC_CNTL`.
- RLC firmware and power-management controls: `mmRLC_CNTL`, `mmRLC_STAT`, `mmRLC_SAFE_MODE`, `mmRLC_UCODE_CNTL`, `mmRLC_PG_CNTL`, `mmRLC_CGCG_CGLS_CTRL`, `mmRLC_DYN_PG_*`, `mmRLC_GPM_*`, `mmRLC_SRM_*`, `mmRLC_SMU_*`, and `mmSMU_RLC_RESPONSE`.
- CGTS/CGTT controls: `mmCGTS_SM_CTRL_REG`, `mmCGTS_CU0_*` through `mmCGTS_CU15_*`, `mmCGTS_CU*_TCPI_CTRL_REG`, `mmCGTT_*_CLK_CTRL`, `mmSQ_POWER_THROTTLE*`, `mmRLC_GFX_RM_CNTL`, and `mmGCEA_CGTT_CLK_CTRL`.
- Virtualization and hypervisor registers: `mmMC_VM_FB_SIZE_OFFSET_VF0` through `VF15`, `mmMC_VM_MARC_*`, `mmVM_IOMMU_MMIO_CNTRL_1`, `mmRLC_GPU_IOV_*`, `mmCP_*_VF*`, `mmCP_MEC_RS64_*`, and KIQ/SDMA status controls.
- Indirect CAC indices: `ixGC_CAC_CNTL`, `ixGC_CAC_WEIGHT_*`, `ixGC_CAC_ACC_*`, `ixGC_CAC_OVRD_*`, plus the minimal `ixSE_CAC_*` set.
- Indirect SQ wave indices: `ixSQ_WAVE_STATUS`, `ixSQ_WAVE_PC_LO/HI`, `ixSQ_WAVE_EXEC_LO/HI`, `ixSQ_WAVE_M0`, `ixSQ_WAVE_TTMP0` through `TTMP15`, and `ixSQ_INTERRUPT_WORD_*`.
- Indirect DIDT/EDC indices: repeated `ixDIDT_{SQ,DB,TD,TCP,DBR}_CTRL*`, stall-control, tuning, weight, EDC threshold/status/delay/overflow, and stall-event-counter registers.

This header is included by GC 9 driver and support files such as `amdgpu/gfx_v9_0.c`, `amdgpu/gfxhub_v1_0.c`, `amdgpu/mxgpu_ai.c`, `amdkfd/kfd_mqd_manager_v9.c`, PSP units, and the Vega10 powerplay include path.

## Control Flow

There is no in-file control flow. Consumer-side control flow follows hardware access protocols:

1. MMIO consumers pass `mm*` offsets into helpers such as `SOC15_REG_OFFSET()`, `RREG32_SOC15()`, `WREG32_SOC15()`, `WREG32_SOC15_RLC()`, or no-KIQ variants.
2. RLC safe-mode users read `mmRLC_CNTL`, write `mmRLC_SAFE_MODE`, and poll the corresponding command field before changing clock/power-gating state. `gfx_v9_0.c` uses this pattern around GC power-gating updates.
3. SQ debug users write `mmSQ_IND_INDEX` with wave, SIMD, thread, and indirect-index fields, then read `mmSQ_IND_DATA`; the `ixSQ_WAVE_*` constants from this chunk identify the requested per-wave state.
4. Powerplay DIDT/CAC programming uses indirect register interfaces, for example `cgs_read_ind_register()` and `cgs_write_ind_register()` with `CGS_IND_REG__DIDT` or `CGS_IND_REG_GC_CAC`, and uses `gc_9_0_sh_mask.h` field masks to update individual fields.
5. Performance monitoring code programs select/control registers, optionally configures RLC SPM ring/mux/sample-delay state, then reads counter low/high result registers or SPM ring data.
6. SR-IOV and hypervisor-aware paths use the VF, GPU IOV, KIQ, CP, RLC, SMU, and SDMA status registers to coordinate virtual functions, resets, interrupts, and virtualization-visible status.

## State And Persistence Behavior

The macros do not hold software state. They identify hardware registers whose state is stored in the GPU until reset, firmware reinitialization, power transition, or explicit driver/firmware writes.

Relevant state categories include:

- Counter state: performance counters, occlusion counters, Z-pass counters, CAC accumulators, DIDT event counters, and GDS/OA counters can change as hardware executes work. Low/high counter halves require ordered reads by consumers if a stable 64-bit sample is needed.
- Trace and debug state: SQ thread-trace base/size/mask/control/status and SQ wave indirect data reflect active GPU execution state. Wave state is volatile and can become stale or invalid if the wave exits between selection and read.
- RLC state: safe mode, firmware control, GPM scratch/log/register windows, SRM command status, power-gating, load-balance, and clock-count registers are persistent hardware/firmware coordination points during a boot or resume cycle, but are not durable across GPU reset.
- Power and clock state: CGTS and CGTT registers configure per-block clock-gating and power behavior. Incorrect writes can affect latency, hangs, performance, and power draw until the next corrective write or reset.
- Virtualization state: VM aperture, MARC, VF, GPU IOV, KIQ, and SDMA status/control registers expose per-virtual-function or hypervisor-mediated state. These registers are especially sensitive to function ownership and reset sequencing.

## Dependencies And Integration Points

This generated offset file must remain synchronized with related AMD register metadata:

- `gc_9_0_sh_mask.h` supplies bit masks and shifts for fields inside the offsets defined here.
- `gc_9_0_default.h` supplies default values for many corresponding registers.
- SOC15 access helpers translate `mm*` offsets and `_BASE_IDX` values into real MMIO addresses for the GC hardware block.
- CGS/Powerplay indirect access helpers translate `ixGC_CAC_*` and `ixDIDT_*` indices into the correct GC CAC and DIDT indirect register paths.
- SQ debug code in `gfx_v9_0.c` depends on `ixSQ_WAVE_*` values matching the hardware SQ indirect protocol.
- RLC, SPM, and power-gating code depends on these offsets matching firmware expectations for safe mode, GPM, SRM, SPM, and SMU mailboxes.
- SR-IOV and virtualization paths depend on the `mmRLC_GPU_IOV_*`, VF aperture, KIQ, CP, and SDMA status offsets being correct for the virtualized ASIC mode.

The enclosing source tree path includes `ceph-client`, but this file is AMD GPU driver metadata and has no distributed-filesystem control path.

## Risks And Edge Cases

- These are untyped constants. A wrong numeric value can compile cleanly and cause writes to the wrong hardware register.
- The chunk mixes direct MMIO offsets and indirect indices. Using an `ix*` index with SOC15 MMIO helpers, or an `mm*` offset with an indirect accessor, would target the wrong register path.
- `_BASE_IDX` values matter for SOC15 addressing. Most values here are `1`; changing them independently of generated block metadata can silently retarget a register.
- Low/high counter pairs can tear if sampled without the hardware-recommended sequence, especially for busy performance or occlusion counters.
- RLC safe-mode and firmware command registers require polling and timeout handling. Incorrect sequencing can leave power-gating or clock-gating transitions incomplete.
- Power and DIDT/EDC tuning registers can throttle or destabilize the GPU if programmed with values intended for a different ASIC, stepping, or firmware policy.
- SR-IOV/hypervisor registers are ownership-sensitive. Guest, host, and firmware code must not assume the same write authority for all offsets.
- The final `#endif` is part of this chunk. Removing or duplicating it would break inclusion of the entire generated header.

## Test Signals

Useful validation signals include:

- Build AMDGPU with GC 9/Vega10 support enabled. Missing or renamed macros should fail in `gfx_v9_0.c`, KFD GC 9 MQD code, gfxhub, PSP, SR-IOV, or powerplay units that include this header.
- Compare this generated block against AMD's authoritative GC 9.0 register database and sibling generated files (`gc_9_0_sh_mask.h`, `gc_9_0_default.h`), allowing only expected generated-header formatting differences.
- Exercise GPU wave-debug dump paths and verify that `ixSQ_WAVE_EXEC_LO/HI`, `PC`, `STATUS`, allocation, trap, IB, `M0`, and mode fields correlate with active waves.
- Exercise perf counter and RLC SPM collection on GC 9 hardware; wrong offsets should show implausible zero/stuck counters, bad ring pointers, or mismatched select/data behavior.
- Test suspend/resume, runtime power management, and gfx clock/power gating. Failures around `mmRLC_SAFE_MODE`, `mmCGTT_*`, or `mmCGTS_*` offsets commonly appear as hangs, timeout logs, or bad power/performance behavior.
- Test Vega10 DIDT/EDC enable/disable and powerplay transitions. Bad `ixDIDT_*` or `ixGC_CAC_*` indices would surface as failed indirect writes, power-feature errors, or incorrect throttling behavior.
- Test SR-IOV reset and VF activity paths where `mmRLC_GPU_IOV_*`, VM aperture, CP, KIQ, and SDMA status registers are used.

## Cross-Chunk Notes

This is the tail chunk of `gc_9_0_offset.h`. The final per-file research document should merge it with earlier chunks that define the initial GC 9 global, GRBM, CP, queue, graphics pipeline, shader, texture/cache, and direct MMIO namespaces. In particular, this chunk starts mid-address-block before `gc_perfddec`, so the preceding chunk is needed to describe the complete graphics-context block that owns the PA/SC, SQ, SQC, TA, DB, GDS, and SPI offsets at the beginning of this range.
