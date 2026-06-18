# sources/distributed-fs/ceph-client/include/linux/mfd/lp8788-isink.h

Purpose: This header defines current-sink register addresses and masks for the TI LP8788 MFD, typically used by LED/backlight current-sink child drivers.

Important APIs, types, and constants: Register macros identify current-sink control, ISINK1/2 output current, ISINK3 output current, and PWM registers for three sinks. Masks define output-current fields for ISINK1, ISINK2, and ISINK3. `LP8788_ISINK_MAX_PWM` bounds PWM value to 63, and `LP8788_ISINK_SCALE_OFFSET` describes scaling/shift behavior used by consumers.

Control flow, state, and persistence: There is no code. Child drivers program current and PWM registers through the LP8788 parent regmap to enable and dim current sinks. Hardware state is current limit/output and PWM duty configuration.

Dependencies and integration points: It integrates with the LP8788 MFD core, regmap, LED class, and backlight drivers.

Risks and test signals: Risks include nibble-mask mistakes for shared ISINK1/2 current register, accepting PWM values above 63, and mismatched scaling in brightness conversions. Test signals include LED brightness ramp tests, current setting readback, shared-register update-bit tests for ISINK1/2, and suspend/resume brightness restoration.
