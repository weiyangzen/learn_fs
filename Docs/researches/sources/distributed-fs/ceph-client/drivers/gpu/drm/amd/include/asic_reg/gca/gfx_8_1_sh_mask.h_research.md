# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gca/gfx_8_1_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002721`: lines 1-4615, `Docs/researches/chunks/subset-b-002721_research.md`
- `subset-b-002722`: lines 4616-9227, `Docs/researches/chunks/subset-b-002722_research.md`
- `subset-b-002723`: lines 9228-13901, `Docs/researches/chunks/subset-b-002723_research.md`
- `subset-b-002724`: lines 13902-19048, `Docs/researches/chunks/subset-b-002724_research.md`
- `subset-b-002725`: lines 19049-21368, `Docs/researches/chunks/subset-b-002725_research.md`

## Chunk Research

### subset-b-002721: lines 1-4615

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gca/gfx_8_1_sh_mask.h lines 1-4615

## Scope

This chunk is the opening slice of the generated AMD GFX 8.1 shift/mask register header. It contains the MIT-style AMD copyright header, include guard, and 4,590 `#define` entries through line 4615. The macro convention is the generated AMD register style:

- `REGISTER__FIELD_MASK` gives the 32-bit mask for a register field.
- `REGISTER__FIELD__SHIFT` gives the bit shift for the same field.

Within the requested range there are 644 distinct generated register names, dominated by 1,780 `CB*` color-buffer definitions and 2,629 `CP*` command-processor definitions. The range starts with complete color-buffer blend/render-target state and then moves into command processor ring, interrupt, queue, DMA, coherency, performance, and HQD/MQD queue-management state. It ends at `CP_HQD_HQ_STATUS1__STATUS_MASK`; the matching `__SHIFT` and following HQD EOP fields are outside this chunk.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU DRM hardware metadata. It does not implement Ceph or distributed filesystem logic.

## Purpose

`gfx_8_1_sh_mask.h` is a compile-time hardware ABI description for GFX 8.1-class AMD graphics blocks. Driver code uses these constants to compose, preserve, or decode fields in 32-bit MMIO registers and command processor state. The constants are intentionally declarative: they encode bit positions and masks, while runtime code supplies register offsets, values, ordering, and access methods.

This chunk covers two major hardware surfaces:

- Color Buffer (`CB`) register fields for blend constants, blend control, render-target base addresses, tile pitch/slice/view layout, color format metadata, CMASK/FMASK/DCC metadata, target masks, shader export masks, CB hardware controls, CB performance counters, clock-gating control, and CB debug buses.
- Command Processor (`CP`, `CPC`, `CPG`, `CPF`, `COHER`, `SCRATCH`) fields for ring buffers, read/write pointers, interrupts, doorbells, microcode ports, clock/power controls, MEC pipe status, performance counters, EOP/fence/stat counters, scratch and append data, atomics, semaphores, coherency, DMA, indirect buffers, stalled/busy/status diagnostics, and the beginning of HQD/MQD queue state.

## Important API Surface

There are no C functions, structs, enums, inline helpers, global variables, or callbacks in this chunk. The macro namespace is the exported API.

Important color-buffer families include:

- `CB_BLEND_RED/GREEN/BLUE/ALPHA`, `CB_COLOR_CONTROL`, and `CB_BLEND0_CONTROL` through `CB_BLEND7_CONTROL`, which describe blend constants, ROP mode, source/destination blend factors, color/alpha combine functions, separate-alpha blending, per-target blend enable, and ROP3 disable bits.
- `CB_COLOR0_BASE` through `CB_COLOR7_BASE`, `CB_COLORn_PITCH`, `CB_COLORn_SLICE`, and `CB_COLORn_VIEW`, which describe render-target base addresses and tile/slice/view bounds.
- `CB_COLORn_INFO`, which packs endian, format, number type, component swap, fast clear, compression, blend clamp/bypass, simple float, round mode, CMASK layout, blend optimization hints, FMASK compression policy, DCC enable, and CMASK address type for each MRT slot.
- `CB_COLORn_ATTRIB`, `CB_COLORn_DCC_CONTROL`, `CB_COLORn_CMASK`, `CB_COLORn_FMASK`, `CB_COLORn_CLEAR_WORD0/1`, and `CB_COLORn_DCC_BASE`, which define tiling, sample/fragment count, destination alpha forcing, DCC block sizing, key clear, color transform, lossy precision, and metadata surface base/clear state.
- `CB_TARGET_MASK` and `CB_SHADER_MASK`, which provide per-target/per-output component enables for render-target writes and shader exports.
- `CB_HW_CONTROL`, `CB_HW_CONTROL_1`, `CB_HW_CONTROL_2`, `CB_HW_CONTROL_3`, and `CB_DCC_CONFIG`, which tune or disable internal CB optimizations, cache eviction points, FIFO depths, overwrite-combiner behavior, DCC cache sizing, and documented hardware workaround bits.
- `CB_PERFCOUNTER_FILTER`, `CB_PERFCOUNTER*_SELECT`, `CB_PERFCOUNTER*_LO/HI`, `CB_CGTT_SCLK_CTRL`, and `CB_DEBUG_BUS_1` through `CB_DEBUG_BUS_22`, which expose CB profiling, clock-gating, busy, stall, compression, fragment, cache, and internal handshake status fields.

Important command-processor families include:

- `CP_DFY_*` data/address/command/status fields for the DFY block, including policy, memory type, LFSR reset, mode, enable, address, data lanes, offset, size, busy, and pending-tag state.
- `CP_RB*` and `CP_RB*_CNTL` fields for graphics ring buffer base, high address, buffer/block sizing, memory type, byte swap, minimum availability, cache policy, no-update mode, and read-pointer writeback enable.
- `CP_RB*_RPTR_ADDR*`, `CP_RB*_WPTR`, `CP_RB_WPTR_POLL_ADDR*`, `CP_RB_DOORBELL_CONTROL`, and doorbell range fields, which connect software ring pointers and doorbells to CP scheduling.
- `CP_INT_CNTL`, `CP_INT_CNTL_RING0/1/2`, `CP_INT_STATUS`, `CP_INT_STATUS_RING0/1/2`, `CPC_INT_CNTL`, `CP_MEx_PIPEn_INT_CNTL`, and matching status/debug families. These define interrupt enables/status for VM doorbells, ECC, wait-reg-mem timeouts, context busy/empty, gfx idle, privileged instruction/register access, opcode errors, timestamps, reserved-bit errors, dequeue requests, query status, and SUA violations.
- `CP_DEVICE_ID`, priority counters, pipe priorities, VMID, endian, microcode address/data ports, clock-gating controls, power controls, memory sleep controls, ECC first-occurrence fields, and write-pointer polling controls.
- `CP_CPC_STATUS`, `CP_CPC_BUSY_STAT`, `CP_CPF_STATUS`, `CP_CPF_BUSY_STAT`, `CP_STALLED_STAT*`, `CP_BUSY_STAT`, `CP_STAT`, `CP_CNTX_STAT`, and related free-count/header-dump fields. These are diagnostic fields for CP/CPC/CPF/MEC state machines, busy sources, stalls, queue availability, and command fetch state.
- `CP_CE/PFP/ME/MEC*_PRGRM_CNTR_START` and interrupt routine start fields, context control, wait timers, VMID reset/preempt/status, instruction cache base/control fields, and MEC halt/step/reset controls.
- `CPG_PERFCOUNTER*`, `CPC_PERFCOUNTER*`, and `CPF_PERFCOUNTER*` selector/data fields for command processor performance monitoring.
- `CP_EOP_DONE_*`, stream-out, primitive count, pipe stats, scratch registers, append/fence registers, atomic pre-operation registers, CP memory read/write address/data registers, semaphore wait/signal fields, and wait-reg-mem timeout fields.
- `CP_COHER_CNTL`, `CP_COHER_*`, and `COHER_DEST_BASE*`, which describe cache/coherency action bits for TC, TCL1, CB, DB, shader caches, destination-base windows, coherency size/base, and coherency status.
- `CP_DMA_ME_*`, `CP_DMA_PFP_*`, `CP_DMA_CNTL`, and `CP_DMA_READ_TAGS`, which describe CP DMA source/destination addresses, memory type, ATC/cache policy, source/destination selection, byte count, endian swap, address increment controls, raw wait, FIFO status, and read-tag validity.
- `CP_PFP_IB_CONTROL`, `CP_PFP_LOAD_CONTROL`, IB/RB/CE offsets, IB base/buffer-size fields, metadata bases, indirect draw/dispatch bases, index base/type, GDS backup base, sample status, ROQ/STQ/MEQ/CEQ thresholds and availability, and command index/data fields.
- `CP_HPD_*`, `CP_MQD_BASE_ADDR*`, `CP_HQD_ACTIVE`, `CP_HQD_VMID`, `CP_HQD_PERSISTENT_STATE`, `CP_HQD_PQ_*`, `CP_HQD_IB_*`, `CP_HQD_IQ_TIMER`, dequeue/offload/semaphore/message fields, HQD atomic preops, and the first HQ scheduler/status/control fields. These are queue and memory queue descriptor fields used by compute/graphics queue management.

## Control Flow

The header has no executable control flow. Its only compile-time flow is C preprocessor inclusion guarded by `GFX_8_1_SH_MASK_H`.

The implied runtime flow in consumers is:

1. ASIC-specific driver code includes this generated shift/mask header and the matching register address/value definitions used by that code path.
2. A caller selects a register, often through generated `reg*` symbols, packet definitions, or a ring/MMIO register table.
3. The caller uses helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, direct mask/shift operations, SOC15-style MMIO helpers, or command packet emission to pack or decode a register value.
4. Hardware state is written, read, polled, or interpreted by AMDGPU/KFD queue, graphics, interrupt, profiling, debug, or reset logic.

Loops and branching are therefore outside this file. Repeated families such as `CB_COLOR0..7`, `CB_BLEND0..7`, `CP_RB0..2`, `CP_ME1/ME2_PIPE0..3`, and `CP_HQD_*` imply indexed driver logic, but this chunk only provides the bit layout each iteration would use.

## State And Persistence Behavior

The macros themselves are stateless compile-time constants. The state they describe is persistent hardware state until changed by command submission, MMIO writes, firmware, context save/restore, power management, reset, or hardware progress.

CB render-target fields are graphics context state. Surface base addresses, tile dimensions, view ranges, formats, compression flags, CMASK/FMASK/DCC metadata bases, clear words, target masks, shader masks, and blend controls can persist across draws in a context until the command stream or context restore changes them. Incorrect fields can corrupt render-target memory or produce valid-looking but wrong pixels.

CB hardware-control, DCC, debug, clock-gating, and performance-counter fields are lower-level configuration or observation state. Some values tune internal FIFOs, cache tags, overwrite combiners, and workarounds. Debug bus and performance counter registers reflect live hardware conditions and may change while being sampled.

