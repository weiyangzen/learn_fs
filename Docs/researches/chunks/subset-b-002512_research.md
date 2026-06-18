# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_sh_mask.h lines 19875-22323

## Purpose

This chunk is generated AMD GC 11.0.0 register bitfield metadata. It contains no executable C code; it publishes `__SHIFT` and `_MASK` constants for packing and decoding 32-bit graphics context, shader, rasterizer, color-buffer, depth-buffer, VRS, and draw-control registers. Driver code combines these constants with register offsets from companion generated headers such as `gc_11_0_0_offset.h` and register helpers such as `REG_SET_FIELD`, `FIELD_GET`, `SOC15_REG_OFFSET`, `RREG32_SOC15`, and `WREG32_SOC15`.

Although the repository subtree is under `ceph-client`, this file is AMDGPU hardware metadata, not filesystem logic.

## Important APIs, Types, And Macros

There are no functions, structs, enums, callbacks, locks, allocations, or global variables in this range. The interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's low bit.
- `<REGISTER>__<FIELD>_MASK` gives the in-register bit mask.

Major register groups in this chunk:

- Viewport scissor and depth ranges: the slice starts inside `PA_SC_VPORT_SCISSOR_9_TL`, then defines `PA_SC_VPORT_SCISSOR_9_BR` through `PA_SC_VPORT_SCISSOR_15_BR`, with `TL_X`, `TL_Y`, `BR_X`, `BR_Y`, and `WINDOW_OFFSET_DISABLE` masks. It also defines `PA_SC_VPORT_ZMIN_0`/`ZMAX_0` through `ZMIN_15`/`ZMAX_15`, all as full-width viewport depth values.
- Raster/scissor routing and context IDs: `PA_SC_RASTER_CONFIG`, `PA_SC_RASTER_CONFIG_1`, `PA_SC_SCREEN_EXTENT_CONTROL`, `PA_SC_TILE_STEERING_OVERRIDE`, `CP_PERFMON_CNTX_CNTL`, `CP_PIPEID`, `CP_RINGID`, `CP_VMID`, and `CONTEXT_RESERVED_REG0/1`.
- Variable rate shading and rate-surface metadata: `PA_SC_VRS_OVERRIDE_CNTL`, `PA_SC_VRS_RATE_FEEDBACK_BASE`, `PA_SC_VRS_RATE_FEEDBACK_BASE_EXT`, `PA_SC_VRS_RATE_FEEDBACK_SIZE_XY`, `PA_SC_VRS_RATE_CACHE_CNTL`, `PA_SC_VRS_RATE_BASE`, `PA_SC_VRS_RATE_BASE_EXT`, and `PA_SC_VRS_RATE_SIZE_XY`. These expose VRS override combiner/rate bits, feedback writeback enable, VRS surface enable, 256-byte base-address fields, XY extents, and cache policy knobs.
- Color/depth fixed-function state: `CB_RMI_GL2_CACHE_CONTROL`, `CB_BLEND_RED/GREEN/BLUE/ALPHA`, `CB_FDCC_CONTROL`, `CB_COVERAGE_OUT_CONTROL`, `DB_STENCIL_CONTROL`, `DB_STENCILREFMASK`, and `DB_STENCILREFMASK_BF`.
- Viewport transform and user clip planes: `PA_CL_VPORT_XSCALE`, `XOFFSET`, `YSCALE`, `YOFFSET`, `ZSCALE`, and `ZOFFSET` are repeated for viewport indices 0-15. `PA_CL_UCP_0_X/Y/Z/W` through `PA_CL_UCP_5_X/Y/Z/W` define full-width user clip plane coefficients, followed by `PA_CL_PROG_NEAR_CLIP_Z`.
- Shader-processor pixel-input setup: `PA_RATE_CNTL` and `SPI_PS_INPUT_CNTL_0` through `SPI_PS_INPUT_CNTL_31`. The PS input controls pack parameter `OFFSET`, default values, flat shading, primitive attribute selection, duplication, FP16 interpolation, and attribute-valid bits; entries 0-19 also include point-sprite texture fields while later entries omit those fields.
- Shader export and interpolation configuration: `SPI_VS_OUT_CONFIG`, `SPI_PS_INPUT_ENA`, `SPI_PS_INPUT_ADDR`, `SPI_INTERP_CONTROL_0`, `SPI_PS_IN_CONTROL`, `SPI_BARYC_CNTL`, `SPI_TMPRING_SIZE`, `SPI_GFX_SCRATCH_BASE_LO/HI`, `SPI_SHADER_IDX_FORMAT`, `SPI_SHADER_POS_FORMAT`, `SPI_SHADER_Z_FORMAT`, and `SPI_SHADER_COL_FORMAT`.
- Shader export/color blend optimization: `SX_PS_DOWNCONVERT_CONTROL`, `SX_PS_DOWNCONVERT`, `SX_BLEND_OPT_EPSILON`, `SX_BLEND_OPT_CONTROL`, `SX_MRT0_BLEND_OPT` through `SX_MRT7_BLEND_OPT`, and `CB_BLEND0_CONTROL` through `CB_BLEND7_CONTROL`.
- Draw and primitive assembly state: `GFX_COPY_STATE`, point size/radius registers, `VGT_DMA_BASE_HI`, `VGT_DMA_BASE`, `VGT_DRAW_INITIATOR`, `VGT_EVENT_ADDRESS_REG`, and `GE_MAX_OUTPUT_PER_SUBGROUP`.
- Depth, clipping, rasterization, and primitive filtering: `DB_DEPTH_CONTROL`, `DB_EQAA`, `CB_COLOR_CONTROL`, `DB_SHADER_CONTROL`, `PA_CL_CLIP_CNTL`, `PA_SU_SC_MODE_CNTL`, `PA_CL_VTE_CNTL`, `PA_CL_VS_OUT_CNTL`, `PA_CL_NANINF_CNTL`, `PA_SU_LINE_STIPPLE_CNTL`, `PA_SU_LINE_STIPPLE_SCALE`, `PA_SU_PRIM_FILTER_CNTL`, and `PA_SU_SMALL_PRIM_FILTER_CNTL`.
- The chunk ends at the first field of `PA_CL_NGG_CNTL` (`VERTEX_REUSE_OFF__SHIFT`); the remaining `PA_CL_NGG_CNTL` masks and following PA registers belong to the next chunk.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by consumers:

