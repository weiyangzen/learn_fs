# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_sh_mask.h lines 17178-19721

## Scope

This chunk is a generated AMD GC 9.0 shift/mask register-header segment. It contains C preprocessor constants only: each hardware register field is represented by a `<REGISTER>__<FIELD>__SHIFT` macro and a matching `<REGISTER>__<FIELD>_MASK` macro for composing or decoding 32-bit GPU register values. There are no functions, structs, enums, global variables, includes, allocations, callbacks, locks, or executable branches in this range.

The selected lines begin at the tail of `VGT_HOS_REUSE_DEPTH`, then cover a large graphics pipeline state block: VGT primitive/group/tessellation/streamout controls, PA scan-converter/rasterizer controls, DB HTILE/stencil preload controls, color-buffer target state for `CB_COLOR0` through `CB_COLOR7`, and finally the beginning of the `gc_gfxudec` command-processor block through `CP_DRAW_INDX_INDR_ADDR`. Although the path is under a `ceph-client` source mirror, this file is AMDGPU DRM hardware metadata, not Ceph filesystem code.

## Purpose

`gc_9_0_sh_mask.h` supplies bit layouts for Graphics Core 9.0 registers. AMDGPU code pairs these field macros with register-address macros from the matching `gc_9_0_offset.h` header, then uses common register helpers such as `REG_SET_FIELD` and `REG_GET_FIELD` or packet construction paths to pack fields for MMIO writes, command-stream state, clear-state tables, hang dumps, and status decoding.

This chunk describes several hardware areas:

- VGT geometry and vertex reuse state: primitive grouping, GS mode/on-chip controls, ES/GS/VS ratios, GS ring offsets and item sizes, primitive ID behavior, DMA/index draw sizing, draw payload controls, instance stepping, tessellation distribution, shader-stage enablement, LS/HS configuration, TF parameters, streamout setup, and geometry shader output sizing.
- PA scan-converter and setup state: MSAA, viewport/scissor, line stipple and line control, centroid priority, vertex quantization, clip/discard adjustment constants, sample locations/masks for four pixel positions, shader/rasterizer control, binner control, conservative rasterization, NGG mode, vertex reuse block, and output deallocation controls.
- DB/color-related context state: HTILE surface policy, stencil-results compare state, preload control, and alpha-to-mask.
- Eight color target slots, `CB_COLOR0` through `CB_COLOR7`, each with base/ext address fields, dimensions/view, format/number type/component swap/blend options, DCC/compression controls, CMASK/FMASK/DCC metadata bases, and clear words.
- `gc_gfxudec` command-processor state: EOP done/fence addresses and data, streamout and pipeline-stat counter addresses, 64-bit primitive/invocation counters, scratch registers, append/atomic/GDS preop registers, ME memory read/write address/data registers, semaphore wait/signal addresses, CP DMA controls and address/command fields, coherency/invalidation controls, ring/IB/CE/ST offsets and buffer sizes, EOP done event/data controls, PFP/CE completion status, predicate status, metadata base addresses, and the first indirect draw address register.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit index of a register field.
- `<REGISTER>__<FIELD>_MASK` gives the 32-bit field mask.
- Register addresses are defined separately in `gc_9_0_offset.h`, for example `mmVGT_GS_MODE`, `mmCB_COLOR0_INFO`, `mmCP_DMA_ME_COMMAND`, and `mmCP_DRAW_INDX_INDR_ADDR`.

Important macro families in this slice include:

