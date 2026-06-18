# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_1_offset.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002628`: lines 1-2515, `Docs/researches/chunks/subset-b-002628_research.md`
- `subset-b-002629`: lines 2516-4992, `Docs/researches/chunks/subset-b-002629_research.md`
- `subset-b-002630`: lines 4993-7473, `Docs/researches/chunks/subset-b-002630_research.md`
- `subset-b-002631`: lines 7474-7483, `Docs/researches/chunks/subset-b-002631_research.md`

## Chunk Research

### subset-b-002628: lines 1-2515

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_1_offset.h lines 1-2515

## Scope

This chunk is the first 2,515 lines of the generated AMD GC 9.1 register-offset header. It contains preprocessor constants only: each visible hardware register is represented as an `mm<REGISTER>` offset macro plus, normally, an `mm<REGISTER>_BASE_IDX` macro. There are no functions, structs, enums, variables, includes, allocations, locks, callbacks, branches, or runtime code in this range.

Within the assigned range, the file declares 2,417 `mm*` macros: 1,209 register-offset macros and 1,208 base-index macros. The count is intentionally uneven because the chunk ends at `mmCOMPUTE_STATIC_THREAD_MGMT_SE3`; its `_BASE_IDX` partner is just outside the line range. All visible base indices in this chunk are `0`, meaning these offsets target the first/primary GC register aperture as interpreted by the AMDGPU SOC15 register helpers.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU DRM graphics-core hardware metadata and is unrelated to Ceph distributed filesystem behavior.

## Purpose

`gc_9_1_offset.h` supplies register addresses for the GC 9.1 graphics core. AMDGPU consumers include this header to avoid hard-coded MMIO offsets when programming graphics, compute, shader, cache, memory-translation, and diagnostics blocks. The matching shift/mask header supplies field layouts; this file supplies the register locations and base-index metadata used to build the final address.

This chunk covers the early GC 9.1 address map:

- Global SQ debug status macros before the first address-block marker.
- `gc_grbmdec` at base `0x8000`: graphics register bus manager controls, status, soft reset, clock enable, traps, errors, UTCL2 invalidation range, scratch registers, and power-related controls.
- `gc_cpdec` at base `0x8200`: command processor CPC/CPF/ME/MEC status, ring read pointers, queue thresholds, ROQ/STQ/MEQ/CEQ availability, instruction pointers, header dumps, preemption, and PRT/stat counters.
- `gc_padec` at base `0x8800`: primitive assembler, VGT, WD, clipper/setup/scan-converter, binner, FIFO, UTCL1, and shader-array configuration offsets.
- `gc_sqdec` at base `0x8c00`: shader queue, SQC, LDS, shader memory, timestamp, indirect SQ access, opcode/debug aliases, local-bus counters, EDC counters, thread-trace words, resource descriptor words, flat scratch, M0/GPR index, and SQC UTCL1 cache controls.
- `gc_shsdec` at base `0x9000`: shader interpolator/export-side controls, pixel shader wave limits, SPI lifecycle controls, CU masks, lifetime limit/status arrays, GDS credits, SX buffer sizing, active wave counters, and trap-screen registers.
- Texture, global data-share, render-backend, EA/RMI/debug, UTCL2/VM, TCP/TCC/TCA, shader-program, shader-user-data, and the start of compute-dispatch state through line 2515.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The public interface is the generated macro naming contract:

