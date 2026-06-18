# sources/distributed-fs/ceph-client/drivers/pwm/pwm-atmel-tcb.c

Purpose: exposes an Atmel Timer Counter Block channel as two PWM outputs, one driven by RA and one by RB, sharing the same RC period.

Important APIs/types/functions: `struct atmel_tcb_pwm_chip` owns clocks, regmap, channel number, counter width, per-output duty/period/divisor state, and suspend backup. `atmel_tcb_pwm_request()` initializes CMR wave mode and imports existing hardware state. `atmel_tcb_pwm_config()` selects divisors and enforces shared period constraints. `atmel_tcb_pwm_enable()` and `atmel_tcb_pwm_disable()` program compare actions and trigger/start/stop the timer. PM callbacks save/restore CMR/RA/RB/RC.

Control flow: probe reads the child `reg` channel, obtains the parent syscon regmap and clocks, handles optional generic clock support, locks clock rates exclusively, initializes a spinlock, marks the chip atomic, and registers two PWMs. Apply runs under the spinlock, disabling or configuring then enabling the selected output.

State and persistence: per-output software state tracks selected divisor, duty, and period because both outputs share the timer period. Suspend stores channel registers and restores them on resume. Hardware registers persist while the block is powered.

Dependencies and integration: depends on AT91 TCB register definitions, syscon/regmap, OF clock names, clocksource headers, and the PWM core. It integrates tightly with parent TCB binding semantics.

Risks and test signals: both PWM outputs must use the same period when the peer output is active; this is a visible functional constraint. Atomic marking must remain valid for regmap and clock usage paths. Resume writes the CCR arguments in a suspicious order (`regmap_write(regmap, ATMEL_TC_CLKEN | ATMEL_TC_SWTRG, ATMEL_TC_REG(...))`) that merits review. Test signals include shared-period rejection, zero/full duty polarity behavior, slow clock fallback, 16/32-bit variants, suspend/resume restore, and concurrent RA/RB users.
