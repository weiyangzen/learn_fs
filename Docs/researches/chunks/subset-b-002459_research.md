# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_sh_mask.h lines 24791-27308

## Scope

This chunk is a generated AMD GC 10.1.0 shift/mask header slice. The requested range spans lines 24791-27308 of `gc_10_1_0_sh_mask.h`, containing 2,143 `#define` entries and 373 visible register/comment groups. Each register field is represented as one or both of:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit position for the field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for the field inside a 32-bit register.

The range starts in the middle of `VGT_GS_MODE`: the comment and early shift/mask fields are in the previous chunk, while this chunk starts at `VGT_GS_MODE__PARTIAL_THD_AT_EOI_MASK` and finishes that register's masks. It ends on the comment for `CP_WAIT_SEM_ADDR_LO`; that register's actual field definitions begin in the next chunk.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU graphics hardware metadata, not Ceph or distributed filesystem logic. It is declarative C preprocessor data used by the Linux AMDGPU and AMDKFD driver code for GC 10.1/Navi-era register programming.

## Purpose

`gc_10_1_0_sh_mask.h` gives driver code symbolic names for bit placement in GC 10.1.0 hardware registers. This chunk covers a large graphics pipeline and command-processor area:

- Vertex grouper/tessellator/input assembler setup: `VGT_*`, `IA_*`, and `WD_*` registers for GS/ES/VS/HS/DS topology, primitive grouping, DMA index handling, primitive IDs, streamout, shader-stage enables, NGG, and tessellation factors.
- Scan converter, setup, clipping, rasterization, antialiasing, and depth-buffer helpers: `PA_SC_*`, `PA_SU_*`, `PA_CL_*`, `DB_*`, and `GE_*` registers.
- Color buffer render-target state for slots 0-7: `CB_COLORn_*` base, pitch, slice, view, format/info, attributes, DCC, CMASK, FMASK, clear colors, extended base-address registers, and `ATTRIB2/ATTRIB3`.
- The start of the `gc_gfxudec` address block: command processor end-of-pipe, streamout, pipeline statistics, performance counter, scratch, append, atomic preoperation, memory-controller read/write, and semaphore address/timer registers.

The practical purpose is to keep register programming readable and ASIC-specific. Consumers can construct values such as `FIELD_VALUE << FIELD__SHIFT` and mask updates with `FIELD_MASK` without hard-coding numeric bit positions.

## Important APIs, Types, And Macros

There are no callable functions, structs, enums, global variables, locks, allocation paths, or runtime MMIO operations in this range. The exported interface is only C preprocessor constants.

Important macro families in this chunk include:

