# sources/distributed-fs/ceph-client/drivers/pwm/pwm-twl.c

## Purpose

`pwm-twl.c` exposes generic TWL4030/TWL6030 PWM outputs. TWL4030 uses PWM0/PWM1 plus pin muxing; TWL6030 uses two PWM outputs controlled by `TOGGLE3`.

## APIs, control flow, and state

`struct twl_pwm_chip` contains a mutex, cached TWL6030 toggle state, and saved TWL4030 mux bits. `twl_pwm_config()` writes relative-duty on/off-cycle registers. TWL4030 request/free save/restore GPIO6/GPIO7 mux fields and enable/disable sequence clock and enable bits. TWL6030 enable/disable use set/reset/toggle semantics and update the cached byte. Apply supports normal polarity and configures/enables or disables active hardware.

State is mostly PMIC registers; the mutex protects multi-step I2C and cached shared bits.

## Dependencies and integration points

The driver depends on TWL MFD I2C helpers, class detection, OF compatibles, and PWM core registration.

## Risks and test signals

TWL4030 mux restore must behave with both channels requested. Zero on-time is not representable in PWM mode. Multi-write TWL6030 disable can partially fail. No `.get_state` exists. Test mux save/restore, cached toggle state, duty endpoints, disable sequences, and I2C failures.
