# sources/distributed-fs/ceph-client/drivers/input/touchscreen.c

## Purpose
`touchscreen.c` implements generic helpers for touchscreen and 2D pointing-device drivers. It parses common firmware properties for axis limits, fuzz, pressure, inversion, and X/Y swapping, then applies those transforms when reporting positions.

## Important APIs, types, and functions
Exported APIs are `touchscreen_parse_properties()`, `touchscreen_set_mt_pos()`, and `touchscreen_report_pos()`. Internal helpers are `touchscreen_get_prop_u32()`, `touchscreen_set_params()`, and `touchscreen_apply_prop_to_x_y()`. The caller-visible state is `struct touchscreen_properties`.

## Control flow
Parsing allocates absinfo, chooses single-touch or MT axes, reads min/size/fuzz properties for X and Y and pressure properties, and updates existing axis parameters only when data is present. If a properties struct is provided, it records maximum X/Y, detects inversion and swapping booleans, normalizes inverted axes to start at zero, and swaps X/Y absinfo when requested. Reporting helpers apply inversion then swapping before filling `input_mt_pos` or reporting ABS_X/ABS_Y or ABS_MT_POSITION_X/Y.

## State and persistence
The helper mutates `input_dev->absinfo` during probe/setup and stores transform flags and pre-inversion maxima in the caller's `struct touchscreen_properties`. There is no global or persistent state.

## Dependencies and integration points
It depends on generic device properties, input absinfo allocation, input multitouch position structs, and exported symbols consumed by touchscreen drivers throughout `drivers/input/touchscreen`.

## Risks
Drivers must set up the relevant ABS axes before parsing; otherwise parameters are ignored with a warning. Size properties are converted to maximum by subtracting one, so zero sizes underflow. Transform order is fixed as invert X/Y before swap, and drivers must use the helper consistently for all reported coordinates.

## Test signals
Test no-property defaults, min/size/fuzz overrides, single-touch vs multitouch axis selection, pressure properties, missing ABS axes warning path, inverted axes normalization, swapped axes, combined invert+swap transforms, and both report APIs.
