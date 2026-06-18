# sources/distributed-fs/ceph-client/drivers/pwm/pwm-apple.c

Purpose: implements a one-channel PWM controller for Apple SoC fixed PWM hardware used on ARM Apple platforms.

Important APIs/types/functions: `struct apple_pwm` stores MMIO base and clock rate. `apple_pwm_apply()` converts period/duty to ON and OFF cycle registers and writes `APPLE_PWM_CTRL` with enable/output/update bits. `apple_pwm_get_state()` reads control, ON, and OFF cycles to reconstruct `pwm_state`. Probe maps MMIO, enables the clock, validates rate, and registers the chip.

Control flow: enabled applies reject inverted polarity, compute on cycles from duty and off cycles from period minus on time, clamp each to 32 bits, write shadowed cycle registers, then write control to update and enable output. Disabled applies clear the control register. Reads report enabled only when both enable and output-enable bits are set.

State and persistence: software state is MMIO base and fixed clock rate; hardware registers keep the current PWM configuration while powered. No PM callbacks are implemented here.

Dependencies and integration: depends on platform/OF matching for `apple,s5l-fpwm`, an enabled clock, MMIO accessors, and the PWM core.

Risks and test signals: off-cycle calculation can underflow if duty exceeds period; the PWM core normally validates this for enabled states, but callers and future waveform paths should preserve that invariant. Cycle clamping may silently lengthen/shorten large requests. Test signals include normal/disabled output, readback consistency, clock-rate validation, duty 0/full-period boundaries, and unsupported inverted polarity.
