<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dc/dc-crtc.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dc/dc-crtc.c

Purpose: Implements DRM CRTC behavior for the i.MX8 DC dual-display pipeline, including modeset, vblank, IRQ completion waits, runtime PM, and primary-plane composition.

Important APIs/types/functions: Public functions are `dc_crtc_init()` and `dc_crtc_post_init()`. Important helper callbacks include vblank counter/enable/disable, atomic check/begin/flush/enable/disable, scanout position, and five IRQ handlers for frame complete, sequence complete, display-engine shadow load, and extdst shadow loads.

Control flow: `dc_crtc_init()` wires a CRTC to display-engine, pixel-engine, constframe/extdst/framegen subblocks and initializes the primary plane. Atomic enable powers display and pixel engines, configures timing, constframes, extdst sources, framegen clock, triggers shadow loads, waits for completions, and checks FIFO/sync status. Atomic flush pushes plane updates through extdst shadow load and queues vblank events. Atomic disable stops framegen, waits for sequence complete, disables clocks, drops PM refs, and sends pending events.

State and persistence behavior: `struct dc_crtc` stores sub-block pointers, IRQ numbers, completions, a pending vblank event, and IRQ metadata. Hardware state is programmed through framegen, constframe, extdst, and plane/layerblend/fetchunit helpers.

Dependencies: DRM atomic helpers, vblank helpers, runtime PM, interrupts/completions, `dc-de.h`, `dc-pe.h`, and `dc-kms.h`.

Integration points: Called from `dc_kms_init()` for each display. Bridges/connectors are attached separately in KMS. Plane update paths feed into the CRTC flush sequence.

Risks: Completion waits are time-limited and log errors but often continue, so missed interrupts can leave inconsistent display state. Event/vblank reference handling must stay balanced. Runtime PM get failures are logged but do not fully abort the modeset path.

Test signals: Modeset enable/disable, page flips with vblank events, IRQ storm/missing IRQ tests, suspend/resume, no-plane background mode, FIFO-empty error observation, and scanout timestamp tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dc/dc-crtc.c -->