- `VGT_GROUP_*`, `VGT_GS_MODE`, `VGT_GS_ONCHIP_CNTL`, `VGT_GS_PER_ES`, `VGT_ES_PER_GS`, `VGT_GS_PER_VS`, `VGT_GSVS_RING_OFFSET_*`, `VGT_GS_OUT_PRIM_TYPE`, and `VGT_GS_MAX_*`: geometry/primitive grouping, GS execution mode, on-chip GS sizing, and GS/VS ring layout.
- `VGT_DMA_*`, `VGT_PRIMITIVEID_*`, `VGT_DRAW_PAYLOAD_CNTL`, `VGT_INSTANCE_STEP_RATE_*`, `VGT_REUSE_OFF`, `VGT_VTX_CNT_EN`, `VGT_SHADER_STAGES_EN`, `VGT_LS_HS_CONFIG`, `VGT_TESS_DISTRIBUTION`, and `VGT_TF_PARAM`: draw indexing, primitive ID reset/generation, tessellation and shader-stage selection, vertex reuse, and instance-rate state.
- `VGT_STRMOUT_*`, `VGT_DMA_EVENT_INITIATOR`, and `VGT_STRMOUT_DRAW_OPAQUE_*`: streamout buffer sizing, stride, offsets, opaque draw accounting, stream/buffer enable masks, and event generation.
- `PA_SC_MODE_CNTL_*`, `PA_SC_LINE_CNTL`, `PA_SC_AA_CONFIG`, `PA_SC_CENTROID_PRIORITY_*`, `PA_SC_AA_SAMPLE_LOCS_PIXEL_*`, `PA_SC_AA_MASK_*`, `PA_SC_SHADER_CONTROL`, `PA_SC_BINNER_CNTL_*`, `PA_SC_CONSERVATIVE_RASTERIZATION_CNTL`, and `PA_SC_NGG_MODE_CNTL`: scan conversion, sample placement, MSAA exposure, rasterization, binning, and NGG behavior.
- `PA_SU_*` and `PA_CL_GB_*`: setup/rasterizer point/line/polygon offset and guard-band clip/discard adjustment state.
- `DB_HTILE_SURFACE`, `DB_SRESULTS_COMPARE_STATE*`, `DB_PRELOAD_CONTROL`, and `DB_ALPHA_TO_MASK`: depth/stencil metadata policy, preload thresholds, stencil compare state, and alpha-to-coverage behavior.
- `CB_COLOR{0..7}_BASE`, `*_BASE_EXT`, `*_ATTRIB2`, `*_VIEW`, `*_INFO`, `*_ATTRIB`, `*_DCC_CONTROL`, `*_CMASK`, `*_FMASK`, `*_DCC_BASE`, `*_CLEAR_WORD0`, and `*_CLEAR_WORD1`: per-render-target color-buffer addresses, metadata addresses, dimensions, slice/mip view, format, compression/DCC policy, swizzle modes, sample/fragment counts, and clear values.
- `CP_EOP_*`, `CP_STREAM_OUT_*`, `CP_NUM_PRIM_*`, `CP_PIPE_STATS_*`, and `CP_*INVOC_COUNT*`: command-processor writeback addresses/data and pipeline-stat counter plumbing.
- `SCRATCH_REG*`, `SCRATCH_UMSK`, `SCRATCH_ADDR`, `CP_APPEND_*`, `CP_ATOMIC_*`, `CP_GDS_ATOMIC*`, and `CP_ME_GDS_ATOMIC*`: CP scratch, append, and pre-operation data surfaces.
- `CP_SIG_SEM_*`, `CP_WAIT_SEM_*`, `CP_WAIT_REG_MEM_TIMEOUT`, `CP_DMA_*`, `CP_COHER_*`, `CP_RB_OFFSET`, `CP_IB*_OFFSET`, `CP_CE_*`, `CP_ST_*`, `CP_EOP_DONE_*`, `CP_PFP_COMPLETION_STATUS`, `CP_CE_COMPLETION_STATUS`, and `CP_PRED_NOT_VISIBLE`: synchronization, DMA copy/fill, coherency/invalidation, ring/IB/CE/ST command buffers, EOP completion, and predicate status.

## Control Flow

This header has no runtime control flow. Its only direct behavior is compile-time macro substitution.

The implied runtime flow in AMDGPU consumers is:

1. Select the GC 9.0 generated register headers for the detected ASIC.
2. Choose a register address from `gc_9_0_offset.h`.
3. Read the current register value or build a context/command-packet value.
4. Use these `__SHIFT` and `__MASK` constants, commonly through `REG_SET_FIELD` or `REG_GET_FIELD`, to pack or extract field values.
5. Write the value through MMIO, program it into a context/clear-state packet, emit it in a command stream, or decode it during diagnostics.

