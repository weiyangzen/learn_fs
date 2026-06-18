# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/atbm8830_priv.h

## Purpose
This private header defines ATBM8830 runtime state and symbolic register addresses used by `atbm8830.c`.

## Important APIs And Types
`struct atbm_state` stores the I2C adapter, const config pointer, and embedded DVB frontend. Register macros cover chip ID, baseband/IF/oscillator configuration, demod run/reset, TS output controls, lock status, ADC configuration, carrier offset, IF/OSC frequency words, analog-detection flags, frame error counters, IQ swap, TPS, AGC target/min/max/lock/PWM, and I2C gate control.

## Control Flow And Integration
`atbm8830.c` uses these macros in init, tuning, metrics, and I2C gate functions. Multi-byte values are written as adjacent little-endian registers. `REG_READ_LATCH` supports atomic multi-register metric reads.

## State And Persistence
The struct is heap-allocated during attach. Register macros are compile-time constants only.

## Dependencies
The header is private and assumes `struct atbm8830_config`, `struct i2c_adapter`, and `struct dvb_frontend` are visible through included implementation headers.

## Risks
Incorrect register constants directly affect hardware programming. Comments mark some adjacent ranges but no helpers enforce valid multi-byte access. The config pointer lifetime risk is defined here because the state stores `const struct atbm8830_config *`.

## Test Signals
Register-write tracing should confirm adjacent multi-byte writes match expected endianness. Static analysis should verify every macro use has error handling where feasible.
