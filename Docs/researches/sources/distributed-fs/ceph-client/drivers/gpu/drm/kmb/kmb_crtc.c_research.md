<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/kmb/kmb_crtc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/kmb/kmb_crtc.c

## Purpose
Implements the Keem Bay LCD controller CRTC side of the DRM pipeline: vblank enable/disable, mode programming, atomic enable/disable/begin/flush, mode validation, and primary plane based CRTC creation.

## Important APIs, types, and functions
`struct kmb_crtc_timing` carries porch and sync widths used for programming. CRTC callbacks include `kmb_crtc_enable_vblank()`, `kmb_crtc_disable_vblank()`, `kmb_crtc_set_mode()`, `kmb_crtc_atomic_enable()`, `kmb_crtc_atomic_disable()`, `kmb_crtc_atomic_begin()`, `kmb_crtc_atomic_flush()`, and `kmb_crtc_mode_valid()`. `kmb_setup_crtc()` creates planes through `kmb_plane_init()` and initializes the DRM CRTC.

## Control flow
Atomic enable prepares the LCD clock, programs DSI via `kmb_dsi_mode_set()`, disables and clears interrupts, writes LCD timing registers, triggers the timing generator, enables the LCD controller, restores interrupt enables, and turns vblank on. Atomic begin masks vertical compare interrupts while a commit is prepared. Atomic flush re-enables vertical compare and arms or immediately sends pending vblank events under the DRM event lock. Atomic disable first disables planes for hardware safety, turns vblank off, and disables the LCD clock. Mode validation only accepts 1920x1080-class modes at 59 to 60 Hz with enough vertical front porch.

## State and persistence
CRTC state lives in the DRM CRTC and `struct kmb_drm_private`. Hardware timing, background color, interrupt compare, and LCD enable bits persist in LCD MMIO until changed or reset. Pending vblank events are consumed in `atomic_flush()`.

## Dependencies and integration points
Uses `kmb_drv.h` register accessors, `kmb_regs.h` register definitions, `kmb_dsi_mode_set()` for downstream MIPI configuration, and `kmb_plane_init()` for the primary/overlay layer set. Integrates with DRM atomic helpers and vblank core.

## Risks
Several timing values are hardcoded rather than derived from the DRM mode, even though logs print the mode porches. Mode validation uses `< KMB_CRTC_MAX_*` tests, effectively rejecting smaller-than-1080p modes despite max naming. Event delivery depends on vblank get succeeding. Disabling planes when the CRTC turns off is required by hardware.

## Test signals
Exercise 1080p60 modesets, invalid resolution/refresh/VFP rejection, vblank interrupt enable/disable, page-flip event delivery, suspend/resume, and CRTC disable with active planes. LCD timing registers and DRM vblank counters are direct diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/kmb/kmb_crtc.c -->
