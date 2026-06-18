<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-imx1.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-imx1.c

Purpose: provides a minimal PWM driver for early i.MX1/i.MX21-style PWM hardware, primarily preserving bootloader-programmed period settings and adjusting duty ratio.

Important APIs/types/functions: `struct pwm_imx1_chip` stores IPG/peripheral clocks and MMIO base. `pwm_imx1_config()` reads `MX1_PWMP` and writes `MX1_PWMS`; `pwm_imx1_enable()` and `pwm_imx1_disable()` manage clocks and `MX1_PWMC_EN`; `pwm_imx1_apply()` provides the PWM callback.

Control flow: probe gets `ipg` and `per` clocks, maps registers, sets ops, and registers one PWM. Apply rejects inverted polarity, disables by clearing enable and dropping clocks, or computes sample register value from requested duty/period and enables clocks plus the control bit when transitioning from disabled.

State and persistence: the driver does not program the hardware period or prescaler; it relies on existing `MX1_PWMP` state and only changes the sample register and enable bit. It keeps no software cache and has no PM callbacks.

Dependencies and integration: depends on platform/OF, clk framework, MMIO, and PWM core. It is intentionally simple and backlight-oriented rather than a full frequency-programming driver.

Risks and test signals: period requests are not actually honored if they differ from bootloader setup. No `.get_state()` exists. Test duty ratio behavior against an already configured PWM period, clock enable/disable balance, polarity rejection, and bootloader/default register assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-imx1.c -->