- `mm<REGISTER>` gives the register offset used by AMDGPU MMIO and indexed-register helpers.
- `mm<REGISTER>_BASE_IDX` gives the SOC15 base-index selector for that register. In this range every visible base index is `0`.
- Matching field-level constants are expected in the GC 9.1 shift/mask header, typically named `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`.
- Consumers normally combine these symbols with AMDGPU register helpers such as `RREG32`, `WREG32`, `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, `REG_SET_FIELD`, `REG_GET_FIELD`, command-stream packet builders, register dumps, debugfs paths, reset code, and firmware/bootstrap routines.

Important macro families in this range include:

- `mmGRBM_*`: global graphics status/control, per-shader-engine status, soft reset, clock gating, read/write/IOV/RSMU errors, trap registers, interrupt credit, UTCL2 invalidation range, revision, and scratch registers.
- `mmCP_*`: command processor status and debug surfaces for CPC, CPF, PFP, ME, CE, MEC1/MEC2, ring buffer read pointers, free counts, queue thresholds, command index/data, and ROQ/STQ/MEQ/CE queue diagnostics.
- `mmVGT_*`, `mmIA_*`, `mmWD_*`, `mmPA_*`, `mmCC_GC_*`, and `mmGC_USER_*`: front-end geometry, primitive assembly, work distributor, clip/setup/scan-converter, shader-array, primitive, binner, and cache-invalidation registers.
- `mmSQ_*`, `mmSQC_*`, `mmLDS_*`, and `mmSH_MEM_*`: shader-core configuration, instruction/data-cache UTCL1 controls, LDS configuration, shader memory bases/config, timestamps, indirect SQ access, opcode decode/debug aliases, thread trace, resource descriptor words, scratch state, and EDC counters.
- `mmSPI_*`: shader interpolator/program interface controls, wave lifetime tracking, CU masks, active wave counters, shader program addresses/resources, per-stage user data for PS, VS, ES, LS, common user-data windows, and stage-specific trap/program registers.
- `mmTD_*`, `mmTA_*`: texture data/address controls, status, scratch, and DSM controls.
- `mmGDS_*`: global data-share configuration, protection fault reporting, VM fault reporting, EDC counters, DSM controls, and WD/GDS command state.
- `mmDB_*`, `mmCB_*`, `mmGB_*`, `mmGC_USER_RB_*`: depth/color/render-backend diagnostics, watermarks, ring/cache policy, DFSM controls, RB redundancy/backend disable, tile and macrotile mode tables, GPU ID, color-buffer hardware controls, and DCC configuration.
- `mmGCEA_*` and `mmRMI_*`: graphics client/Ethernet-address style arbitration and memory fabric controls, probe/error/status registers, SDP credits, DRAM/IO priority maps, address normalization/decode/hash registers, and RMI crossbar/formatter/TLB controls.
- `mmport_*`: debug-unit port address/data windows for ports A through D.
- `mmATC_L2_*`, `mmVM_L2_*`, `mmVM_CONTEXT*`, `mmVM_INVALIDATE_ENG*`, and `mmMC_VM_*`: L2 translation/cache controls, dummy/protection fault reporting, identity aperture, VM context controls, invalidate engine sem/request/ack/range registers, page-table base/start/end registers, shared virtual-memory apertures, framebuffer/AGP/system apertures, and MX L1 TLB controls.
- `mmTCP_*`, `mmTC_*`, `mmTCI_*`, `mmTCC_*`, and `mmTCA_*`: texture/cache pipeline invalidation, status, address/channel steering, cache policy, EDC counters, TCC/TCA controls, L2 writeback/invalidate, and soft reset.
- `mmCOMPUTE_*` at the end of the chunk: the beginning of compute-dispatch state, including dimensions, start coordinates, thread-group sizes, pipeline/perfcount enables, program address, dispatch packet and scratch base addresses, resource registers, VMID, limits, and static thread-management registers through `SE3`.

## Control Flow

This header has no runtime control flow. Its direct behavior is compile-time macro substitution.

The implied AMDGPU runtime flow is:

1. Select the GC 9.1 register headers for the active ASIC generation.
2. Use an `mm<REGISTER>` offset and its `_BASE_IDX` selector to compute an MMIO register address through SOC15 or direct register-access helpers.
3. Combine that address with shift/mask macros from the companion header when composing or decoding a field value.
4. Read or write the hardware register during initialization, command submission, VM setup, shader setup, cache/TLB invalidation, reset, suspend/resume, power management, performance collection, or debug capture.

The header does not encode ordering rules. For example, VM invalidation requires writing address ranges and request registers and then observing acknowledgements; shader program setup requires staging program addresses, resource registers, and user-data state before dispatch or draw submission; TCC writeback/invalidate and GRBM soft reset require hardware-specific wait/idle sequencing. Those flows live in driver code and firmware protocols, not in this generated offset table.

## State And Persistence Behavior

The macros themselves hold no state and persist nothing. They describe hardware-visible state:

- Control registers such as GRBM reset/clock controls, CP queue thresholds, PA/SQ/SPI configuration, VM context controls, page-table base/start/end registers, MC aperture registers, cache policy registers, and shader program/user-data registers persist in hardware until rewritten, reset, power-gated, context-switched, or reinitialized by firmware/driver code.
- Status registers such as GRBM/CP/SQ/SPI/TD/TA/GDS/TCP/TCI/TCC/ATC/VM status and EDC/fault counters reflect live hardware and can change asynchronously as graphics, compute, DMA, firmware, and memory-translation activity proceeds.
- Fault registers such as GDS protection faults, VM dummy/protection fault status/address/default address, and VMID/page-table state may be sticky or clear-sensitive depending on semantics defined outside this header.
- Indexed or windowed surfaces, including SQ indirect access, CP command index/data, debug-unit ports, and some cache/debug counters, require external sequencing. The offset macro only identifies the selector/data register.
- Repeated arrays such as tile modes, macrotile modes, VM contexts, invalidate engines, page-table range registers, SPI user-data windows, and compute static thread-management registers represent structured hardware tables. Persistence and ownership depend on context management and ASIC-specific programming flows.

## Dependencies And Integration Points

The primary dependency is the companion GC 9.1 generated shift/mask header for field packing and decoding. The offset and shift/mask headers must remain synchronized with AMD's GC 9.1 register database; this file alone does not define bit positions or access semantics.

Likely AMDGPU integration points include:

- Graphics block bring-up and reset code that reads `mmGRBM_STATUS*`, programs `mmGRBM_SOFT_RESET`, handles GRBM errors, waits for idle, and manages clock/power controls.
- Command processor initialization and diagnostics that use `mmCP_*` status, queue, ring pointer, instruction pointer, scratch, and preemption registers.
- Graphics pipeline state setup and debugging through PA/VGT/WD/SPI/SQ registers for draw handling, shader-array configuration, cache invalidation, primitive assembly, binner behavior, and wave lifecycle counters.
- Shader program and pipeline state emission that writes `mmSPI_SHADER_PGM_*`, `mmSPI_SHADER_PGM_RSRC*`, `mmSPI_SHADER_USER_DATA_*`, and related PS/VS/ES/GS/LS/HS register windows.
- Compute dispatch paths using `mmCOMPUTE_*` registers for dimensions, program address, VMID, scratch base, resources, thread-management, and dispatch packet metadata.
- GPUVM setup and invalidation paths using `mmVM_CONTEXT*`, `mmVM_L2_*`, `mmVM_INVALIDATE_ENG*`, `mmATC_L2_*`, `mmMC_VM_*`, and fault-status/address registers.
- Cache and memory-fabric code using TCP/TCC/TCA, GCEA, RMI, and MC aperture registers for steering, cache policy, EDC reporting, address normalization, DRAM/IO priority, and writeback/invalidate.
- Debugfs, register dump, hang triage, profiling, and validation paths that decode status, busy, EDC, fault, thread-trace, local-bus counter, and performance counter registers.

Because this is generated hardware metadata, concrete behavior is expressed in consumers through AMDGPU helper macros and register-access wrappers rather than in this file.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong offset or base index can compile cleanly while reading or programming the wrong register.
- This chunk is an artificial slice of a larger 7,483-line header. It begins at the file start, but it ends mid-macro-pair: `mmCOMPUTE_STATIC_THREAD_MGMT_SE3` appears on line 2515 while its `_BASE_IDX` is outside this chunk.
- Several different semantic aliases share the same offset. For example, many SQ opcode/thread-trace word macros map to common debug/readout addresses. Consumers must understand when a name is a view of shared hardware rather than a unique register.
- All visible base indices are `0`; code that assumes that remains true for the rest of the file or for other ASIC generations can break when registers live in a different SOC15 base.
- Reset, clock, trap, debug, soft-reset, invalidation, writeback, and fault-control registers may have side effects, write-one-to-clear behavior, pulse semantics, or ordering constraints not represented by an offset macro.
- VM invalidate engines are highly repetitive (`SEM`, `REQ`, `ACK`, address-range low/high for engines 0-17). Off-by-one register selection can invalidate the wrong range or wait on the wrong acknowledgement.
- VM context page-table base/start/end registers are repeated for contexts 0-15 and split into low/high halves. Incorrect pairing or sequencing can cause page faults, address aliasing, or GPU memory corruption.
- Tile mode, macrotile mode, RB backend disable, address decode, and memory aperture registers describe physical memory layout. Misprogramming them can create rendering corruption that is difficult to attribute to a single offset.
- Shader program/user-data windows are stage-specific and densely repeated. Using a PS offset for VS/ES/LS/common data, or vice versa, can silently corrupt pipeline state.
- The header does not express access permissions. Some registers may be safe only during initialization, only while idle, only under RLC/firmware mediation, or only on specific GC 9.1 variants.

## Test Signals

Useful validation should combine generated-data checks, build coverage, and hardware/runtime diagnostics:

- Build AMDGPU code paths that include `gc_9_1_offset.h` and the matching shift/mask header; missing or renamed macros should surface at compile time.
- Mechanically compare this range against AMD's authoritative GC 9.1 register database. Each complete register in the range should have the expected offset and `_BASE_IDX`, and companion field definitions should exist where the register has documented fields.
- Run static sanity checks for repeated families: GRBM scratch registers 0-7, VM contexts 0-15, invalidate engines 0-17, invalidate address-range low/high pairs, tile modes 0-31, macrotile modes 0-15, SPI user-data windows 0-31, SPI lifetime status 0-20, and compute/static thread-management registers.
- Exercise GC 9.1 GPU initialization, suspend/resume, reset, and idle-wait paths. Signals include clean GRBM/CP status transitions, no unexpected read/write/IOV errors, stable clock/reset handling, and successful recovery after reset.
- Run graphics and compute workloads that use PS/VS/ES/GS/LS/HS and compute program/user-data registers, then verify rendered output, shader dispatch completion, and absence of CP/SQ/SPI hangs.
- Run GPUVM tests that program contexts, page-table ranges, identity apertures, MC apertures, and invalidate engines. Expected signals include correct invalidation acknowledgements, controlled fault reporting, and no stale translations.
- Run cache/TLB stress tests that exercise TCP/TCC/TCA/ATC/VM L2 invalidation and writeback paths, checking for data coherency and absence of unexpected EDC/fault status.
- Capture register dumps during known-good workloads and hang scenarios, then compare decoded GRBM, CP, SQ, SPI, VM, TCP/TCC, GDS, and GCEA/RMI values against simulator traces or vendor-known baselines.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002628`. The final per-file research should merge it with later chunks before describing the complete `gc_9_1_offset.h` register map. The next chunk should begin by completing the `mmCOMPUTE_STATIC_THREAD_MGMT_SE3` macro pair and then continue the remaining compute, graphics, and generated GC 9.1 offset definitions.