CP ring and queue fields represent active command-submission state: ring base addresses, read/write pointers, doorbell range/control, pointer polling, queue priorities, VMID assignment, HQD active state, PQ/IB/IQ pointers, dequeue requests, and persistent-state bits. These values affect which command buffers hardware consumes and which VMID/queue owns execution.

CP interrupt, status, stalled, busy, and ECC fields describe hardware-reported state. Some bits may be sticky, write-one-to-clear, latched, or read-clear according to the hardware spec, but that access policy is not encoded in this header.

Coherency, semaphore, DMA, EOP, append, atomic, scratch, and indirect-buffer fields describe command processor side effects and synchronization surfaces. Values can point at GPU memory, trigger cache actions, report fence/completion data, control waits, or drive CP DMA transfers. Ordering, alignment, and timeout rules are properties of the consuming code and hardware, not the macro definitions.

## Dependencies And Integration Points

This file depends syntactically only on the C preprocessor. Semantically, it depends on AMD's generated GFX 8.1 register database and must remain synchronized with the corresponding register address and enum/value definitions. In this source tree the immediate sibling `gfx_8_1_enum.h` provides generated field values, while this header provides bit masks and shifts.

A direct include search in the current mirror found only the header itself, so this specific GFX 8.1 `gca` header may be retained generated inventory rather than an actively included path in the mirrored kernel subset. The macro names still match the standard AMDGPU/KFD register-helper pattern used throughout nearby ASIC generations.

Integration points for the macro contract include:

- AMDGPU register helper macros such as `REG_SET_FIELD` and `REG_GET_FIELD`, which rely on the `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT` naming convention.
- MMIO and command-submission paths that write registers or packet payloads for CB render state, CP ring setup, interrupt enables, queue descriptors, coherency actions, EOP/fence reporting, and DMA/semaphore commands.
- KFD/MQD queue-management code patterns that populate `cp_hqd_pq_control`, HQD VMID, PQ/IB bases, doorbell controls, and persistent-state fields using the same CP_HQD macro families in VI and later ASIC managers.
- Profiling and debug paths that select and sample CB/CP/CPC/CPG/CPF performance counters, stalled/busy/status fields, debug bus outputs, and header dumps.
- Reset, suspend/resume, firmware, and bring-up paths that must restore or reinitialize ring buffers, microcode ports, CP power/clock settings, interrupt masks, VMID state, and queue descriptors.

## Risks And Edge Cases

- Bitfield drift is the central risk. A wrong mask or shift compiles normally but can program unrelated hardware bits, causing rendering corruption, queue hangs, lost interrupts, bad cache coherency, or misleading diagnostics.
- This chunk is boundary-partial. It includes the include guard as a `#define`, and it ends with only `CP_HQD_HQ_STATUS1__STATUS_MASK`; the matching shift and later HQD EOP fields are in the next chunk.
- Repeated register families are vulnerable to one-slot copy or generation errors. CB slots 0-7, blend controls 0-7, ME pipe interrupt blocks, ring buffer variants, and HQD queue fields can fail only on specific targets or queues.
- Address fields often encode aligned addresses, not raw byte pointers. Examples include 256-byte color/DCC/CMASK/FMASK bases, 4-byte or 8-byte-aligned CP pointer/report addresses, and high/low address splits. Consumers must preserve required alignment and high bits.
- Reserved and workaround-style fields such as `CHICKEN_BITS`, `RESERVED`, `OBSOLETE`, `RSV_*`, and generated typo-compatible names must not be cleaned up casually. Renaming a generated macro can break consumers even when the name looks wrong.
- CP coherency, DMA, semaphore, EOP, and wait fields are sequencing-sensitive. This header does not encode required fences, polling loops, timeout policy, cache flush ordering, or engine ownership.
- Status and control fields are interleaved in the same namespace. Debug/status names may be passive reads, while reset, halt, step, dequeue, offload, interrupt-enable, cache-action, or DMA command bits can have side effects.
- Low/high counter pairs and live status registers can race hardware updates. The header gives field positions only; coherent sampling requires caller-side latching or retry logic.

## Test And Validation Signals

- Build coverage should compile any active AMDGPU/KFD paths that include the GFX 8.1 generated headers or use same-generation generated macro names. Missing or renamed macros should fail at compile time.
- Generated-data validation should compare all line 1-4615 definitions with AMD's authoritative GFX 8.1 register database, including mask/shift pairing, mask alignment to shift, and repeated-family completeness.
- Boundary validation should verify that `CP_HQD_HQ_STATUS1__STATUS_MASK` is intentionally unpaired in this chunk and paired by the following chunk before final per-file reconciliation.
- Graphics runtime testing should cover multi-render-target blending, ROP modes, color write masks, shader export masks, fast clears, DCC, CMASK/FMASK, MSAA sample/fragment layouts, mip/slice views, and context restore.
- CP runtime testing should cover ring initialization, read/write pointer reporting, doorbell writes, interrupt enable/status paths, privileged/opcode error handling, VMID reset/preempt, MEC pipe scheduling, and queue priority behavior.
- Synchronization and memory tests should exercise CP coherency packets, EOP fence writes, append/fence registers, wait-reg-mem, signal/wait semaphores, atomics, and CP DMA transfers while watching for hangs, stale data, or timeout interrupts.
- Profiling/debug validation should program CB and CP/CPC/CPG/CPF performance counters, read low/high counter pairs, inspect stalled/busy/status registers, and compare results against known workloads or hardware traces.
- Power-management and recovery tests should cover suspend/resume, GPU reset, CP microcode reload, clock/power gating, memory sleep controls, and queue teardown/restart, because many fields in this chunk persist until explicitly restored.

## Cross-Chunk Notes

This first chunk starts at the beginning of `gfx_8_1_sh_mask.h` and contains complete CB render-target state plus a large but not complete CP block. The next chunk should continue at `CP_HQD_HQ_STATUS1__STATUS__SHIFT` and then cover the remaining HQD EOP/queue-management definitions. The merge lane should join these artificial chunk boundaries before making any final statement about complete HQD/MQD coverage for the full source file.

### subset-b-002722: lines 4616-9227

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gca/gfx_8_1_sh_mask.h lines 4616-9227

## Scope

This chunk is a large middle slice of the generated AMD GFX 8.1 shift/mask register header. It contains C preprocessor constants only: each hardware register field is represented by `<REGISTER>__<FIELD>_MASK` and `<REGISTER>__<FIELD>__SHIFT` macros used to compose or decode 32-bit MMIO register values.

The range starts in the middle of command-processor HQD queue status/control definitions and then covers 713 distinct register macro families across these blocks:

- CP HQD end-of-pipe, context-save, GDS-resource, and queue error/status fields.
- DB depth/stencil surface, render, query, debug, performance counter, watermark, and cache/FIFO fields.
- CC/GC/GB render-backend redundancy, address configuration, tile-mode, macrotile-mode, and EDC/RAS signature fields.
- GRBM status, indexing, traps, read/write errors, soft reset, debug, scratch, and performance counter fields.
- PA_CL, PA_SU, and PA_SC viewport, clipping, point/line, polygon offset, rasterization, scissor, sample-location, trap-screen, debug, and performance counter fields.
- Clipper, SXIFCCG, and setup debug-register fields.
- Compute dispatch, program-resource, thread-management, wave-restore, user-data, CSPRIV connection, and thread-trace fields.
- RLC control, safe mode, memory sleep, clocking, performance monitoring, load-balance, GPM debug/microcode, GPU BIST, and the beginning of `RLC_ROM_CNTL`.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU DRM hardware metadata. It has no Ceph or distributed filesystem behavior.

## Purpose

`gfx_8_1_sh_mask.h` is the bit-layout companion to the GFX 8.1 register-offset headers. Offset headers identify registers such as `DB_DEPTH_CONTROL`, `GRBM_GFX_INDEX`, `PA_SC_RASTER_CONFIG`, `COMPUTE_PGM_RSRC1`, and `RLC_CNTL`; this header identifies the fields inside those registers.

