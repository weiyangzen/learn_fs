# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/adreno/a8xx_descriptors.xml

## Purpose
`a8xx_descriptors.xml` defines A8xx texture sampler and texture memory-object descriptor layouts. It reflects a descriptor reorganization from A6xx/A7xx texture constants into A8xx sampler plus memory-object dwords while reusing common A6xx format/filter/clamp/type encodings and A8xx-specific swizzles.

## Important definitions
The file imports `freedreno_copyright.xml`, `adreno_common.xml`, `adreno_pm4.xml`, `a6xx_enums.xml`, and `a8xx_enums.xml`. It defines two 32-bit domains: `A8XX_TEX_SAMP` and `A8XX_TEX_MEMOBJ`.

`A8XX_TEX_SAMP` is a four-dword sampler descriptor. Dword 0 contains near mip filtering, `MIPMAPING_DIS`, XY filters, wrap modes, MSAA box filtering, LOD bias, and anisotropy. Dword 1 contains max/min LOD, reduction mode, compare function, chroma-linear enable, cubemap seam filtering disable, and unnormalized coordinates. Dword 2 contains fast-border-color enable, fast border color value, and border-color field. Dword 3 is reserved.

`A8XX_TEX_MEMOBJ` is a 16-dword memory-object descriptor with `varset="chip"`. It holds base address, texture type, depth, width/height, sample count, format, color swap, A8xx swizzle fields, tile mode, UBWC/flag state, sparse/PRT enable, tile-all and sRGB, U/V planar base overlays, flag buffer pitch/address, all-samples-center, mutable enable, line offset and alignment, mip levels, array slice offset, array offset unit, minimum array slice offset, GMEM fallback/full-surface/corner flags, UV chroma offset overlays, flag array pitch/log dimensions, V-plane overlays, min LOD clamp, and UV pitch.

## Control flow and generation behavior
The XML is intended for the same generated-header path as other Adreno XML files. `a8xx_enums.xml.h` is listed in the Makefile, while this descriptor file supplies the A8xx descriptor domain source for generator use alongside A6xx descriptors. Runtime packing code uses generated masks/shifts to build sampler and memory-object descriptors that are submitted to the GPU. The XML itself has no runtime parser.

## State and persistence
The file is static source. Its generated constants control GPU-visible descriptor state stored in command buffers or descriptor memory. Those descriptor dwords persist for the life of the submitted state/buffer and affect texture fetches, memory layout interpretation, UBWC/flag access, planar formats, and sparse/PRT behavior.

## Dependencies and integration points
The file depends on `a6xx_enums.xml` for shared texture formats and sampler enum types, `a8xx_enums.xml` for `a8xx_tex_swiz`, and `adreno_common.xml` for MSAA, compare, and color swap types. It integrates with A8xx driver code that includes generated A8xx/A6xx enum headers and with any userspace or kernel descriptor packing logic that must match A8xx memory-object layout.

## Risks
Address shift changes from A6xx are high risk: A8xx base/flag/U/V fields use bit ranges starting at bit 6 with `shr="6"`, while A6xx uses bit 5 shifts in many descriptor address fields. The descriptor has many intentional overlays for multiplanar and single-planar interpretations, so a generator or use-site misunderstanding can corrupt UV planes, flag buffers, or min-LOD/pitch fields. A typo such as `MIN_ARRAY_SLIZE_OFFSET` is part of the generated naming surface and could leak into code or tooling. Sparse/PRT and GMEM flags are also sensitive because incorrect bits can affect memory residency or tiling behavior.

## Test signals
Build signals include successful XML validation and generated-header use. Runtime signals include A8xx texture sampling tests for 1D/2D/3D/cube/buffer textures, MSAA texture fetches, mipmapping, min/max LOD, anisotropy, planar YUV formats, UBWC/flag-buffer formats, sparse/PRT cases if supported, GMEM fallback behavior, and conformance tests comparing swizzle/format results against expected pixels.