1. ASIC-specific code includes `gc/gc_11_0_0_sh_mask.h` with compatible GC 11 offset headers.
2. Driver or command-submission code selects a concrete register offset for the GC block and ASIC instance.
3. The code composes values using the generated masks/shifts or decodes hardware state read from MMIO, indirect registers, command processor state, or saved context images.
4. Surrounding driver paths handle sequencing, locking, reset, suspend/resume, command-stream packet construction, firmware cooperation, and user-mode API validation.

For draw and graphics state, these masks are normally consumed indirectly through PM4 context-register packets or clear-state tables rather than by ad hoc MMIO writes. For example, `clearstate_gfx11.h` contains initial values for many registers in this exact range, including VRS rate registers, all `SPI_PS_INPUT_CNTL_*` registers, pixel input masks, blend controls, depth controls, and clipping/rasterization controls.

## State And Persistence Behavior

The file stores no software state and persists nothing by itself. It describes hardware-visible state that is programmed by the kernel driver, firmware, or command streams and then lives in GPU context state until changed, reset, or restored.

The viewport, scissor, Z range, VRS, SPI interpolation, SX/CB blend, DB depth/stencil, PA clipping, and VGT draw fields represent graphics pipeline state. Some fields are part of per-context state saved/restored by the command processor or initialized through clear-state images; others are programmed by kernel initialization or command buffers. Values can be lost or reset across GPU reset, suspend/resume, graphics context teardown, or power transitions unless reloaded by the appropriate driver/firmware path.

The base-address style fields, such as VRS rate/feedback bases and VGT DMA base fields, encode hardware address fragments rather than arbitrary CPU pointers. Their persistence and coherency depend on GPU virtual-memory setup, command submission lifetime, cache policy fields, and reset handling. Full-width masks such as `0xFFFFFFFFL` on viewport floats, clip-plane coefficients, blend constants, and scratch/base fields mean "all bits in the register are payload," not that every payload is valid in every hardware mode.

The macros do not encode access class. Fields may be read-only, write-only, write-one-to-clear, self-clearing, sticky, reserved, context-save-only, command-packet-only, or MMIO-accessible depending on the hardware specification and offset header.

## Dependencies And Integration Points

