# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/icl_dsi.h

## Purpose

`icl_dsi.h` is the public internal header for Gen11+ Intel DSI support. It exposes initialization and command-mode frame-update entry points to the rest of the i915 display driver while keeping the encoder implementation private to `icl_dsi.c`.

## Important APIs, Types, And Functions

The header forward declares `struct intel_display`, `struct intel_bios_encoder_data`, and `struct intel_crtc_state`. It declares `icl_dsi_init(struct intel_display *display, const struct intel_bios_encoder_data *devdata)` for VBT-driven encoder/connector creation and `icl_dsi_frame_update(struct intel_crtc_state *crtc_state)` for requesting a TE-gated command-mode frame update on the relevant DSI port.

## Control Flow

The header has no direct control flow. Display initialization calls `icl_dsi_init()` when firmware/VBT enumerates a DSI child device. Command-mode update paths call `icl_dsi_frame_update()` after inspecting CRTC mode flags that indicate TE0 or TE1 use.

## State And Persistence Behavior

No state is stored in this header. `icl_dsi_init()` creates and persists encoder, connector, DSI host, panel, and backlight state in heap objects and DRM lists. `icl_dsi_frame_update()` affects hardware frame-update request bits through the implementation.

## Dependencies And Integration Points

The header is intentionally light and depends only on forward declarations. It integrates DSI implementation with BIOS encoder enumeration and CRTC update code, and it avoids exposing MIPI DSI, PHY, or register details to unrelated display files.

## Risks And Edge Cases

Callers must pass a valid VBT encoder data object to initialization; a missing or invalid port causes the implementation to return without creating a connector. Frame-update calls rely on `crtc_state->mode_flags` being populated by the DSI command-mode configuration/readout path. If additional DSI entry points are added, this header should remain a narrow boundary rather than exposing register-level helpers.

## Test Signals

Compile coverage, DSI child-device probe, command-mode frame-update behavior for TE0, TE1, and dual-link configurations, and symbol checks for users of the two declared functions are the main validation signals.
