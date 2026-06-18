# sources/distributed-fs/ceph-client/drivers/input/misc/powermate.c

## Purpose
`powermate.c` is a USB input driver for the Griffin PowerMate/SoundKnob and compatible Contour jog device. It reports knob button state as `BTN_0`, rotation as `REL_DIAL`, and exposes the device LED pulse configuration through an `EV_MSC`/`MSC_PULSELED` input event.

## Important APIs, Types, and Functions
`struct powermate_device` owns interrupt and control URBs, coherent input data, a USB control request, input device, LED state, an update bitmask, and a spinlock. `powermate_irq()` parses interrupt data and resubmits the interrupt URB. `powermate_sync_state()` serializes pending LED updates into vendor control transfers. `powermate_config_complete()` chains follow-up LED updates after asynchronous control completion. `powermate_pulse_led()` clamps and marks LED state changes. `powermate_input_event()` decodes `MSC_PULSELED`. `powermate_probe()` allocates USB/input resources and starts polling; `powermate_disconnect()` tears them down.

## Control Flow
Probe validates an interrupt-in endpoint, sends a class control request, allocates coherent buffers and two URBs, configures input capabilities, submits the interrupt URB before input registration, registers the input device, then forces a default LED configuration. Interrupt completions report button and dial values, then resubmit themselves. Userspace LED events update desired state under `pm->lock`; if no control URB is active, a vendor request is submitted. Control completion grabs the same lock and sends the next pending LED update until the bitmask is empty. Disconnect stops both URBs, unregisters input, frees buffers, and releases the state object.

## State and Persistence Behavior
Device state tracks the last desired LED static brightness, pulse speed/table, asleep/awake behavior, and `requires_update` bits. Hardware LED state persists on the USB device until later control requests or disconnect/power reset. Input key/relative state is transient through input core. The interrupt URB is continuously resubmitted while the device is connected; the control URB is single-flight and drains pending updates in priority order.

## Dependencies and Integration Points
The driver integrates with USB core, coherent DMA buffer APIs, input core, and evdev clients. It uses vendor/product IDs for Griffin and Contour devices and USB interrupt/control pipes. The `MSC_PULSELED` convention is the userspace integration point for LED programming.

## Risks and Edge Cases
`powermate_alloc_buffers()` returns `-ENOMEM` for the control request allocation but returns `-1` for coherent data failure, losing a precise errno. Probe submits the interrupt URB before registering the input device, so an unusually fast interrupt could race with input registration state. Payload sizes outside 3 to 6 bytes are warned about and clamped to max, which may mask unsupported devices. LED updates are coalesced, so intermediate user-requested LED states can be skipped. Disconnect relies on URB killing before freeing shared structures.

## Test Signals
Signals include USB probe on each ID, malformed endpoint rejection, button/rotation event delivery, high-rate dial events, LED command decoding for brightness/pulse/table/asleep/awake bits, concurrent LED updates while a control URB is active, disconnect while both URBs are pending, and kmemleak/USB fault-injection for allocation and submit failures.
