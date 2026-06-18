<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/input/touch-overlay.h -->
# sources/distributed-fs/ceph-client/include/linux/input/touch-overlay.h

Purpose: Declares helper APIs for mapping touchscreen contacts through overlay regions.

Important APIs/types/functions: `touch_overlay_map()` associates overlay data with an input device. `touch_overlay_get_touchscreen_abs()` retrieves adjusted absolute ranges. `touch_overlay_mapped_touchscreen()` reports whether overlays exist. `touch_overlay_process_contact()` transforms or filters per-slot `input_mt_pos` contacts. `touch_overlay_sync_frame()` completes frame processing.

Control flow: Touchscreen drivers parse/map overlays, process each contact before reporting, then sync overlay state each frame.

State/persistence: Overlay definitions live in the passed list; per-frame/contact state is managed by implementation code.

Dependencies/integration: Depends on input devices, multitouch positions, list heads, and touchscreen firmware/property parsing.

Risks: Coordinate transforms must match input abs ranges; slot-specific filtering can drop contacts if sync is mishandled.

Test signals: Overlay mapped/unmapped devices, transformed coordinates, filtered contacts, multitouch slot behavior, and frame sync.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/input/touch-overlay.h -->
