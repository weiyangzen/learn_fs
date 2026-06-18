# sources/distributed-fs/ceph-client/drivers/input/touch-overlay.c

## Purpose
`touch-overlay.c` provides helper functions for touchscreen overlay regions described in firmware. It maps rectangular segments that either define a touchscreen sub-area or on-screen buttons, adjusts coordinates, reports overlay key presses, and filters contacts that should not be processed by the client touchscreen driver.

## Important APIs, types, and functions
`struct touch_overlay_segment` stores rectangle origin/size, optional key code, pressed state, and tracking slot. Exported APIs are `touch_overlay_map()`, `touch_overlay_get_touchscreen_abs()`, `touch_overlay_mapped_touchscreen()`, `touch_overlay_sync_frame()`, and `touch_overlay_process_contact()`. Internal helpers parse firmware properties and test whether a contact lies inside a segment.

## Control flow
`touch_overlay_map()` looks for a `touch-overlay` child node under the input device's parent, allocates one segment per available child, reads `x-origin`, `y-origin`, `x-size`, `y-size`, and optional `linux,code`, sets key capabilities for button segments, and appends to the caller's list. During event processing, button segments are checked first to prioritize overlapping buttons. A contact on a button reports key down and marks the MT slot as consumed for the frame. Contacts in a touchscreen segment are shifted to that segment's origin; contacts outside a defined touchscreen area are dropped. Sync releases pressed buttons whose tracked slot is no longer used.

## State and persistence
Segments are devm-allocated and live with the parent device. Each button segment tracks `pressed` and `slot` across frames. Coordinate shifts mutate the caller-provided `input_mt_pos`. There is no persistent state beyond firmware-defined geometry.

## Dependencies and integration points
The helper uses firmware node/property APIs, input multitouch slot state, input key reporting, list management, and `linux/input/touch-overlay.h`. Client touchscreen drivers own the segment list and call these helpers from their report paths.

## Risks
`touch_overlay_get_touchscreen_abs()` uses `x_size - 1` and `y_size - 1`; zero-sized firmware properties would underflow. Button `slot` defaults to zero, so sync logic must only release when `pressed` is true. The first touchscreen segment controls outside-area filtering; multiple touchscreen areas or ordering mistakes may not behave as expected. Clients must call `touch_overlay_sync_frame()` for slot release semantics to work.

## Test signals
Test firmware parsing with no overlay, touchscreen-only, button-only, overlapping button/touchscreen, missing and malformed properties, zero/edge sizes, coordinate shifting, MT slot consumption, slide-out button release, and sync-frame release when a slot disappears.
