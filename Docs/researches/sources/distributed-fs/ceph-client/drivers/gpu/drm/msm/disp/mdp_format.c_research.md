# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp_format.c

Purpose: Defines MSM/MDP pixel format metadata and default color-space conversion tables used by MDP5 and related display blocks.

Important APIs/functions: `mdp_get_format()` maps a DRM fourcc plus modifier to a `struct msm_format`, selecting the linear table for modifier 0 or the UBWC table for `DRM_FORMAT_MOD_QCOM_COMPRESSED`. `mdp_get_default_csc_cfg()` returns default `struct csc_cfg` entries for RGB/RGB, YUV/RGB, RGB/YUV, and YUV/YUV. Macro families define packed RGB/RGBA/RGBX, DX 10-bit variants, interleaved YUV, pseudo-planar YUV, planar YUV, and UBWC/tiled variants.

Control flow: Callers ask for a format at framebuffer validation/programming time. The lookup rejects unknown modifiers and unsupported fourccs with DRM errors. Plane programming consumes fields such as fetch type, bits per component, unpack order/count, bpp, chroma sample, fetch mode, flags, plane count, and tile height.

State and persistence: The format and CSC tables are static const/static global data. Returned pointers are immutable shared metadata, except CSC table returns non-const pointer to static entries.

Dependencies/integration: Depends on DRM fourcc/modifier definitions, DRM framebuffer info, MSM driver logging, generic MDP register enums, and the `mdp_kms.h` CSC type definitions.

Risks and test signals: UBWC aliases intentionally map some ARGB/XRGB formats to hardware-native ABGR/ARGB ordering, so format/modifier validation must match hardware expectations. Unsupported modifiers fail hard. Test framebuffer creation for all advertised formats, UBWC scanout, YUV CSC, P010/DX formats, and error messages for invalid fourcc/modifier pairs.
