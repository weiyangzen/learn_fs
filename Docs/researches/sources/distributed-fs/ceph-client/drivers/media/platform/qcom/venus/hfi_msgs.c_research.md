# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi_msgs.c

## Purpose
`hfi_msgs.c` parses firmware-to-host HFI messages, demultiplexes them to core or session handlers, converts firmware events into driver callbacks, completes synchronous waits, extracts firmware capabilities/properties, and maps buffer-done messages back to V4L2-visible metadata.

## Important APIs And Functions
- Public message entry points: `hfi_process_msg_packet()` and `hfi_process_watchdog_timeout()`.
- Event handlers: `event_seq_changed()`, `event_release_buffer_ref()`, `event_sys_error()`, `event_session_error()`, `hfi_event_notify()`.
- System response handlers: init done, property info/image version, release resource, ping ack, idle, PC prepare done.
- Session response handlers: property info, init/load/start/stop/flush/release/end/abort/sequence-header done, ETB done, FTB done.
- `to_instance()` maps firmware session IDs back to `venus_inst` using `hash32_ptr()`.
- Static `handlers[]` maps HFI message packet IDs to minimum sizes, optional alternate size, callback, and system/session classification.

## Control Flow
`hfi_process_msg_packet()` looks up the packet type in `handlers[]`, validates packet size against the expected structure(s), resolves a session for non-system messages, and calls the handler. System packets operate with `inst == NULL`; session packets require a valid hashed session ID except system-error events.

Sequence-change events parse a variable list of changed properties from `ext_event_data`, handling frame size, profile/level, bit depth, picture structure, color space, entropy, buffer requirements, input crop, and DPB counts. It validates remaining bytes before each read and reports `EVT_SYS_EVENT_CHANGE`.

Sync response handlers set `core->error` or `inst->error` and complete the matching completion used by `hfi.c`. Buffer-done handlers call session `buf_done()` with HFI buffer type, output/input tag, bytes used, offsets, V4L2 keyframe/P/B/LAST flags, raw HFI flags, and timestamps. Firmware image-version messages parse known string formats into `core->venus_ver`, copy the version string into Qualcomm SMEM when available, and complete core init when a minimum firmware check is required.

## State And Persistence
- Mutates `core->error`, `core->venus_ver`, `inst->error`, and `inst->hprop`.
- Completes `core->done` and `inst->done`.
- Writes the firmware version string into SMEM image version table when available, which is externally visible platform state.
- Delivers events and buffer completions through callbacks, which update higher-level V4L2/session state outside this file.

## Dependencies And Integration Points
- HFI message struct definitions from `hfi_msgs.h`, constants from `hfi_helper.h`, parser from `hfi_parser.h`, core/instance state from `core.h`, SMEM API, and V4L2 buffer flags.
- Complements command builders in `hfi_cmds.c` and state waits in `hfi.c`.
- Integrates with system-error recovery in `core.c` through core event callbacks.

## Risks And Edge Cases
- Packet-size validation is minimal-size based; variable payload parsing must remain careful to avoid out-of-bounds reads.
- `to_instance()` uses hashed pointer IDs, so rare collisions or stale session IDs could misroute messages.
- System-error events may have no valid session; other invalid session IDs are logged and ignored, which can leave waiters timing out.
- Firmware version parsing accepts only known string formats; unrecognized formats log and can leave version fields zero.
- Sequence-change parsing sets `size_read = 0` for unknown property IDs, which risks not advancing over unknown payloads if firmware includes them.

## Test Signals
- HFI init should complete and populate codec capabilities through `hfi_parser()`.
- Firmware image-version responses should populate `core->venus_ver` and allow minimum-version checks.
- Buffer done should produce correct V4L2 LAST/keyframe/P/B flags and timestamps for encoder and decoder.
- Dynamic resolution change should deliver complete event data, including size, crop, bit depth, picture structure, and buffer count.
- Fault injection/watchdog should call core event recovery paths without stuck completions.
