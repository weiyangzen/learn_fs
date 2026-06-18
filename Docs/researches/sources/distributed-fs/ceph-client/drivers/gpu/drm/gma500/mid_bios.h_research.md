# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/mid_bios.h

## Purpose
This header exposes the MID platform setup hook used by Oaktrail/Moorestown-specific chip setup. It is intentionally small and keeps MID BIOS/GCT parsing private to `mid_bios.c`.

## Important APIs, Types, and Functions
The only declaration is `int mid_chip_setup(struct drm_device *dev);`, with a forward declaration for `struct drm_device`.

## Control Flow
There is no executable flow. Consumers include this header and call `mid_chip_setup()` during chip initialization before output probing, so display code can rely on fuse, core clock, and GCT state in `drm_psb_private`.

## State and Persistence Behavior
The header owns no state. The called implementation writes state into `drm_psb_private`, notably `core_freq`, display selection flags, `has_gct`, and `gct_data`.

## Dependencies and Integration Points
It integrates `oaktrail_device.c` with `mid_bios.c` while avoiding exposure of the private GCT parser helpers.

## Risks
Because the contract is a single broad setup call, callers cannot distinguish partial success unless the implementation returns errors; the current implementation generally returns `0` after logging problems.

## Test Signals
Build coverage should ensure Oaktrail chip setup resolves `mid_chip_setup()`. Runtime signals are the MID discovery logs and populated platform fields before LVDS/HDMI initialization.
