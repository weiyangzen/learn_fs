# sources/distributed-fs/ceph-client/drivers/pwm/pwm-rcar.c

## Purpose

`pwm-rcar.c` is the Renesas R-Car PWM Timer driver. It exposes one normal-polarity PWM backed by `RCAR_PWMCR` and `RCAR_PWMCNT`. The hardware cannot generate 0% duty because zero cycle or phase fields are prohibited.

## APIs, control flow, and state

`struct rcar_pwm_chip` stores MMIO base and clock. `rcar_pwm_get_clock_division()` chooses a divider up to 24 so the 10-bit cycle field can represent the period. `rcar_pwm_set_counter()` computes cycle and phase fields and rejects zero values. `.request`/`.free` use runtime PM; `.apply` disables directly for disabled state, otherwise sets `SYNC`, writes counter and clock control, clears `SYNC`, and sets `EN0`.

No software period/duty state is kept; register state is persistent hardware state. Runtime PM is held for the requested lifetime, so apply assumes an active device.

## Dependencies and integration points

The driver binds `renesas,pwm-rcar`, uses platform MMIO, one clock, runtime PM, and the PWM core.

## Risks and test signals

Enabled 0% duty returns `-EINVAL`, long periods can return `-ERANGE`, and no `.get_state` reports boot state. `pm_runtime_get_sync()` in request is not balanced on failure. Test divider boundaries, zero duty rejection, inverted polarity rejection, disable clearing `EN0`, sync bracketing, and PM failure handling.