Driver code uses these definitions through common AMDGPU/KFD helper patterns such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32`, `WREG32`, SOC15-era read/write wrappers in newer code, packet emission helpers, register dump code, and performance/debug tooling. The macros are the hardware ABI for GFX 8.1-era blocks: changing a mask or shift changes which hardware bits are read or written.

## Important Macro Families

### CP HQD Queue And EOP State

The opening CP section covers hardware queue descriptor fields for the command processor:

- `CP_HQD_HQ_STATUS1` and `CP_HQD_HQ_CONTROL1` expose full-width HQ status/control words.
- `CP_HQD_EOP_BASE_ADDR`, `CP_HQD_EOP_BASE_ADDR_HI`, `CP_HQD_EOP_CONTROL`, `CP_HQD_EOP_RPTR`, `CP_HQD_EOP_WPTR`, `CP_HQD_EOP_EVENTS`, `CP_HQD_EOP_WPTR_MEM`, and `CP_HQD_EOP_DONES` describe the end-of-pipe ring base, ring sizing, memory type/cache policy, read/write pointers, availability, event counts, and done counts.
- `CP_HQD_CTX_SAVE_*`, `CP_HQD_CNTL_STACK_*`, `CP_HQD_WG_STATE_OFFSET`, and `CP_HQD_CTX_SAVE_SIZE` define context-save backing storage and stack/state offsets.
- `CP_HQD_GDS_RESOURCE_STATE` tracks ordered-append/GWS requirements and allocation state for queues.
- `CP_HQD_ERROR` decodes HQD error status such as EDC and SUA error bits.

These fields integrate with KFD/amdgpu queue management and compute ring execution. The header does not describe the required queue suspend, drain, context-save, or EOP polling sequence; it only provides the bit positions used by that code.

### DB Depth, Stencil, Queries, And Debug

The DB block is the largest early section in the chunk. It defines depth and stencil surface programming:

- `DB_Z_READ_BASE`, `DB_STENCIL_READ_BASE`, `DB_Z_WRITE_BASE`, and `DB_STENCIL_WRITE_BASE` are full-width base-address fields in the hardware's expected alignment units.
- `DB_DEPTH_INFO`, `DB_Z_INFO`, `DB_STENCIL_INFO`, `DB_DEPTH_SIZE`, `DB_DEPTH_SLICE`, and `DB_DEPTH_VIEW` describe array mode, pipe/bank layout, tile split, format, sample count, compression/multisample state, pitch/height, slice range, and mip level.
- `DB_RENDER_CONTROL`, `DB_COUNT_CONTROL`, `DB_RENDER_OVERRIDE`, `DB_RENDER_OVERRIDE2`, `DB_EQAA`, `DB_SHADER_CONTROL`, `DB_DEPTH_CONTROL`, `DB_STENCIL_CONTROL`, and `DB_ALPHA_TO_MASK` define render policy, z/stencil compare behavior, hierarchical Z/stencil controls, EQAA sample/fragment rules, shader export interactions, alpha-to-mask behavior, and override/debug disables.
- `DB_DEPTH_BOUNDS_MIN/MAX`, `DB_STENCIL_CLEAR`, `DB_DEPTH_CLEAR`, `DB_HTILE_DATA_BASE`, `DB_HTILE_SURFACE`, `DB_PRELOAD_CONTROL`, `DB_STENCILREFMASK`, and `DB_STENCILREFMASK_BF` encode clear/reference/mask and HTILE metadata state.
- `DB_OCCLUSION_COUNT*`, `DB_ZPASS_COUNT_*`, and `DB_SRESULTS_COMPARE_STATE*` provide query/comparison counter fields.

The same block includes DB performance counters (`DB_PERFCOUNTER*_SELECT`, `*_SELECT1`, `*_LO`, `*_HI`), deep debug controls (`DB_DEBUG` through `DB_DEBUG4`), credit/watermark/cache controls, FIFO depths, clock-gating delay controls, ring control, and read-debug windows. Many of these are active hardware state or debug override knobs, not passive metadata.

### Render Backend, Addressing, Tile Modes, And RAS

The `CC_*`, `GC_USER_*`, `GB_*`, and `RAS_*` families describe chip-level graphics backend layout:

- `CC_RB_REDUNDANCY`, `CC_RB_BACKEND_DISABLE`, `GC_USER_RB_REDUNDANCY`, and `GC_USER_RB_BACKEND_DISABLE` expose render-backend disable/redundancy maps.
- `GB_ADDR_CONFIG` and `GB_BACKEND_MAP` describe pipe, bank, shader-engine, render-backend, row-size, and backend mapping fields used by surface/tile programming.
- `GB_TILE_MODE0` through `GB_TILE_MODE31` and `GB_MACROTILE_MODE0` through `GB_MACROTILE_MODE15` encode array mode, pipe config, tile split, micro tile mode, sample split, bank dimensions, macro aspect, and bank swizzle.
- `GB_EDC_MODE`, `CC_GC_EDC_CONFIG`, `RAS_SIGNATURE_CONTROL`, `RAS_SIGNATURE_MASK`, and the per-block `RAS_*_SIGNATURE*` registers expose EDC/RAS signature collection for SX, DB, PA/VGT/SC/IA/SPI/TA/TD/CB/BCI-style blocks.

These definitions are consumed by initialization, surface layout, diagnostics, and RAS paths. Incorrect values can corrupt tiling interpretation or hide/trigger backend and error-reporting behavior.

### GRBM Global Graphics Manager

The GRBM section spans status, routing, reset, trap, error, scratch, and profiling fields:

- `GRBM_HYP_CAM_INDEX`, `GRBM_CAM_INDEX`, `GRBM_*_CAM_DATA`, `GRBM_CNTL`, `GRBM_SKEW_CNTL`, and `GRBM_PWR_CNTL` configure low-level graphics-manager indexing, skew, and power controls.
- `GRBM_STATUS`, `GRBM_STATUS2`, and `GRBM_STATUS_SE0..SE3` expose busy/clean/active status across CP, VGT, IA, PA, SC, SPI, SX, DB, CB, GUI_ACTIVE, TAs, and per-shader-engine resources.
- `GRBM_SOFT_RESET`, `GRBM_DEBUG_CNTL`, `GRBM_DEBUG_DATA`, `GRBM_DEBUG`, `GRBM_DEBUG_SNAPSHOT`, `DEBUG_INDEX`, and `DEBUG_DATA` provide reset and debug access.
- `GRBM_GFX_INDEX` selects shader engine, shader array, instance, and broadcast routing for indexed register accesses.
- `GRBM_READ_ERROR`, `GRBM_READ_ERROR2`, `GRBM_WRITE_ERROR`, `GRBM_INT_CNTL`, and `GRBM_TRAP_*` decode MMIO access errors and trap address/data windows.
- `GRBM_PERFCOUNTER*` and `GRBM_SE*_PERFCOUNTER*` configure and read global/per-SE GRBM counters.
- `GRBM_SCRATCH_REG0..7`, `GRBM_NOWHERE`, and related full-width data fields provide scratch and discard/write sink registers.

GRBM fields are sensitive integration points because register routing and reset controls affect all graphics blocks behind GRBM. Callers must preserve broadcast/index state around per-instance register access and must not treat status/error registers as ordinary persistent configuration.

### PA_CL, PA_SU, And PA_SC Graphics Pipeline State

The PA block dominates the middle of the chunk and represents graphics viewport, clipping, setup, and rasterization state:

- `PA_CL_VPORT_*` defines viewport scale/offset for viewport 0 plus indexed viewport 1 through 15 variants.
- `PA_CL_VTE_CNTL`, `PA_CL_VS_OUT_CNTL`, `PA_CL_NANINF_CNTL`, `PA_CL_CLIP_CNTL`, guard-band adjustment registers, and `PA_CL_UCP_*` define viewport transform enable, vertex-shader output interpretation, NaN/Inf handling, clip/discard policy, guard-band clipping, and user clip planes.
- `PA_CL_POINT_*` and `PA_CL_ENHANCE` cover point radius/size and clipper enhancement/debug behavior.
- `PA_SU_VTX_CNTL`, `PA_SU_POINT_*`, `PA_SU_LINE_*`, `PA_SU_PRIM_FILTER_CNTL`, `PA_SU_SC_MODE_CNTL`, `PA_SU_POLY_OFFSET_*`, `PA_SU_HARDWARE_SCREEN_OFFSET`, and `PA_SU_LINE_STIPPLE_VALUE` define setup-unit point/line, primitive filtering, culling/front-face/fill, polygon offset, and line stipple state.
- `PA_SC_AA_CONFIG`, `PA_SC_AA_MASK_*`, `PA_SC_AA_SAMPLE_LOCS_PIXEL_*`, and `PA_SC_CENTROID_PRIORITY_*` describe multisample configuration, sample masks, per-sample locations, and centroid selection.
- `PA_SC_CLIPRECT_*`, `PA_SC_EDGERULE`, `PA_SC_LINE_*`, `PA_SC_MODE_CNTL_*`, `PA_SC_RASTER_CONFIG`, `PA_SC_RASTER_CONFIG_1`, `PA_SC_GENERIC_SCISSOR_*`, `PA_SC_SCREEN_SCISSOR_*`, `PA_SC_WINDOW_*`, `PA_SC_VPORT_SCISSOR_*`, and `PA_SC_VPORT_ZMIN/ZMAX_*` encode rasterizer routing, scissor rectangles, screen/window bounds, viewport scissor rectangles, and depth ranges.
- `PA_SC_ENHANCE`, `PA_SC_ENHANCE_1`, `PA_SC_DSM_CNTL`, FIFO size fields, EOV max counts, line-stipple state, screen extent fields, trap-screen registers, clock controls, and debug controls expose implementation-specific tuning and diagnostics.
- `PA_SU_PERFCOUNTER*` and `PA_SC_PERFCOUNTER*` define PA setup/scanner performance counter selectors and low/high data words.

These macros back user-visible graphics behavior: viewport transforms, clipping, culling, polygon offset, scissor, depth range, AA sample locations, and rasterization can all be affected by wrong field definitions.

### Clipper, SXIFCCG, And Setup Debug

`CLIPPER_DEBUG_REG00` through `CLIPPER_DEBUG_REG19`, `SXIFCCG_DEBUG_REG0` through `SXIFCCG_DEBUG_REG3`, and `SETUP_DEBUG_REG0` through `SETUP_DEBUG_REG5` are dense debug and tuning registers. Their fields include bypass/disables, FIFO and arbitration controls, event/debug selectors, stall controls, primitive and clipper counters, and implementation-specific extra debug payloads.

These definitions are mostly diagnostic or bring-up oriented. They should be used from debug paths or known-good init tables rather than opportunistically changed in normal rendering paths.

### Compute Dispatch And CSPRIV State

The compute section describes command-processor compute-dispatch programming:

- `COMPUTE_DISPATCH_INITIATOR` defines dispatch mode, dimensionality, partial-TG handling, thread-trace, and launch-policy bits.
- `COMPUTE_DIM_*`, `COMPUTE_START_*`, `COMPUTE_NUM_THREAD_*`, and `COMPUTE_RESTART_*` describe grid dimensions, starting coordinates, workgroup thread dimensions, and restart coordinates.
- `COMPUTE_PGM_LO/HI`, `COMPUTE_TBA_LO/HI`, `COMPUTE_TMA_LO/HI`, `COMPUTE_PGM_RSRC1`, and `COMPUTE_PGM_RSRC2` describe shader program addresses, trap/metadata addresses, VGPR/SGPR counts, priority, float mode, DX10 clamp, debug mode, LDS size, scratch enable, user SGPR count, trap handler, and TGID/XNACK-related resources.
- `COMPUTE_VMID`, `COMPUTE_RESOURCE_LIMITS`, `COMPUTE_STATIC_THREAD_MGMT_SE0..SE3`, and `COMPUTE_TMPRING_SIZE` define VMID, CU masks/resource limits, per-SE thread management, and scratch/temp-ring sizing.
- `COMPUTE_THREAD_TRACE_ENABLE`, `COMPUTE_MISC_RESERVED`, `COMPUTE_DISPATCH_ID`, `COMPUTE_THREADGROUP_ID`, `COMPUTE_RELAUNCH`, `COMPUTE_WAVE_RESTORE_*`, and `COMPUTE_USER_DATA_0..15` expose tracing, dispatch identification, wave relaunch/restore, and user SGPR payload state.
- `CSPRIV_CONNECT` maps doorbell offset, queue ID, VMID, and unordered-dispatch behavior; `CSPRIV_THREAD_TRACE_TG*` and `CSPRIV_THREAD_TRACE_EVENT` expose compute thread-trace group/event fields.

These fields integrate with KFD queues, compute rings, shader dispatch packet emission, debugger/trap support, and thread tracing. Program-resource fields are especially ABI-sensitive because they must match compiler-generated shader metadata.

### RLC, Clocking, Load Balance, GPM, And BIST

The final section covers run-list controller state:

- `RLC_CNTL`, `RLC_DEBUG_SELECT`, `RLC_DEBUG`, `RLC_MC_CNTL`, and `RLC_STAT` define enable/step/cache controls, debug selection/data, memory-controller request attributes, and busy status.
- `RLC_SAFE_MODE`, `RLC_RLCV_SAFE_MODE`, `RLC_SMU_SAFE_MODE`, `SMU_RLC_RESPONSE`, and `RLC_RLCV_COMMAND` provide command/response fields for safe-mode or SMU/RLCV coordination.
- `RLC_MEM_SLP_CNTL`, `RLC_CLK_CNTL`, `RLC_PERFMON_CLK_CNTL`, `CGTT_RLC_CLK_CTRL`, `CGTT_PA_CLK_CTRL`, and `CGTT_SC_CLK_CTRL` define memory sleep, clock, on-delay, off-hysteresis, and soft override controls.
- `RLC_PERFMON_CNTL`, `RLC_PERFCOUNTER*_SELECT`, and `RLC_PERFCOUNTER*_LO/HI` define RLC profiling state.
- `RLC_LB_CNTL`, `RLC_LB_CNTR_MAX`, `RLC_LB_CNTR_INIT`, and `RLC_LOAD_BALANCE_CNTR` expose RLC load-balance control/counter fields.
- `RLC_JUMP_TABLE_RESTORE`, `RLC_PG_DELAY_2`, `RLC_GPM_DEBUG_SELECT`, `RLC_GPM_DEBUG`, `RLC_GPM_DEBUG_INST_*`, `RLC_GPM_UCODE_ADDR`, and `RLC_GPM_UCODE_DATA` expose firmware/GPM debug and microcode-address/data paths.
- `GPU_BIST_CONTROL` configures BIST stop-on-fail and loop-count fields.
- The chunk ends at `RLC_ROM_CNTL__SLP_MODE_EN_MASK`; its corresponding shift and later `RLC_ROM_CNTL` fields are outside this chunk.

RLC controls are power-management and firmware-adjacent integration points. Safe-mode, microcode, sleep, and clock fields can affect register accessibility and GPU liveness.

## APIs, Types, And Functions

This chunk defines no C functions, types, structs, enums, storage, callbacks, locks, or exported symbols. Its API surface is the macro namespace itself. The naming convention is consistent:

- `REGISTER__FIELD_MASK` gives the already-shifted bit mask for a field.
- `REGISTER__FIELD__SHIFT` gives the field's least-significant bit position.
- Full-width data/address/counter fields usually use mask `0xffffffff` and shift `0x0`.
- Reserved fields are present for documentation of hardware bit layout, but consumers should generally preserve reserved bits in read-modify-write flows unless writing a trusted full-register init value.

Because the header is generated hardware metadata, consumers depend on exact spelling. A typo is usually a compile-time break for direct users, but a semantically wrong numeric mask may compile cleanly and misprogram hardware.

## Control Flow

There is no runtime control flow in this chunk. It contains only preprocessor definitions. The implied runtime flow is:

1. GFX 8.1 AMDGPU/KFD code includes the appropriate offset and shift/mask headers.
2. A call site selects a register offset and target instance, sometimes through GRBM indexed access.
3. The call site uses these macros through `REG_SET_FIELD`, `REG_GET_FIELD`, or equivalent bit operations.
4. The resulting value is emitted through MMIO reads/writes, packetized command streams, queue programming, debugfs/register-dump paths, profiler paths, or firmware/RLC control flows.

Ordering rules, locking, polling loops, timeout handling, reset sequences, cache flushes, W1C/W1S behavior, and privilege checks are implemented in surrounding driver code and hardware/firmware protocols, not here.

## State And Persistence Behavior

The macros themselves hold no software state and persist nothing. They describe hardware-visible state with different lifetimes:

- DB/PA/compute registers hold context or command state that persists until another context restore, command packet, reset, or explicit write changes it.
- CP HQD and CSPRIV fields describe queue state, doorbell routing, VMID, context-save storage, EOP rings, and completion counters that are shared with hardware execution.
- GB tile/macrotile and backend fields are chip-configuration state used by surface layout and render backend routing.
- GRBM index, reset, trap, and debug fields affect global routing and access to per-instance graphics registers.
- RAS/EDC signature and error/status fields are diagnostic hardware state, potentially latched or sticky depending on the underlying register.
- Performance counters are hardware-updated while enabled; low/high halves may need a coherent sampling sequence outside this header.
- RLC safe-mode, clock, memory sleep, microcode, and BIST fields can alter power/firmware behavior and may need handshakes before and after writes.

Any read-modify-write sequence using these macros should preserve unrelated fields unless the caller intentionally owns the full register value.

## Dependencies And Integration Points

The header depends only on the C preprocessor and the include guard at the top of the file. Practical consumers depend on:

- Sibling GFX 8.1 register offset headers that define the register addresses.
- AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32`, `WREG32`, indexed GRBM access helpers, and command-stream packet builders.
- KFD queue management for CP HQD and compute/CSPRIV programming.
- Graphics command emission for DB/PA/GB/GRBM state and render context setup.
- RAS/debug/performance infrastructure for EDC signatures, status/error decoding, performance counters, thread trace, debug-index/data, and register dumps.
- RLC firmware and power-management code for safe mode, clock gating, memory sleep, GPM debug, microcode address/data, and BIST controls.

