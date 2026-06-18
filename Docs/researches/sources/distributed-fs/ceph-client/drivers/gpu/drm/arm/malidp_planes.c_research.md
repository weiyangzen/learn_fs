# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/malidp_planes.c

## Purpose

`malidp_planes.c` implements Mali-DP display-engine plane creation, validation, atomic state management, modifier support, MMU prefetch selection, YUV color conversion programming, AFBC decoder programming, and plane register updates/disable.

## Important APIs, Types, And Functions

Exported APIs are `malidp_de_planes_init()` and `malidp_format_mod_supported()`. Important helpers include custom plane state reset/duplicate/destroy/print, `malidp_de_plane_check()`, `malidp_de_plane_update()`, `malidp_de_plane_disable()`, `malidp_se_check_scaling()`, prefetch helpers, `malidp_de_set_color_encoding()`, `malidp_de_set_plane_afbc()`, and `malidp_set_plane_base_addr()`.

## Control Flow

Plane initialization builds a per-layer format list from the hardware map, filters modifiers when SPLIT is unsupported, allocates one primary plane plus overlay planes, attaches helper funcs, creates alpha and blend-mode properties, adds rotation properties except on SMART layers, initializes alpha LUTs, and creates YUV color properties for video layers. Atomic check maps the framebuffer format/modifier to a hardware format ID, checks pitch/tile alignment, line-size limits, three-plane stride restrictions, scaling support, rotation restrictions, SMART AFBC rejection, rotation-memory requirement, alpha blending limitations, and MMU prefetch settings. Atomic update writes format, base addresses, MMU control, strides, color conversion, source/destination/offset sizes, SMART rectangle registers, AFBC crop/control, rotation/flip/blend/alpha/flow config, and finally enables the layer.

## State And Persistence Behavior

`struct malidp_plane_state` persists derived values: internal format ID, plane count, rotation memory size, MMU prefetch mode, and prefetch page size. CRTC state receives `scaled_planes_mask` for later scaling-engine setup. Hardware state persists in layer format/control/size/offset/stride/address/YUV2RGB/AFBC/MMU registers until another update or disable.

## Dependencies And Integration Points

The file depends on DRM atomic, blend, format/modifier helpers, GEM DMA helpers, IOMMU page-size information, Mali-DP hardware maps, CRTC state, and register definitions. It integrates tightly with `malidp_crtc.c` for scaling and rotation-memory budgeting and with `malidp_hw.c` for format IDs, pitch alignment, and AFBC feature support.

## Risks And Edge Cases

Modifier validation has many format-specific rules: AFBC requires one plane, RGB requires YTR, YUV forbids YTR, SPLIT requires SPARSE and is limited for subsampled formats, CBR requires subsampling, and some formats are linear-only or AFBC-only. Partial MMU prefetch is heuristic and depends on scatterlist lengths. AFBC base addressing ignores source crop because crop registers handle it. Hardware cannot combine plane alpha and pixel alpha. Rotation restrictions differ by layer and compression state.

## Test Signals

Coverage should include all layer types, every advertised format/modifier combination, invalid AFBC modifier combinations, pitch and tile-alignment failures, scaling on one plane and rejection on unsupported/multiple planes, rotation/flips on each layer, SMART layer restrictions, three-plane stride equality, YUV color property changes, MMU prefetch state printing, AFBC crop correctness, and disable clearing enable/flow bits.
