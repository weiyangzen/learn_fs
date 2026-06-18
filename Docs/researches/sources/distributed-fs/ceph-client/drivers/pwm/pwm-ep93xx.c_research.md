# sources/distributed-fs/ceph-client/drivers/pwm/pwm-ep93xx.c

Purpose: implements PWM support for Cirrus Logic EP93xx SoCs, exposing one PWM channel per platform device instance.

Important APIs/types/functions: `struct ep93xx_pwm` stores MMIO base and `pwm_clk`. `ep93xx_pwm_apply()` handles polarity changes, clock gating, period/duty conversion to 16-bit cycles, ordered register updates while running, and enable/disable. Probe maps the channel registers, gets the PWM clock, and registers one PWM.

Control flow: apply disables the output before changing polarity, enables the clock for register access, writes the invert register, then handles disabled requests. Enabled configuration enables the clock if needed, calculates `TERM_COUNT` and `DUTY_CYCLE`, writes in an order chosen to avoid transient duty greater than period, disables the clock again if the channel was not already enabled, and finally enables output when transitioning from disabled.

State and persistence: no software cache beyond base and clock. The driver relies on PWM core cached state for previous polarity/enabled decisions and hardware registers for output.

Dependencies and integration: depends on platform or OF matching `cirrus,ep9301-pwm`, MMIO word accesses, the clock framework, and PWM core callbacks.

Risks and test signals: no `get_state` means boot state is not imported. The clock is toggled multiple times in one apply path; failures after partial configuration need careful observation. Period/duty must fit 16 bits. Test signals include polarity changes while enabled, period/duty boundary fit, register-write ordering while running, enable/disable clock balance, and single-channel platform instances for SoC variants.
