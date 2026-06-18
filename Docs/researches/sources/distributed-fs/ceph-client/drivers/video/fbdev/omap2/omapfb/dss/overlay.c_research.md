# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/overlay.c

## Purpose
`overlay.c` allocates OMAP DSS overlay objects, initializes overlay sysfs nodes, exposes overlay lookup APIs, and provides common validation helpers for overlay capabilities, color modes, scaling, z-order, rotation type, display bounds, and replication needs.

## Important APIs, types, and functions
Public APIs include `omap_dss_get_num_overlays`, `omap_dss_get_overlay`, `dss_init_overlays`, `dss_uninit_overlays`, `dss_ovl_simple_check`, `dss_ovl_check`, and `dss_ovl_use_replication`. It initializes overlays named `gfx`, `vid1`, `vid2`, and `vid3` based on feature-reported overlay count.

## Control Flow
Initialization allocates the overlay array, assigns names/ids, fills capabilities and supported color modes from DSS feature tables, and creates a sysfs kobject per overlay. Uninit removes kobjects and frees the array. Simple checks reject scaling on non-scaling overlays, unsupported color modes, too-high zorder, and unsupported rotation type. Full checks compute effective output size and ensure the overlay rectangle is inside manager timings. Replication is selected only for RGB12U/RGB16 over wider LCD ports.

## State and Persistence
Global runtime state is `num_overlays` and the allocated `overlays` array. Each overlay stores callback pointers and runtime info managed by other DSS code. No state persists after driver uninit.

## Dependencies and Integration Points
The file depends on DSS feature tables, manager timings, overlay sysfs, exported OMAP DSS APIs, and caller-supplied overlay callback implementations.

## Risks
Allocation failure uses `BUG_ON`. `omap_dss_get_overlay` checks upper bound but not negative input. Bounds checks use `pos + size` and should be watched for integer wrap if inputs are not sanitized elsewhere. Validation only covers common constraints; DISPC-specific limits are in lower layers.

## Test Signals
Test overlay count/name/capability per SoC, sysfs lifecycle, unsupported color/scaling/rotation, zorder bounds, placement outside display, zero output-size fallback, replication decisions, and lookup edge cases.