### subset-b-002629: lines 2516-4992

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

### subset-b-002630: lines 4993-7473

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_1_offset.h lines 4993-7473

Covered source range: lines 4993-7473 of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_1_offset.h`

## Purpose

This chunk is a generated AMDGPU GC 9.1 register-offset header segment. It contains C preprocessor constants only: no functions, structs, enums, variables, storage, allocations, locking, callbacks, or executable branches. The constants map named Graphics Core hardware registers to offsets and, for ordinary MMIO registers, pair each address macro with a generated `_BASE_IDX` macro.

The selected range begins in the middle of an unnamed-by-comment MMIO block that is already active before line 4993. It starts at `mmCP_DMA_PFP_SRC_ADDR` and continues through command processor, graphics frontend, shader, render backend, memory/cache, performance, RLC, power, hypervisor, CAC, SQ indirect, and DIDT indirect register families. It ends inside the `didtind` address block at `ixDIDT_DBR_EDC_STALL_DELAY_1`; the rest of the DIDT DBR block continues after this chunk. The final per-file report should reconcile those chunk-boundary splits.

The file path sits under a `ceph-client` source mirror, but this header is AMD DRM GPU hardware metadata, not Ceph filesystem logic.

## Scope and Register Areas

This range has 2,421 `#define` lines: 2,040 `mm*` defines, 381 `ix*` indirect-register defines, 1,020 `_BASE_IDX` lines, and 1,401 address-bearing macros. The dominant direct MMIO families are `RLC`, `CP`, `CGTS`, `SQ`, `PA`, `MC`, `GDS`, `VGT`, `GRBM`, `SPI`, `DB`, `CGTT`, `VM`, `WD`, `RMI`, `TCC`, `TCA`, `CB`, `TCP`, `SX`, `IA`, `TA`, `CPG`, `CPF`, `CPC`, `TD`, `ATC`, `SQC`, `UTCL2`, `SMU`, and `GCEA`.

