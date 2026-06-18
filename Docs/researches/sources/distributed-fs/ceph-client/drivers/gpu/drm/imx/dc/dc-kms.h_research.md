<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dc/dc-kms.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dc/dc-kms.h

Purpose: Defines i.MX8 DC KMS-specific CRTC, plane, and IRQ state structures.

Important APIs/types/functions: Defines `DC_CRTC_IRQS`, `struct dc_crtc_irq`, `struct dc_crtc`, and `struct dc_plane`.

Control flow: Header only.

State and persistence behavior: `struct dc_crtc` stores DRM CRTC base, subblock pointers, IRQ numbers, completions, cached vblank event, and IRQ metadata. `struct dc_plane` stores DRM plane base plus fetchunit/constframe/layerblend/extdst pipeline pointers.

Dependencies: DRM CRTC/plane/vblank, Linux completion, and DC display/pixel/fetchunit headers.

Integration points: Shared among CRTC, plane, KMS, and driver aggregate definitions.

Risks: The comments document the safety/content stream design; code assumes these pointers are valid after component post-bind. CRTC IRQ count must match initialization arrays.

Test signals: Build coverage, successful CRTC/plane initialization, and vblank/page-flip event operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dc/dc-kms.h -->
