# sources/distributed-fs/ceph-client/drivers/hid/hid-bigbenff.c

Purpose: provides descriptor correction, LED class devices, and rumble force-feedback for the BigBen Interactive PS3OFMINIPAD gamepad.

Important APIs/types/functions: `pid0902_rdesc_fixed[]` replaces the original 137-byte descriptor with a gamepad-correct mapping. `struct bigben_device` stores the HID output report, LED state, rumble state, lock, removed flag, four LED class devices, and worker. `bigben_worker()` serializes LED and FF output messages into the output report using `hid_output_report()` and sends raw set-report requests. `hid_bigben_play_effect()` updates right/left motor state for `FF_RUMBLE`. `bigben_set_led()`/`bigben_get_led()` implement LED class operations. `bigben_probe()` parses, starts HID with generic FF disabled, validates the output report, registers memless FF and four LEDs, and schedules initial LED/rumble state. `bigben_remove()` marks removed, cancels work, and stops hardware.

Control flow: report fixup runs before parsing and fully substitutes the descriptor when the original size matches. Probe connects normal input, validates there is an output report with eight values, registers FF and LED devices, initializes LED1 on and rumble off, then schedules the worker. LED brightness changes and FF callbacks only set state and work flags under a spinlock; actual HID transfers happen in process-context work.

State/persistence: LED and motor values persist in `struct bigben_device` and are mirrored to the controller. The removed flag prevents new work from being scheduled during teardown. LED class registrations are devm-managed, while worker cancellation is explicit.

Dependencies/integration: depends on HID parser/output helpers, input FF memless, LED classdev, workqueues, spinlocks, and BigBen USB IDs.

Risks: output report format is hard-coded. The same buffer is reused for LED and FF messages in one worker run, so ordering and work flags matter. LED `brightness_set` can run concurrently with remove; the removed flag and cancel path are the main protection. Unexpected descriptors are allowed but warned, which may leave mappings wrong.

Test signals: verify descriptor replacement, all four LEDs via `/sys/class/leds`, initial LED1 state, rumble weak/strong behavior, no output after remove, warning on descriptor-size mismatch, and normal gamepad button/axis mappings matching Linux gamepad expectations.