Important direct-address groups in the opening portion include:

- `CP_*`, `CPF_*`, `CPG_*`, and `CPC_*`: command processor DMA, PFP/ME/CE buffers, indirect-buffer offsets, scratch registers, coherency registers, command buffer sizes, EOP completion controls, metadata bases, indirect draw/dispatch addresses, index state, GDS backup addresses, sample status, and ME coherency status.
- `GRBM_GFX_INDEX`: per-instance, shader-array, and shader-engine register targeting control. This register is central to programming per-SE/SH hardware and has matching field definitions in `gc_9_1_sh_mask.h`.
- `VGT_*`, `IA_*`, and `WD_*`: geometry/input front-end state such as primitive type, index type, streamout filled sizes, vertex index bounds, instance/index counts, tessellation/ring memory bases, GS/ES/VS ring item sizes, primitive distribution, draw distribution controls, draw-init status, and wave allocation limits.
- `PA_*`, `SPI_*`, and `SQ_*`: setup, scanner, shader processor input, and shader queue addresses for viewport/primitive state, shader program resources and user data, wave limits, trap/debug registers, LDS sizing, shader scratch, thread-trace, performance counters, interrupt messages, and SQ command/control registers.
- `SX_*`, `DB_*`, `CB_*`, `GDS_*`, `TA_*`, `TD_*`, `TCP_*`, `TCC_*`, `TCA_*`, `RMI_*`, `MC_*`, `ATC_*`, and `VM_*`: color/depth/backend, global-data-share, texture, cache, memory-interface, VM, and address-translation registers used for pipeline state, caches, faults, counters, flushes, and diagnostics.