The file path is source-tree-aligned under `drivers/gpu/drm/amd/include/asic_reg/gca`, so merged research should stay attached to the AMDGPU generated-register-header area rather than to Ceph storage code.

## Risks And Edge Cases

- The chunk begins and ends on macro boundaries chosen by line range, not by semantic register family. It starts after prior `CP_HQD_HQ_STATUS1` definitions and ends halfway through `RLC_ROM_CNTL`; the next chunk must complete that family.
- These macros are ASIC-specific. Reusing a GFX 8.1 mask with a nearby but different ASIC generation can silently program the wrong bits.
- Full-width-looking fields can be addresses, counters, opaque debug payloads, or command data. Callers must still respect register-specific alignment, latching, side effects, and ordering.
- Debug and override registers such as `DB_DEBUG*`, `CLIPPER_DEBUG_REG*`, `SETUP_DEBUG_REG*`, `SXIFCCG_DEBUG_REG*`, `GRBM_DEBUG*`, and `RLC_GPM_*` can disable optimizations, force misses/stalls, alter clocking, or expose implementation state.
- `GRBM_GFX_INDEX` changes which shader engine/array/instance subsequent indexed register accesses target; failure to restore broadcast/default state can misdirect later writes.
- Performance counters and status registers can change while being read. Split low/high counters need the sampling protocol used by the owning performance code.
- Reserved masks appear in several registers. Treating reserved bits as writable feature flags can cause undefined hardware behavior.
- Surface-layout fields in `DB_*`, `GB_TILE_MODE*`, `GB_MACROTILE_MODE*`, and `GB_ADDR_CONFIG` are high blast-radius: wrong fields can corrupt depth/stencil rendering, compression metadata, or tiling interpretation.
- Compute program resource fields must agree with shader compiler metadata and queue ABI; wrong VGPR/SGPR/LDS/scratch/user-SGPR values can hang waves or produce invalid execution.
- RLC safe-mode, memory sleep, clock, GPM microcode, and BIST controls may require firmware/SMU handshakes that are not represented by masks alone.

## Test Signals

Useful validation signals for changes touching this header or generated-register consumers include:

- Kernel build coverage for AMDGPU/KFD configurations that include GFX 8.1-era ASIC support; macro spelling mistakes should fail compilation at direct call sites.
- Static comparison against AMD's authoritative generated register database or known-good upstream `gfx_8_1_sh_mask.h` to detect numeric mask/shift drift.
- Boot and GPU reset smoke tests on affected GFX 8.1 hardware, watching for GRBM busy bits clearing, RLC safe-mode handshakes completing, and absence of GPU hangs.
- KFD queue tests that create/destroy compute queues, dispatch kernels, exercise doorbells, EOP completion, and context-save/restore behavior.
- Graphics rendering tests that cover depth/stencil, HTILE, EQAA/MSAA, scissor/viewport, polygon offset, line/point rasterization, tile/macrotile modes, and occlusion/Z-pass queries.
- Performance counter and debug tooling tests that select DB/GRBM/PA/RLC counters and verify nonzero, coherent counter updates under workload.
- RAS/debug register dump tests that decode GRBM read/write errors, RAS signatures, and DB/PA/RLC debug data without malformed field extraction.

### subset-b-002723: lines 9228-13901

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gca/gfx_8_1_sh_mask.h lines 9228-13901

## Purpose

This chunk is a generated AMD GCA/GFX 8.1 shader-mask header slice. It defines preprocessor constants for register bitfields: each field is represented as `<REGISTER>__<FIELD>_MASK` and `<REGISTER>__<FIELD>__SHIFT`. Driver code uses these constants with the matching GFX 8.1 offset header and AMDGPU bitfield helpers to compose or decode 32-bit MMIO register values.

The repository path is under `distributed-fs/ceph-client`, but this source is AMD GPU driver hardware metadata, not Ceph or filesystem logic. The chunk contains no executable C code, no structs, no functions, no callbacks, and no software-owned storage.

This specific range starts in the middle of `RLC_ROM_CNTL`, covers a large run of RLC, CGTT/CGTS, and SPI field layouts, then enters SQ/SQC fields near the end. The major hardware areas are:

- RLC ROM, clock-count, GPM, power-gating, SMU handshake, SERDES, scratch, save/restore, interrupt, SPM, CP table, and global-control fields.
- Clock-gating and clock-tree controls for RLC, BCI, SPI, and repeated per-CU shader/texture blocks.
- SPI pixel input, shader program, resource, user-data, trap, debug, performance-counter, wave-lifetime, GDS/export/scoreboard, and load-balance fields.
- SQ and SQC control/cache/DSM fields at the tail of the chunk.

## Important APIs, Types, And Macros

There are no C APIs in the ordinary function/type sense. The public interface is the generated macro namespace consumed by AMDGPU and KFD code:

- `<REGISTER>__<FIELD>__SHIFT` names the bit offset of a field.
- `<REGISTER>__<FIELD>_MASK` names the raw register mask.
- Full-width `0xffffffff` fields identify data, counter, scratch, address, or bitmap-style registers, but do not imply that arbitrary writes are safe.

Important register families in this chunk include:

- `RLC_*`: register-list-controller fields for ROM control, GPU clock counters, microcode flags, GPM status, power gating, clock gating, load balancing, GPM threads/VMIDs, SERDES read/write control, scratch/general registers, GPM performance counters, SRM index/data windows, interrupt controls, SPM mux/ring controls, SMU messages/arguments, CP table programming, and global RLC state.
- `RLC_GPM_STAT`: a dense status word for RLC busy state, graphics power/clock/light-sleep status, context/GFX/compute processing, register save/restore, static/dynamic CU power transitions, aborted power-down sequence, and power-gating error status.
- `RLC_PG_CNTL`: GFX power-gating enable/source, dynamic/static per-CU power gating, pipeline power gating, override/disable bits, CHUB/SMU handshake controls, and SMU clock-slowdown controls.
- `RLC_CGCG_CGLS_CTRL`, `RLC_CGCG_RAMP_CTRL`, `RLC_MGCG_CTRL`, and `CGTT_*`: coarse/fine clock-gating controls, sleep-mode behavior, hysteresis/delay fields, soft override/stall fields, and clock-ramp timing.
- `CGTS_CU*_SP0_CTRL_REG`, `CGTS_CU*_SP1_CTRL_REG`, `CGTS_CU*_LDS_SQ_CTRL_REG`, `CGTS_CU*_TA_CTRL_REG`, `CGTS_CU*_TA_SQC_CTRL_REG`, and `CGTS_CU*_TD_TCP_CTRL_REG`: repeated per-CU clock/tree-status controls. Each group exposes block masks plus override, busy-override, light-sleep override, and SIMD-busy override fields for shader processors, LDS/SQ, texture address/SQC, and texture data/TCP blocks.
- `CGTS_SM_CTRL_REG` and `CGTS_SM_CTRL_REG_2`: shader-module level clock/tree controls, including CP/RLC/SX/TA/TD/TCP/SQC/SQ/LDS fields, override bits, sleep/busy override bits, and multipipe controls.
- `SPI_*`: shader processor interpolator and shader-stage programming metadata. This includes `SPI_CONFIG_CNTL`, `SPI_GFX_CNTL`, `SPI_PS_INPUT_ENA`, `SPI_PS_INPUT_ADDR`, `SPI_PS_INPUT_CNTL_0..31`, shader position/color/Z format controls, LDS/GDS ring controls, debug and trap controls, performance counters, and wave-lifetime/load-balance counters.
- `SPI_SHADER_*`: shader program address, trap base/memory address, resource, user SGPR/user-data, and stage resource fields for PS, VS, GS, ES, HS, and LS. Resource registers define VGPR/SGPR counts, priority, float mode, privileged/debug/IEEE/DX10 behavior, scratch/trap/LDS/exception enables, CU masks, wave limits, lock thresholds, and group FIFO depth.
- `SQ_CONFIG` and `SQC_CONFIG`: shader queue and scalar instruction/data cache control fields, including debug behavior, soft-clause disables, export-ready priority behavior, replay sleep count, cache sizing, FIFO depths, hash behavior, per-VMID invalidate behavior, LRU policy, bank forcing, and clock-disable fields.
- `SQC_CACHES`, `SQC_WRITEBACK`, and the beginning of `SQC_DSM_CNTL`: cache invalidate/writeback targets, completion status, dirty/writeback status, and diagnostic/scan-mux controls.

