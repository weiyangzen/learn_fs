<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-ntxec.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-ntxec.c

Purpose: exposes the Netronix embedded controller backlight/PWM interface as a one-channel PWM provider using EC register writes.

Important APIs/types/functions: `struct ntxec_pwm` stores the parent `ntxec` device. `ntxec_pwm_set_raw_period_and_duty_cycle()` writes period and duty low/high bytes. `ntxec_pwm_apply()` validates normal polarity and period limit, converts nanoseconds to 125 ns ticks, writes raw period/duty, and toggles the enable register. Probe allocates and registers one PWM.

Control flow: apply rejects inverted polarity and periods above 16-bit tick range, disables immediately when requested, otherwise writes period/duty registers and enables the output. Duty is clamped to the requested period before conversion.

State and persistence: the EC owns actual register state. The driver keeps no cache and has no get-state or PM restore; EC reset/power behavior must be handled by reapplying consumer state.

Dependencies and integration: depends on the Netronix EC parent driver, EC register access helper, platform device creation, and PWM core.

Risks and test signals: EC communication failures can leave partial period/duty state if multi-register writes fail mid-sequence. Test max period (`125 ns * 0xffff`), 0/100% duty, disable behavior, parent EC reset, and register-write error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-ntxec.c -->
