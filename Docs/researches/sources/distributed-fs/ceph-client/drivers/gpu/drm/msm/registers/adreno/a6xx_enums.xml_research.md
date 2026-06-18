# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/adreno/a6xx_enums.xml

## Purpose
`a6xx_enums.xml` defines A6xx-family enum values and one inline protection bitset used by generated Adreno register headers. It centralizes hardware numeric encodings for texture descriptors, shader/debug state identifiers, 2D interface formats, tessellation modes, depth modes, and sampler behavior so descriptor and register XML can reference named values instead of duplicating numbers.

## Important definitions
The file imports `freedreno_copyright.xml`, `adreno_common.xml`, and `adreno_pm4.xml`. Its inline bitset `a6x_cp_protect` packs CP protected-register regions with `BASE_ADDR` bits 0..17, `MASK_LEN` bits 18..30, and a boolean `READ` bit.

It defines 17 enums. `a6xx_tile_mode` covers linear and tiled modes. `a6xx_format` is the large 131-entry texture/render format catalog, spanning normalized, signed, unsigned, float, packed, depth/stencil, ETC, BC, and ASTC formats and ending with `FMT6_NONE = 0xff`. `a6xx_polygon_mode`, `a6xx_depth_format`, `a6xx_ztest_mode`, `a6xx_tess_spacing`, and `a6xx_tess_output` encode draw/raster/depth/tessellation choices. `a6xx_shader_id` maps shader-state and internal RAM selector IDs, while `a6xx_debugbus_id` maps debug-bus blocks from CP/RBBM/VBIF/HLSQ through SPTP instances. Texture-specific enums include `a6xx_2d_ifmt`, `a6xx_tex_type`, `a6xx_tex_filter`, `a6xx_tex_clamp`, `a6xx_tex_aniso`, `a6xx_reduction_mode`, `a6xx_fast_border_color`, and `a6xx_tex_swiz`.

## Control flow and generation behavior
This file is resolved by `gen_header.py` before any XML that references its enum names. Generated C definitions are then included by `a6xx_gpu.h` through `a6xx_enums.xml.h`. Descriptor XML such as `a6xx_descriptors.xml` and `a8xx_descriptors.xml` use these enum names as bitfield `type` attributes, so the generator can emit typed masks, shifts, and value constants with stable names.

## State and persistence
The XML has no runtime state. Its persistent effect is the numeric ABI between driver command construction and Adreno hardware. Values such as `FMT6_*`, texture type, swizzle, and debug-bus IDs are embedded into generated headers and then into compiled driver code or command streams.

## Dependencies and integration points
The enum catalog is shared by A6xx and by later XML where encodings remain compatible. `a8xx_descriptors.xml` imports it for common texture formats, filter/clamp/aniso modes, tile modes, sample count dependencies through `adreno_common.xml`, and texture type. The generated header is listed in the msm Makefile and included by `a6xx_gpu.h`, making it visible to A6xx/A7xx driver code.

## Risks
The broad `a6xx_format` enum is a high-risk compatibility surface because format numbers must match GPU hardware and userspace expectations exactly. Debug-bus and shader IDs are diagnostic rather than normal rendering state, but wrong values can break crash capture, performance debugging, or firmware/state inspection. The `a6x_cp_protect` bitset differs from the common `adreno_cp_protect` layout, so accidental interchange can program the wrong protected region policy.

## Test signals
Build-time signals include XML validation and successful generation/compilation of `a6xx_enums.xml.h`. Functional signals include format conversion tests, sampler descriptor tests, protected-register programming tests, GPU state capture/debug-bus reads, and conformance suites that exercise ASTC/BC/depth/stencil formats, texture buffers, swizzles, and tessellation modes.
