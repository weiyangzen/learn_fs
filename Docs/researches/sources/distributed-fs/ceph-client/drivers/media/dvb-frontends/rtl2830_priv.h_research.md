<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/rtl2830_priv.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/rtl2830_priv.h

## Purpose
`rtl2830_priv.h` defines the private runtime state and register-table tuple used by the RTL2830 demodulator driver.

## Important APIs, Types, And Functions
`struct rtl2830_dev` holds platform data, I2C client, regmap, I2C mux core, DVB frontend, sleeping flag, PID filter bitmap, cached frontend status, cumulative post-bit error/count counters, and previous error count for old `read_ber()`. `struct rtl2830_reg_val_mask` represents one masked register update with 16-bit logical register address, value, and mask.

## Control Flow
The header has no executable flow. `rtl2830.c` allocates `rtl2830_dev` in probe, fills all fields, uses it from frontend callbacks through `i2c_get_clientdata()`, and frees it in remove.

## State And Persistence
All fields are in-memory and per I2C client. Hardware register and PID state persists separately in the demod after writes, while these fields cache frontend status and aggregate counters for userspace reads.

## Dependencies And Integration Points
It includes DVB frontend, integer-log, public RTL2830 platform data, I2C mux, math64, regmap, and bitops headers. It is private to `rtl2830.c` and should not be consumed by board drivers.

## Risks
The `filters` bitmap is an `unsigned long` but the driver treats it as 32 PID filter bits; this is fine on 32/64-bit kernels but should not be extended without revisiting serialization and register layout. Counter fields are updated in status reads without explicit locking, relying on frontend call serialization expectations. Lifetime is tied to I2C clientdata and remove.

## Test Signals
Build coverage, probe/remove memory lifetime checks, PID filter bitmap updates, cumulative BER accounting across repeated status/read_ber calls, and sleep/status state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/rtl2830_priv.h -->
