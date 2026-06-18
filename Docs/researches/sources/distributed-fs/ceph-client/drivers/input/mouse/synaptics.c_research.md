<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/synaptics.c -->
# sources/distributed-fs/ceph-client/drivers/input/mouse/synaptics.c

## Purpose
`synaptics.c` is the PS/2 Synaptics TouchPad protocol driver. It detects Synaptics devices through PS/2 sliced commands, queries firmware capabilities, chooses a PS/2 absolute/relative mode or SMBus InterTouch path, decodes touchpad packets, reports Linux input events, and handles many historical hardware quirks.

## Important APIs, Types, and Functions
The public entry points are `synaptics_module_init()`, `synaptics_detect()`, `synaptics_init_absolute()`, `synaptics_init_relative()`, `synaptics_init_smbus()`, `synaptics_init()`, and `synaptics_reset()`. Internally, `synaptics_query_hardware()` chains identify, model, firmware, mode, capability, and resolution queries into `struct synaptics_device_info`. `struct synaptics_data` stores the queried info, current mode byte, absolute/relative choice, pass-through serio state, advanced gesture state, and ForcePad click state. Packet handling centers on `synaptics_process_byte()`, `synaptics_parse_hw_state()`, `synaptics_process_packet()`, `synaptics_report_mt_data()`, and `synaptics_report_buttons()`.

## Control Flow
Detection sends four `SETRES` commands followed by `GETINFO` and expects the Synaptics signature byte. Initialization resets the psmouse, queries hardware, optionally tries SMBus InterTouch for devices advertising `SYN_CAP_INTERTOUCH`, and otherwise configures the PS/2 native path through `synaptics_init_ps2()`. In absolute PS/2 mode, six-byte packets are validated byte-by-byte, classified as pass-through or touchpad packets, decoded into `struct synaptics_hw_state`, and translated to `BTN_TOUCH`, button, absolute axis, pressure, tool-width, and multitouch slot events. Relative mode falls back to the generic PS/2 packet handler but keeps Synaptics mode and gesture controls.

## State and Persistence
Runtime state is per `psmouse` in `psmouse->private`. It is not persistent across module unload or reconnect, but sysfs writes to `disable_gesture` change the active device mode until disconnect/reconnect. DMI-derived flags (`impaired_toshiba_kbc`, `broken_olpc_ec`, `cr48_profile_sensor`) are initialized once at module init. Hardware-derived quirks and capability flags are re-queried during reconnect and compared against the original identity to avoid silently binding to a different device.

## Dependencies and Integration Points
The driver integrates with the serio/libps2 `psmouse` core, Linux input multitouch helpers, DMI matching, RMI/SMBus support through `psmouse_smbus_init()`, and optional pass-through serio ports for guest devices such as TrackPoints. It relies on capability macros and data definitions from `synaptics.h`. It also routes some extended stick buttons through the pass-through port using out-of-band serio data.

## Risks and Edge Cases
Protocol parsing is dense and firmware-specific; relaxed packet validation exists because some newabs devices do not satisfy strict masks. Coordinate wraparound handling treats large 13-bit values as negative or edge sentinels. ForcePad click emulation depends on timing and continuing reports while stationary. SMBus setup intentionally leaves breadcrumbs on some failures, which `synaptics_disconnect()` and fallback paths must clean. Reconnect can fail if hardware reports different identity/capability data, and several DMI/PNP quirks alter coordinate ranges or protocol choice.

## Test Signals
Useful signals include successful `psmouse` protocol selection, kernel logs for queried coordinates and capability IDs, `evtest` output for absolute axes, pressure, tool buttons, multitouch slots, clickpad/ForcePad buttons, pass-through TrackPoint behavior, and suspend/resume reconnect. SMBus-capable systems should be tested both with InterTouch enabled and with fallback to PS/2.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/synaptics.c -->
