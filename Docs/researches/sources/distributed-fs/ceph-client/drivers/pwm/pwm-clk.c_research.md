# sources/distributed-fs/ceph-client/drivers/pwm/pwm-clk.c

Purpose: adapts a clock with rate and duty-cycle control into a one-channel PWM provider.

Important APIs/types/functions: `struct pwm_clk_chip` stores the underlying clock and whether this driver has enabled it. `pwm_clk_apply()` enables/disables the clock, sets clock rate from requested period, inverts duty for inverted polarity, and calls `clk_set_duty_cycle()`. Probe gets a prepared clock and registers the PWM chip; remove unregisters and disables any active clock.

Control flow: enabled applies first enable the clock if previously disabled, then set rate and duty cycle through the clock API. Disabled applies disable only if the previous PWM state was enabled. The driver has no readback because the clock API does not expose enough state.

State and persistence: `clk_enabled` is a local software guard for cleanup. Requested PWM state is cached by the framework; actual clock state belongs to the clock provider.

Dependencies and integration: depends on the common clock framework, compatible `clk-pwm`, platform devices, and PWM core. Behavior is largely defined by the underlying clock provider.

Risks and test signals: enabling before programming creates a window with stale clock settings, and rate/duty programming is not atomic. Error after enabling may leave the clock enabled because apply returns without rollback. Test signals include enable failure, `clk_set_rate` failure, duty-cycle failure, inverted polarity mapping, remove while enabled, and clock providers that cannot produce 0 or 100 percent duty.
