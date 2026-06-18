# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lgs8gxx.h

## Purpose
`lgs8gxx.h` is the public configuration header for the Legend Silicon DMB-TH/DTMB demodulator family driver.

## Important APIs, Types, and Functions
It defines product IDs for LGS8913, LGS8GL5, LGS8G42, LGS8G52, LGS8G54, and LGS8G75. `struct lgs8gxx_config` describes product type, demod I2C address, serial/parallel TS mode, TS clock polarity and gating, IF clock/frequency, external ADC and ADC data-format flags, IF sampling/negative-center options, LGS8G75 ADC Vpp selection, and tuner slave address. `lgs8gxx_attach()` is declared under `CONFIG_DVB_LGS8GXX` and stubbed otherwise.

## Control Flow
Board drivers fill this structure and call attach. The C file branches heavily on `prod` to choose register addresses, init sequences, firmware loading, lock checks, and signal metric formulas.

## State and Persistence
The header itself is immutable configuration. Runtime state stores a pointer to the config; therefore board-provided config storage must outlive the frontend.

## Dependencies and Integration Points
It depends on DVB frontend and I2C headers and is consumed by board/card drivers that instantiate the demodulator and tuner.

## Risks and Edge Cases
The config uses raw `u8` flags rather than enums for most booleans, making invalid combinations possible. `tuner_address == 0` disables the demodulator I2C gate in the implementation. IF clock/frequency values directly affect fixed-point NCO calculation, so zero or mismatched clock values can produce invalid tuning.

## Test Signals
Validate enabled/disabled builds, product-specific register behavior, TS output electrical mode, IF/ADC combinations, tuner gate enablement, and LGS8G75 ADC range choices.
