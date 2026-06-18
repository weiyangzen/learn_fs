# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rz-du/rzg2l_du_crtc.c

## Purpose

`rzg2l_du_crtc.c` implements the single CRTC used by the RZ/G2L DU driver. It programs DU timing registers, manages clocks/reset, starts/stops display output, coordinates VSP enable/flush, and handles vblank/page-flip events.

## Important APIs, Types, and Functions

Public functions are `rzg2l_du_crtc_create()` and `rzg2l_du_crtc_finish_page_flip()`. Important internals include `rzg2l_du_crtc_set_display_timing()`, `rzg2l_du_crtc_setup()`, `rzg2l_du_crtc_get()`, `rzg2l_du_crtc_put()`, `rzg2l_du_crtc_start/stop()`, atomic enable/disable/flush callbacks, custom CRTC state duplication/reset, and vblank enable/disable callbacks.

## Control Flow

Creation gets shared reset and `aclk`, `pclk`, and `vclk`, initializes the flip wait queue, obtains the primary VSP plane for the selected pipe, initializes the DRM CRTC, and attaches helper callbacks. Atomic enable idempotently enables bus/peripheral clocks, deasserts reset, programs display timings and pixel clock, enables VSP LIF, turns vblank on, then sets `DU_MCR0_DI_EN`. Atomic flush arms a pending page-flip event under `event_lock` and flushes the VSP pipe. The VSP completion callback calls `finish_page_flip()`, which sends the vblank event and drops the vblank reference. Atomic disable waits for pending flips, disables vblank and VSP, stops DU output, gates clocks, asserts reset, and sends any disable event.

## State and Persistence Behavior

`struct rzg2l_du_crtc` persists inside `rzg2l_du_device` and stores clock/reset handles, VSP pointer/pipe, event pointer, wait queue, vblank flag, and `initialized` guard. Hardware timing and enable bits persist while clocks/reset are active.

## Dependencies and Integration Points

The CRTC depends on DRM atomic/vblank helpers, Linux clock/reset APIs, `rzg2l_du_vsp`, and the DU MMIO block in `rzg2l_du_device`. It is created from `rzg2l_du_modeset_init()`.

## Risks and Edge Cases

- `rzg2l_du_crtc_set_display_timing()` enables `dclk` before setting its rate and does not check return values.
- Page flip timeout forcibly completes the event after 50 ms; this prevents userspace hangs but can mask hardware/VSP stalls.
- Atomic enable ignores the return from `rzg2l_du_crtc_get()`, so a clock/reset failure may still fall through to start.
- The driver assumes one CRTC and one DU register block.

## Test Signals

Mode-set tests should check timing register programming, vclk rate, enable/disable sequencing, page-flip completion under VSP callbacks, vblank enable/disable, suspend/shutdown paths, and failure injection for clocks/resets.
