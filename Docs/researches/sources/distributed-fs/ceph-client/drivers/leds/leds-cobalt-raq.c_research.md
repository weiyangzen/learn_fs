# sources/distributed-fs/ceph-client/drivers/leds/leds-cobalt-raq.c

## Purpose
Implements LED support for Cobalt RaQ systems using a memory-mapped byte port. It exposes a web LED and a power-off LED, the latter using the `power-off` default trigger.

## Important APIs, Types, And Functions
Global `led_port`, `led_value`, and `led_value_lock` manage the shared byte register. `raq_web_led_set` and `raq_power_off_led_set` update individual bits. `cobalt_raq_led_probe` maps the resource and registers both classdevs.

## Control Flow
Probe maps the first memory resource, registers `raq::power-off`, then registers `raq::web`; on failure it unregisters the first LED and clears the port pointer. Each brightness callback takes the spinlock, sets or clears its bit in `led_value`, writes the byte, and releases the lock.

## State And Persistence
Shared `led_value` is the software shadow for both LED bits. Hardware state is the mapped byte port. The driver is built in via `builtin_platform_driver`, so it is expected as platform support rather than a removable module.

## Dependencies And Integration Points
Depends on platform memory resources, MMIO byte writes, spinlocks, and LED class. Platform driver name is `cobalt-raq-leds`.

## Risks
There is no remove path because the driver is builtin. Initial `led_value` defaults to zero until a LED is changed. All shared port writes depend on the spinlock and software shadow staying coherent with hardware.

## Test Signals
Probe should register both LED class devices, power-off trigger should bind to `raq::power-off`, toggling either LED should preserve the other bit in `led_value`, and registration failure should unregister the already-created LED.
