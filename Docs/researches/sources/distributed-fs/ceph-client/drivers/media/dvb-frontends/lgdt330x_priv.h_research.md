# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lgdt330x_priv.h

## Purpose
`lgdt330x_priv.h` centralizes register names for the LGDT3302/LGDT3303 driver.

## Important APIs, Types, and Functions
The private `enum I2C_REG` maps symbolic names for top control, IRQ mask/status, VSB carrier NCO, QAM MSE, carrier lock, AGC, demux control, chip-specific error registers, and packet error counters.

## Control Flow
The C file uses these enum values in I2C read/write helpers, initialization tables, reset paths, status checks, SNR calculations, and block-error counter reads.

## State and Persistence
There is no software state in the header; it documents volatile register addresses for the demodulator.

## Dependencies and Integration Points
It is included only by `lgdt330x.c` and is not a public board-driver ABI.

## Risks and Edge Cases
Several symbolic registers are chip-specific even though they share one enum; using an LGDT3302-only address with LGDT3303 or vice versa would produce wrong metrics. The enum has no width/type checks beyond C integer constants.

## Test Signals
Regression signals are successful init/status/SNR paths on both LGDT3302 and LGDT3303, with packet counter and lock registers matching expected chip-specific addresses.
