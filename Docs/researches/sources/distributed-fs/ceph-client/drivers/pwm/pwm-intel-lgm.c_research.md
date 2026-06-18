<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-intel-lgm.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-intel-lgm.c

Purpose: drives the Intel Lightning Mountain dedicated fan PWM controller. The hardware exposes one fixed-period, normal-polarity, two-wire fan PWM output with duty stored in an 8-bit field and max-RPM configuration.

Important APIs/types/functions: `struct lgm_pwm_chip` stores the regmap and fixed period. `lgm_pwm_apply()`, `lgm_pwm_get_state()`, `lgm_pwm_enable()`, and `lgm_pwm_init()` implement the PWM behavior. Probe uses MMIO regmap, a clock, reset control, and devm cleanup actions for clock disable and reset assert.

Control flow: probe maps registers, initializes regmap, enables the clock, deasserts reset, initializes mode to two-wire and default max RPM, then registers one PWM. Apply rejects non-normal polarity and periods shorter than the fixed 40 ms period, writes scaled duty into `LGM_PWM_FAN_CON0`, and toggles enable. Get-state reads enable and duty fields and reports the fixed period.

State and persistence: runtime state is in fan controller registers; software only stores `period`. Device-managed actions assert reset and disable the clock on teardown. There is no suspend/resume logic in this file.

Dependencies and integration: depends on platform/OF, clk, reset controller, regmap MMIO, and PWM core. It is intended for fan-control consumers rather than arbitrary PWM waveform generation.

Risks and test signals: consumers requesting a shorter period or inverted polarity will fail. Duty changes may affect the first period immediately. Test fixed-period acceptance, duty scaling endpoints, reset/clock cleanup, get-state readback, and fan controller mode/max-RPM initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-intel-lgm.c -->
