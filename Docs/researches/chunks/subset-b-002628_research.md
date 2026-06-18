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
