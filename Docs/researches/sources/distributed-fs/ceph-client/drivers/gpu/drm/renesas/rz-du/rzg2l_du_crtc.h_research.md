# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rz-du/rzg2l_du_crtc.h

## Purpose

`rzg2l_du_crtc.h` defines the RZ/G2L DU CRTC private data and CRTC state extensions.

## Important APIs, Types, and Functions

`struct rzg2l_du_crtc` embeds `drm_crtc` and stores DU device, initialization flag, vblank flag, pending event, flip wait queue, VSP pointer/pipe, optional source names, reset, and three clocks. `struct rzg2l_du_crtc_state` extends DRM CRTC state with output routing bits. Inline conversions expose container lookups. Public declarations are `rzg2l_du_crtc_create()` and `rzg2l_du_crtc_finish_page_flip()`.

## Control Flow

KMS init populates the structure before registering the CRTC. Atomic callbacks duplicate/destroy/reset the extended state and use the private data for VSP and clock control.

## State and Persistence Behavior

The structure persists for the DRM device lifetime. The `event` field is protected by DRM `event_lock`; `initialized` protects repeated clock/reset enable.

## Dependencies and Integration Points

It depends on DRM CRTC/writeback headers, Linux wait/spinlock/container helpers, `media/vsp1.h`, and forward declarations for reset/clock/VSP types.

## Risks and Edge Cases

The `outputs` field is defined but not heavily used in this subset, so future routing changes must keep it synchronized with encoder possible CRTC masks. Event locking rules must be preserved.

## Test Signals

Atomic state duplication/reset tests and page-flip event lifecycle tests are the main validation signals.
