# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_offset.h lines 4983-7445

## Scope

This chunk is a generated AMD GPU GC 10.3.0 register-offset header slice. It contains 2,435 `#define` lines in the requested range: 1,217 visible register-offset macros plus 1,218 `_BASE_IDX` macros. The extra base-index macro is the first line of the chunk, `mmCP_HQD_IQ_RPTR_BASE_IDX`, whose matching offset definition is immediately before the chunk boundary.

The range starts inside the `gc_cpphqddec` queue descriptor block, then covers `gc_didtdec`, `gc_gccacdec`, `gc_tcpdec`, `gc_gdspdec`, `gc_gfxdec0`, `gc_gfxudec`, and the beginning of `gc_cprs64dec`. It ends at `mmCP_MES_GP5_LO_BASE_IDX`, so the MES general-purpose register sequence continues in a later chunk.

This file is declarative hardware metadata. There are no C functions, structs, enums, branches, loops, allocations, locks, or direct MMIO reads/writes in this range.

## Purpose

`gc_10_3_0_offset.h` gives AMDGPU code symbolic register numbers for the GC 10.3.0 graphics IP block. Runtime code combines these `mm...` constants with SOC15 register helpers such as `SOC15_REG_OFFSET`, `WREG32_SOC15`, `RREG32_SOC15`, and offset variants to address the correct MMIO register for queue management, GDS partitioning, graphics context programming, counters, scratch registers, and MES control.

Although this repository path is under `sources/distributed-fs/ceph-client`, the source is AMDGPU DRM driver metadata, not distributed filesystem or Ceph logic.

## Exported API Surface

The public surface is a generated preprocessor namespace:

- `mm<REGISTER>` defines the register's offset inside its decoded GC address block.
- `mm<REGISTER>_BASE_IDX` selects the SOC15 base-index slot used by register access helpers. In this chunk, early CP/GDS/DIDT/CAC/TCP registers use base index `0`; graphics context, user/config, GDS atomics/remap, and MES registers use base index `1`.

Major register families in the chunk are:

- `mmCP_HQD_*`, `mmCP_MQD_*`, and `mmCP_HPD_*`: compute hardware queue descriptor, memory queue descriptor, pipe/queue priority, dequeue/offload, AQL, EOP, context-save, pointer, DDID, scheduler, and status offsets. The chunk begins after the `mmCP_HQD_IQ_RPTR` offset and includes only its base-index line.
- `mmDIDT_*`: indexed DIDT access registers and auto-increment control.
- `mmGC_CAC_*`, `mmGC_EDC_*`, `mmGC_THROTTLE_*`, `mmEDC_*`, `mmPCC_*`, `mmPWRBRK_*`, `mmGC_CAC_IND_*`, and `mmSE_CAC_IND_*`: clock/power/current/EDC/throttle and indirect CAC register surfaces.
- `mmTCP_*`: texture cache pipe watchpoint address/control registers, UTCL status, and performance-counter filters.
- `mmGDS_*`: VMID base/size tables, GWS and ordered-append VMID mappings, reset masks, context-switch counters, resource state, atomics, reads/writes, GWS resources, OA counters, and GDS memory cleanup.
- `mmDB_*`, `mmCB_*`, `mmPA_*`, `mmVGT_*`, `mmSPI_*`, `mmSX_*`, `mmTA_*`, `mmIA_*`, `mmGE_*`, `mmWD_*`, `mmCOHER_*`, and `mmCONTEXT_*` in `gc_gfxdec0`: depth/color backend, primitive assembly, scissor/viewport, clipping, streamout, shader interpolation/resource, rasterization, and context-state offsets used by graphics pipelines.
- `mmCP_*`, `mmSCRATCH_*`, `mmSQ_THREAD_TRACE_*`, `mmRLC_GPM_*`, `mmUCONFIG_*`, `mmSQC_*`, and additional `mmGDS_*` in `gc_gfxudec`: command processor counters, EOP/fence/append data, streamout and pipeline statistics, scratch registers, atomics, indirect buffers, wait/dispatch/draw state, thread trace control, and user/config-space GDS access.
- `mmCP_MES_*`: MES program counter, trap/vector, interrupt, scratch, instruction pointer, RISC-V-style machine CSRs, cycle/time/instret counters, doorbell controls, process quantum, debug interrupt pointer, and general-purpose register halves.

