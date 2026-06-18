# sources/distributed-fs/ceph-client/drivers/pwm/pwm-bcm-kona.c

Purpose: implements the six-channel Broadcom Kona PWM controller, whose hardware lacks a conventional disable bit and applies settings via trigger edges.

Important APIs/types/functions: `struct kona_pwmc` stores MMIO base and clock. `kona_pwmc_prepare_for_settings()` and `kona_pwmc_apply_settings()` handle smooth/trigger sequencing and required 400 ns delays. `kona_pwmc_config()` computes prescale, period count, and duty count. `kona_pwmc_set_polarity()`, `kona_pwmc_enable()`, `kona_pwmc_disable()`, and `kona_pwmc_apply()` implement the PWM operations.

Control flow: probe briefly enables the clock, configures push/pull type bits for all channels, disables the clock, and registers six PWMs. Apply handles polarity changes by disabling first if needed, simulates disable by programming zero duty/period, enables the clock for active channels, and configures requested duty/period through the trigger sequence.

State and persistence: the driver relies on PWM core cached state for enabled/polarity decisions and hardware registers for output. It does not implement `get_state` or PM save/restore.

Dependencies and integration: depends on clock framework, MMIO, OF compatible `brcm,kona-pwm`, and the PWM core.

Risks and test signals: hardware semantics are unusual: disabling by zero duty, trigger/smooth timing, and clock disable can leave the line high or low depending on instant. Enabling before configuration is preserved for compatibility but may glitch. Test signals include enable-from-disabled glitches, polarity changes, zero duty disable, long-period smooth behavior, and clock enable/disable balancing.