- `VGT_GS_MODE` tail and `VGT_GS_ONCHIP_CNTL`: geometry shader mode/on-chip sizing fields such as partial thread behavior, cut suppression, ES/GS write optimization, on-chip mode, ES vertices per subgroup, GS primitives per subgroup, and GS instance primitives per subgroup.
- `PA_SC_MODE_CNTL_0` and `PA_SC_MODE_CNTL_1`: scan-converter mode bits for MSAA, viewport scissor, line stipple, tile-walk/supertile-walk controls, ZMM extents, post-HiZ kill behavior, multi-shader-engine/multi-GPU primitive discard, GPU ID override, forced EOV behavior, and out-of-order primitive watermarks.
- `VGT_DMA_SIZE`, `VGT_DMA_MAX_SIZE`, and `VGT_DMA_INDEX_TYPE`: index-buffer DMA count, maximum count, index type, byte swap, buffer type, request policy, ATC, EOP, request path, and memory type fields.
- `VGT_PRIMITIVEID_EN`, `VGT_PRIMITIVEID_RESET`, `VGT_MULTI_PRIM_IB_RESET_EN`, `VGT_DRAW_PAYLOAD_CNTL`, `VGT_EVENT_INITIATOR`, and `VGT_DMA_EVENT_INITIATOR`: primitive ID generation/reset, multi-primitive index-buffer reset, draw payload enables, and event-initiation fields.
- `IA_MULTI_VGT_PARAM`, `VGT_ESGS_RING_ITEMSIZE`, `VGT_GSVS_RING_ITEMSIZE`, `VGT_GS_VERT_ITEMSIZE[_1..3]`, `VGT_GS_PER_ES`, `VGT_ES_PER_GS`, `VGT_GS_PER_VS`, and `VGT_GSVS_RING_OFFSET_[1..3]`: graphics pipeline sizing and ring layout values.
- `VGT_SHADER_STAGES_EN`, `VGT_LS_HS_CONFIG`, `VGT_TF_PARAM`, `VGT_TESS_DISTRIBUTION`, and `GE_NGG_SUBGRP_CNTL`: shader-stage enable fields, NGG/primitive-generation controls, tessellation partitioning/topology/distribution, DS wave count, memory type, and LS/HS patch control.
- `VGT_STRMOUT_*`: streamout buffer size, stride, offset, opaque draw offset/filled-size/stride, streamout enable/configuration, buffer enables, and primitive-needed count control.
- `DB_HTILE_SURFACE`, `DB_SRESULTS_COMPARE_STATE0/1`, `DB_PRELOAD_CONTROL`, and `DB_ALPHA_TO_MASK`: depth/HTILE surface fields, stencil result comparison state, DB preload windows, and alpha-to-mask offsets.
- `PA_SU_POLY_OFFSET_*`, `PA_SU_VTX_CNTL`, `PA_CL_GB_*`, `PA_SC_CENTROID_PRIORITY_*`, `PA_SC_LINE_CNTL`, `PA_SC_AA_CONFIG`, `PA_SC_AA_SAMPLE_LOCS_*`, `PA_SC_AA_MASK_*`, `PA_SC_SHADER_CONTROL`, `PA_SC_BINNER_CNTL_0/1`, `PA_SC_CONSERVATIVE_RASTERIZATION_CNTL`, and `PA_SC_NGG_MODE_CNTL`: viewport/depth bias, clip/discard guard bands, centroid priority, lines, AA sample locations/masks, shader control, binning, conservative rasterization, and NGG scan-converter mode.
- `CB_COLOR0_*` through `CB_COLOR7_*`: repeated render-target slot metadata. Each slot has base, pitch, slice, view, `INFO`, `ATTRIB`, `DCC_CONTROL`, CMASK/FMASK addresses and slices, clear words, DCC base, extended base fields, `ATTRIB2`, and `ATTRIB3`.
- `CP_EOP_*`, `CP_STREAM_OUT_*`, `CP_NUM_PRIM_*`, `CP_PIPE_STATS_*`, `CP_VGT_*COUNT*`, `CP_PA_*COUNT*`, `CP_SC_*COUNT*`, and `CP_VGT_CSINVOC_COUNT*`: command processor addresses/data/fences and 64-bit low/high counter registers for graphics pipeline statistics.
- `SCRATCH_REG0` through `SCRATCH_REG7`, `SCRATCH_UMSK`, and `SCRATCH_ADDR`: scratch register fields, including obsolete mask/swap/address aliases retained in the register description.
- `CP_APPEND_*`: append addresses, data, last CS/PS fence fields, DDID count, cache policy, command selection, and CS/PS selector.
- `CP_PFP_ATOMIC_*`, `CP_ME_ATOMIC_*`, `CP_GDS_ATOMIC*`, and `CP_ME_GDS_ATOMIC*`: preoperation low/high values for CP/PFP/ME atomics and GDS atomics.
- `CP_ME_MC_WADDR_*`, `CP_ME_MC_WDATA_*`, `CP_ME_MC_RADDR_*`: command-processor micro-engine memory-controller write/read address and data fields, including address alignment and cache policy.
- `CP_SEM_WAIT_TIMER`, `CP_SIG_SEM_ADDR_LO/HI`, and `CP_WAIT_REG_MEM_TIMEOUT`: semaphore wait timer, signal semaphore address/swap/use-mailbox/signal-type/client/select fields, and wait-register-memory timeout. The next chunk owns the fields for `CP_WAIT_SEM_ADDR_LO`.

## Control Flow

This header has no local control flow. It does not branch, loop, validate inputs, read registers, or write registers. Runtime behavior is supplied by driver code that includes this header and uses the macros when composing register writes or decoding register reads.

Typical usage is:

