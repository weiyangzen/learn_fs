# sources/distributed-fs/ceph-client/drivers/pwm/pwm-sophgo-sg2042.c

## Purpose

`pwm-sophgo-sg2042.c` supports SG2042 and SG2044 four-channel PWM controllers. Both use `PERIOD` and `HLPERIOD`; SG2044 adds polarity, output direction, and start controls.

## APIs, control flow, and state

`struct sg2042_pwm_ddata` stores MMIO and APB clock rate. SG2042 apply rejects inverted polarity, disables by writing zeros, and converts period/duty to ticks. SG2044 apply writes polarity, duty registers, toggles `PWMSTART` to refresh, and enables output direction/start for enabled states. `get_state()` reads period/high-period, clamps duty, and reports disabled on zero period.

No software state is kept; clock rate is cached and locked exclusively.

## Dependencies and integration points

The driver binds `sophgo,sg2042-pwm` and `sophgo,sg2044-pwm`, uses MMIO, enabled `apb` clock, optional shared reset, exclusive clock-rate APIs, and atomic PWM ops.

## Risks and test signals

SG2044 `get_state()` does not read polarity and always reports normal. Tick conversion saturates to `U32_MAX`; shared SG2044 control registers are read-modify-written without a local lock. Test both variants, SG2044 inverted polarity, disable semantics, clock-rate validation, and period/high-period readback.
