<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/trackpoint.h -->
# sources/distributed-fs/ceph-client/drivers/input/mouse/trackpoint.h

## Purpose
`trackpoint.h` defines the IBM TrackPoint PS/2 command set, variant IDs, RAM/register addresses, toggle masks, default parameter values, and the per-device data structure used by `trackpoint.c`.

## Important APIs, Types, and Functions
The header provides `TP_COMMAND`, `TP_READ_ID`, variant IDs, reset/power commands, memory access commands, sensitivity/speed/threshold addresses, toggle masks, double-tap values, default settings, and `MAKE_PS2_CMD()`. `struct trackpoint_data` stores variant, firmware, integer tunables, and boolean toggles. It declares `trackpoint_detect()`.

## Control Flow
No executable flow lives here, but the constants directly drive `ps2_command()` packet construction and sysfs attribute generation in `trackpoint.c`.

## State and Persistence
`struct trackpoint_data` is the volatile software mirror of programmable TrackPoint settings. The defaults represent hardware power-on values used to skip unnecessary writes after a successful reset.

## Dependencies and Integration Points
The header is consumed by the TrackPoint PS/2 driver and assumes psmouse integration. The command values map to IBM TrackPoint engineering documentation and compatible vendor variants.

## Risks and Edge Cases
Incorrect command or mask constants can make the pointing stick unusable until hardware reset. The same RAM location is used for `TP_DRAGHYS` and `TP_DOUBLETAP` semantics, so callers must use the right value for the intended feature.

## Test Signals
Compile-time coverage and runtime `trackpoint_detect()` behavior are the main signals. Sysfs default values should match the constants and write operations should produce expected hardware changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/trackpoint.h -->
