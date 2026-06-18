# sources/distributed-fs/ceph-client/drivers/leds/leds-lt3593.c

Purpose: GPIO pulse driver for Linear Technology LT3593 LED controllers.

Important APIs/types/functions: `struct lt3593_led_data` stores one LED class device and one control GPIO. `lt3593_led_set()` implements the controller's pulse protocol. `lt3593_led_probe()` validates exactly one LED child, obtains `lltc,ctrl` GPIO, handles `default-state`, and registers the LED.

Control flow: nonzero brightness is converted into a number of falling-edge pulses that reduce current from maximum; zero drives the GPIO low. Full brightness resets the internal level by a low-delay-high sequence. Probe sets initial LED class brightness based on firmware node state but does not explicitly pulse hardware to that state before registration.

State and persistence: current level is stored inside the LT3593 after pulse programming; the driver does not cache it except LED class brightness. Power loss or GPIO reset changes hardware state.

Dependencies and integration: depends on platform devices, firmware-node properties, GPIO descriptors that can sleep, LED class extended registration, and OF compatible `lltc,lt3593`.

Risks: pulse timing is implemented with microsecond delays and can be affected by sleepable GPIO latency. Brightness changes are relative to the chip reset protocol, so missed pulses desynchronize actual current from requested brightness.

Test signals: oscilloscope/GPIO trace for pulse counts and timing, brightness 0/1/255 behavior, default-state handling, missing/multiple child-node failures, and slow GPIO controller behavior.
