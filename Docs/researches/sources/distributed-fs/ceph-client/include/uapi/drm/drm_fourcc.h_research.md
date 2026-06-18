# sources/distributed-fs/ceph-client/include/uapi/drm/drm_fourcc.h

## Purpose

`drm_fourcc.h` is the DRM UAPI registry for framebuffer pixel format FourCC values and format modifiers. It defines stable identifiers used by KMS, GEM/GBM, EGL, Vulkan WSI, media blocks, display controllers, and DMA-BUF import/export paths to agree on component order, plane layout, tiling, compression, endian handling, and vendor-specific memory layout. The file is a protocol catalog, not executable code; changing values or semantics changes ABI expectations across kernel drivers and user-space graphics stacks.

## Important APIs, Types, And Constants

The foundational API is `fourcc_code(a, b, c, d)`, which packs four bytes into a `__u32`. `DRM_FORMAT_BIG_ENDIAN` marks endian variants and `DRM_FORMAT_INVALID` reserves zero. The `DRM_FORMAT_*` catalog covers indexed/monochrome formats, single-channel red formats, RG/RGB/RGBA/BGR packed layouts, high-bit-depth integer and floating formats, packed and planar YUV formats, semi-planar video formats, and media-specific YUV layouts.

Modifiers use `DRM_FORMAT_MOD_VENDOR_*` namespaces and `fourcc_mod_code(vendor, val)` to produce 64-bit layout tokens. Important modifier families include Intel tiled/CCS layouts, NVIDIA block-linear layouts, Broadcom SAND/UIF helpers, Arm AFBC/AFRC and miscellaneous Mali tiling, Allwinner tiled YUV, Amlogic FBC, MediaTek modifier bit fields, Apple GPU tiled/compressed layouts, and AMD tiled/DCC field helpers (`AMD_FMT_MOD_SET/GET/CLEAR`).

## Control Flow

There are no runtime functions. The control flow is ABI negotiation: userspace queries supported FourCC/modifier pairs, allocates/imports buffers with those attributes, and passes them to DRM ioctls such as `ADDFB2`, plane property blobs, GBM/EGL/Vulkan image creation, or DMA-BUF sharing. Kernel drivers validate the numeric pair against supported layouts and then enforce modifier-specific plane, pitch, offset, alignment, and mapping rules.

## State And Persistence

The header defines persistent ABI tokens. The values themselves are stable state shared by compiled userspace and kernels. Runtime buffer state lives elsewhere, but the format/modifier pair persists in metadata attached to framebuffers, DMA-BUFs, and image allocations. Once a modifier is published, aliasing or repurposing it can break cross-driver sharing.

## Dependencies And Integration Points

The header depends on `drm.h` for UAPI integer types. It integrates directly with `drm_mode.h` framebuffer metadata (`pixel_format`, `modifier[]`, `drm_format_modifier_blob`), DMA-BUF negotiation, Mesa/GBM/EGL/Vulkan, and vendor DRM drivers. Exynos IPP and other driver-specific UAPIs consume these format and modifier values by contract.

## Risks

Major risks are ABI instability, duplicate aliases for the same physical layout, incorrect interpretation of multi-plane modifiers, assuming CPU mmap works for producer-private compressed layouts, and bitfield mistakes in dense vendor encodings such as AMD, Arm AFBC/AFRC, Amlogic, and MediaTek. Endianness and component order are also common sources of incorrect imports.

## Test Signals

Useful checks include UAPI compile tests, ABI-diff checks for constant stability, KMS `ADDFB2` validation for RGB/YUV/modifier combinations, `IN_FORMATS` blob round-trips, DMA-BUF import/export across drivers, GBM/EGL/Vulkan format enumeration, and negative tests for invalid format/modifier pairs, plane counts, pitches, offsets, unsupported mmap, and unknown future modifiers.
