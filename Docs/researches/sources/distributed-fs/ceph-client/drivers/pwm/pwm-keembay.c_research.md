<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-keembay.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-keembay.c

Purpose: implements Intel Keem Bay six-channel PWM hardware, where each channel has a lead-in register with enable bit and a high/low count register with 16-bit high and low phases.

Important APIs/types/functions: `struct keembay_pwm` stores the MMIO base, clock, and clock-rate-derived nanosecond scale. `keembay_pwm_get_state()` decodes enable/high/low counts; `keembay_pwm_apply()` computes 16-bit high and low counts from requested period/duty and writes channel registers; small helpers manage enable bits and clock lifetime.

Control flow: probe maps registers, gets/enables the clock with devm cleanup, stores clock rate, and registers six PWMs. Apply rejects inverted polarity, disables when requested, otherwise computes high count from duty and low count from period minus duty, rejects values above `U16_MAX`, writes high/low fields, and sets the enable bit. Get-state reconstructs duty and period from counts and cached clock rate.

State and persistence: hardware registers hold enable and high/low counts; the software cache is only the input clock rate. No suspend/resume is implemented, so power-domain reset would require consumers to reapply state.

Dependencies and integration: depends on platform/OF, clk, MMIO, bitfield helpers, and PWM core. It is a straightforward fixed-clock counter backend.

Risks and test signals: period and duty limits are hard 16-bit count limits. Clock-rate changes after probe are not tracked. Test 0%, 100%, max-count periods, polarity rejection, get-state round trips, and clock cleanup on probe failure/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-keembay.c -->
