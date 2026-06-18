<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-lp3943.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-lp3943.c

## Purpose
`gpio-lp3943.c` exposes the 16 GPIO-capable pins of the TI/National LP3943 MFD device. It arbitrates pins shared with other LP3943 functions and tracks direction in software because hardware lacks a direction register.

## Important APIs, types, and functions
`struct lp3943_gpio` stores the gpiochip, parent `struct lp3943`, and `input_mask`. Request/free use `lp3943->pin_used`. `lp3943_gpio_set_mode()` writes mux configuration; get reads either input status registers or mux output state depending on `input_mask`.

## Control flow
Probe gets the parent MFD data, copies a gpiochip template, sets parent, and registers it. Direction input marks the bit in `input_mask` and writes input mux mode. Direction output writes the requested output mode and clears the input bit. Get chooses input or output readback based on the software mask.

## State and persistence behavior
The parent MFD tracks pin ownership in `pin_used`. The GPIO driver tracks direction in `input_mask`; hardware only exposes input and output status. Output levels are encoded through mux mode values rather than a separate output register.

## Dependencies and integration points
It is a platform child of the LP3943 MFD, uses LP3943 reg helpers and mux tables, and binds to `ti,lp3943-gpio`.

## Risks and edge cases
Direction state can become stale if another function changes mux state outside this driver. Requesting a pin already assigned to another LP3943 subfunction returns `-EBUSY`. Output get returns `-EINVAL` for unexpected mux states.

## Test signals
Test pin ownership conflicts, input and output direction transitions, reads from GPIO A/B input registers, output readback from mux registers, and coexistence with LP3943 LED/PWM functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-lp3943.c -->