The chunk then enters named address blocks:

- `gc_perfddec` at base `0x34000`: many `CGTS_*` and `CGTT_*` performance and clock/throttle selector, counter, control, and status registers, plus `GCEA_PERF_*`, `GC_PERF_*`, and miscellaneous GC performance controls.
- `gc_utcl2_atcl2pfcntrdec`, `gc_utcl2_vml2prdec`, `gc_utcl2_atcl2pfcntldec`, and `gc_utcl2_vml2pldec`: UTCL2/ATCL2/VML2 performance counter read, select, control, status, and invalidate controls.
- `gc_perfsdec`: global GC performance monitor configuration, per-block counter selection, counter low/high values, 64-bit counter pairs, and master control/status.
- `gc_rlcpdec`: a dense RLC block covering performance monitors, golden-setting support, power/power-gating handshakes, profiling/data ports, graphics memory save/restore pointers, virtual-function interface registers, CP/MEC/GRBM status mirrors, interrupt/status, and ucode control.
- `gc_pwrdec` and `gc_ea_pwrdec`: power, clock-gating, stutter, light-sleep, power-status, and SRAM/logic gating controls across GRBM, CP, RLC, SPI, SQ, DB, CB, TCC, TCP, TA, TD, WD, VM, PA, GDS, CPF/CPG/CPC, RMI, and MC.
- `gc_utcl2_vmsharedhvdec` and `gc_hypdec`: hypervisor/virtualization-facing registers such as VRAM page-table base/limit, VM context control and faults, VF/VMID controls, GRBM virtualization, scrubber/cleaner, PASID mapping, and ATS/ATC/VML2 cache invalidation controls.
- `gccacind` and `secacind`: indirect clock/activity counter control, weights, accumulators, and overrides for many GC and SE subblocks.
- `sqind`: shader wave indirect debug state including wave status, mode, trap status, hardware ID, GPR/LDS allocation, program counter, instruction dwords, TTMP registers, `M0`, execution mask, and interrupt-word aliases.
- `didtind`: dynamic power/current control, stall, tuning, EDC, threshold, status, overflow, rolling-power-delta, and stall-delay registers. This chunk covers SQ, DB, TD, TCP, and the beginning of DBR DIDT groups.

## Important APIs, Types, and Macros

There are no callable APIs or C types in this chunk. The public interface is the generated macro namespace:

- `mm<REGISTER>` gives a direct GC 9.1 MMIO register offset.
- `mm<REGISTER>_BASE_IDX` gives the SOC15 base-index selector for that register. In this chunk the direct MMIO registers use base index `1`.
- `ix<REGISTER>` gives an indirect register index. These occur in `gccacind`, `secacind`, `sqind`, and `didtind` blocks and do not have `_BASE_IDX` companion macros in this range.

The address macros are normally used with AMDGPU register helper infrastructure rather than hand-built addresses. Common integration patterns include `SOC15_REG_OFFSET(GC, instance, mm...)`, `RREG32_SOC15`, `WREG32_SOC15`, direct `RREG32`/`WREG32` where the generation-specific offset is already selected, and specialized indirect helpers such as DIDT or SQ wave-indirect accessors. Bit fields for these registers live in the companion `gc_9_1_sh_mask.h` header, for example `GRBM_GFX_INDEX__*` and `SQ_IND_INDEX__*`.

