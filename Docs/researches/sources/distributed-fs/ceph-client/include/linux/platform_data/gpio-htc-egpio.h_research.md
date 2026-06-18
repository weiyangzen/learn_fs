
# sources/distributed-fs/ceph-client/include/linux/platform_data/gpio-htc-egpio.h

## Purpose
This header defines platform data for HTC's simple EGPIO GPIO/IRQ extender. It describes register ranges that become GPIO chips plus IRQ acknowledgement behavior.

## Important APIs And Types
`HTC_EGPIO_OUTPUT` and `HTC_EGPIO_INPUT` are descriptive all-output/all-input masks. `struct htc_egpio_chip` defines register start, GPIO base, GPIO count, direction bitfield, and initial output values. `struct htc_egpio_platform_data` defines bus/register width, IRQ base/count, ack inversion, ack register, chip descriptor array, and descriptor count.

## Control Flow, State, And Persistence
The driver consumes chip descriptors at probe to create gpiochips, initialize direction/output state, and wire IRQ handling. IRQ flow depends on `invert_acks`: some hardware acknowledges by writing zero instead of one. State is hardware register state and Linux GPIO/IRQ registration.

## Dependencies And Integration Points
It integrates HTC board files with gpiochip and irqchip registration for external GPIO expanders.

## Risks And Test Signals
Risks include wrong register width or bus alignment, GPIO base overlap, bad direction masks, and inverted IRQ ack configuration causing interrupt storms or lost IRQs. Test signals include GPIO direction/value tests, initial output state verification, IRQ trigger/ack tests, and multi-chip range registration.
