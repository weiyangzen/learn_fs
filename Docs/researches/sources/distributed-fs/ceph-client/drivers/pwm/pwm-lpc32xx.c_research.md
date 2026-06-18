<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-lpc32xx.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-lpc32xx.c

Purpose: provides a simple one-channel PWM driver for LPC32xx, programming one combined control register with enable, pin level, duty, and period-derived fields.

Important APIs/types/functions: `struct lpc32xx_pwm_chip` stores clock and MMIO base. `lpc32xx_pwm_config()`, `lpc32xx_pwm_enable()`, `lpc32xx_pwm_disable()`, and `lpc32xx_pwm_apply()` form the PWM implementation.

Control flow: probe maps the register block, gets the clock, and registers one PWM. Apply rejects inverted polarity, disables by clearing enable and dropping the clock, or enables the clock, computes register fields from requested period/duty and clock rate, writes configuration, and sets enable.

State and persistence: hardware register contents and clock enable are the only runtime state; the driver keeps no cache and provides no `.get_state()`. The disabled output is controlled through the configured pin-level bit.

Dependencies and integration: depends on OF/platform probing, clk framework, MMIO, and PWM core. It targets `nxp,lpc3220-pwm`.

Risks and test signals: without get-state or PM hooks, state recovery is limited. Test clock enable/disable balance, period/duty conversion at extremes, disabled output level, polarity rejection, and probe failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-lpc32xx.c -->