For VGT/PA/DB/CB context registers, normal flow is graphics pipeline setup before draw execution. The driver or userspace command stream programs vertex/index/tessellation/geometry/streamout, rasterization/MSAA/binning, depth/stencil metadata, and render-target descriptors so the hardware can launch and rasterize work with the expected target layout.

For the CP block, normal flow is command-processor synchronization and writeback setup. Runtime code programs EOP fence and event destinations, streamout/pipeline-stat counter writeback addresses, semaphore wait/signal targets, DMA source/destination/command fields, coherency flush ranges/actions, ring and indirect-buffer offsets, CE/ST command buffers, and completion/predicate status handling. The macros do not encode the required packet ordering, cache flush waits, VMID ownership, or engine-specific sequencing.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe stateful GPU registers whose values are owned by hardware, firmware, ring initialization, command submission, and context switching.

VGT, PA, DB, and CB registers are mostly draw/context state. Values persist until another context or packet rewrites them, a clear-state sequence restores defaults, or the GPU resets. Incorrect render-target base/ext fields, metadata bases, swizzle modes, DCC/CMASK/FMASK settings, sample counts, slice/mip views, or clear words can corrupt memory, render into the wrong address, produce incorrect colors, or break compression/decompression. VGT/PA mistakes can produce malformed primitive assembly, missing geometry, incorrect streamout counters, wrong tessellation or GS behavior, bad sample coverage, and rasterizer/binning artifacts.

The CP registers represent command-processor state, counters, addresses, synchronization, and command-buffer bookkeeping. Fence and EOP writeback addresses/data, append/atomic preop registers, semaphore addresses, DMA source/destination addresses, coherency base/size/action fields, ring/IB offsets, CE buffer bases/sizes, and metadata/indirect-draw addresses persist until reprogrammed. Status fields such as completion, predicate, coherency status, DMA FIFO state, and read tags are live hardware state and may change while engines run.

Many full-width masks in this range are still semantically constrained. Address fields are split into low/high registers and frequently use alignment units such as 256-byte or 4-byte granularity. Counter and data fields may be latched or written by hardware. Control fields can trigger side effects, including DMA execution, cache invalidation/writeback, semaphore signaling/waiting, EOP writeback, and command-buffer loading.

## Dependencies And Integration Points

This chunk depends on the generated GC 9.0 register set remaining synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_offset.h` provides matching register addresses and base indices.
- Other generated GC 9.0 headers, including defaults and enums where present, provide reset values and symbolic field values that consumers may pair with these masks.
- Common AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32*`, `WREG32*`, `SOC15_REG_OFFSET`, command-packet builders, golden-register tables, and clear-state arrays consume these definitions.
- `drivers/gpu/drm/amd/amdgpu/clearstate_gfx9.h` contains clear-state values for related registers such as `VGT_GS_MODE`, `PA_SC_BINNER_CNTL_0`, and `CB_COLOR0_INFO`.

Integration points include graphics ring setup, context/clear-state emission, draw and indirect draw paths, tessellation/geometry/NGG setup, streamout, pipeline statistics queries, render-target and DCC/CMASK/FMASK metadata programming, MSAA sample position setup, depth/stencil metadata setup, CP DMA packets, EOP fence/event handling, semaphore synchronization, cache coherency events, indirect-buffer/ring management, constant-engine command buffers, predicate control, and hang/debug dumps.

## Risks And Edge Cases

