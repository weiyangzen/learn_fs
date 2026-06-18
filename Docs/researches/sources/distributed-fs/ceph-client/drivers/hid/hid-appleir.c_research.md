# sources/distributed-fs/ceph-client/drivers/hid/hid-appleir.c

## Purpose

`hid-appleir.c` is a HID driver for Apple infrared remote receivers. Apple remotes send short vendor-specific raw HID packets rather than a normal keyboard-like report descriptor, so this driver decodes the raw packet patterns into Linux input key events for menu, play/pause, forward, back, volume up/down, enter, and repeats.

## Important APIs, Types, and Functions

- `appleir_key_table[]` maps decoded key indices to Linux key codes.
- `struct appleir` stores the input device, HID device, mutable keymap, key-up timer, spinlock, current pressed key, and the first key index for two-packet commands.
- `get_key()` extracts a key index from bits 2..9 of the command byte and returns negative indices for two-packet command prefixes.
- `key_down()`, `key_up()`, and `battery_flat()` wrap input reporting and diagnostics.
- `key_up_tick()` releases the current key after a timeout because the remote does not send ordinary key-up packets.
- `appleir_raw_event()` decodes keydown, repeat, and flat-battery packet prefixes and emits input events while leaving reports visible to hidraw and hiddev.
- `appleir_input_configured()` installs the keymap and input capabilities.
- `appleir_input_mapping()` returns `-1` to suppress generic HID mappings.
- `appleir_probe()` forces HID input registration, initializes state and timer, parses the device, and starts hardware with HIDDEV forced.

## Control Flow

Probe allocates `struct appleir`, stores the HID pointer, sets `HID_QUIRK_HIDINPUT_FORCE`, initializes the spinlock and timer, parses the descriptor, and starts hardware with `HID_CONNECT_DEFAULT | HID_CONNECT_HIDDEV_FORCE`.

When the input device is configured, the driver assigns its keymap storage, enables `EV_KEY` and `EV_REP`, copies the default key table, marks all mapped keys as supported, and clears `KEY_RESERVED`.

Raw event flow only handles 5-byte packets while HID input is claimed. Packets starting `25 87 ee` are keydown packets. The driver releases any previously pressed key, handles pending two-packet state, decodes the current key, reports it down, schedules a key-up timer for one eighth of a second, and clears two-packet state. If `get_key()` returns a negative value, the index is stored as `prev_key_idx` and the next keydown packet completes the command. Packets starting `26` are repeats: they re-report the current key and extend the release timer. Packets starting `25 87 e0` log a possible flat battery message and then fall through to the normal return path.

## State and Persistence Behavior

All persistent runtime state is per device. `current_key` tracks the key currently considered pressed, and the timer releases it if no repeat extends the timeout. `prev_key_idx` carries state between the two packets used by some remote generations to distinguish middle versus play/pause commands. Access to `current_key` in timer and raw-event paths is protected by `spinlock_t lock` for keydown handling and timer release. There is no storage beyond the device lifetime.

## Dependencies and Integration Points

- Depends on HID raw event, input configured, input mapping, probe, and remove hooks.
- Uses the input subsystem keymap fields so userspace can inspect or change key codes.
- Uses kernel timers and spinlocks to synthesize key releases safely.
- Forces HID input and HIDDEV paths while returning `0` from raw event so hidraw/hiddev still receive the underlying reports.
- Matches five Apple IR receiver USB device IDs from `hid-ids.h`.

## Risks and Edge Cases

- The repeat packet path reads and reports `current_key` without taking the spinlock, while the timer can clear it under lock. This may be benign for an int-sized field but is a concurrency edge.
- If a repeat packet arrives before any keydown, `current_key` is zero and `key_down()` can report key code `0`, which maps to `KEY_RESERVED`.
- `prev_key_idx` is reset outside the spinlock on non-keydown paths, while keydown handling updates it under lock.
- The decoder hard-codes 5-byte packets and prefix bytes from known remotes. Newer remotes with different packet lengths or prefixes will pass through without input events.
- The timeout-based key release can create short releases during long holds if repeat packets are delayed beyond `HZ / 8`.

## Test Signals

- Raw packet tests should feed known packet sequences for old and newer remotes and verify decoded key codes.
- Two-packet tests should verify `0x5c/0x5d` plus follow-up maps to `KEY_ENTER` and `0x5e/0x5f` plus follow-up maps to play/pause.
- Repeat tests should verify repeat packets extend the timer and do not emit unexpected keys when no current key exists.
- Timer tests should confirm keys are released after one eighth of a second without repeat.
- Input configuration tests should verify keymap size, `EV_KEY`, `EV_REP`, supported key bits, and generic HID mapping suppression.
- Remove tests should verify `timer_delete_sync()` prevents timer callbacks after `hid_hw_stop()`.
