# sources/distributed-fs/ceph-client/drivers/hid/hid-wiimote-core.c

## Purpose

`hid-wiimote-core.c` is the protocol engine for Nintendo Wii Remote, Wii Remote Plus, Balance Board, and Wii U Pro Controller devices over Bluetooth HID. It sends output reports, performs synchronous register/EEPROM commands, detects device and extension types, manages Motion Plus hotplug, selects data-report modes, dispatches incoming report payloads to module handlers, and exposes sysfs/debug integration.

## Important APIs, Types, and Functions

- Output queue: `wiimote_hid_send`, `wiimote_queue_worker`, and `wiimote_queue` serialize HID output reports through a spinlock-protected ring and workqueue.
- Protocol requests: `wiiproto_req_rumble`, `wiiproto_req_leds`, `wiiproto_req_drm`, `wiiproto_req_status`, `wiiproto_req_accel`, `wiiproto_req_ir1`, `wiiproto_req_ir2`, `wiiproto_req_rmem`, and private write-memory helpers build native Wiimote reports.
- Synchronous command helpers: `wiimote_cmd_write` and `wiimote_cmd_read` rely on the mutex/completion contract defined in `hid-wiimote.h`.
- Extension and Motion Plus detection: `wiimote_cmd_init_ext`, `wiimote_cmd_read_ext`, `wiimote_cmd_init_mp`, `wiimote_cmd_read_mp`, `wiimote_cmd_map_mp`, and `wiimote_cmd_read_mp_mapped`.
- Module lifecycle: `wiimote_modules_load/unload`, `wiimote_ext_load/unload`, and `wiimote_mp_load/unload` call the ops tables from `hid-wiimote-modules.c`.
- Initialization/hotplug state machine: `wiimote_init_detect`, `wiimote_init_check`, `wiimote_init_hotplug`, `wiimote_init_worker`, and `wiimote_init_timeout`.
- Report handlers: `handler_status`, `handler_data`, `handler_return`, `handler_drm_*`, `handler_ext`, `handler_ir`, and `handlers[]`.
- Driver entry points: `wiimote_hid_probe`, `wiimote_hid_remove`, `wiimote_hid_event`, `wiimote_create`, and `wiimote_destroy`.

## Control Flow

Probe sets `HID_QUIRK_NO_INIT_REPORTS`, allocates `struct wiimote_data`, parses HID, starts only HIDRAW connection support, opens hardware I/O, creates `extension` and `devtype` sysfs files, initializes debugfs, and schedules detection. Detection sends a status request, optionally initializes the extension bus, reads extension ID bytes, picks a device class by extension/name/VID/PID, and loads the module list for that device.

Runtime output reports are copied into `wdata->queue.outq` and sent by `wiimote_queue_worker`. Synchronous command callers hold `state.sync`, set `state.cmd` and `state.opt` under `state.lock`, queue the relevant output report, and wait up to one second for `handler_data`, `handler_return`, or `handler_status` to complete the command.

Incoming raw reports are matched by report ID and minimum size in `handlers[]`. Each handler runs under `state.lock`, parses button/accelerometer/IR/extension/Motion Plus slots, updates cached status such as battery and hotplug flags, and forwards payloads to the active device or extension module. Hotplug changes schedule `init_worker`, which checks whether the current extension/Motion Plus mapping is still expected; if not, it disables forwarding, reinitializes extension and MP registers, loads/unloads modules, maps MP passthrough when required, updates expected flags, and requests a fresh status report.

## State and Persistence Behavior

Persistent state lives in `struct wiimote_data` and `struct wiimote_state`: queue indices, protocol flags, current DRM, device/extension/MP type, command completion state, cached battery, command read buffer pointer, calibration caches, rumble cache, timer, and loaded input/LED/power-supply/debug objects. `state.lock` protects most protocol state and dispatch-side changes. `state.sync` ensures only one synchronous command is outstanding. The timer persists while MP polling is needed and is cancelled when MP is actively mapped.

## Dependencies and Integration Points

The file integrates with HID core (`hid_parse`, `hid_hw_start`, `hid_hw_open`, raw-event callback), input core via module-created devices, sysfs device attributes, debugfs through `hid-wiimote-debug.c`, and module ops from `hid-wiimote-modules.c`. It depends on Nintendo constants in `hid-ids.h` and shared protocol definitions in `hid-wiimote.h`.

## Risks and Edge Cases

- `wiimote_queue` calls `wiimote_cmd_abort` while holding `queue.lock`, not `state.lock`, on oversized/full queue paths; most command helpers document state-lock requirements.
- Report matching uses `h->size < size`, so a report exactly equal to the expected payload plus ID length is accepted, but the convention is subtle and easy to break when adding handlers.
- Hotplug handling is heuristic because extension and MP registers can alias during remapping. Races between status reports, MP polling, and user opens are the highest-risk behavior.
- Command waits time out after one second; slow Bluetooth links or sleeping devices can surface as `-EIO`.
- Error paths in probe partially duplicate cleanup and must stay aligned with `wiimote_destroy`.

## Test Signals

- Pair each supported Nintendo class and verify `devtype`, `extension`, and module load logs.
- Use `evtest` for core buttons, accelerometer open/close, IR open/close, LEDs, rumble, battery, and all extension types.
- Hotplug Nunchuk/Classic/Guitar/Drums/Turntable and Motion Plus while readers are active and watch for lockdep, stale input devices, or stuck DRM modes.
- Exercise sysfs `extension` write with `scan` and debugfs DRM locking.
- Fault inject output-report failures and queue-full paths to confirm synchronous commands wake with errors.