## Address Blocks Covered

The chunk covers these generated address-block declarations and visible register counts:

- Continuation of `gc_cpphqddec` at base `0xc800`: 43 visible register-offset definitions, plus the dangling `mmCP_HQD_IQ_RPTR_BASE_IDX` from the previous register.
- `gc_didtdec` at base `0xca00`: 3 offsets.
- `gc_gccacdec` at base `0xca10`: 24 offsets.
- `gc_tcpdec` at base `0xca80`: 16 offsets.
- `gc_gdspdec` at base `0xcc00`: 92 offsets.
- `gc_gfxdec0` at base `0x28000`: 641 offsets.
- `gc_gfxudec` at base `0x30000`: 328 offsets.
- `gc_cprs64dec` at base `0x32000`: 70 offsets in this chunk, with more MES registers expected after the boundary.

The largest region is `gc_gfxdec0`, where repeated viewport, scissor, color target, blend, streamout, and shader/geometry setup registers dominate the range. `gc_gfxudec` then switches to CP-visible counters, scratch, atomics, dispatch/draw, GDS, and remap/user-data style registers.

## Control Flow And State Behavior

There is no local control flow. Runtime behavior is introduced by driver code that includes this header, selects a GC instance/base via SOC15 helpers, and performs MMIO reads or writes using the generated constants.

The hardware state named by this chunk includes:

- Compute queue state: HQD active state, VMID, queue priority, quantum, packet queue base/read/write pointers, doorbell control, indirect-buffer pointers, dequeue/offload requests, EOP buffers, context-save locations, suspend offsets, error/status registers, and DDID counters.
- Power and telemetry state: DIDT indirect indexes/data, CAC aggregate and soft controls, EDC thresholds/status/overflow/rolling power delta, throttle controls/status, and performance counters.
- Texture-cache debug state: TCP watchpoints, UTCL status, and performance-counter filtering.
- GDS state: per-VMID GDS base/size allocation, GWS/OA ownership, resource resets, context-switch counters, memory-clean controls, atomics, ordered-append ring controls, and per-resource counters.
- Graphics pipeline context state: depth/stencil control and base addresses, color target masks/bases/views/DCC/compression, scissor and viewport rectangles, viewport depth ranges, raster config, primitive assembly limits, streamout controls, shader stage resource/user-data pointers, interpolation/barycentric settings, and geometry/NGG controls.
- Command processor and user/config state: EOP done/fence addresses, primitive/shader invocation counters, pipe statistics, streamout addresses, scratch registers, atomic preop registers, append/fence data, indirect-buffer tracking, wait/draw/dispatch state, thread-trace controls, and GDS atomic/read/write windows.
- MES microcontroller state: program and trap vectors, interrupts, scratch/indexed scratch, instruction pointer, machine status/cause/bad-address/IP registers, cycle/time/instret counters, machine identity registers, cache op controls, timer compare, doorbells, and general-purpose register halves.

Persistence is entirely hardware-defined. The header does not encode reset values, access permissions, sticky status semantics, write-one-to-clear behavior, self-clearing bits, privilege requirements, power-domain validity, or ordering constraints. Related `gc_10_3_0_default.h` and `gc_10_3_0_sh_mask.h` files provide defaults and bitfields, while actual sequencing lives in AMDGPU runtime code and firmware.

## Dependencies And Integration Points

The syntactic dependency is only the C preprocessor. Semantically, this chunk must stay synchronized with the GC 10.3.0 register database, the companion `gc_10_3_0_sh_mask.h` bitfield header, and `gc_10_3_0_default.h` reset/default values.

Direct include sites in this tree include:

- `drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v10_3.c`, which uses this header for KFD compute queue setup, VMID/PASID mapping support, interrupt setup, queue dequeue, HQD loading/dumping, and SRBM-selected queue access.
- `drivers/gpu/drm/amd/amdgpu/sdma_v5_2.c`, `gfxhub_v2_1.c`, and shared SDMA/GFX paths that include matching GC 10.3.0 register metadata.
- `drivers/gpu/drm/amd/pm/swsmu/smu11/vangogh_ppt.c`, which includes the GC offset and mask headers for power-management interactions on Vangogh-family hardware.

