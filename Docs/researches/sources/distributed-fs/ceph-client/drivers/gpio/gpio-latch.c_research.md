<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-latch.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-latch.c

## Purpose
`gpio-latch.c` implements a virtual output-only GPIO controller backed by latch hardware driven by GPIO consumers. It multiplexes a set of data GPIOs across one or more latch clock GPIOs.

## Important APIs, types, and functions
`struct gpio_latch_priv` stores the gpiochip, clock GPIO array, latched data GPIO array, timing properties, shadow bitmap, and either a mutex or spinlock. `gpio_latch_set_unlocked()` updates shadowed values, drives all data lines for a latch, delays, pulses the clock, and returns errors from underlying GPIO sets. Probe chooses sleeping or atomic callbacks based on `gpiod_cansleep()`.

## Control flow
Probe gets `clk-gpios` and `latched-gpios`, computes `ngpio = n_latches * n_latched_gpios`, allocates the shadow bitmap, chooses `set` or `set_can_sleep`, clamps optional nanosecond timing properties to 5000 ns, and registers an output-only gpiochip. Setting any virtual line rewrites the full data bus for its latch and pulses that latch's clock.

## State and persistence behavior
The driver maintains `shadow` as the authoritative value for all virtual latch outputs because readback is not available. The physical latch holds values until power loss or the next clock pulse. No input or IRQ state exists.

## Dependencies and integration points
It binds to `gpio-latch`, uses GPIO consumer arrays, gpiolib provider APIs, pinconf-independent timing properties, and can operate in sleeping or non-sleeping contexts depending on underlying GPIO controllers.

## Risks and edge cases
Every set operation rewrites all data inputs for that latch, so concurrent updates require correct locking. Timing above 5 us is truncated because the driver uses `ndelay()`. Underlying GPIO set errors can leave shadow state updated before all hardware lines are driven.

## Test signals
Test multiple latch and data widths, can-sleep and atomic GPIO providers, setup/clock timing clamps, repeated set operations preserving other shadow bits, and failure injection from underlying GPIO descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-latch.c -->
