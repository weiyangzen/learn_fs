# sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dcss/dcss-kms.h

## Purpose
Defines the small private KMS object model shared by the DCSS KMS, CRTC, and plane implementation files.

## Important APIs, types, and functions
- `struct dcss_plane` embeds `struct drm_plane` and stores the DCSS channel number.
- `struct dcss_crtc` embeds `struct drm_crtc`, keeps three plane pointers, the IRQ number, cached state pointer, and a flag controlling context-load IRQ disabling.
- `struct dcss_kms_dev` embeds the DRM device and contains the single DCSS CRTC, encoder, and connector pointer.
- Declarations expose `dcss_kms_attach()`, `dcss_kms_detach()`, `dcss_kms_shutdown()`, `dcss_crtc_init()`, `dcss_crtc_deinit()`, and `dcss_plane_init()`.

## Control flow
This header has no executable flow. It fixes object ownership boundaries: KMS allocation creates `dcss_kms_dev`, CRTC code owns `dcss_crtc`, and plane initialization returns `dcss_plane` instances indexed by z-position/channel.

## State and persistence
The declared structures persist for the lifetime of the DRM device. `ch_num` is the stable mapping from a DRM plane to the DCSS DPR/scaler/DTG hardware channel. `disable_ctxld_kick_irq` is CRTC-managed state used to coordinate context-load interrupt behavior.

## Dependencies and integration points
Includes DRM encoder definitions and relies on other included source files for the full `dcss_dev` type. It is the local integration contract among DCSS KMS setup, CRTC setup, and plane setup.

## Risks
The hardware has exactly three DCSS planes/channels in this model; changing that requires updating fixed arrays and zpos/channel assumptions across plane, CRTC, scaler, DPR, and DTG code. The public prototypes hide no ownership annotations, so callers must follow local cleanup ordering.

## Test signals
Compile coverage catches structure/prototype drift. Runtime signals are correct plane-to-channel mapping, valid connector/encoder access through `dcss_kms_dev`, and successful teardown of CRTC and planes.
