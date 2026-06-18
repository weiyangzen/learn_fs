# sources/distributed-fs/ceph-client/drivers/pwm/pwm-sun4i.c

## Purpose

`pwm-sun4i.c` supports Allwinner sun4i-family PWM controllers with variant-specific channel counts, prescaler bypass, and direct module-clock output.

## APIs, control flow, and state

`struct sun4i_pwm_data` describes variant features. `get_state()` reads shared control and period registers, handles direct bypass specially, and reconstructs polarity/enable/period/duty. `sun4i_pwm_calculate()` chooses bypass or prescaler/counts. Apply enables the mod clock as needed, updates bypass/prescaler/period/duty/polarity/enable bits, waits one old period before final disable, then gates the clock.

No software state is kept. Bus clock stays enabled for register access; mod clock is active only when needed.

## Dependencies and integration points

The driver binds multiple Allwinner compatibles, uses optional `mod`/`bus` clocks, optional reset, MMIO, and PWM core state.

## Risks and test signals

Direct bypass ignores normal period-completion semantics. Bypass detection multiplies period by clock rate and should be checked for overflow on extreme values. Disable can sleep for long periods. Test all variants, bypass modes, polarity, long disable, boot readback, reset, and period boundaries.