Common integration mechanisms are `SOC15_REG_OFFSET(GC, inst, mm...)`, `WREG32_SOC15`, `RREG32_SOC15`, `WREG32_SOC15_OFFSET`, and SRBM/GRBM selection for per-queue or per-VMID registers. Several offsets in this chunk are also accessed by adding small register strides, such as per-VMID GDS base/size tables and repeated color/viewport/scissor/counter families.

## Risks And Edge Cases

- Generated-header drift is the central risk. A wrong offset or base index can compile cleanly while reading or writing the wrong MMIO register.
- The first line is a chunk-boundary fragment: `mmCP_HQD_IQ_RPTR_BASE_IDX` belongs with an offset macro in the previous chunk. Merge logic should not treat this as an orphan in the full file.
- The last visible MES register, `mmCP_MES_GP5_LO`, is not the end of the MES register set. Later chunks should continue the GP register sequence and any remaining `gc_cprs64dec` definitions.
- Register aliases share offsets, such as HQ scheduler/status and DMA/offload names in the HQD region, or scratch/atomic and append/fence low-word aliases in `gc_gfxudec`. Consumers must preserve the intended semantic name for the operation being performed.
- Base index matters. Mixing index `0` queue/GDS telemetry offsets with index `1` graphics/user/MES offsets can point access helpers at the wrong address aperture.
- Many registers are sequencing-sensitive. Queue dequeue/offload, MQD/HQD programming, context-save/suspend pointers, EOP buffers, GDS VMID allocation, and MES doorbells require driver/firmware ordering outside this header.
- Address pairs and high/low halves are common. Partial writes to 64-bit addresses, counters, fences, append data, MES CSRs, or GDS atomics can create inconsistent hardware-visible state.
- Context registers are often packet-programmed by command streams rather than arbitrary CPU MMIO writes. Incorrect direct writes can desynchronize command processor state, shadow state, or per-context programming.
- Status and control surfaces are represented the same way as macros. The header does not distinguish read-only status, clear-on-read, write-one-to-clear, privileged, debug-only, or reserved registers.

## Test Signals

Useful validation is primarily build-time, generation-time, and hardware-integration oriented:

- Compile AMDGPU configurations that include GC 10.3.0, KFD, SMU11/Vangogh, SDMA v5.2, and GFXHUB v2.1 paths. Missing or renamed macros should fail at include or register-table use sites.
- Mechanically compare the full `gc_10_3_0_offset.h` against the authoritative register database and the companion `gc_10_3_0_sh_mask.h`/`gc_10_3_0_default.h` files.
- Verify that every visible `mm...` offset in this chunk has a matching `_BASE_IDX`, allowing the known boundary case for `mmCP_HQD_IQ_RPTR`.
- Exercise KFD compute queue creation, MQD/HQD load, queue drain/reset/save, context save/restore, suspend/resume, and queue teardown on GC 10.3.0 hardware.
- Exercise GDS allocation and release across VMIDs, GWS/OA usage, ordered append, GDS atomics, and context-switch accounting.
- Run graphics workloads that stress depth/stencil, color targets, DCC, scissor/viewport arrays, streamout, geometry/tessellation/NGG, shader resource programming, and draw/dispatch CP paths.
- Validate counters and diagnostics: primitive/shader invocation counters, pipe statistics, scratch registers, thread trace, TCP watchpoints, CAC/EDC/throttle telemetry, and MES debug/interrupt state.
- Include suspend/resume, GPU reset, power-gating, and firmware reload tests to catch persistence assumptions around HQD/MQD, GDS, CP fences, scratch, and MES registers.

## Chunk Notes For Merge

This document intentionally covers only lines 4983-7445 of `gc_10_3_0_offset.h`. The previous chunk should provide the beginning of `gc_cpphqddec` and the `mmCP_HQD_IQ_RPTR` offset. The next chunk should continue `gc_cprs64dec` after `mmCP_MES_GP5_LO_BASE_IDX`. The final per-file research should treat the whole file as generated GC 10.3.0 offset metadata paired with mask/default headers, not as standalone runtime logic.