Direct dependencies are the matching generated GC 11 offset and hardware-definition headers. Include users in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v11_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v11.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v3_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v6_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mes_v11_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/imu_v11_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/soc21.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_v11.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_v11.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_plane.c`

Important integration points include:

- GFX11 initialization, register access self-tests, reset, clock/power management, interrupt setup, and ring command emission in `gfx_v11_0.c`.
- Clear-state programming in `clearstate_gfx11.h`, which provides reset/default graphics context values for many registers covered by this slice.
- Command stream construction for graphics context registers, including `PACKET3_SET_CONTEXT_REG` and related PM4 packets. The header defines the bit layout; packet builders and user-mode drivers decide when specific fields are emitted.
- Graphics pipeline state supplied by Mesa/ROCm/user command buffers and validated by kernel command submission, especially SPI pixel inputs, blend controls, depth/stencil state, viewport transforms, VRS, and clip/rasterization controls.
- Display-plane and DCN integration through `amdgpu_dm_plane.c`, which includes this header for GPU-side surface/format/rate-control definitions used around display scanout and graphics/display interop.
- KFD and MES integration, which include the same GC11 mask header for queue, shader, and context-state programming even when this particular slice is more graphics-state heavy than compute-queue heavy.

## Risks And Edge Cases

- Header/offset mismatch is the main structural risk. These untyped constants can compile with the wrong generated offset family and silently target incorrect bit positions or registers.
- The chunk starts and ends mid-register-family: it begins after the first `PA_SC_VPORT_SCISSOR_9_TL` field and ends before the complete `PA_CL_NGG_CNTL` block. Adjacent chunks are required for a complete per-file view.
- Context-register sequencing matters. Programming dependent SPI, PA, DB, CB, SX, and VGT fields out of order can produce malformed rendering, hangs, or stale context state even though each field value is syntactically valid.
- Repeated register families are off-by-one prone: 16 viewport transforms, 16 viewport Z ranges, 32 PS input controls, eight MRT blend-optimization registers, and eight CB blend-control registers all share nearly identical layouts.
- Not all repeated PS input controls are identical. `SPI_PS_INPUT_CNTL_0` through `_19` include point-sprite texture fields, while `_20` through `_31` omit them; code that assumes a uniform 32-entry layout can write nonexistent/reserved bits.
- Address and size fields have hardware units. VRS base registers use 256-byte granularity, VRS size fields use packed X/Y maxima, VGT event addresses expose low address bits only, and base high registers often expose a limited number of upper bits.
- Cache-policy fields in `PA_SC_VRS_RATE_CACHE_CNTL` and `CB_RMI_GL2_CACHE_CONTROL` affect coherency and performance. Wrong policies can cause stale VRS rate reads, incorrect color/DCC behavior, or workload-specific performance regressions.
- VRS combiner/rate fields interact with primitive, vertex, HTILE, and sample-rate sources outside this exact chunk. Misprogramming can produce visible shading-rate artifacts while passing basic rendering tests.
- `DB_SHADER_CONTROL`, `DB_DEPTH_CONTROL`, `DB_EQAA`, and stencil-ref fields affect early/late Z, stencil operations, coverage export, over-rasterization, and color-write behavior. Small bit errors can look like application bugs rather than driver faults.
- Full-width float/payload registers do not validate format. Viewport, clip-plane, point-size, blend-constant, scratch, and export-format fields rely on higher-level state validation.
- Reserved-bit preservation is caller-owned. The masks expose named fields but do not force read-modify-write discipline or prevent writes to undocumented bits.

## Test Signals

Useful validation is mostly build, static, command-stream, and hardware rendering coverage:

- Build coverage for GC11 users that include `gc_11_0_0_sh_mask.h`, especially `gfx_v11_0.c`, `clearstate_gfx11.h`, KFD/MES files, SDMA v6, display DM, and SOC21 paths.
- Generated-header consistency checks that every `__SHIFT` has a matching `_MASK`, masks are aligned to their shifts, fields do not overlap within a register except documented aliases, and register names match the compatible offset header.
- Clear-state validation that `clearstate_gfx11.h` register order and default values match GC11 context-register offsets for all covered state blocks.
- Graphics conformance and piglit/dEQP-style tests covering multiple viewports/scissors, viewport depth ranges, user clip planes, point sprites, flat/centroid/sample interpolation, FP16 interpolation, VRS rate surfaces, blend constants, per-MRT blend modes, alpha-to-coverage, depth/stencil operations, EQAA/MSAA behavior, and conservative/early-depth interactions.
- Command-stream tests or traces that exercise all 32 `SPI_PS_INPUT_CNTL_*` entries and verify the different point-sprite field availability between low and high entries.
- Reset, suspend/resume, and GPU recovery tests while graphics queues are active, because context state and clear-state reload must restore the registers described here.
- Negative indicators include render corruption limited to one MRT, viewport, or PS input slot; VRS artifacts; unexpected depth/stencil pass/fail results; stuck graphics fences after state-heavy draws; VM faults on VRS or VGT base-address programming; or failures limited to GC11 ASICs.
