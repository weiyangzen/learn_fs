# sources/distributed-fs/ceph-client/drivers/spi/spi-offload-trigger-pwm.c

Purpose: Generic PWM-backed SPI offload trigger provider. It exposes a PWM output as a periodic trigger source for offloaded SPI transfers, rounding requested frequency/offset to what the PWM controller can produce and driving a 50 percent duty waveform while enabled.

Important APIs, types, and functions: `struct spi_offload_trigger_pwm_state` stores device and PWM handles. `spi_offload_trigger_pwm_match()` accepts `SPI_OFFLOAD_TRIGGER_PERIODIC` with no fwnode args. `spi_offload_trigger_pwm_validate()` computes a `pwm_waveform`, calls `pwm_round_waveform_might_sleep()`, and writes rounded frequency/offset back to config. `spi_offload_trigger_pwm_enable()` programs the waveform. `spi_offload_trigger_pwm_disable()` reads the current waveform and sets duty to zero. Probe gets the PWM, applies an enabled zero-duty initial state, registers a devm release action that disables the PWM, and registers trigger ops.

Control flow: during probe the PWM is initialized enabled but inactive. A consumer validates a periodic config, possibly getting adjusted values. On trigger enable the offload core first enables the offload instance, then this driver sets waveform timing. Disable is called through the offload core and zeros duty to stop triggering while preserving period/offset.

State and persistence: private state is just the PWM handle and device pointer. Runtime waveform state lives in the PWM provider hardware. Devm cleanup disables the PWM at device teardown. There is no internal active flag, so disable errors are logged but not persisted.

Dependencies and integration points: integrates with the generic SPI offload trigger registry, PWM waveform API, fwnode matching through compatible `"pwm-trigger"`, and platform device probing. It expects `trigger-sources` references from offload providers/consumers to resolve to this fwnode.

Risks: duty cycle is fixed at 50 percent and has a `REVISIT`, so hardware needing pulse-width control cannot express it. Validation mutates frequency using rounded period length; consumers must re-check the returned values. `disable()` depends on reading the current waveform and logs errors without forcing state otherwise. Zero frequency is rejected.

Test signals: validate/enable/disable periodic triggers at supported and unsupported rates, offset rounding, zero-frequency rejection, PWM provider probe deferral, cleanup disabling PWM on driver removal, and interaction with offload trigger enable rollback when PWM programming fails.
