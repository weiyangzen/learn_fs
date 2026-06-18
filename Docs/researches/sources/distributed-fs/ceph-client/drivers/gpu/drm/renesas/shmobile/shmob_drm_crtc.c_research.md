# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/shmobile/shmob_drm_crtc.c

## Purpose

`shmob_drm_crtc.c` implements CRTC, encoder, and connector handling for the legacy SH Mobile LCDC DRM driver. It programs display timing/format registers, handles page flips and vblank events, creates primary/overlay planes, supports platform-data connectors, and supports OF bridge connectors.

## Important APIs, Types, and Functions

Public functions are `shmob_drm_crtc_create()`, `shmob_drm_crtc_finish_page_flip()`, `shmob_drm_encoder_create()`, and `shmob_drm_connector_create()`. Internals include bus format mapping, `shmob_drm_crtc_setup_geometry()`, start/stop, atomic enable/disable/flush, legacy page flip, vblank enable/disable, encoder mode fixup, and platform-data connector helpers.

## Control Flow

CRTC creation initializes the flip wait queue, creates one primary and four overlay planes, initializes the DRM CRTC, attaches helpers, and starts with vblank off. Atomic enable resumes runtime PM, resets/enables LCDC, stops output and masks interrupts, configures power/dot clock, writes geometry and bus format based on connector display info, enables display output, starts LCDC, and turns vblank on. Disable waits for any page flip, disables vblank, stops LCDC, disables output, and drops runtime PM. IRQ-side completion is in the driver file. Encoder creation either attaches a simple DPI encoder for platform-data mode or attaches an OF bridge. Connector creation either builds a legacy fixed-mode connector from platform data or uses `drm_bridge_connector_init()`.

## State and Persistence Behavior

`struct shmob_drm_crtc` stores the DRM CRTC, pending event pointer, and wait queue. Platform-data connectors store a fixed `videomode`. Hardware state persists in LCDC registers while runtime PM keeps the clock enabled.

## Dependencies and Integration Points

The file depends on DRM atomic/bridge/connector/vblank helpers, Linux OF/PM runtime/clk headers, video mode conversion, local plane code, driver state, KMS format metadata, and LCDC register macros.

## Risks and Edge Cases

- `shmob_drm_crtc_start_stop()` busy-waits on power status with no timeout.
- The atomic flush path sends CRTC state events immediately, while legacy page flip events wait for vblank; this difference should be intentional.
- Clock divider programming has a FIXME for SH7724 divider limitations.
- Platform-data connector cleanup path calls `drm_connector_cleanup()` on error, while the allocated wrapper may require careful ownership handling.

## Test Signals

Legacy platform-data fixed panel, OF bridge panel, all supported bus formats/flags, page flip/vblank event ordering, overlay plane creation, runtime PM enable/disable, and LCDC stop timeout behavior should be tested.
