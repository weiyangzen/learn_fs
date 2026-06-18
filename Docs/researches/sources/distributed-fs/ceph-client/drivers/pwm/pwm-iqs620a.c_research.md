<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-iqs620a.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-iqs620a.c

Purpose: exposes the Azoteq IQS620A MFD PWM generator on GPIO3/LTX as a one-channel, fixed-1 ms PWM provider backed by parent regmap registers and reset notifications.

Important APIs/types/functions: `struct iqs620_pwm_private` stores parent `iqs62x_core`, mutex, notifier, and cached `duty_scale`. `iqs620_pwm_init()` writes duty or disables PWM output; `iqs620_pwm_apply()` validates fixed-period/normal polarity and updates hardware; `iqs620_pwm_get_state()` reports cached state; `iqs620_pwm_notifier()` restores PWM configuration after parent device reset.

Control flow: probe retrieves parent MFD data, reads current enable/duty state, initializes the mutex, registers a blocking notifier on the parent reset chain, adds devm cleanup to unregister it, and registers one PWM. Apply clamps duty to 1 ms, maps it to 0..256 scale, uses zero scale to disable output, and updates cached state under lock after successful regmap writes.

State and persistence: hardware holds the duty register and PWM output bit, while `duty_scale` is the software source of truth for get-state and reset restore. No nonvolatile persistence is provided. Parent reset events require reinitialization from the cached scale.

Dependencies and integration: depends on the IQS62x MFD core, parent regmap, blocking notifier chain, mutex, platform device created by the MFD, and PWM core.

Risks and test signals: the hardware cannot generate true 0% while enabled, so low duty is represented by disabling output and relying on an external pull-down. Test reset notifier restore, initial hardware state import, 0/1/255/256 scale boundaries, fixed-period rejection, polarity rejection, and notifier unregister cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-iqs620a.c -->
