# sources/distributed-fs/ceph-client/drivers/leds/leds-cobalt-qube.c

## Purpose
Implements the front LED for Cobalt Qube systems using one memory-mapped byte port. It exposes a single LED classdev named `qube::front` with the `default-on` trigger.

## Important APIs, Types, And Functions
Global `led_port` stores the mapped MMIO address and `led_value` stores the byte written. `qube_front_led_set` is the LED callback; `cobalt_qube_led_probe` maps the resource and registers the classdev.

## Control Flow
Probe obtains the first memory resource, maps it, sets both front LED bits on, writes the byte, and registers the LED through devm. Brightness on writes both front LED bits; brightness off writes the inverse of both bits.

## State And Persistence
State is global and single-instance. Hardware state is the byte written to the mapped port. The classdev starts at `LED_FULL`.

## Dependencies And Integration Points
Depends on platform memory resources, MMIO byte access, and LED class. Platform alias is `cobalt-qube-leds`.

## Risks
The off value is `~(LED_FRONT_LEFT | LED_FRONT_RIGHT)` assigned to `u8`, which sets all other bits high and assumes that is safe for the port. Global state prevents multiple instances. There is no locking because only one LED is exposed.

## Test Signals
Probe should map the resource, write the initial on byte, and create `qube::front`. Brightness toggles should write expected bytes and default trigger should keep the LED on unless userspace changes it.