## Control Flow and Data Flow

This header has no runtime control flow. Its behavior is compile-time macro substitution:

1. A GC 9.1-aware AMDGPU source file includes this generated offset header, often alongside `gc_9_1_sh_mask.h` and default-value headers.
2. Runtime code selects the detected ASIC/IP block and the desired register instance.
3. A register helper combines the SOC15 block base, instance, macro offset, and base index into an MMIO address, or an indirect helper writes a selector register and then reads/writes an indirect data port.
4. The driver reads, writes, polls, or composes register values using the address macro plus field masks from the matching shift/mask header.

For direct MMIO registers, the data flow is usually driver or firmware programming to hardware state, followed by readback/polling for status and fault information. For `sqind` and `didtind`, the macro value is an index into an indirect register window rather than a CPU-visible MMIO address by itself. SQ wave dump paths typically program `SQ_IND_INDEX` with wave/SIMD/thread/index fields, then read `SQ_IND_DATA` for indexes such as `ixSQ_WAVE_STATUS`, `ixSQ_WAVE_PC_LO`, or `ixSQ_WAVE_EXEC_LO`. DIDT paths use DIDT-specific accessors such as `RREG32_DIDT` and `WREG32_DIDT`.

## State and Persistence Behavior

The macros store no state. They describe hardware registers whose values are owned by GPU hardware, firmware, command submission, initialization, power management, debug paths, and reset/recovery code.

Several groups represent persistent configuration until reset or later programming: CP ring and indirect-buffer bases/sizes, VGT geometry state, shader program/user-data addresses, PA/SPI/SQ setup controls, backend/cache policy, RLC save/restore pointers, virtualization mappings, and clock/power-gating policy. Other registers are volatile status or counters: busy/status registers, performance counters, fault records, EDC counters, wave debug state, and power/stutter status can change while the GPU is running.

Indirect groups have additional sequencing state. Reading `ixSQ_WAVE_*` depends on the current indirect selector fields and selected wave context. DIDT and CAC indirect registers depend on their access window and are not interchangeable with direct `mm*` addresses. Hypervisor and virtualization registers may persist VMID/PASID/fault ownership state across queue activity and are sensitive during GPU reset or SR-IOV transitions.

## Dependencies and Integration Points

This chunk depends on the rest of `gc_9_1_offset.h` for the include guard, earlier direct MMIO blocks, and trailing DIDT definitions. It is designed to stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_1_sh_mask.h`, which defines field shifts/masks for the addresses in this header.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_1_default.h`, where reset/default values are available for related registers.
- SOC15 register helper code that interprets the `mm*` offset plus `_BASE_IDX` convention.

