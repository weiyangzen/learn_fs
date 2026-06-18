<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-gpio.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-gpio.c

Purpose: implements a software PWM generator using one non-sleeping GPIO and an hrtimer. It is useful for simple GPIO-backed modulation where hardware PWM is unavailable and atomic GPIO access is possible.

Important APIs/types/functions: `struct pwm_gpio` stores the GPIO descriptor, current and pending `pwm_state`, hrtimer, spinlock, and timer flags. `pwm_gpio_round()` quantizes requested period/duty to `hrtimer_resolution`; `pwm_gpio_toggle()` writes the GPIO and schedules the next edge; `pwm_gpio_timer()` applies pending state changes at period boundaries. `pwm_gpio_apply()` and `pwm_gpio_get_state()` implement PWM core callbacks.

Control flow: probe acquires one GPIO as `GPIOD_ASIS`, rejects `gpiod_cansleep()` GPIOs, initializes an hrtimer and atomic PWM chip, and registers cleanup to cancel the timer. Apply validates that nonzero high/low phases are at least one hrtimer tick, starts the GPIO as output when needed, and either disables immediately, queues a next-state update for the end of the current period, or starts the timer from an idle state.

State and persistence: all state is in `struct pwm_gpio`; there is no hardware persistence beyond the current GPIO output level. The spinlock protects timer and pwm_ops state. `changing` tells `get_state()` to report the pending state, and `running` distinguishes continuous toggling from fixed 0/100% outputs.

Dependencies and integration: depends on the PWM core, GPIO consumer API, hrtimers, spinlocks, platform/OF matching for `pwm-gpio`, and non-sleeping GPIO controllers. It sets `chip->atomic = true`, so apply paths must remain IRQ-safe once the GPIO direction has been configured.

Risks and test signals: timing quality is bounded by hrtimer latency and scheduler/IRQ behavior, not hardware precision. Sleeping GPIOs are rejected because timer callbacks cannot sleep. Tests should cover 0%, 100%, inverted polarity, very small duty/low phases, state changes while running, hrtimer cancellation on remove, and GPIO value behavior after disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-gpio.c -->
