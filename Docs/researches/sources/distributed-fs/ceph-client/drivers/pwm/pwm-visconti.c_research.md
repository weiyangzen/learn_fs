# sources/distributed-fs/ceph-client/drivers/pwm/pwm-visconti.c

## Purpose

`pwm-visconti.c` drives Toshiba Visconti four-channel PWM hardware. The input clock is fixed at 1 MHz with divisors 1, 2, 4, or 8. Active updates are shadowed until `PCSR` is written and the current period completes.

## APIs, control flow, and state

`struct visconti_pwm_chip` stores MMIO base. Apply disables by writing zero period, otherwise caps period, clamps duty, converts ns to microsecond ticks, chooses the smallest fitting divider, writes polarity/divider to `PWMC`, duty to `PDUT`, and period to `PCSR` last to latch. `get_state()` reads PCSR/PDUT/PWMC and reconstructs period, duty, and polarity.

No software state exists; hardware registers are source of truth.

## Dependencies and integration points

The driver binds `toshiba,visconti-pwm`, uses MMIO and the PWM core, and manages no clocks or resets directly.

## Risks and test signals

`get_state()` always reports enabled even if `PCSR` is zero, so disabled state can be misreported. Over-maximum periods are capped rather than rejected. Sub-microsecond periods return `-ERANGE`. Test disable readback, max capping, polarity, period-boundary updates, and all four offsets.