1. A GC 10.x AMDGPU or AMDKFD source file includes `gc/gc_10_1_0_offset.h` for register offsets and `gc/gc_10_1_0_sh_mask.h` for fields.
2. The driver computes a register address through SOC15 helpers or PM4 packet encoding.
3. The driver builds the field value with the matching `__SHIFT` and `_MASK` constants.
4. MMIO helpers, ring packets, queue descriptors, or command packets carry the final 32-bit register value to the GPU.

Direct include sites found in this tree include:

- `drivers/gpu/drm/amd/amdgpu/gfx_v10_0.c`, the main GFX10 AMDGPU implementation.
- `drivers/gpu/drm/amd/amdgpu/nv.c`, `gfxhub_v2_0.c`, `mxgpu_nv.c`, `sdma_v5_0.c`, `mmhub_v2_0.c`, `amdgpu_sdma.c`, and `amdgpu_amdkfd_gfx_v10.c`.
- `drivers/gpu/drm/amd/amdkfd/kfd_packet_manager_v9.c`, `kfd_mqd_manager_v10.c`, and `kfd_device_queue_manager_v10.c`.

Many registers in this particular chunk are also represented by clear-state tables such as `amdgpu/clearstate_gfx10.h`, where the register names appear as comments with reset/clear values. The macros here provide the field-level view, while those tables provide prebuilt state packets.

## State And Persistence Behavior

This chunk stores no software state. Its constants describe hardware-visible state that persists according to GPU register, context, reset, power, VM, queue, and command-processor rules.

State represented by the VGT/IA/GE/WD portion includes:

- Primitive grouping, index-buffer interpretation, primitive ID behavior, event initiation, draw payload fields, instance step rates, shader-stage enables, tessellation parameters, GS/ES/VS ring item sizes, streamout configuration, and NGG/primitive-generation settings.
- Values written here can be per-draw, per-context, or part of graphics clear state depending on how the command stream programs them.

State represented by the PA/DB/CB portion includes:

- Rasterizer/scissor/tile-walk behavior, AA sample positions and masks, centroid priority, line rules, conservative rasterization mode, binning behavior, depth/HTILE state, alpha-to-mask behavior, and render-target slot configuration.
- Color target state is repeated for eight slots. The base, pitch, slice, view, format, DCC, CMASK, FMASK, clear color, and extended base registers together define where render output lands in memory and how compression/metadata is interpreted.

State represented by the CP/gfxudec portion includes:

- EOP and streamout memory addresses/data/fences, primitive and shader invocation counters, pipe-statistics destination/control/doorbell registers, scratch registers, append/fence state, atomic preoperation values, micro-engine memory-controller read/write state, and semaphore wait/signal address fields.
- Low/high counter pairs are effectively 64-bit values split across two 32-bit registers by hardware convention. Software must read or write paired registers consistently if it needs a coherent value.
- Doorbell offset fields are aligned from bit 2 (`0x0FFFFFFC` masks), so callers must preserve hardware-required low-bit alignment.

Fields with names such as `COUNT`, `STATUS`, `DONE`, `OBSOLETE`, `LAST_FENCE`, or `SCRATCH` can have special read/write semantics in the hardware, but this header does not encode those semantics. It only exposes bit placement.

## Dependencies And Integration Points

The syntactic dependency is the C preprocessor. Semantically, this generated header must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_offset.h`, which supplies the corresponding register offsets and base indices.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_default.h`, which supplies default values for many GC 10.1.0 registers.
- SOC15 access helpers and register-table macros in the AMDGPU driver, which combine HWIP instance, register offset, base index, shift, and mask data.
- AMDKFD packet and MQD code, which includes this header when constructing process, queue, and dispatch metadata for GFX9/GFX10-family hardware.
- User-mode graphics and compute stacks indirectly, because command streams and queue descriptors depend on these fields matching the ASIC register database.

The range is centered on the programmable graphics pipeline state used by draw and compute submission paths:

- Graphics command streams rely on VGT/PA/DB/CB fields to interpret topology, tessellation, shader stages, render-target layout, antialiasing, streamout, depth/stencil, and rasterization.
- Kernel queue management and KFD paths rely on adjacent GC 10.1 definitions for queue descriptors, process state, and trap/debug-related packet fields.
- Reset, suspend/resume, GPU recovery, virtualization, and clear-state initialization depend on these register definitions matching the firmware and hardware expectations for the selected ASIC family.

