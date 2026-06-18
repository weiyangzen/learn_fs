# sources/distributed-fs/ceph-client/include/media/i2c/ds90ub9xx.h

## Purpose
Defines platform data for TI DS90UB9xx FPD-Link serializers connected behind a deserializer.

## Important APIs, Types, and Functions
Forward-declares `struct i2c_atr`. `struct ds90ub9xx_platform_data` contains deserializer RX `port`, I2C address translator pointer `atr`, and back-channel clock rate `bc_rate`.

## Control Flow
Deserializer/serializer drivers pass this platform data when creating serializer clients so the serializer can use the correct RX port, ATR, and back-channel timing.

## State and Persistence Behavior
The data is static relationship state between deserializer port, remote serializer, and ATR. Back-channel rate persists in link configuration after programming.

## Dependencies and Integration Points
Depends on I2C ATR infrastructure and FPD-Link media topology drivers. Integrates remote I2C devices with media graph endpoints.

## Risks
Wrong port or ATR pointer can route remote transactions to the wrong serializer. Incorrect back-channel rate can destabilize link control.

## Test Signals
Multi-port deserializer probing, remote serializer I2C access through ATR, back-channel rate changes, and link recovery after unplug/reset.