The one direct include found in this repository copy is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v10_0.c`, which includes `gc/gc_9_1_offset.h` for GC 9.1 device support while handling PSP v10 microcode, firmware quirks, ring setup, and mailbox polling. Even when a specific consumer does not spell many of these macros directly in this tree, the generated header is part of the ASIC register contract used by AMDGPU bring-up, firmware handoff, debug, reset, and power-management code.

Related integration patterns elsewhere in AMDGPU show how the same macro families are used:

- `GRBM_GFX_INDEX` is selected before programming per-instance/per-SE/per-SH registers, with locking requirements called out around GRBM index/control access in virtualization paths.
- SQ indirect wave-state dumps program `SQ_IND_INDEX` and read `SQ_IND_DATA` with `ixSQ_WAVE_*` indexes.
- Legacy DIDT power-management code reads and writes `ixDIDT_SQ_CTRL0`, `ixDIDT_DB_CTRL0`, `ixDIDT_TD_CTRL0`, and `ixDIDT_TCP_CTRL0` through `RREG32_DIDT`/`WREG32_DIDT`.
- Performance, RLC, clock-gating, and power registers feed golden-register programming, runtime power policy, hang diagnostics, and GPU reset/recovery validation.

## Risks and Gotchas

- Manual edits are high risk. A wrong offset or `_BASE_IDX` compiles cleanly but can redirect MMIO to the wrong register, wrong hardware instance, or wrong indirect index.
- The chunk starts and ends mid-logical area. It starts after prior CP DMA/ME/coherency definitions and ends before the full DIDT DBR group is complete.
- `mm*` and `ix*` macros are different address spaces. Treating an indirect `ix*` value as a direct MMIO offset, or vice versa, would access the wrong hardware path.
- `_BASE_IDX` values are part of the SOC15 addressing contract. Dropping or changing base index `1` for this direct-register range can silently shift accesses into the wrong aperture.
- `GRBM_GFX_INDEX` changes the target of many subsequent accesses. Code using it must preserve broadcast/index semantics and honor existing locking or access-control conventions.
- Many registers are control or debug knobs, not simple status values. CP, RLC, power-gating, DIDT, clock-gating, DSM/debug, virtualization, and cache/TLB registers can affect command execution, reset behavior, power throttling, memory translation, or fault visibility.
- Some registers are counters, latched faults, clear-on-read, write-one-to-clear, or hardware-owned status in practice. The offset header does not encode access type, volatility, side effects, or reset semantics.
- Repeated aliases and same-offset aliases are intentional in generated register headers. For example, multiple `ixSQ_INTERRUPT_WORD_*` names share `0x20c0`; tooling should not treat this as a duplicate-generation bug without hardware context.
- Generated headers often have near-identical names across GC versions. Mixing GC 9.1 offsets with a different generation's shift/mask header can produce valid C with invalid hardware behavior.

## Test and Validation Signals

Useful validation is mostly build-time, static consistency, and hardware smoke coverage:

- Compile coverage for translation units that include `gc_9_1_offset.h`, especially `psp_v10_0.c` in this source tree.
- Static checks that every direct `mm*` define in this range has exactly one matching `_BASE_IDX` define, and that indirect `ix*` defines are not expected to have `_BASE_IDX` companions.
- Static comparison against the generated register database or adjacent GC 9.x headers for known shared offsets such as `mmCP_DMA_PFP_SRC_ADDR`, `mmGRBM_GFX_INDEX`, `mmGRBM_GFX_INDEX_SR_SELECT`, `mmGRBM_GFX_INDEX_SR_DATA`, `ixSQ_WAVE_STATUS`, and `ixDIDT_SQ_CTRL0`.
- Runtime GC 9.1 smoke on Raven/Picasso-class hardware covering PSP initialization, graphics ring setup, basic command submission, suspend/resume, GPU reset, and power-management transitions.
- Debug/hang-dump validation that SQ wave indirect reads return plausible wave status/PC/EXEC data and that DIDT/CAC/performance accesses use the correct indirect path.
- Fault and virtualization tests that exercise VMID/PASID/fault registers, ATC/UTCL2 invalidation, and RLC/GRBM virtualization controls without spurious protected-register or read/write errors.

## Chunk Boundary Notes

This is a chunk-only research document for `subset-b-002630`. It covers only lines 4993-7473 of `gc_9_1_offset.h`; it is not the final per-file report. The merge/reconciliation lane should combine this with preceding chunks for the earlier CP/SQ/etc. direct MMIO definitions and following chunks for the remainder of `didtind` and the file epilogue.

### subset-b-002631: lines 7474-7483

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_1_offset.h lines 7474-7483

## Purpose

This chunk closes the generated GC 9.1 register-offset header with DIDT stall-event counter register offsets and the final include-guard `#endif`. The relevant macros expose indexed (`ix`) offsets for Dynamic Inductive Droop Throttling telemetry counters in the graphics core:

- `ixDIDT_SQ_STALL_EVENT_COUNTER` at `0x00a0`
- `ixDIDT_DB_STALL_EVENT_COUNTER` at `0x00a1`
- `ixDIDT_TD_STALL_EVENT_COUNTER` at `0x00a2`
- `ixDIDT_TCP_STALL_EVENT_COUNTER` at `0x00a3`
- `ixDIDT_DBR_STALL_EVENT_COUNTER` at `0x00a4`

Lines 7474-7475 also show the immediately preceding DBR EDC telemetry offsets, which confirms this chunk belongs to the DIDT register block rather than ordinary memory-mapped `mm` GC registers.

## Important APIs, Types, And Data

The chunk contains only preprocessor constants. There are no C functions, structs, enums, or runtime APIs. The important API surface is the macro naming contract consumed by AMDGPU/PowerPlay register-access helpers:

