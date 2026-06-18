# sources/distributed-fs/ceph-client/drivers/extcon/extcon-gpio.c

## Purpose
`extcon-gpio.c` is a simple single-state extcon provider driven by one GPIO input and its IRQ.

## Important APIs, types, and functions
`struct gpio_extcon_data` stores the extcon device, delayed work, GPIO descriptor, extcon cable ID, debounce, and resume-check flag. `gpio_extcon_work()` reads the GPIO and synchronizes the extcon state. `gpio_irq_handler()` queues work. `gpio_extcon_probe()` acquires resources and runs initial detection.

## Control flow
Probe allocates private state, requests the `"extcon"` input GPIO, converts it to an IRQ, chooses rising or falling trigger based on active-low polarity, allocates/registers the extcon device, initializes devm-managed delayed work, requests the IRQ, stores driver data, and reads the initial state. Resume optionally queues another check when `check_on_resume` is set.

## State and persistence behavior
Runtime state is only the GPIO descriptor, extcon state, and delayed work. There is no persistence.

## Dependencies and integration points
The driver depends on GPIOLIB, extcon provider APIs, platform devices, IRQs, devm delayed-work helpers, and system power-efficient workqueues.

## Risks and edge cases
`extcon_id`, `debounce`, and `check_on_resume` are never populated from firmware or platform data in this file, so default zero values mean the provider reports cable ID 0 with no debounce unless another mechanism initializes the structure. The FIXME notes that extcon ID discovery is unresolved. IRQ triggering is single-edge based on active polarity, so detach transitions may be missed for level-stable GPIOs unless IRQ type is externally configured.

## Test signals
Probe with active-high and active-low GPIOs, initial state reporting, attach/detach IRQs, resume recheck, invalid GPIO-to-IRQ, missing firmware extcon ID support, and devm cleanup with pending work.
