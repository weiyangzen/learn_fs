# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_plane.c

## Purpose

`rcar_du_plane.c` implements direct DU KMS planes for R-Car DU hardware. It allocates scarce hardware planes during atomic checks, validates plane state, programs scanout/format/color-key registers, handles memory versus live VSP sources, exposes alpha/zpos/colorkey properties, and creates primary/overlay planes per group.

## Important APIs, Types, and Functions

- Hardware allocator helpers: `rcar_du_plane_needs_realloc()`, `rcar_du_plane_hwmask()`, `rcar_du_plane_hwalloc()`, and `rcar_du_atomic_check_planes()`.
- Register programming helpers: `rcar_du_plane_write()`, `rcar_du_plane_setup_scanout()`, `rcar_du_plane_setup_mode()`, `rcar_du_plane_setup_format_gen2()`, `rcar_du_plane_setup_format_gen3()`, `rcar_du_plane_setup_format()`, and `__rcar_du_plane_setup()`.
- Atomic validation/update: `__rcar_du_plane_atomic_check()`, `rcar_du_plane_atomic_check()`, and `rcar_du_plane_atomic_update()`.
- State/property helpers duplicate, destroy, reset, set, and get `struct rcar_du_plane_state`.
- `rcar_du_planes_init()` creates one primary plane per CRTC plus seven overlays, attaches helper funcs, alpha, immutable/dynamic zpos, and colorkey property.

## Control Flow

Atomic check first identifies disabled planes and planes needing reallocation due to format plane-count or source changes. If reallocation is needed, it locks all planes in affected groups through `drm_atomic_get_plane_state()`, computes free hardware plane masks excluding locally freed planes, and assigns hardware planes, preferring planes already associated with the target CRTC to avoid group restart flicker.

Atomic update programs visible planes only. It writes format, destination, alpha/color-key, scanout address/pitch/source positions, and for two-plane formats configures the adjacent hardware plane. If the source changes between memory and live VSP, it marks the group for restart because the VSPS bit only latches under reset. VSPD1 sink changes update DPAD/VSP routing and also request restart.

## State and Persistence Behavior

Driver plane state persists in `struct rcar_du_plane_state`: selected format descriptor, hardware plane index, source, and colorkey. Hardware state persists in PnMR, PnALPHAR, PnTC2R/PnTC3R, PnDDCR2/PnDDCR4, destination registers, pitch/source registers, DMA base registers, and group routing/restart state.

## Dependencies and Integration Points

- Uses DRM atomic, plane, blend, framebuffer, GEM DMA, fourcc, and helper APIs.
- Depends on R-Car group, KMS format descriptors, driver feature/quirk data, and register definitions.
- Called from CRTC update paths via `rcar_du_plane_setup()` and from KMS atomic checks for non-VSP-backed hardware.

## Risks and Edge Cases

- Hardware plane allocation is complex and can return `-EBUSY` when fragmentation or fixed VSPD source constraints prevent assignment.
- Two-plane formats require adjacent hardware planes with wraparound; allocation and programming must stay synchronized.
- Several scanout coordinate adjustments are based on hardware observations not fully documented, especially interlaced and NV12/NV21 Y positioning.
- Source changes and DPTSR association changes require group restarts and visible flicker.
- Color key property uses bit 24 as enable flag and lower RGB bits as key; userspace must encode it exactly.
- Gen3 no-blending feature strips ALP/EOR bits; incorrect feature flags can produce invisible or incorrectly blended planes.

## Test Signals

- Atomic plane tests should cover enable/disable, one- and two-plane formats, fixed VSPD0/VSPD1 sources, hardware plane exhaustion, zpos ordering, CRTC reassignment, and memory/live source switching.
- Register tests should validate pitch/source/destination/DMA programming for RGB, packed YUV, NV12/NV21/NV16, interlaced, and Gen2 versus Gen3.
- Property tests should cover alpha, primary immutable zpos, overlay zpos range, and colorkey enable/disable and RGB conversion.
