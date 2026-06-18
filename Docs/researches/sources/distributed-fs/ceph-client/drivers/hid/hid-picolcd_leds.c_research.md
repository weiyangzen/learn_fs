<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-picolcd_leds.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-picolcd_leds.c

## Purpose
This module exposes PicoLCD's eight general-purpose output bits as LED class devices named `GPO0` through `GPO7`, and writes their combined bitmask through `REPORT_LED_STATE`.

## Important APIs, types, and functions
`picolcd_leds_set` sends the cached bitmask to hardware. `picolcd_led_set_brightness` and `picolcd_led_get_brightness` implement per-LED class operations by locating the LED pointer in `data->led[]`. `picolcd_init_leds` validates the LED report and registers eight allocated `led_classdev` instances. `picolcd_exit_leds` unregisters and frees them.

## Control flow
On initialization, each LED classdev is allocated with space for its name, registered, and stored in `data->led[i]`. Setting brightness toggles the corresponding bit in `data->led_state`; if the bit changes, the aggregate state is sent under `data->lock`. `picolcd_leds_set` is also called after reset to restore the cached output state.

## State and persistence behavior
The LED state is an 8-bit runtime cache in `data->led_state` plus the registered LED pointers. It is restored after reset/resume but is not stored persistently.

## Dependencies and integration points
The module depends on HID output reports, LED class, and the shared PicoLCD lock/status. LED class callbacks derive `hdev` from the parent device to recover `picolcd_data`.

## Risks and test signals
Risks include partially registered LEDs on allocation failure, pointer arithmetic in brightness callbacks, and updates during removal. Tests should toggle each GPO independently, verify aggregate report bytes, test registration failure unwind, reset restore, and remove while LEDs are visible in sysfs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-picolcd_leds.c -->
