<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/trackpoint.c -->
# sources/distributed-fs/ceph-client/drivers/input/mouse/trackpoint.c

## Purpose
`trackpoint.c` detects IBM-compatible PS/2 TrackPoint devices, configures their programmable parameters, exposes sysfs knobs, and enables model-specific features such as middle-button support and double-tap on capable Lenovo devices.

## Important APIs, Types, and Functions
The public entry point is `trackpoint_detect()`. Low-level I/O helpers are `trackpoint_read()`, `trackpoint_write()`, `trackpoint_toggle_bit()`, `trackpoint_update_bit()`, and `trackpoint_power_on_reset()`. Sysfs attributes are generated through `TRACKPOINT_INT_ATTR` and `TRACKPOINT_BIT_ATTR` for sensitivity, speed, inertia, thresholds, press-to-select, skipback, and external-device toggling. `trackpoint_sync()`, `trackpoint_defaults()`, `trackpoint_reconnect()`, and `trackpoint_disconnect()` manage lifecycle.

## Control Flow
Detection starts with `TP_READ_ID` and accepts known variant IDs. On property setup, it allocates `struct trackpoint_data`, stores variant/firmware IDs, sets psmouse vendor/name callbacks, queries extended button info for IBM devices, adds input capabilities, optionally power-on-resets, synchronizes non-default or unknown-state parameters, creates the sysfs attribute group, logs firmware/buttons, and enables double-tap when the serio firmware ID passes the Lenovo PNP allow/deny logic. Reconnect re-runs protocol start, attempts power-on reset for IBM devices, then syncs current settings back into hardware.

## State and Persistence
Per-device state lives in `psmouse->private` and mirrors hardware tunables. Sysfs writes update both the private field and the device RAM/register bit immediately. Values persist only while the driver instance is active; reconnect writes the remembered settings back after reset.

## Dependencies and Integration Points
The driver integrates with psmouse/libps2 commands, serio device sysfs, Linux input capability reporting, and psmouse attribute helper macros. It relies on constants and `struct trackpoint_data` from `trackpoint.h`.

## Risks and Edge Cases
Only IBM variants expose the full sysfs set; non-IBM variants expose a limited subset. Bit toggles are guarded to command locations 0x20..0x2e because toggling outside that range is unsafe. Some firmware reports zero or unreadable extended button data, so the driver assumes three buttons. Double-tap enablement is gated by PNP ID because several Lenovo devices are known incapable.

## Test Signals
Validate sysfs attribute visibility by variant, writes that change hardware behavior, reconnect after suspend with settings preserved, middle-button capability reporting, and double-tap enablement only on allowed PNP IDs. Fault-inject failed `ps2_command()` calls to ensure detection and reconnect abort cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/trackpoint.c -->
