# sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_crtc.c

## Purpose
CRTC implementation for the TI Display SubSystem DRM driver. It maps DRM atomic CRTC operations, vblank handling, page-flip event completion, mode validation, plane overlay positioning, runtime power, and color management onto TIDSS/DISPC videoport hardware.

## Important APIs, Types, And Functions
IRQ entry points are `tidss_crtc_vblank_irq()`, `tidss_crtc_framedone_irq()`, and `tidss_crtc_error_irq()`. Atomic helper callbacks include `tidss_crtc_atomic_check()`, `tidss_crtc_atomic_flush()`, `tidss_crtc_atomic_enable()`, `tidss_crtc_atomic_disable()`, and `tidss_crtc_mode_valid()`. `tidss_crtc_position_planes()` programs overlay layers based on normalized z-position and visibility. CRTC funcs cover vblank enable/disable, state reset/duplicate/destroy, and object destruction. `tidss_crtc_create()` allocates and initializes the CRTC.

## Control Flow
Atomic check rejects invalid enabled modes with `dispc_vp_mode_valid()`, updates CRTC info for modesets, then delegates bus validation to `dispc_vp_bus_check()`. Flush for non-modeset commits verifies GO is idle, sets videoport properties and plane positions, obtains a vblank ref, asserts GO, stores the pending event under `event_lock`, and lets the vblank IRQ complete it. Enable gets runtime PM, sets and enables the videoport clock, configures the videoport and planes, turns vblank on, prepares/enables hardware, and sends any enable event immediately. Disable reinitializes framedone completion, disables all overlay layers as a hardware workaround, disables the videoport, waits up to 500 ms for framedone, unprepares, sends pending event, turns vblank off, disables clock, and drops runtime PM.

## State And Persistence
Persistent runtime state is in `struct tidss_crtc`: embedded DRM CRTC, hardware videoport id, pending vblank event, and framedone completion. Extended atomic state stores `plane_pos_changed`, `bus_format`, and `bus_flags`. Hardware state lives in DISPC videoport clocks, GO bit, overlay layer enable/position, and vblank/framedone IRQ state. No filesystem persistence exists.

## Dependencies And Integration Points
The file integrates DRM atomic helpers, vblank/event locking, TIDSS runtime PM, IRQ control, `tidss_plane` zpos/hardware ids, DISPC videoport and overlay APIs, and DRM color management. It is linked into the TIDSS driver by the Makefile and exposed through prototypes in `tidss_crtc.h`.

## Risks And Maintenance Notes
Event lifetime is delicate: `drm_crtc_vblank_get()` must pair with vblank completion, and pending events are protected by `event_lock`. The GO-bit race before vblank is explicitly handled in `tidss_crtc_finish_page_flip()`. Early returns after runtime get or clock setup failures in enable do not visibly unwind prior steps in this function, so callers rely on surrounding atomic error handling. Plane-position programming assumes all affected planes are present in atomic state. Disable depends on framedone IRQ delivery and logs a timeout after 500 ms.

## Test Signals
Signals are primarily integration/runtime: successful atomic modesets, valid mode rejection through `MODE_*`, vblank events delivered once, page flips completed after GO clears, no sync-lost errors under plane reuse, framedone completion during disable, and color-management properties exposed with expected gamma/CTM support.