- Generated-header drift is the dominant risk. A wrong shift or mask compiles cleanly but writes the wrong hardware bits or decodes misleading status.
- The chunk starts and ends mid-family. It begins after `VGT_HOS_REUSE_DEPTH__REUSE_DEPTH__SHIFT` and ends at `CP_DRAW_INDX_INDR_ADDR`; adjacent chunks are required for the complete HOS/tessellation context before line 17178 and the rest of the CP indirect draw/index/sample/GDS definitions after line 19721.
- The eight `CB_COLOR*` register families are structurally repetitive but target different render slots. Copy/paste or indexing mistakes can bind one slot's base/metadata/format to another slot.
- Full-register writes can damage reserved bits or unrelated fields. Many context registers should be updated through field helpers or known-good packet values rather than ad hoc constants.
- Address fields with `_BASE_256B`, `_ADDR_LO`, `_ADDR_HI`, or shifted low-address masks require correct alignment and high/low splitting. Incorrect packing can cause GPU writes to arbitrary memory.
- DCC, CMASK, FMASK, fast clear, blend optimization, sample/fragment count, swizzle mode, and pipe/RB alignment fields must match the actual BO layout and metadata allocation. Mismatches may appear as subtle corruption, not immediate faults.
- VGT GS/tessellation/streamout fields must match shader compiler output and pipeline state. Bad ring sizes, item sizes, stream masks, primitive IDs, or tessellation distribution can hang or lose geometry.
- PA sample-location, AA mask, centroid, conservative-raster, binner, and NGG fields affect coverage and primitive distribution; small field errors can create workload-specific rendering differences.
- CP DMA, coherency, semaphore, EOP, and IB/CE/ST fields have side effects. Misprogramming can lead to stale cache data, missed fences, stuck waits, invalid command buffer fetches, out-of-order memory visibility, or GPU reset loops.
- Live status/counter fields may be volatile or hardware-updated. Diagnostic reads need appropriate synchronization if they are used as test or recovery signals.

## Test Signals

Useful validation is mostly generated-data consistency, build coverage, and hardware runtime behavior:

- Kernel build coverage for AMDGPU paths that include `gc_9_0_sh_mask.h`, especially GC 9.0 graphics, clear-state, ring, CP DMA, fence, query, debug, reset, and KFD/compute integration paths.
- Mechanical comparison against AMD's authoritative GC 9.0 register database to confirm every `__SHIFT` and `__MASK` value in this slice.
- Cross-checks that every register family in this chunk has matching address macros in `gc_9_0_offset.h` and expected default/clear-state entries where applicable.
- Static mask/shift sanity checks: masks align with shifts, fields in each register do not overlap unexpectedly, full-width fields use `0xFFFFFFFFL`, 256-byte and 4-byte address-unit fields have the expected low-bit masks, and repeated `CB_COLOR{0..7}` definitions stay slot-consistent.
- Graphics draw tests covering indexed and indirect draws, primitive ID reset/generation, tessellation, GS/on-chip GS, streamout, vertex reuse, NGG mode, binner transitions, conservative rasterization, line/point/polygon offset, MSAA sample locations, centroid selection, alpha-to-mask, and viewport/scissor behavior.
- Render-target stress tests covering all eight color slots, multiple mips/slices, MSAA fragments/samples, DCC enablement, fast clears, CMASK/FMASK metadata, clear words, swizzle modes, resource types, RB/pipe alignment, and blend optimization paths.
- Depth/stencil/HTILE tests that exercise HTILE surface policy, stencil compare state, preload controls, and interactions with color/alpha-to-mask output.
- Query and streamout tests that validate `CP_NUM_PRIM_*`, `CP_VGT_*`, `CP_PA_*`, `CP_SC_*`, `CP_PIPE_STATS_*`, streamout filled-size counters, and opaque streamout draw state.
- Synchronization tests for EOP fence writeback, event data selection, semaphore signal/wait, predicate state, PFP/CE completion status, CP DMA source/destination/cache policy, coherency base/size/action fields, and ring/IB/CE/ST buffer offsets.
- Runtime warning signals include bad render-target output, DCC/metadata corruption, lost streamout data, incorrect query counters, stuck CP coherency status, CP DMA FIFO saturation, missed EOP fences, semaphore timeouts, invalid indirect draw addresses, and repeated GPU resets.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002622`. It covers lines 17178-19721 of `gc_9_0_sh_mask.h`. The final per-file research should merge this with adjacent chunks to complete the surrounding HOS/tessellation definitions before this range and the remaining command-processor indirect draw/index/GDS/sample-status definitions after this range.
