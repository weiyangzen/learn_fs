# sources/distributed-fs/ceph-client/drivers/media/rc/pwm-ir-tx.c

Purpose: implements a platform `RC_DRIVER_IR_RAW_TX` transmitter that emits raw IR pulse/space durations by toggling a PWM device. It supports generic `pwm-ir-tx` and `nokia,n900-ir` device-tree compatibles.

Important APIs and functions: `struct pwm_ir` stores the PWM handle, optional hrtimer/completion state, carrier, duty cycle, and active transmit buffer cursor. rc-core callbacks are `pwm_ir_set_duty_cycle`, `pwm_ir_set_carrier`, `pwm_ir_tx_sleep`, and `pwm_ir_tx_atomic`; platform binding is through `pwm_ir_probe` and `module_platform_driver`.

Control flow: probe allocates private state, obtains the PWM, initializes 38 kHz/50 percent defaults, allocates an rc-core TX-only device, then chooses either sleepable or atomic transmission depending on `pwm_might_sleep()`. The sleepable path applies PWM state and sleeps until each target edge. The atomic path stores a stack `pwm_state` pointer, starts an hrtimer, toggles PWM state in `pwm_ir_timer`, advances the expiry by each duration, and completes when all entries are consumed.

State and persistence: state is per-device and devm-managed. Carrier and duty cycle persist only while the platform device is bound. Active transmit state lives in `struct pwm_ir` for the duration of one synchronous `tx_ir` call; hardware PWM state is disabled at the end of sleepable sends and after the atomic timer reaches completion.

Dependencies and integration points: depends on Linux PWM, hrtimer, completion, platform/OF, and rc-core TX APIs. It integrates with rc-core through `devm_rc_allocate_device`, `devm_rc_register_device`, `s_tx_carrier`, `s_tx_duty_cycle`, and `tx_ir`.

Risks and edge cases: the atomic timer applies PWM state before checking whether `txbuf_index >= txbuf_len`, so completion can perform one extra state application with the final index. The atomic path points `pwm_ir->state` at a stack variable while waiting synchronously; it relies on the timer completing before return. Sleepable PWM providers are explicitly less accurate. There is no remove hook to cancel a possible in-flight hrtimer, though `tx_ir` waits synchronously. A zero carrier is rejected, but duty cycle range is not locally constrained.

Test signals: device-tree probe, rc-core registration as TX-only, carrier/duty sysfs or lirc ioctl updates, oscilloscope validation of carrier period/duty and pulse train durations for both sleepable and atomic PWM providers, and unload/removal under no active transmit.
