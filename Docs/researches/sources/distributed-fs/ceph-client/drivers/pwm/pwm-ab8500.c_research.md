# sources/distributed-fs/ceph-client/drivers/pwm/pwm-ab8500.c

Purpose: implements a single-channel PWM provider for ST-Ericsson/Analog Baseband AB8500 MFD PWM output generators.

Important APIs/types/functions: `struct ab8500_pwm_chip` stores the AB8500 hardware id. `ab8500_pwm_apply()` converts requested period/duty to the AB8500 divisor and 10-bit duty fields, writes `AB8500_PWM_OUT_CTRL1/2`, and toggles `AB8500_PWM_OUT_CTRL7`. `ab8500_pwm_get_state()` reads the same registers back. `ab8500_pwm_probe()` validates platform id, allocates one PWM, and registers it.

Control flow: requests are handled by the PWM core. Apply rejects inverted polarity, computes a supported period divisor from the fixed 9.6 MHz clock, rejects too-short periods, writes low/high duty bytes, and enables the selected output bit. Disable clears the enable bit. State read first checks enable, then reconstructs period and duty from divisor and duty steps.

State and persistence: driver state is only the per-chip `hwid`; hardware registers hold the active PWM configuration. No suspend/resume or persistent software cache is provided.

Dependencies and integration: depends on AB8500 MFD register access through `abx500_*_register_interruptible()`, platform-device ids, and the PWM core. Kconfig restricts it to AB8500 core on U8500.

Risks and test signals: supported period range is narrow and quantized; polarity is fixed normal. The duty calculation clamps with `max_t(..., 1024)`, which can push most nonzero requests to full duty and deserves review against intended rounding. Test signals include MFD register read/write failures, period boundary values, 0/full duty, disable producing low output, and `get_state` consistency.
