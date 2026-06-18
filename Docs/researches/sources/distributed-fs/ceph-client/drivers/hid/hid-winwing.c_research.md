# sources/distributed-fs/ceph-client/drivers/hid/hid-winwing.c

## Purpose

`hid-winwing.c` supports WinWing Orion 2 throttle grips. It remaps high-numbered HID buttons into Linux key codes, registers three LED class devices, and enables two-channel rumble force feedback for grip variants that support it.

## Important APIs, Types, and Functions

- `struct winwing_drv_data`: per-device state for report buffers, LED objects, rumble work, cached rumble strengths, and model capability.
- `winwing_led_write` and `winwing_init_led`: send vendor-style output reports and register backlight/A-A/A-G LEDs.
- `winwing_map_button` and `winwing_input_mapping`: translate button numbers 1..112 into joystick, trigger-happy, macro, or reserved key codes depending on `has_grip15`.
- `convert_magnitude`, `winwing_haptic_rumble`, `winwing_play_effect`, and `winwing_init_ff`: implement memless `FF_RUMBLE` by sending separate left/right output reports.
- `winwing_probe`, `winwing_input_configured`, and `winwing_remove`: allocate state, start HID, initialize LED/FF after input configuration, and cancel work on removal.

## Control Flow

Probe parses the HID descriptor, allocates flexible per-device state for three LEDs, stores model capability from `driver_data`, initializes rumble work, and starts HID. During input mapping, button usages in the joystick application collection are remapped. Once HID input is configured, the driver registers LED class devices and, for grip-15 variants, installs memless force feedback. LED writes and rumble work send 14-byte vendor output reports through `hid_hw_output_report`.

## State and Persistence Behavior

LED state persists through registered classdevs and a shared `report_lights` buffer protected by `lights_lock`. Rumble state persists in `data->rumble`, `rumble_left`, and `rumble_right`, with output performed asynchronously by `rumble_work`. Device-managed allocations are released automatically after remove.

## Dependencies and Integration Points

The driver integrates with HID parsing/input mapping, LED class devices, Linux input force feedback, workqueues, mutexes, and USB HID output reports. The id table hard-codes four WinWing USB product IDs and uses `driver_data` as a capability bit.

## Risks and Edge Cases

- `lights_lock` is declared but not initialized in `winwing_probe`, yet `winwing_led_write` uses it.
- `winwing_init_ff` does not check `report_rumble` allocation failure before using the buffer later.
- `winwing_input_configured` ignores the return value of `winwing_init_ff`.
- Rumble effect writes assign `data->rumble` without a lock while the work item reads it.
- Vendor output report formats are derived from captures; firmware changes may require report updates.

## Test Signals

- Confirm every listed product binds and maps buttons to non-conflicting key codes.
- Use LED class brightness writes for all three LEDs and check serialized output reports.
- On grip-15 devices, run `fftest` and confirm left/right rumble magnitudes change only when values differ.
- Run lockdep/KASAN to catch the uninitialized mutex and allocation failure paths.