## Risks And Edge Cases

- The chunk starts in the middle of `VGT_GS_MODE`, so final per-file analysis must merge this with the previous chunk before treating `VGT_GS_MODE` as complete.
- The chunk ends on `CP_WAIT_SEM_ADDR_LO` with no fields for that register. The next chunk owns the actual wait semaphore address low definitions.
- Generated-header drift is the core risk. A wrong shift or mask compiles cleanly but can place a field into an adjacent bit, causing rendering corruption, hangs, bad counters, wrong memory addresses, or missed synchronization.
- Repeated `CB_COLOR0` through `CB_COLOR7` layouts are easy to validate mechanically but easy to misread manually. A slot-specific typo could affect only particular MRT configurations.
- Address fields split into low/high or base/ext registers require coordinated programming. Mixing old and new halves can direct CP, streamout, append, CMASK, FMASK, DCC, or color output to the wrong memory location.
- Several fields control compression metadata (`DCC`, `CMASK`, `FMASK`, HTILE). Incorrect masks can create silent corruption rather than immediate faults because metadata and surface payload no longer agree.
- Counter registers are split into low/high pairs. Reading them without rollover handling can produce inconsistent values even when bit definitions are correct.
- `OBSOLETE` fields are still defined. Their presence should not be interpreted as safe or useful for new code without checking the hardware database and driver access layer.
- Doorbell and semaphore address fields encode alignment and selection bits. Incorrect masks or shifts can break queue signaling, EOP completion, streamout completion, pipe statistics, or semaphore waits.
- Reserved, status, test, and control fields all use the same macro style. This header alone does not tell callers which fields are writable, read-only, sticky, write-one-to-clear, privileged, or context-saved.
- The file is broad GC metadata, not Ceph logic. Distributed filesystem tests will not exercise these definitions unless they build or load the mirrored AMDGPU tree.

## Test Signals

Useful validation is mostly build-time, generator-level, and hardware-integration oriented:

- Build AMDGPU and AMDKFD code paths that include `gc_10_1_0_offset.h` and `gc_10_1_0_sh_mask.h`, especially `gfx_v10_0.c`, KFD MQD management, KFD packet management, SDMA, GFXHUB, MMHUB, and NV initialization.
- Mechanically verify that each complete register field in this range has a matching `__SHIFT` and `_MASK`, with documented exceptions for the partial `VGT_GS_MODE` start and `CP_WAIT_SEM_ADDR_LO` boundary.
- Cross-check the range against the authoritative GC 10.1.0 register database and `gc_10_1_0_offset.h`, especially around address-block transition `gc_gfxudec`.
- Compare repeated render-target groups (`CB_COLOR0_*` through `CB_COLOR7_*`) for intentional symmetry and slot-number-only differences.
- Run graphics tests that exercise tessellation, geometry shaders, NGG/primitive generation, streamout, indexed draws, primitive IDs, multisampling, conservative rasterization, scissor/viewport behavior, depth/stencil/HTILE, alpha-to-mask, and multiple render targets.
- Run workloads using DCC/CMASK/FMASK and clear/decompress paths, then validate output and metadata behavior across suspend/resume and GPU reset.
- Exercise CP event, EOP, streamout, pipe-statistics, primitive-count, shader-invocation-count, append/fence, scratch, atomic-preop, memory-controller read/write, and semaphore paths with register dumps or tracepoints.
- Validate doorbell and semaphore signaling under normal queue submission, queue teardown, GPU reset, and virtualization/SR-IOV flows.
- Use register dumps before and after clear-state programming to confirm `PA_SC_MODE_CNTL_*`, `VGT_SHADER_STAGES_EN`, `VGT_TF_PARAM`, `CB_COLORn_*`, and `CP_*` fields decode as expected.

## Chunk Notes For Merge

This document intentionally covers only lines 24791-27308 of `gc_10_1_0_sh_mask.h`. Adjacent chunks must provide the earlier `VGT_GS_MODE` comment and initial fields, plus the `CP_WAIT_SEM_ADDR_LO` definitions after this chunk boundary. The final per-file document should treat this source as generated AMD GC 10.1.0 register metadata used by AMDGPU/AMDKFD, not as handwritten runtime logic.
