
# sources/distributed-fs/ceph-client/include/uapi/linux/input.h

## Purpose

`input.h` defines the evdev/input UAPI record layouts, ioctls, device ID and bus constants, multitouch tool types, force-feedback structures, force-feedback effect type constants, and compatibility timestamp layout. The complete 539-line file was read.

## Important APIs, Types, and Functions

Key structs are `input_event`, `input_id`, `input_absinfo`, `input_keymap_entry`, `input_mask`, `ff_replay`, `ff_trigger`, `ff_envelope`, `ff_constant_effect`, `ff_ramp_effect`, `ff_condition_effect`, `ff_periodic_effect`, `ff_rumble_effect`, `ff_haptic_effect`, and `ff_effect`. Important ioctls include `EVIOCGVERSION`, `EVIOCGID`, keycode get/set v1/v2, name/phys/uniq/property queries, `EVIOCGMTSLOTS`, capability/state queries, abs get/set, force-feedback upload/erase/count, grab/revoke, event mask get/set, and `EVIOCSCLOCKID`.

## Control Flow

Applications read `input_event` records from evdev fds and use ioctls to query or change device metadata, capabilities, absolute-axis calibration, event masks, and force-feedback effects. Kernel input core converts driver events into evdev records and applies per-client masks/grabs.

## State and Persistence Behavior

Per-device state includes capabilities, keymaps, abs info, repeat settings, force-feedback effect slots, and clock selection. Per-client state includes event masks, grabs, revocation, and read queues.

## Dependencies and Integration Points

It conditionally includes libc headers for user space, includes `linux/types.h`, and includes `input-event-codes.h`. It integrates with evdev, input drivers, HID, force-feedback drivers, libinput, SDL/game frameworks, and desktop stacks.

## Risks and Edge Cases

`input_event` timestamp layout varies with word size and `__USE_TIME_BITS64`; this is a core compat risk. Other risks include `__user *custom_data` in force-feedback uploads, variable ioctl buffer lengths, per-client event mask semantics, revoked fds returning `ENODEV`, and force-feedback effect ID limits around `FF_GAIN`.

## Test Signals

Input selftests should cover 32/64-bit timestamp layout, keymap v1/v2 ioctls, abs calibration, multitouch slot queries, event masks, grab/revoke, force-feedback upload/update/delete, and clock id selection.