- `ixDIDT_*` names identify indirect DIDT register offsets.
- The adjacent `gc_9_1_sh_mask.h` definitions describe these counter registers as a single full-width field: `DIDT_*_STALL_EVENT_COUNTER__DIDT_STALL_EVENT_COUNTER__SHIFT` is `0x0`, and the mask is `0xFFFFFFFFL`.
- The same mask header defines clear bits in `DIDT_SQ_CTRL0`, `DIDT_DB_CTRL0`, `DIDT_TD_CTRL0`, `DIDT_TCP_CTRL0`, and `DIDT_DBR_CTRL0` via `DIDT_STALL_EVENT_COUNTER_CLEAR` at bit 26.

The five blocks represented are shader queue (`SQ`), depth block (`DB`), texture data (`TD`), texture cache pipe (`TCP`), and depth block rasterizer (`DBR`) DIDT domains.

## Control Flow

There is no executable control flow in this header fragment. At compile time, users include this generated header to bind symbolic register names to literal offsets. Runtime control flow is introduced only by callers that pass these macros to SOC15/register-indexed accessors or table-driven PowerPlay programming sequences.

The closest local integration pattern appears in `drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_powertune.c`, where DIDT control-register masks are listed in tables used to clear stall-event counters. That file references the clear bits rather than these counter offsets directly, but it shows how the DIDT counter state is managed: control-register writes clear hardware counters; later reads of the counter offsets can report accumulated stall events.

## State And Persistence Behavior

The macros themselves are stateless and compile-time-only. The hardware registers they name are volatile 32-bit counters with default value `0x00000000` in related GC generation default headers. Counter state is owned by GPU hardware and persists only until reset, power-gating/reset sequences, or explicit clearing through the corresponding `DIDT_*_CTRL0__DIDT_STALL_EVENT_COUNTER_CLEAR` bit.

No software persistence, disk state, or memory-backed cache is implemented here. Any sampling layer must handle wraparound because the masks indicate 32-bit counters.

## Dependencies

This header depends on the generated ASIC register layout staying synchronized with the GC 9.1 hardware specification. Consumers depend on:

- `gc_9_1_offset.h` for offsets.
- `gc_9_1_sh_mask.h` for field masks and shifts.
- AMDGPU SOC15/register helper macros that know how to address GC blocks and indexed register spaces.
- PowerPlay/DPM code that enables DIDT and clears or samples stall counters during power tuning.

The offsets match nearby GC 9.x headers such as `gc_9_0_offset.h`, `gc_9_2_1_offset.h`, and `gc_9_4_2_offset.h`, where these counters occupy `0x00a0` through `0x00a4`. GC 10.x moves comparable counters to `0x00c0` and later, so callers must include the generation-appropriate offset header.

## Integration Points

The immediate integration point is the AMDGPU generated ASIC register include tree under `drivers/gpu/drm/amd/include/asic_reg/gc/`. Higher-level users include this header through GC 9.1-specific register definitions and use the symbolic macros to avoid hard-coded offsets.

Potential runtime users include:

- PowerTune/DIDT setup and diagnostics code that clears or samples stall counters.
- Debug or telemetry paths that read DIDT counters for SQ, DB, TD, TCP, and DBR throttling behavior.
- ASIC-specific initialization tables that compare GC 9.1 register definitions with masks/defaults from sibling generated headers.

## Risks

- Incorrect offsets would silently read or write the wrong indirect DIDT register and could corrupt power-management behavior or produce misleading telemetry.
- Cross-generation reuse is risky: GC 9.x and GC 10.x use different DIDT counter offsets.
- Counter reads need wraparound-aware handling because each field is a full 32-bit hardware counter.
- Clearing counters through the related `CTRL0` clear bits is a destructive operation for telemetry consumers; sampling code should avoid racing with power-management code that resets the same counters.
- Since this file is generated-style register metadata, manual edits can diverge from AMD's ASIC register source and should be treated cautiously.

## Test Signals

Useful validation signals are mostly build-time and hardware/runtime oriented:

- Compile coverage for GC 9.1 AMDGPU code that includes `gc_9_1_offset.h`.
- Static checks that each `ixDIDT_*_STALL_EVENT_COUNTER` offset has a matching `gc_9_1_sh_mask.h` field mask and clear bit in the matching `DIDT_*_CTRL0` register.
- Runtime register-read smoke tests on supported GC 9.1 hardware showing DIDT stall counters read as 32-bit values and reset to zero after the corresponding clear bit is exercised.
- Power-management regression tests that enable DIDT/PowerTune paths without invalid register-access errors.
