<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/pwm.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/pwm.h

Purpose: defines the userspace character-device ABI for querying PWM chips and getting/setting PWM channel state.

Important APIs and types: `struct pwmchip_info` reports chip name, npwm, and reserved fields. `struct pwm_args` carries default period and polarity. `struct pwm_state` carries period, duty cycle, polarity, enabled flag, and reserved padding. Ioctls are `PWM_GETCHIPINFO`, `PWM_GETARGS`, `PWM_GETSTATE`, and `PWM_SETSTATE` with magic `'p'`.

Control flow: userspace opens a PWM chip/channel cdev, queries chip/channel defaults, reads current state, and writes a new state. The kernel PWM core validates duty <= period, polarity support, and provider callbacks before programming hardware.

State and persistence: PWM state is runtime hardware/provider state: period, duty cycle, polarity, and enablement. It may survive process exit while the device remains configured but is not guaranteed persistent across reboot/driver reset.

Dependencies and integration points: depends on Linux ioctl/types. Integrates with PWM core, platform PWM providers, fan/backlight/motor control tools, and device-tree/default PWM arguments.

Risks and test signals: risks include unsafe duty/period values, polarity mismatch, unit confusion in nanoseconds, and racing kernel consumers. Test get/set state, invalid duty > period, enable/disable transitions, provider removal, and concurrent users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/pwm.h -->
