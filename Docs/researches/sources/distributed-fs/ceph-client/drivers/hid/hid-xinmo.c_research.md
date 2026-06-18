# sources/distributed-fs/ceph-client/drivers/hid/hid-xinmo.c

## Purpose

`hid-xinmo.c` fixes Xin-Mo arcade controller axis events that report `-2` even though the descriptor logical minimum is `-1`. Without this correction, hid-input drops the out-of-range negative direction.

## Important APIs, Types, and Functions

- `xinmo_event`: HID event hook that intercepts ABS_X, ABS_Y, ABS_Z, and ABS_RX values below `-1`, emits a corrected `-1` input event, and consumes the original.
- `xinmo_devices[]`: binds Xin-Mo Dual Arcade and THT 2P Arcade USB IDs.
- `xinmo_driver`: registers only an `.event` hook.

## Control Flow

After normal HID parsing and input setup, every input event for the matched devices passes through `xinmo_event`. Only the four affected axes are changed; all other usages and values fall back to HID core.

## State and Persistence Behavior

There is no persistent state. Each event is corrected independently based on usage code and value.

## Dependencies and Integration Points

The driver uses HID core event hooks and input core `input_event` on the field's input device. It integrates with arcade joystick userspace through corrected evdev absolute axis values.

## Risks and Edge Cases

- Values below `-1` are all collapsed to `-1`; this matches the descriptor but loses any hypothetical extra range.
- Only four axes are corrected. Additional affected axes on future devices would still be dropped.
- The hook assumes `field->hidinput->input` is valid for the corrected event path.

## Test Signals

- Move each player axis in negative directions and confirm evdev reports `-1`, not missing events.
- Check positive and neutral directions remain unchanged.
- Validate both USB IDs bind to the driver.
