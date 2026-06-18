# sources/distributed-fs/ceph-client/drivers/staging/greybus/pwm.c

## Purpose
Greybus PWM bridged-PHY child driver. It exposes remote Greybus PWM channels as a Linux `pwm_chip`.

## Important APIs, Types, And Functions
`struct gb_pwm_chip` embeds the Linux `pwm_chip` private data and connection. Protocol helpers implement count, activate/deactivate, config, polarity, enable, and disable operations. Linux PWM callbacks are `gb_pwm_request()`, `gb_pwm_free()`, and `gb_pwm_apply()`, collected in `gb_pwm_ops`.

## Control Flow
Probe creates/enables the connection, queries the highest PWM ID and converts it to count, allocates a `pwm_chip`, stores it as gbphy data, registers it, and releases the gbphy PM reference. Request activates a PWM. Apply changes polarity with disable-if-needed, clamps 64-bit period/duty to Greybus 32-bit fields, configures duty/period, and enables if requested. Disable releases the runtime-PM reference held since enable.

## State And Persistence
Linux PWM core owns desired state; the driver does not maintain a separate channel cache. Runtime PM is held while a PWM is enabled and released on disable/deactivate.

## Dependencies And Integration Points
Uses `gbphy`, Greybus PWM protocol, Linux PWM core, and runtime PM. The chip parent is the `gbphy_device`.

## Risks
PM balance depends on `gb_pwm_enable_operation()` retaining a reference on success and `gb_pwm_disable_operation()` always putting it. If free occurs while enabled, the driver warns but deactivates. Period/duty truncation to `U32_MAX` may change requested waveform semantics.

## Test Signals
Test count query, request/free, apply disabled/enabled states, polarity change while enabled, period/duty clamping, duty greater than period, enable failure PM balance, remove with active PWM, and registration failure unwind.