## Control Flow

This header chunk has no runtime control flow. Its effect is entirely through C preprocessing.

Typical consumer flow is:

1. A GFX 8.1-era driver source includes `gfx_8_1_offset.h` and `gfx_8_1_sh_mask.h`.
2. The caller selects a register offset macro from the offset header and one or more field macros from this mask header.
3. Driver code uses helper patterns such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32`, `WREG32`, `RREG32_SOC15`, or generation-specific wrappers to update or decode a 32-bit register value.
4. The hardware-visible MMIO read/write, indexed access, polling, firmware table programming, or debug dump happens in the consumer source, not in this header.

Examples visible in this tree show the same field families used by older and newer AMDGPU paths:

- `gfx_v6_0.c`, `gfx_v7_0.c`, and later SOC15-era `gfx_v10_0.c`, `gfx_v11_0.c`, `gfx_v12_0.c`, and `gfx_v12_1.c` manipulate `RLC_PG_CNTL` fields around GFX power gating, static/dynamic per-CU power gating, SMU slowdown, and SMU handshake behavior.
- `mxgpu_vi.c` programs VI golden settings for `CGTT_*` and `CGTS_CU*` registers, showing these generated field layouts are used for virtualization and bring-up register tables.
- Clear-state headers such as `clearstate_si.h` and `clearstate_gfx11.h` carry repeated `SPI_PS_INPUT_CNTL_0..31` entries, matching the repeated pixel-input-control field family defined here.

The header does not define valid programming order. It also does not state whether a field is read-only, write-one-to-clear, sticky, firmware-owned, indexed by GRBM, safe during active waves, or reset/power-gating sensitive.

## State And Persistence Behavior

The macros persist no software state. They describe hardware state in GFX 8.1 graphics blocks.

The represented hardware state includes:

- Persistent-until-reprogrammed configuration: RLC power/clock gating, CGTT/CGTS clock tree controls, SPI shader-stage programming, pixel input interpolation controls, shader resource controls, GDS/export/scoreboard buffer sizing, and SQ/SQC cache configuration.
- Live status: RLC busy and power-transition status, CU work-pending bitmaps, SERDES busy/read data, GPM performance counters, SPI debug busy/status fields, wave-lifetime counters, CSQ active counters, SQC cache completion/dirty state, and power-gating status bitmaps.
- Trigger/control windows: GPU clock capture, SERDES read/write commands, GPM scratch index/data windows, SRM index/data windows, SMU command/argument registers, SPM sample/mux/ring controls, cache invalidate/writeback controls, trap/debug controls, and performance counter control fields.
- Shader ABI state: shader program base addresses, trap base/memory addresses, user SGPR/user-data registers, scratch/trap/exception enables, VGPR/SGPR counts, LDS sizes, and per-stage resource limits. These fields are part of how graphics and compute work is launched on the GPU.

Persistence is hardware-defined. Configuration values are usually reestablished during ASIC initialization, suspend/resume, reset recovery, virtualization transitions, or golden-setting programming. Status, counter, interrupt, and command fields may be volatile, latched, clear-on-read/write, or meaningful only while a specific block is selected or idle.

## Dependencies

This chunk depends on the generated AMD GFX 8.1 register family remaining synchronized:

- `gfx_8_1_sh_mask.h` supplies the field masks and shifts documented here.
- The companion GFX 8.1 offset header supplies the matching register addresses, usually with `mm*` register names for pre-SOC15/VI-era code.
- AMDGPU bitfield helpers rely on exact macro spelling, especially the `__SHIFT` and `_MASK` suffix conventions.
- RLC/CP firmware initialization, clock-gating tables, power-management code, KFD/queue setup, graphics pipeline programming, and debug/RAS-like dump paths depend on these layouts matching the actual ASIC register specification.
- Cross-generation code often has nearly identical register names. Similar fields in SI/CIK/VI, GFX9, GFX10, GFX11, or GFX12 headers may differ in width, ownership, or semantics.

## Integration Points

Primary integration points are:

- GFX power management and RLC control: `RLC_PG_CNTL`, `RLC_GPM_STAT`, `RLC_CGCG_CGLS_CTRL`, `RLC_MGCG_CTRL`, `RLC_AUTO_PG_CTRL`, and SMU message/argument fields are consumed by bring-up, power-gating, clock-gating, and reset/recovery paths.
- Golden-setting tables: CGTT/CGTS/RLC/SPI fields are commonly programmed from generation-specific register tables. In this tree, `mxgpu_vi.c` shows VI golden settings for `CGTT_*`, `CGTS_CU*`, `RLC_CGCG_CGLS_CTRL`, and related fields.
- Shader pipeline setup: `SPI_SHADER_PGM_*`, `SPI_SHADER_PGM_RSRC*`, `SPI_SHADER_USER_DATA_*`, `SPI_PS_INPUT_*`, `SPI_SHADER_POS_FORMAT`, `SPI_SHADER_COL_FORMAT`, and `SPI_SHADER_Z_FORMAT` define the bit layout for graphics shader stages and per-stage user data.
- Trap/debug/diagnostic flows: `SPI_GDBG_*`, `SPI_CDBG_*`, `SPI_DEBUG_*`, `SPI_SLAVE_DEBUG_BUSY`, `SPI_P*_TRAP_SCREEN_*`, SQ debug fields, SQC DSM fields, and RLC scratch/index windows support debugging, hang analysis, trap handling, and register dumps.
- Performance and telemetry: RLC GPM counters, RLC SPM mux/ring controls, SPI performance counters, SPI wave lifetime counters, CSQ active counts, and SQC cache status fields support performance monitoring and low-level diagnostics.
- Cache coherency and invalidation: `SQC_CACHES` and `SQC_WRITEBACK` fields describe scalar cache invalidate/writeback operations and completion/dirty reporting. Consumers must supply the correct sequencing and polling.

## Risks And Edge Cases

- The chunk boundaries are artificial. It starts after `RLC_ROM_CNTL__SLP_MODE_EN_MASK` from the previous chunk and ends after `SQC_DSM_CNTL__EN_SINGLE_WR_ICACHE_BANKC_MASK`, before the remaining `SQC_DSM_CNTL` fields in the next chunk.
- Header/offset mismatch is the main risk. A GFX 8.1 mask macro can compile with the wrong generation's offset or register name but program the wrong bit on hardware.
- Repeated register families are easy to copy incorrectly. `SPI_PS_INPUT_CNTL_0..31`, `SPI_SHADER_USER_DATA_*_0..15`, shader-stage resource registers, and `CGTS_CU*` controls are regular but not universally identical across stages or CU groups.
- Reserved masks are explicit throughout the header. Read-modify-write users should preserve reserved bits unless the hardware programming sequence requires a full-register write.
- RLC power-gating and clock-gating fields can affect active queues, firmware handshakes, CU availability, and reset behavior. Incorrect writes can cause hangs, failed power transitions, or missed SMU/RLC handshakes.
- CGTS per-CU override and busy/light-sleep fields can force shader, LDS, SQ, TA, SQC, TD, or TCP blocks into unexpected clock/power behavior. This is particularly risky under virtualization or golden-setting programming.
- Shader program/user-data/resource fields are ABI-sensitive. Wrong masks or shifts can misprogram program addresses, trap addresses, SGPR/VGPR counts, LDS size, exception enables, scratch state, user SGPR mapping, CU masks, or wave limits.
- SQC invalidate/writeback fields are action-oriented. Treating them as passive configuration can trigger cache operations or make polling observe stale/incomplete state.
- Many data/status fields are full-width. Full-width masks hide field-level semantics; consumers must know whether the underlying register is data, address, command, status, scratch, or write-triggered.

## Test Signals

Useful validation signals include:

- Build coverage for AMDGPU/KFD code that includes the GFX 8.1 offset and mask headers, especially VI-era GFX, power-management, virtualization, and golden-setting code.
- Static generated-header checks that every field has matching `__SHIFT` and `_MASK` macros, masks align with shifts, repeated groups are complete, and chunk boundaries reconcile with adjacent chunks.
- Cross-checks against the companion GFX 8.1 offset header so every register family named here has matching `mm*` offsets where expected.
- Hardware bring-up on GFX 8.1/VI devices, confirming RLC firmware load, clock-gating initialization, power-gating transitions, SMU handshakes, graphics queue startup, and suspend/resume work without register access warnings or ring timeouts.
- Golden-setting validation that `CGTT_*`, `CGTS_CU*`, `RLC_CGCG_CGLS_CTRL`, and related clock-gating values are written with expected masks and do not disturb reserved bits.
- Graphics and compute smoke tests that exercise shader stage setup, user-data SGPR programming, traps, scratch/LDS allocation, pixel input interpolation, export/GDS resources, and CU masks/wave limits.
- Cache and diagnostic tests that issue SQC invalidate/writeback operations, poll completion, and validate no stale instruction/data-cache behavior.
- Debug and hang-dump tests that read SPI/RLC/SQ/SQC status, counters, scratch/index windows, wave lifetime counts, and performance counters without causing new hangs or false status decoding.

### subset-b-002724: lines 13902-19048

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gca/gfx_8_1_sh_mask.h lines 13902-19048

## Scope

This chunk is part of the generated AMD GFX 8.1 ASIC register field mask header. It contains C preprocessor constants only: each hardware register field is represented by a `<REGISTER>__<FIELD>_MASK` value and a matching `<REGISTER>__<FIELD>__SHIFT` value. There are no functions, structs, enums, storage definitions, or executable control-flow blocks in this range.

The covered line range starts in shader/SQC control masks, moves through SQ performance, thread trace, wave debug, shader resource descriptor, instruction-encoding, SX export/blend, TCC/TCA/TA/TD/TCP cache/texture, GDS, VGT/IA/WD primitive pipeline, and ends in WD debug register masks.

## Purpose

The purpose of this header chunk is to give AMDGPU driver code stable symbolic names for GFX 8.1 register bitfields. Callers combine these masks and shifts with register addresses from companion ASIC register headers to read, write, pack, unpack, and validate values for Southern Islands/GCN-style graphics hardware blocks.

The constants let driver code avoid hard-coded bit positions when it:

- Builds values for MMIO register writes.
- Extracts status and counter fields from MMIO register reads.
- Programs shader resources, image resources, samplers, and scratch descriptors.
- Configures performance counters and thread trace collection.
- Decodes wave state, instruction words, interrupts, and debug buses.
- Tunes or diagnoses cache, clock-gating, GDS, VGT, IA, and WD hardware blocks.

## Macro Interface

Every definition follows the same ABI-like macro pattern:

- `<REG>__<FIELD>_MASK` is the bit mask for a field in a 32-bit register word.
- `<REG>__<FIELD>__SHIFT` is the right-shift count needed to align the masked field to bit 0.

Typical use by consumers is expected to look like:

```c
field = (reg_value & REG__FIELD_MASK) >> REG__FIELD__SHIFT;
reg_value = (reg_value & ~REG__FIELD_MASK) |
            ((field_value << REG__FIELD__SHIFT) & REG__FIELD_MASK);
