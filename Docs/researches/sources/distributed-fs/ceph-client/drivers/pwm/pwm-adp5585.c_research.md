# sources/distributed-fs/ceph-client/drivers/pwm/pwm-adp5585.c

Purpose: exposes the PWM function in Analog Devices ADP5585/ADP5589 MFD chips as a one-channel PWM controller.

Important APIs/types/functions: `struct adp5585_pwm_chip` describes variant register offsets; `struct adp5585_pwm` stores the parent regmap and external config register. `pwm_adp5585_request()` muxes pin R3 to PWM output, `pwm_adp5585_free()` restores GPIO4, `pwm_adp5585_apply()` writes off/on 16-bit counters and enables continuous PWM mode, and `pwm_adp5585_get_state()` reads counters and enable state.

Control flow: probe obtains the parent `adp5585_dev`, selects variant register data from `platform_device_id`, inherits the parent's OF node, and registers one PWM. Apply disables by clearing `ADP5585_PWM_EN`; enabled requests require normal polarity and a minimum period, clamp to hardware maximum, write OFF then ON counts, and set enable/mode bits.

State and persistence: runtime state is parent regmap plus static variant offsets. Hardware registers persist while the MFD device remains powered; the driver does not keep an additional cache.

Dependencies and integration: integrates with the ADP5585 MFD parent, regmap bulk little-endian accesses, platform id matching, and PWM pin mux through the extender config register.

Risks and test signals: only normal polarity is supported and disabling drives the output low immediately. The enable sequence performs an update-bits call followed by `regmap_set_bits()` for enable, which should be verified against hardware latching. Test signals include ADP5585 and ADP5589 variants, request/free pin muxing, min/max period, disabled state, endian counter readback, and MFD regmap failures.
