<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-imx27.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-imx27.c

Purpose: implements the i.MX27-and-newer single-channel PWM controller, including period/duty programming, clock management, polarity, state readback, FIFO handling, and a documented erratum workaround.

Important APIs/types/functions: `struct pwm_imx27_chip` stores bulk clocks, MMIO base, and cached duty for disabled readback. `pwm_imx27_get_state()`, `pwm_imx27_sw_reset()`, `pwm_imx27_wait_fifo_slot()`, and `pwm_imx27_apply()` are the core routines. Register definitions cover `PWMCR`, `PWMSR`, `PWMSAR`, `PWMPR`, and `PWMCNR`.

Control flow: probe gets `ipg` and `per` clocks, maps registers, temporarily enables clocks to detect boot-enabled PWM state, and keeps them on only if already running. Apply computes prescale, period, and duty cycles from `per` clock, resets FIFO when enabling from disabled, waits for a FIFO slot when already enabled, applies ERR051198 workaround around decreasing duty with local IRQs disabled, writes sample and period registers, caches duty, and writes the control register with polarity and enable bits.

State and persistence: enabled hardware keeps clocks prepared. The driver caches `duty_cycle` because `PWMSAR` cannot be read while disabled. Register state persists only while hardware remains powered; no explicit system PM hooks are present here.

Dependencies and integration: depends on bulk clocks, platform/OF, MMIO, PWM core, local IRQ masking, and timing helpers. It integrates with PWM consumers as a one-channel provider.

Risks and test signals: the FIFO/erratum path is timing-sensitive, especially high-frequency PWM and decreasing duty updates. Test enabled-to-enabled duty changes, disabled readback, inverted polarity, very small and maximum periods (`PWMPR_MAX`), probe with boot-enabled hardware, and warning paths for full FIFO or reset timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-imx27.c -->
