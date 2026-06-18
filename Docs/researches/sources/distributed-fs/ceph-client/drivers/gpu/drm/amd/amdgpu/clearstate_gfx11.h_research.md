# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/clearstate_gfx11.h

## Purpose
`clearstate_gfx11.h` provides the static clear-state context register defaults for GFX11 AMDGPU devices. It is included by `gfx_v11_0.c` and supplies the generation-specific `gfx11_cs_data` table used to size and populate the RLC clear-state block and to build clear-state command streams.

## Important APIs, Types, and Data
The file defines `gfx11_SECT_CONTEXT_def_1` through `gfx11_SECT_CONTEXT_def_7`, wraps them in `gfx11_SECT_CONTEXT_defs[]`, and exposes `gfx11_cs_data[]` as a `SECT_CONTEXT` section. It uses the `cs_extent_def`/`cs_section_def` structures from `clearstate_defs.h` and terminates extent/section arrays with zero sentinels.

The extents cover `0x0000a000` for 215 registers, `0x0000a0d8` for 272, `0x0000a1f5` for 4, `0x0000a1ff` for 158, `0x0000a2a0` for 2, `0x0000a2a3` for 1, and `0x0000a2a6` for 282. Compared with GFX10, the last extent is consolidated and starts at `0xa2a6`; comments also show GFX11-specific naming such as `DB_RESERVED_REG_*`, `DB_SPI_VRS_CENTER_LOCATION`, conservative rasterization control, and updated color-buffer base/DCC extension coverage. Nonzero defaults preserve expected scissor rectangles, masks, viewport depth max values, clip controls, and rasterization defaults.

## Control Flow and Integration
The file has no functions. `gfx_v11_0_get_csb_size()` iterates `gfx11_cs_data`, accepting only `SECT_CONTEXT` and counting each extent as packet header plus data. `gfx_v11_0_get_csb_buffer()` uses generic helpers (`amdgpu_gfx_csb_preamble_start()`, `amdgpu_gfx_csb_data_parser()`, and `amdgpu_gfx_csb_preamble_end()`) after `adev->gfx.rlc.cs_data` is set to `gfx11_cs_data`. The GFX11 startup path also programs `PA_SC_TILE_STEERING_OVERRIDE` separately from runtime configuration.

## State and Persistence Behavior
The table is immutable static data. It does not retain runtime state and has no persistence beyond the driver image. Its values become persistent GPU baseline context state only after they are copied into the clear-state buffer or emitted through CP packets during initialization/resume. Because the table is static, suspend/resume consistency depends on the consumer reusing it rather than modifying it.

## Dependencies
Dependencies include the clear-state struct definitions, GFX11 register layout, CP `PACKET3_SET_CONTEXT_REG` semantics, RLC clear-state allocation in common AMDGPU graphics code, and the `gfx_v11_0.c` assignment of `adev->gfx.rlc.cs_data`. The include guard prevents accidental duplicate definitions within a translation unit.

## Risks
The most important risk is positional mismatch: comments do not drive behavior, so the table must exactly match hardware register order and the declared extent lengths. GFX11-specific reserved/register additions make copy-forward from older generations risky. Any malformed terminator can overrun consumer walks. Incorrect nonzero defaults in scissor, mask, VRS, conservative rasterization, or color-buffer metadata registers can surface as subtle rendering corruption rather than immediate compile failures.

## Test Signals
Validation should include GFX11 boot and resume, successful `amdgpu_gfx_rlc_init_csb()` setup, no clear-state parser rejection, and GPU ring progress after clear-state preambles. Rendering tests should stress VRS/conservative rasterization, depth/stencil, clip/scissor, viewport arrays, color target metadata, DCC, and multi-target output. Static checks should compare the seven extent counts with actual array element counts.
