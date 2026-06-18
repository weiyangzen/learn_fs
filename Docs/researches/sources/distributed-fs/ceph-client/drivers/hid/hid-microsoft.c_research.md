# sources/distributed-fs/ceph-client/drivers/hid/hid-microsoft.c

## Purpose

`hid-microsoft.c` collects quirks for Microsoft-branded HID devices and compatible Bluetooth controllers. It fixes a specific bad report descriptor, maps vendor usages on ergonomic keyboards and presenters, suppresses duplicate usages or unwanted Surface Dial axes, applies selected HID core quirks, and provides Bluetooth Xbox/8BitDo rumble support through a worker-sent output report.

## Important APIs, Types, and Functions

- Quirk bits `MS_HIDINPUT`, `MS_ERGONOMY`, `MS_PRESENTER`, `MS_RDESC`, `MS_NOGET`, `MS_DUPLICATE_USAGES`, `MS_SURFACE_DIAL`, and `MS_QUIRK_FF` select behavior from the ID table.
- `struct ms_data` stores quirks, HID device pointer, FF work item, current strong/weak magnitudes, and a DMA-safe output report buffer.
- `ms_report_fixup()` patches Wireless Desktop Receiver Model 1028 descriptor bytes from Usage Min/Max to Physical Min/Max.
- `ms_ergonomy_kb_quirk()`, `ms_presenter_8k_quirk()`, and `ms_surface_dial_quirk()` implement input mapping decisions.
- `ms_event()` handles vendor-packed ergonomic keyboard events for keypad symbols, scroll wheel deltas, and F14-F18 style keys.
- `ms_init_ff()`, `ms_play_effect()`, `ms_ff_worker()`, and `ms_remove_ff()` implement Xbox-style rumble report 3.
- `ms_probe()` allocates state, applies HID quirks, parses/starts HID, and initializes FF; `ms_remove()` stops HID and cancels FF work.

## Control Flow

The ID table supplies quirk bits. Probe stores them, sets `HID_QUIRK_NOGET` or `HID_QUIRK_INPUT_PER_APP` where required, parses, then starts HID with normal connections plus `HID_CONNECT_HIDINPUT_FORCE` when needed. During descriptor parsing, `.report_fixup`, `.input_mapping`, and `.input_mapped` adjust mappings. Runtime `.event` consumes special ergonomic keyboard vendor usages that need value decoding instead of normal one-usage mapping.

For FF devices, `ms_init_ff()` takes the first input, allocates an `xb1s_ff_report`, registers `FF_RUMBLE`, and uses `input_ff_create_memless()`. Playback scales 16-bit magnitudes to 0-100, stores them in `ms_data`, and schedules `ms_ff_worker()`, which builds report ID 3 with weak/strong enables, maximum duration/loop count, and the two magnitudes before calling `hid_hw_output_report()`.

## State and Persistence Behavior

Quirk selection is persistent for the HID device lifetime. FF state is cached as two 8-bit magnitudes and a reusable output buffer. The ergonomic key handler has a function-static `last_key` used to release the previously emitted F14-F18 key; because it is static, it is shared across devices. There is no durable storage.

## Dependencies and Integration Points

The driver integrates HID core callbacks for report fixup, input mapping, mapped cleanup, events, probe/remove, Linux input key/relative events, workqueues, and input FF. Device IDs and key constants come from kernel HID/input headers and `hid-ids.h`.

## Risks and Edge Cases

- `ms_remove()` calls `hid_hw_stop()` before `ms_remove_ff()`. Any pending worker is canceled after hardware stop, which prevents future sends but means ordering should be reviewed if FF teardown changes.
- The static `last_key` in `ms_event()` is shared across all devices and could release the wrong key if multiple matching keyboards emit interleaved events.
- Descriptor fixup uses exact size/byte offsets and will skip near variants.
- FF playback writes shared `strong`/`weak` values without explicit locking; repeated effects coalesce through the workqueue and may drop intermediate states, which is acceptable for rumble but worth noting.
- Surface Dial filtering returns `-1` for several axes, so descriptor changes could hide useful controls.

## Test Signals

Test descriptor fixup on the exact Model 1028 descriptor, ergonomic vendor-usage mapping and value event decoding, presenter mappings, duplicate usage clearing, Surface Dial ignored axes, `HID_QUIRK_NOGET`, and forced hidinput connection. FF tests should validate report bytes for zero/nonzero rumble, worker cancellation on remove, and no warnings on unsupported effect types.
