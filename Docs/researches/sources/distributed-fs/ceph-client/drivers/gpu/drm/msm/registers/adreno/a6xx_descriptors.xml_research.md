# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/adreno/a6xx_descriptors.xml

## Purpose
`a6xx_descriptors.xml` is an rnndb/freedreno XML database fragment for A6xx texture and UBO descriptor dword layouts. It does not execute at runtime; it is consumed by `drivers/gpu/drm/msm/registers/gen_header.py` through the DRM msm Makefile to generate C macros in `generated/a6xx_descriptors.xml.h`. Those macros are part of the low-level contract used by Adreno command-stream and state programming code to pack descriptor dwords consistently with A6xx hardware.

## Important definitions
The file imports `freedreno_copyright.xml`, `adreno_common.xml`, `adreno_pm4.xml`, and `a6xx_enums.xml`, so its bitfields can refer to common compare, MSAA, color-swap, texture format, tiling, filter, clamp, anisotropy, reduction, border-color, swizzle, and texture-type enums. It defines three 32-bit domains: `A6XX_TEX_SAMP`, `A6XX_TEX_CONST`, and `A6XX_UBO`.

`A6XX_TEX_SAMP` is a four-dword sampler descriptor. Dword 0 holds mip-filtering, magnification/minification filter modes, S/T/R wrap modes, anisotropy, and signed fixed-point LOD bias. Dword 1 carries clamp-enable, depth-compare function, cubemap seam filtering disable, unnormalized coordinates, far mip filtering, and min/max LOD. Dword 2 carries reduction mode, fast border color controls, chroma-linear enable, and the border-color table/address field. Dword 3 is intentionally empty/reserved.

`A6XX_TEX_CONST` is a 16-dword texture-resource descriptor with `varset="chip"`. It covers tile mode, sRGB, component swizzles, mip levels, chroma midpoint flags, sample count, `a6xx_format`, color swap, width/height, A7xx+ mutable enable, buffer-texture struct size/start offset overlays, pitch alignment, pitch/stride, texture type, array pitch, minimum layer size, tile-all, UBWC/flag controls, base and flag addresses, depth, min LOD clamp, plane pitch, flag-buffer array pitch, flag-buffer pitch, and flag-buffer log dimensions. Several fields intentionally overlap, such as `MIPLVLS` with chroma midpoint flags, buffer-typed fields with pitch fields, `MIN_LOD_CLAMP` with `PLANE_PITCH`, and resource address fields for planar/flag layouts.

`A6XX_UBO` is a compact two-dword uniform-buffer descriptor: dword 0 is the low address, and dword 1 stores high address bits plus `SIZE`, documented in vec4 units.

## Control flow and generation behavior
The XML is declarative input to the header generator. The control flow is: the kernel build sees generated header targets in `drivers/gpu/drm/msm/Makefile`, invokes `gen_header.py --rnn registers --xml registers/adreno/a6xx_descriptors.xml c-defines`, resolves imports, validates against `rules-fd.xsd` when `CONFIG_DRM_MSM_VALIDATE_XML` enables validation, and emits C preprocessor definitions. Driver code then uses generated field macros while building descriptors, rather than parsing this XML at runtime.

## State and persistence
There is no runtime persistence in this XML. Its persistent state is the checked-in hardware description and the generated header products under the build directory. Descriptor fields here represent GPU-visible packed state that is later written into command buffers or descriptor memory; mistakes persist indirectly as incorrect GPU state packets, texture fetch behavior, or uniform buffer addressing.

## Dependencies and integration points
The file depends on `a6xx_enums.xml` for the A6xx texture-specific field types and on `adreno_common.xml` for cross-generation fields such as `adreno_compare_func`, `a3xx_msaa_samples`, and `a3xx_color_swap`. It integrates with the msm generated-header build path listed in the Makefile and with A6xx/A7xx code paths that include generated XML headers via `a6xx_gpu.h` and related Adreno sources. The descriptor domains are also conceptually coupled to userspace Mesa/freedreno descriptor packing because kernel and userspace must agree on hardware encodings.

## Risks
The highest risk is silent field-position drift: a one-bit error in format, pitch, address shift, or swizzle fields can produce corrupted sampling, out-of-bounds memory access, or GPU faults. Overlapping fields require careful use-site discipline because valid interpretation depends on texture type, planar format, UBWC flag use, and chip generation. The `MUTABLEEN` field is gated with `variants="A7XX-"`, so generated code must preserve variant guards correctly. Comments also flag uncertain hardware details, such as LOD bias bit width and D3D structured UAV interpretation; those are research debt and should be treated conservatively.

## Test signals
Useful validation signals are successful XML schema validation, successful generation of `a6xx_descriptors.xml.h`, and successful compilation of msm Adreno sources that include generated headers. Runtime signals include texture-format conformance tests, mipmapping and LOD tests, sampler clamp/wrap/filter tests, planar and UBWC texture tests, CTS/deqp coverage for Vulkan/OpenGL texture sampling, and absence of GPU faults when exercising buffer textures, multisample textures, and UBO addressing.
