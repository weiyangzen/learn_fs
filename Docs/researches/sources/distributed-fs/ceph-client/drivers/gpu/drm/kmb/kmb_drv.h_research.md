<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/kmb/kmb_drv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/kmb/kmb_drv.h

## Purpose
Defines Keem Bay DRM private data, platform limits, clock containers, LCD register access helpers, and CRTC setup prototypes shared by the KMB driver files.

## Important APIs, types, and functions
Important types are `struct kmb_clock` and `struct kmb_drm_private`. Helper functions/macros include `to_kmb()`, `crtc_to_kmb_priv()`, `kmb_write_lcd()`, `kmb_read_lcd()`, `kmb_set_bitmask_lcd()`, and `kmb_clr_bitmask_lcd()`. Constants define 1920x1080 display limits, refresh constraints, default LCD clock, and driver version.

## Control flow
Only inline MMIO accessors execute. They read or write LCD controller registers and implement read-modify-write bit set/clear sequences.

## State and persistence
The private structure is the central runtime state for LCD MMIO, clock handles, DRM CRTC, saved atomic suspend state, IRQ fields, per-plane init state, and underflow recovery flags.

## Dependencies and integration points
Includes DRM device definitions, KMB plane types, and register constants. Used by `kmb_drv.c`, `kmb_crtc.c`, and `kmb_plane.c`.

## Risks
Read-modify-write helpers are not internally locked, so callers must hold appropriate serialization when racing IRQ and atomic paths. The min/max naming around 1920x1080 constants is confusing and can cause incorrect mode-validation changes.

## Test signals
Build coverage catches structure and prototype drift. Runtime signals are correct MMIO programming through users of these helpers and stable underflow state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/kmb/kmb_drv.h -->
