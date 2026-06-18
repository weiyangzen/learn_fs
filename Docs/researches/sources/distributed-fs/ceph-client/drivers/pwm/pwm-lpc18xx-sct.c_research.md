<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-lpc18xx-sct.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-lpc18xx-sct.c

Purpose: implements PWM output on the NXP LPC18xx State Configurable Timer by using SCT match/events/output set-clear resources. It exposes 16 PWM outputs with one shared period event.

Important APIs/types/functions: `struct lpc18xx_pwm_chip` stores base, clock, rate, period, and an array of per-channel enabled state. Helpers include `lpc18xx_pwm_config_period()`, `lpc18xx_pwm_config_duty()`, `lpc18xx_pwm_enable()`, `lpc18xx_pwm_disable()`, `request/free`, and `apply`. Register macros cover config/control, match/matchrel, event control/masks, output set/clear, and conflict resolution.

Control flow: probe enables the clock, configures the SCT as unified unidirectional counter, initializes period event 0, sets output conflict behavior, and registers 16 PWMs. Request configures a channel event and default duty. Apply reprograms the shared period when necessary, updates duty match for the channel, then enables/disables output actions according to state and polarity.

State and persistence: period is cached in the driver because it is shared. Hardware match/event/output registers hold channel state. Per-channel `enabled` flags track requested output state for shared period changes. Remove unregisters the chip and disables the clock.

Dependencies and integration: depends on platform/OF, clock framework, MMIO, PWM core, and SCT hardware resource mapping where event 0 is reserved for period and channels use subsequent events.

Risks and test signals: shared-period changes can affect all channels, and event allocation is fixed. Test multiple enabled outputs, polarity changes, 0/100% duty, maximum timer values, request/free resource cleanup, and clock-rate-derived period rounding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-lpc18xx-sct.c -->
