# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mb86a16_priv.h

## Purpose
`mb86a16_priv.h` defines the private MB86A16 register addresses and bit masks used by the demodulator implementation.

## Important APIs, Types, And Functions
The file is a macro-only register map. It names transport output, FEC, AGC, symbol-rate, Viterbi, frame-sync, carrier/filter, reset/status, BER, DiSEqC, tone, frequency, AFC, signal, VIMAG/VISET, and monitor registers. Bit masks such as `MB86A16_TSOUT_*`, `MB86A16_FEC_*`, `MB86A16_DCC1_*`, and `MB86A16_DCCOUT_DISEN` document individual fields used by `mb86a16.c`.

## Control Flow
There is no control flow. The C file uses these constants in ordered I2C write/read sequences for initialization, tuning, status reporting, BER/SNR/strength reads, DiSEqC control, and tone generation.

## State And Persistence
The header defines the address space but no state. Values written to these registers are transient hardware state owned by the demodulator.

## Dependencies And Integration Points
The header is private to the MB86A16 driver and is included after `mb86a16.h`. It is part of the source-level contract between the tuning algorithm and the chip data sheet.

## Risks
Wrong register numbers or bit masks directly produce wrong hardware programming. A few macro names have inconsistent capitalization (`Mb86A16_*`), which is harmless only because users reference the exact macro names. Register aliases for literal addresses used in `mb86a16.c` are incomplete, so future maintenance can accidentally duplicate or mislabel magic values.

## Test Signals
Coverage is indirect: module build, attach, acquisition, SEC control, and statistics reads all validate subsets of the register map. Hardware regression tests are the meaningful signal because compile tests cannot detect incorrect numeric constants.
