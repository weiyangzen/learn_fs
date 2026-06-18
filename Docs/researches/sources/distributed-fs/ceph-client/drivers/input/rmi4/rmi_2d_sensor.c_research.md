<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_2d_sensor.c -->
# sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_2d_sensor.c

## Purpose
`rmi_2d_sensor.c` provides shared helpers for RMI4 2D pointing functions such as F11 and F12. It applies axis alignment, clipping, offsets, tracking, input capability setup, absolute multitouch reporting, relative reporting, and device-tree parsing.

## Important APIs, Types, and Functions
Exported helpers are `rmi_2d_sensor_abs_process()`, `rmi_2d_sensor_abs_report()`, `rmi_2d_sensor_rel_report()`, `rmi_2d_sensor_configure_input()`, and `rmi_2d_sensor_of_probe()`. The code operates on `struct rmi_2d_sensor` and `struct rmi_2d_sensor_abs_object` from `rmi_2d_sensor.h`.

## Control Flow
Function drivers parse raw object data, call `rmi_2d_sensor_abs_process()` to transform coordinates and update `tracking_pos`, then call `rmi_2d_sensor_abs_report()` to select an MT slot and report position, pressure, major/minor touch dimensions, orientation, and slot state. Relative deltas pass through `rmi_2d_sensor_rel_report()`, which clamps to signed 8-bit range and applies axis flips/swaps. `rmi_2d_sensor_configure_input()` attaches the shared RMI input device and sets MT/REL capabilities according to sensor flags. OF probing fills axis, sensor type, physical size, report mask, and rezero wait parameters from device properties.

## State and Persistence
The helper mutates per-function `struct rmi_2d_sensor` state: clipped min/max, tracking positions, tracking slots, input pointer, and optional `dmax`. It does not persist configuration beyond the active device binding; DT/platform data provides static configuration.

## Dependencies and Integration Points
The file depends on Linux input MT helpers, OF property helpers, RMI debug, and `rmi_driver_data->input`. F11/F12 function drivers use this shared code to avoid duplicating sensor setup and event reporting.

## Risks and Edge Cases
The clipping high path uses `min(sensor->max_x, obj->x)` and `min(sensor->max_y, obj->y)` after checking high clip fields, so the configured high clips only constrain `sensor->max_*` earlier in input setup. Kernel tracking and function-provided slot IDs must match allocated arrays. Resolution and `dmax` depend on physical dimensions being present. Released fingers retain prior coordinates by design.

## Test Signals
Validate axis flip, swap, offsets, clipping, touchpad versus touchscreen MT flags, kernel tracking, relative movement clamping, DT property parsing, and F11/F12 raw object conversion through `evtest` or input selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_2d_sensor.c -->
