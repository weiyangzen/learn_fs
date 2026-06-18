# sources/distributed-fs/ceph-client/drivers/pwm/pwm-airoha.c

Purpose: implements PWM support for the Airoha EN7581 SoC GPIO/SIPO LED flash hardware, exposing 33 logical PWM channels backed by only eight shared waveform generator buckets.

Important APIs/types/functions: `struct airoha_pwm` holds a regmap, initialized-channel bitmap, per-generator buckets, and channel-to-bucket cache. Helpers convert nanoseconds to 4 ms period ticks and 8-bit duty ticks. `airoha_pwm_get_generator()`, `airoha_pwm_consume_generator()`, and `airoha_pwm_release_bucket_config()` manage shared generators. `airoha_pwm_sipo_init()` programs the serial GPIO shift register path. `airoha_pwm_apply()` and `airoha_pwm_get_state()` are the PWM callbacks.

Control flow: probe gets the parent syscon regmap and registers 33 PWMs. Apply disables by clearing the flash-map enable bit and releasing the assigned bucket. Enabled requests require normal polarity, clamp period to 1 s, quantize to 4 ms ticks, compute duty ticks, select or allocate a generator bucket, program period/duty registers, maps the GPIO/SIPO channel to that bucket, and reinitializes SIPO hardware when needed.

State and persistence: the driver maintains software reference counts for shared buckets plus per-channel initialization state; hardware flash-map and cycle registers hold active output. State is not persisted across driver unload.

Dependencies and integration: depends on parent MFD/syscon regmap, regmap polling, OF platform matching, bitmap helpers, and the PWM core. It integrates GPIO pins and SIPO pins as one PWM namespace.

Risks and test signals: bucket sharing is the main risk: only eight distinct waveforms can run, bucket reuse affects rounding, and failed programming must roll back reference counts correctly. SIPO initialization has polling timeouts. Test signals include more than eight unique waveforms, full-duty bucket reuse, SIPO channel enable/disable, all channels disabled clearing SIPO mode, readback of mapped buckets, and regmap failure injection.