```

This chunk does not provide helper macros to perform those operations; it only exports the constants. Correctness therefore depends on callers pairing the right mask with the right shift and constraining field values before shifting.

## Register Families Covered

### SQ and SQC Shader Core

The opening section covers shader queue and shader instruction/data cache controls:

- `SQC_DSM_CNTL` controls DSM/irritator data selection and single-write enables for SQC instruction and data cache banks.
- `SQ_DSM_CNTL` exposes wavefront stall, SPI backpressure, SGPR/LDS/SP DSM irritator data selection, and single-write enables.
- `SQ_RANDOM_WAVE_PRI`, `SQ_REG_CREDITS`, and `SQ_FIFO_SIZES` describe scheduling priority, command/register credit accounting, overflow status, and FIFO sizing.
- `CC_GC_SHADER_RATE_CONFIG` and `GC_USER_SHADER_RATE_CONFIG` carry shader rate knobs such as DPFP rate, SQC balance disable, and half-LDS configuration.
- `CC_SQC_BANK_DISABLE` and `USER_SQC_BANK_DISABLE` mask SQC bank-disable fields per SQC instance.

These masks are integration points for shader initialization, clock/power tuning, debug/stress modes, and low-level fault diagnostics.

### SQ Performance Counters and Clock/Power Controls

The chunk defines 16 SQ performance counter low/high data registers and 16 `SQ_PERFCOUNTER*_SELECT` registers. Select fields include event select, SQC bank/client masks, SPM mode, SIMD mask, and performance mode. `SQ_PERFCOUNTER_CTRL`, `SQ_PERFCOUNTER_MASK`, and `SQ_PERFCOUNTER_CTRL2` gate counters by shader stage, sampling rate, force-enable, and shader array masks.

Clock and power fields include:

- `CGTT_SQ_CLK_CTRL`, `CGTT_SQG_CLK_CTRL` with on-delay, off-hysteresis, and override bits.
- `SQ_ALU_CLK_CTRL`, `SQ_TEX_CLK_CTRL`, `SQ_LDS_CLK_CTRL` for forcing CUs on per shader half.
- `SQ_POWER_THROTTLE` and `SQ_POWER_THROTTLE2` for min/max power, power delta, interval, ratio, and reference-clock selection.
- `SQ_TIME_HI` and `SQ_TIME_LO` timestamp fields.

These definitions are consumed by performance monitoring, power management, and debug code that must preserve unrelated fields during read-modify-write sequences.

### SQ Thread Trace

Thread trace register masks include:

- Trace buffer base/size registers: `SQ_THREAD_TRACE_BASE`, `SQ_THREAD_TRACE_BASE2`, and `SQ_THREAD_TRACE_SIZE`.
- Selection and gating: `SQ_THREAD_TRACE_MASK`, `SQ_THREAD_TRACE_MODE`, `SQ_THREAD_TRACE_TOKEN_MASK`, `SQ_THREAD_TRACE_TOKEN_MASK2`, and `SQ_THREAD_TRACE_PERF_MASK`.
- Runtime state: `SQ_THREAD_TRACE_WPTR`, `SQ_THREAD_TRACE_STATUS`, `SQ_THREAD_TRACE_CNTR`, and `SQ_THREAD_TRACE_HIWATER`.
- User data payload registers `SQ_THREAD_TRACE_USERDATA_0` through `_3`.

This section also defines masks for decoded thread trace packet words: common, instruction, PC, userdata, timestamp, wave, misc, wave-start, register, compute-shader register, event, issue, and perf packet formats. These packet masks are useful for trace parsing tools and driver debug code that interpret trace memory after capture.

Risk is high when these fields drift from the hardware packet format: trace output may still be collected but parsed incorrectly, causing misleading profiling or debug data.

### Error Detection and Wave Debug

Error and wave-state fields include:

- `SQC_EDC_CNT`, `SQ_EDC_SEC_CNT`, `SQ_EDC_DED_CNT`, and `SQ_EDC_INFO` for single/double error counters and wave/SIMD/source/VMID attribution.
- Wave register masks for instruction words, program counter, execution mask, status, mode, trap status, hardware ID, GPR/LDS allocation, wait counters, M0, trap base/metadata addresses, and temporary trap registers.
- `SQ_IND_INDEX`, `SQ_IND_DATA`, and `SQ_CMD` for indexed wave/register access and SQ commands.
- `SQ_DEBUG_STS_GLOBAL`, `SQ_DEBUG_STS_GLOBAL2`, `SQ_DEBUG_STS_GLOBAL3`, `SQ_DEBUG_STS_LOCAL`, and `SQ_DEBUG_CTRL_LOCAL` for global/local SQ debug status.

These masks are used by wave dump, trap/debug, hang diagnosis, and EDC reporting paths. State represented here is hardware state, not persistent software state.

### Shader Resource, Image Resource, Sampler, and Scratch Descriptors

The chunk includes descriptor word layouts:

- `SQ_BUF_RSRC_WORD0` through `WORD3`: base address, high address, stride, record count, destination swizzles, numeric/data format, element size, index stride, TID addition, ATC, hash, heap, memory type, and resource type.
- `SQ_IMG_RSRC_WORD0` through `WORD7`: base address, min LOD, data/number format, width/height/depth/pitch, perf modifier, interlace, swizzle selectors, mip levels, tiling index, ATC, type, array bounds, metadata address, compression, alpha/color transform, and lost-bit fields.
- `SQ_IMG_SAMP_WORD0` through `WORD3`: clamp modes, anisotropy, depth compare, unnormalized coordinates, coordinate truncation, degamma, filter modes, LOD bounds/bias, border color pointer/type, and precision fixes.
- `SQ_FLAT_SCRATCH_WORD0/1`, `SQ_M0_GPR_IDX_WORD`, and `SH_MEM_*` masks for scratch and shader memory configuration.

These fields are central to command submission and shader setup. Incorrect packing can corrupt GPU memory access, sampling behavior, cacheability, or VM/ATC behavior.

### Instruction Encoding Masks

The chunk defines bit layouts for several GCN instruction formats:

- Scalar formats: `SQ_SOP1`, `SQ_SOP2`, `SQ_SOPC`, `SQ_SOPK`, `SQ_SOPP`, and `SQ_SMEM_0/1`.
- Vector formats: `SQ_VOP1`, `SQ_VOP2`, `SQ_VOP3_0`, `SQ_VOP3_0_SDST_ENC`, `SQ_VOP3_1`, `SQ_VOPC`, `SQ_VOP_SDWA`, and `SQ_VOP_DPP`.
- Memory/export/interp formats: `SQ_MUBUF_0/1`, `SQ_MTBUF_0/1`, `SQ_MIMG_0/1`, `SQ_FLAT_0/1`, `SQ_DS_0/1`, `SQ_EXP_0/1`, and `SQ_VINTRP`.
- `SQ_INST` exposes the full 32-bit instruction encoding word.

These masks are integration points for disassembly, debug decode, trace decode, trap handling, and any tooling that inspects wave instruction state. They are not instruction implementations.

### SX Export/Blend Block

The SX section includes:

- `CGTT_SX_CLK_CTRL0` through `CGTT_SX_CLK_CTRL4` clock-gating controls.
- `SX_DEBUG_BUSY` through `SX_DEBUG_BUSY_4` detailed busy/valid state across position, column, DBIF, buffer, and command paths.
- `SX_DEBUG_1` blend/quad/pixel optimization debug controls.
- Four SX performance counters with select, mode, low, and high masks.
- `SX_PS_DOWNCONVERT`, `SX_BLEND_OPT_EPSILON`, `SX_BLEND_OPT_CONTROL`, and per-MRT `SX_MRT0_BLEND_OPT` through `SX_MRT7_BLEND_OPT`.

Consumers are expected in color export, render backend interaction, perf monitoring, and hang debug paths. Debug fields are numerous and hardware-specific, making stale documentation or wrong masks a diagnostic risk.

### TCC, TCA, TA, TD, TCP, and TCI Cache/Texture Paths

Cache and texture-related masks include:

- `TCC_CTRL`, `TCC_EDC_CNT`, redundancy/execute-disable/DSM controls, TCC/TCA clock-gating, and TCC/TCA performance counters.
- `TD_CNTL`, `TD_STATUS`, TD debug, DSM, counters, scratch, and clock-gating.
- `TA_CNTL`, `TA_CNTL_AUX`, TA base address, status, debug, performance counters, scratch, and clock-gating.
- `TCP_INVALIDATE`, `TCP_STATUS`, `TCP_CNTL`, channel steering, address configuration, credits, counters, buffer address hashing, EDC counters, watchpoint address/control, GATCL1 control, DSM control, and clock disable controls.
- `TC_CFG_L1_LOAD_POLICY0/1`, `TC_CFG_L1_STORE_POLICY`, `TC_CFG_L2_LOAD_POLICY0/1`, `TC_CFG_L2_STORE_POLICY0/1`, `TC_CFG_L2_ATOMIC_POLICY`, and L1/L2 volatile controls.
- `TCI_STATUS`, `TCI_CNTL_1`, and `TCI_CNTL_2`.

These definitions support cache invalidation, address hashing, VMID-aware watchpoints, cache policy selection, EDC reporting, and performance counter setup. Integration is sensitive to hardware generation because cache policy encodings and channel/bank layouts are ASIC-specific.

### GDS, GWS, OA, and Context Switch State

The GDS section is large and covers:

- Global control/status: `GDS_CONFIG`, `GDS_CNTL_STATUS`, `GDS_ENHANCE`, `GDS_ENHANCE2`, and clock-gating.
- Fault and EDC status: `GDS_PROTECTION_FAULT`, `GDS_VM_PROTECTION_FAULT`, `GDS_EDC_CNT`, `GDS_EDC_GRBM_CNT`, `GDS_EDC_OA_DED`.
- Direct read/write and burst access registers.
- Atomic controls, operands, results, base/size, offsets, destination, and completion status.
- GWS resource control/status, resource counts, global reset masks for 64 resources, and targeted resource reset.
- Ordered append controls: counters, address, inc/dec, ring size, VMID masks, reset, reset masks, and CGPG restore identity fields.
- Debug registers `GDS_DEBUG_REG0` through `GDS_DEBUG_REG6` and GDS performance counters.
- Per-VMID base/size masks for GDS, GWS per-VMID base/size, and OA VMID masks.
- Context-switch status and counters for compute, graphics, vertex shader, and pixel shader slots.

These fields expose state that is directly tied to GPU queues, VMIDs, ordered append, global wave synchronization, and context switching. Misprogramming risks include VM isolation mistakes, lost or stuck GWS resources, incorrect context-save/restore accounting, and hard-to-debug hangs.

### VGT, IA, and WD Primitive Pipeline

The VGT/IA/WD section defines masks for graphics primitive setup and draw control:

- Draw/event initiators and event address fields.
- DMA base, index type, number of instances, size, max size, primitive type, and DMA control.
- Immediate data, index type, index counts, primitive ID enable/reset, vertex count, reuse controls, min/max index, index offset, and multi-primitive reset.
- Tessellation and geometry shader controls: output path, HOS controls, group primitive/vector controls, vector format controls, GS mode/on-chip control/output primitive type, cache invalidation, reset debug, FIFO depths, GS/ES/VS ratios, shader stage enables, LS/HS config, tessellation factor parameters, tessellation distribution, TF ring/memory, offchip buffering, GS instance count, ESGS/GSVS ring sizes/offsets/itemsizes, and max wave IDs.
- Streamout configuration, buffer sizes/offsets/strides/filled sizes, opaque draw offsets, and streamout buffer config.
- IA and VGT busy status, debug select/data registers, and clock-gating controls.
- WD status, QoS, debug select/data registers, and detailed `WD_DEBUG_REG0` through `WD_DEBUG_REG7` pipeline/FIFO/handshake state.
- Shader/primitive array masks: `CC_GC_SHADER_ARRAY_CONFIG`, `GC_USER_SHADER_ARRAY_CONFIG`, `CC_GC_PRIM_CONFIG`, and `GC_USER_PRIM_CONFIG`.

These constants are used by graphics pipeline setup, draw packet handling, tessellation/GS programming, streamout, multi-VGT/dual-IA configuration, and hang/debug diagnostics. They are especially stateful because many fields represent live hardware FIFOs, busy bits, or resource counts.

## Dependencies

This chunk has no include directives in the line range and no direct C dependencies. Its practical dependencies are:

- Companion register offset/address headers for GFX 8.1, typically in the same `asic_reg/gca` generated header set.
- AMDGPU register access helpers and macros that perform read-modify-write, masking, and field packing.
- Hardware documentation or generated register database used to produce `gfx_8_1_sh_mask.h`.
- Consumers in DRM/AMDGPU code that use these masks for SI/CI/VI-era GCN register programming and diagnostics.

Because the constants are generated hardware ABI data, the main dependency contract is semantic rather than link-time: each mask/shift pair must match the actual GFX 8.1 register layout.

## Control Flow

There is no runtime control flow in this chunk. Control flow appears only in downstream code that uses these constants. Conceptually, downstream access follows these patterns:

- Read a register and test status bits such as busy, full, valid, fault, overflow, or EDC counters.
- Build a control value from multiple fields, then write the register.
- Configure counters by programming select/mode fields, then read low/high counter values.
- Program descriptors by packing resource/sampler/image fields before GPU consumption.
- Decode trace, interrupt, wave, instruction, or debug words by applying mask and shift pairs.

The absence of helper code means there is no central runtime guard against invalid field values or mismatched mask/shift use.

## State and Persistence Behavior

The file itself is static compile-time data. It persists only as source code and preprocessor output.

The registers described by the masks represent volatile GPU hardware state. Some fields are configuration state that persists until reset or reprogramming, such as cache policy, clock-gating overrides, shader stage enables, descriptor words, and VMID GDS bounds. Other fields are transient status/counter/debug state, such as busy bits, FIFO levels, EDC counters, wave status, trace write pointers, performance counters, and protection-fault latches.

Driver suspend/resume, GPU reset, context switch, and queue teardown code must not assume this header stores state. It only names fields that other code may save, restore, or inspect.

## Integration Points

Important integration surfaces include:

- AMDGPU register read/write helpers for GFX 8.1 hardware blocks.
- Graphics pipeline setup code for VGT, IA, WD, tessellation, GS, and streamout.
- Shader setup and descriptor construction paths for buffer, image, sampler, scratch, and static memory configuration.
- Debugfs, GPU hang collection, wave dump, trap, thread trace, and performance counter code.
- Cache and memory-system setup paths for SQC, TCP, TCC, TCA, TCI, GATCL1, ATC, and TC policy controls.
- GDS/GWS/OA allocation, VMID protection, context switch, and reset handling.
- Hardware generation gating that selects GFX 8.1-specific headers and avoids applying these masks to incompatible ASICs.

## Risks

- Mask/shift drift from hardware documentation can silently corrupt register programming.
- Pairing a mask from one register with a shift from another register can compile cleanly and fail only at runtime.
- Unmasked shifted values can bleed into adjacent fields if callers do not apply the mask after shifting.
- Writing debug, DSM, force-miss, force-hit, clock override, or reset fields in production paths can cause severe performance loss or hangs.
- Reserved and unused fields appear throughout the chunk; callers should preserve them unless hardware documentation explicitly says otherwise.
- Many fields are status or counter latches. Treating them as ordinary writable configuration bits can break diagnostics or clear important evidence.
- Descriptor field mistakes can cause GPU virtual memory faults, wrong cacheability/ATC behavior, incorrect image sampling, or data corruption.
- VMID-specific GDS/GWS/OA masks are isolation-sensitive; incorrect base, size, or mask values can expose or corrupt another VMID's resources.
- Instruction and trace decode masks must match the exact ISA/hardware generation; reusing them for another GFX version can produce plausible but wrong debug output.

## Test Signals

Useful validation signals for changes to this chunk or its generator include:

- Build coverage for AMDGPU paths that include `gfx_8_1_sh_mask.h`.
- Static checks that every `*_MASK` has a corresponding `*__SHIFT` in the same register/field family.
- Register pack/unpack unit tests where available: `(value << shift) & mask` round-trips expected field values and does not affect neighboring fields.
- GPU boot and mode-setting on affected GFX 8.1 hardware.
- Shader/resource descriptor tests using buffer, image, sampler, scratch, ATC, compression, and format fields.
- Perf counter tests for SQ, SX, TCC/TCA, TA/TD/TCP, and GDS counter select/read paths.
- Thread trace capture and parser validation against known packet streams.
- GPU reset and hang-dump tests that verify busy/status/debug fields decode correctly.
- GDS/GWS/OA allocation, reset, VMID isolation, and context-switch tests.
- Graphics pipeline tests covering indexed draws, tessellation, geometry shader, streamout, primitive restart/reset, and multi-VGT/dual-IA cases.

## Chunk Notes for Merge

This is a partial chunk report for one oversized source file. It should be merged with neighboring chunk reports before producing the final source-tree-aligned per-file research document for `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gca/gfx_8_1_sh_mask.h`.

No final per-file report is produced here. The merge lane should retain that this chunk covers macro definitions only and that the source path is a generated GFX 8.1 register mask header, not an implementation file.

### subset-b-002725: lines 19049-21368

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gca/gfx_8_1_sh_mask.h lines 19049-21368

## Scope And Purpose

This chunk is the final range of the generated AMD GFX 8.1 register-mask header. It contains C preprocessor constants for bit masks and shifts, not executable code. The covered register families are:

- `WD_DEBUG_REG7` through `WD_DEBUG_REG10`, exposing Work Distributor debug/status bits for shader-engine arbitration, thread-group traffic, TF/TC handshakes, patch/TF fetch state, and WD-to-TE output FIFOs.
- `IA_DEBUG_REG0` through `IA_DEBUG_REG9`, exposing Input Assembler busy flags, normal and high-priority DMA paths, DMA pipeline stages, pipe request arbitration, FIFO occupancy, current index/data state, EOP/null flags, and TC/MC return-path status.
- `VGT_DEBUG_REG0` through `VGT_DEBUG_REG36` except skipped/reserved numbers, exposing Vertex Grouper/Tessellator pipeline debug state, event/EOP markers, counters, shader-engine/pipe routing state, DMA/IA/WD handshakes, and several reserved/spare bitfields.
- `VGT_PERFCOUNTER*`, `IA_PERFCOUNTER*`, and `WD_PERFCOUNTER*` selector and data registers, defining event-selection, counter mode, perf mode, and 64-bit low/high counter halves for VGT, IA, and WD blocks.
- `DIDT_IND_INDEX` and `DIDT_IND_DATA`, the indirect access window for DIDT registers.
- `DIDT_{SQ,DB,TD,TCP,DBR}_CTRL*`, `*_CTRL_OCP`, and `*_WEIGHT*` registers, defining dynamic power/current control fields for Shader Queue, Depth Block, Tessellator, Texture Cache Pipe, and Depth Buffer/DBR domains.

The file closes the `GFX_8_1_SH_MASK_H` include guard at line 21368. The companion address header is `gfx_8_1_d.h`; this header supplies only the field layout for composing or decoding 32-bit register values.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or runtime APIs in this range. The effective interface is the macro naming convention:

- `<REGISTER>__<FIELD>_MASK` gives the 32-bit mask for a field.
- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset for the same field.

Driver code typically uses these macros directly with bitwise operations or through AMD helper macros such as `REG_SET_FIELD`/`REG_GET_FIELD` when the register family is available to those helpers. The DIDT fields in this chunk are visibly consumed by power-management code. For example, `kv_dpm.c` reads and writes DIDT indirect registers with `RREG32_DIDT`/`WREG32_DIDT`, toggling fields such as `DIDT_SQ_CTRL0__DIDT_CTRL_EN_MASK`, `DIDT_DB_CTRL0__DIDT_CTRL_EN_MASK`, `DIDT_TD_CTRL0__DIDT_CTRL_EN_MASK`, and `DIDT_TCP_CTRL0__DIDT_CTRL_EN_MASK`. `smu7_powertune.c` uses the same mask/shift pairs in configuration tables for DIDT weights, min/max power limits, interval sizing, phase/clock controls, and enable bits.

The debug and perf-counter macros are lower-level register definitions. They are integration points for debugfs, perf-counter programming, bring-up diagnostics, GPU hang triage, and any ASIC-specific code that has selected the GFX 8.1 register layout. They do not perform reads or writes by themselves.

## Register Groups

### Work Distributor Debug Registers

`WD_DEBUG_REG7` continues WD debug coverage from earlier chunks. It exposes per-shader-engine arbitration and thread-group signals: SE0/SE1 input FIFO empty/full/read state, `SE1VGT_WD_thdgrp_send_in`, `se*_thdgrp_is_event`, `se*_thdgrp_eop`, `tfreq_arb_tgroup_rtr`, `arb_tfreq_tgroup_rts`, `arb_tfreq_tgroup_event`, and `te11_arb_busy`. These fields are useful when diagnosing whether thread groups are stuck before or after WD arbitration.

`WD_DEBUG_REG8` and `WD_DEBUG_REG9` describe TF/TC and TTP pipeline handshakes: `pipe*_dr`, `pipe*_rtr`, TF data/skid FIFO empty/full/busy/count state, TC read request/return valid/stall bits, first/last request markers, event/null flags, `ttp_patch_fifo_*`, `ttp_tf_fifo_empty`, `tf_fetch_state_q`, `tf_pointer_p0_q`, dynamic hull-shader state, and pipe4 traffic. Together they show whether WD is blocked by TF fetch, TC memory return, or patch FIFO state.

`WD_DEBUG_REG10` covers TTP-to-patch/PD state and WD output toward TE instances. It contains patch/event/EOP/EOPG flags, pipe handshakes, donut and patch shader-engine switching markers, `patch_accum_q`, and per-SE `wd_te11_out_se{0..3}_fifo_full/empty` flags. These fields are diagnostic state only, but stale or incorrect masks would make WD hang dumps misleading.

### Input Assembler Debug Registers

`IA_DEBUG_REG0` is a top-level IA activity summary. It includes extended and non-DMA busy state, DMA request/busy state, MC translator busy state, group busy/read/valid flags, clock-busy flags, and sclk validity flags.

`IA_DEBUG_REG1` and `IA_DEBUG_REG2` are parallel normal and high-priority DMA decode/status maps. Both expose input FIFO empty/full, start-new-packet markers, DMA request valid state, zero-index and buffer-type bits, request path, discard-first/second-chunk flags, TC return selection, last-read-request state, mask/data/request FIFO status, stage2-stage4 valid/ready handshakes, skid FIFO status, group DMA valid/read bits, current-data-valid, out-of-range detection, mask FIFO write enable, and return-data write enable. This symmetry is important: normal and high-priority DMA paths must be decoded with their own `hp_` masks rather than by reusing normal-path fields.

`IA_DEBUG_REG3` through `IA_DEBUG_REG9` cover per-pipe read-request validity/read/null/EOP/use-TC bits, MC/TC request ready/send state, pair/quad assembly state, current and previous index/data registers, EOP/null flags, DMA counter state, output FIFO state, and pipe selection arbitration. These fields bridge IA's front-end fetch/decode logic to VGT/WD and memory clients.

### VGT Debug Registers

`VGT_DEBUG_REG0` through `VGT_DEBUG_REG36` form the largest part of the debug range. The fields are mostly raw internal state from the VGT front end: busy/active signals, input and output FIFO status, per-pipe draw/request handshakes, primitive/thread-group/event/EOP flags, state-machine values, per-SE routing, counters, reserved `SPARE*` fields, and handshakes with IA, WD, and tessellation/geometry units.

Because these are generated hardware definitions, the field names are the authoritative semantic labels. Driver code should treat reserved/spare fields as read-only diagnostics unless the hardware programming guide explicitly assigns behavior. The dense use of `*_state_q`, `*_cnt_q`, `*_fifo_*`, `*_rtr`, and `*_dr` names indicates sampled pipeline state rather than persistent software state.

### Performance Counters

The VGT, IA, and WD perf-counter blocks use the same broad pattern:

- Select registers hold event selectors and modes. `VGT_PERFCOUNTER0_SELECT`/`1_SELECT` and `IA_PERFCOUNTER0_SELECT` can select two events (`PERF_SEL` and `PERF_SEL1`) plus `CNTR_MODE`, `PERF_MODE1`, and `PERF_MODE`. VGT/IA select1 registers add `PERF_SEL2`, `PERF_SEL3`, `PERF_MODE2`, and `PERF_MODE3`. Later counters expose narrower selectors with `PERF_SEL` and `PERF_MODE`.
- `WD_PERFCOUNTER0_SELECT` through `WD_PERFCOUNTER3_SELECT` each define an 8-bit `PERF_SEL` and upper-nibble `PERF_MODE`.
- Each counter has `*_LO__PERFCOUNTER_LO_MASK` and `*_HI__PERFCOUNTER_HI_MASK`, both full-width `0xffffffff`, so software must combine low and high halves carefully when reading a 64-bit count.
- `VGT_PERFCOUNTER_SEID__SEID_MASK` selects the shader-engine instance for VGT counter collection.

Programming these counters requires address definitions from the matching `gfx_8_1_d.h` file plus an ordering policy from the caller. This header only defines the field layout.

### DIDT Power Control Registers

`DIDT_IND_INDEX` and `DIDT_IND_DATA` are full-width 32-bit fields for selecting and accessing indirect DIDT registers. In the AMDGPU driver, indirect DIDT access is serialized by `adev->reg.didt.lock` in ASIC helpers such as `cik_didt_rreg`/`cik_didt_wreg` and `vi_didt_rreg`/`vi_didt_wreg`: the driver writes the index register, then reads or writes the data register.

The DIDT block definitions repeat the same register pattern across `SQ`, `DB`, `TD`, `TCP`, and `DBR`:

- `*_CTRL0` has enable, reference-clock, phase-offset, reset, clock-enable-override, and unused/reserved fields.
- `*_CTRL1` has `MIN_POWER` and `MAX_POWER` half-word fields.
- `*_CTRL2` has `MAX_POWER_DELTA`, `SHORT_TERM_INTERVAL_SIZE`, `LONG_TERM_INTERVAL_RATIO`, and reserved fields.
- `*_CTRL_OCP` provides an over-current protection maximum power field plus reserved bits.
- `*_WEIGHT0_3`, `*_WEIGHT4_7`, and `*_WEIGHT8_11` pack four 8-bit weight values per register.

PowerTune code uses these masks and shifts to build tables of per-domain DIDT parameters, then applies them through indirect DIDT register writes. The repeated layout across domains lowers software complexity but increases the risk of copy/paste mistakes when adding or adjusting a domain.

## Control Flow

This header contributes no control flow. Runtime flow is supplied by callers:

1. Include the ASIC address and mask headers matching the detected GPU generation.
2. Read a register or construct a new register value.
3. Clear a field with `value &= ~FIELD_MASK`.
4. Insert a field with `(field_value << FIELD_SHIFT) & FIELD_MASK`, or use a register-field helper.
5. Write the register through the correct MMIO or indirect register accessor.

DIDT indirect access has an extra two-step control flow: callers select the DIDT offset via `DIDT_IND_INDEX` and then transfer the value through `DIDT_IND_DATA`. Existing ASIC accessors lock around that index/data pair to avoid races between concurrent readers and writers.

## State And Persistence Behavior

The macros are compile-time constants and have no in-memory state. The state they describe lives in hardware registers:

- Debug registers are sampled hardware status. Reads reflect transient GPU pipeline state and are primarily useful during diagnostics, hang analysis, and hardware validation.
- Perf-counter select registers persist until reprogrammed or reset by the GPU/IP block. Counter low/high registers accumulate hardware events according to the selected event and mode.
- DIDT registers persist hardware power-control configuration until reset, suspend/resume reinitialization, ASIC reset, or another power-management path rewrites them.

Because DIDT and perf-counter fields affect live hardware behavior, caller-side read-modify-write sequencing matters. Reserved fields must be preserved unless the programming sequence intentionally initializes the entire register.

## Dependencies And Integration Points

This chunk depends on the matching GFX 8.1 register address header for `mm*` and `ix*` register offsets. It integrates with:

- AMDGPU register access helpers such as `RREG32`, `WREG32`, `RREG32_DIDT`, and `WREG32_DIDT`.
- ASIC-specific indirect DIDT accessors in `cik.c` and `vi.c`, which serialize `DIDT_IND_INDEX`/`DIDT_IND_DATA` access.
- Power-management code in `pm/legacy-dpm/kv_dpm.c` and `pm/powerplay/hwmgr/smu7_powertune.c`, which uses DIDT mask/shift pairs to enable blocks and program power-tuning tables.
- Debug and performance tooling paths that decode VGT/IA/WD debug registers or program/read their performance counters.
- Generated-register conventions shared with nearby headers such as `gfx_8_0_sh_mask.h`, later `gc_*_sh_mask.h` files, and helper macros that assume the `<REGISTER>__<FIELD>_{MASK,__SHIFT}` naming scheme.

## Risks And Edge Cases

- Mask/shift mismatches are high-impact despite the file being declarative: an incorrect mask can silently set reserved bits, fail to enable DIDT, select the wrong perf event, or misdecode a debug dump.
- The DIDT indirect window is race-prone if accessed without the existing lock. Interleaved index/data operations can read or write the wrong DIDT register.
- Full-width counter halves require careful 64-bit reads. If callers read high/low halves without considering rollover, sampled perf counts can be inconsistent.
- Debug fields are transient; tests or diagnostics that expect stable FIFO/handshake state must account for GPU activity and clock/power gating.
- Repeated DIDT layouts across `SQ`, `DB`, `TD`, `TCP`, and `DBR` invite wrong-domain macro use. A value intended for one domain may have the same bit layout but target a different hardware block.
- Reserved `SPARE*` and `UNUSED_*` fields should not be interpreted as stable software-visible ABI. They may differ across ASIC revisions even when nearby functional fields look similar.
- This is a generated hardware header. Manual edits can diverge from hardware source data and should be avoided unless they are part of a verified register-definition update.

## Test Signals

There are no direct unit tests for this header in the chunk. Useful validation signals are indirect:

- Successful compilation of AMDGPU code that includes GFX 8.1 register headers and references these masks.
- Power-management tests or hardware smoke tests that enable/disable DIDT on supported ASICs and verify stable clocks, power limits, and no GPU reset/hang.
- Register readback tests for DIDT programming: after table application, reading each DIDT register should show expected field values while preserving reserved bits.
- Perf-counter tests that program VGT/IA/WD selector fields, run known GPU workloads, and observe nonzero, monotonic, and domain-plausible low/high counter values.
- Debugfs or hang-dump validation that decodes VGT/IA/WD debug registers without field overlap, impossible bit positions, or all-zero/all-reserved interpretation.
- Static checks can verify that every field has exactly one mask and one shift, that masks do not overlap within a register except for documented full-register fields, and that `(mask >> shift)` has the intended field width.
