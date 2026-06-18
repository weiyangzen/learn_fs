# sources/distributed-fs/ceph-client/drivers/hid/hid-zydacron.c

## Purpose

`hid-zydacron.c` supports the Zydacron remote control by fixing invalid consumer-page descriptor bytes, mapping several remote usages to Linux key codes, and synthesizing press/release behavior for reports that otherwise do not generate clean key transitions.

## Important APIs, Types, and Functions

- `struct zc_device`: stores the endpoint input device pointer and up to four last pressed keys.
- `zc_report_fixup`: patches three descriptor locations from `0xffbc` to consumer page `0x000c` when the expected byte pattern exists.
- `zc_input_mapping`: maps selected consumer usages to `KEY_MODE`, `KEY_SCREEN`, `KEY_INFO`, `KEY_RADIO`, `KEY_PVR`, `KEY_TV`, `KEY_AUDIO`, `KEY_AUX`, `KEY_VIDEO`, `KEY_DVD`, `KEY_MENU`, and `KEY_TEXT`.
- `zc_raw_event`: releases previously tracked keys and emits new press events for report IDs 2 and 3.
- `zc_probe`: allocates device state, parses HID, and starts hardware.

## Control Flow

Probe allocates `zc_device`, installs it as driver data, parses descriptors after fixup, and starts HID. During input mapping, recognized consumer usages are remapped and `last_key` is reset. Raw events for reports 2/3 first release any tracked keys, then decode `data[1]` into one of four special keys and emit a press while recording it for release on the next packet.

## State and Persistence Behavior

Per-device state is devm-managed. `input_ep81` persists as the target input device captured during mapping, and `last_key[4]` tracks synthetic key-down state between raw events.

## Dependencies and Integration Points

The driver depends on HID report-fixup, input-mapping, and raw-event hooks plus Zydacron IDs from `hid-ids.h`. User-space sees standard evdev key events rather than raw consumer usages.

## Risks and Edge Cases

- Descriptor patch offsets are hard-coded and guarded only by size and byte pattern.
- `zc_input_mapping` stores `hi->input` unconditionally before checking usage page; multi-input descriptors could overwrite the endpoint pointer.
- Raw-event release synthesis assumes a new report arrives to break the previous key; lost final reports can leave user-space seeing a key held until another event or device removal.
- Only four special report 2/3 keys use synthetic state; report 4 mappings rely on normal HID handling.

## Test Signals

- Verify descriptor fixup log on the known remote and no patching for changed patterns.
- Press each mapped remote key and confirm press/release pairs in `evtest`.
- Test report IDs 2 and 3 for synthetic keys and report 4 for normal mapped keys.
- Disconnect while a key is logically down and check user-space behavior.
