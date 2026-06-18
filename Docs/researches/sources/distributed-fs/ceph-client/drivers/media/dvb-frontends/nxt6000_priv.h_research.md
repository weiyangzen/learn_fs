<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/nxt6000_priv.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/nxt6000_priv.h

## Purpose
`nxt6000_priv.h` is the private register and bit-mask map for the NXT6000 DVB-T demodulator. It gives `nxt6000.c` names for RS, BER, Viterbi, OFDM, AGC, tuner I2C, diagnostics, TS format, and chip revision registers.

## Important APIs, Types, And Functions
The header defines register addresses such as `RS_COR_STAT`, `BER_CTRL`, `VIT_SYNC_STATUS`, `OFDM_COR_CTL`, `OFDM_COR_STAT`, `OFDM_COR_MODEGUARD`, `OFDM_AGC_CTL`, `OFDM_ITB_CTL`, `OFDM_SYR_STAT`, `OFDM_TRL_NOMINALRATE_*`, `OFDM_CHC_SNR`, `OFDM_MSC_REV`, `ENABLE_TUNER_IIC`, `EN_DMD_RACQ`, `DIAG_CONFIG`, `SUB_DIAG_MODE_SEL`, and `TS_FORMAT`. Bit masks include lock/status indicators, reset bits, BER control flags, AGC/mode flags, clock inversion, TS signal polarity flags, and `NXT6000ASICDEVICE`.

## Control Flow
There is no executable flow. The C file uses these constants to write the initialization sequence, tune DVB-T parameters, read lock/statistics, and gate the tuner bus.

## State And Persistence
The definitions represent hardware register state. Writes persist in the chip until reset/power loss; this header stores no kernel state.

## Dependencies And Integration Points
It is private to the NXT6000 driver and expects the C file to provide I2C read/write helpers. The register names encode the interface between frontend callbacks and demod hardware.

## Risks
Changing constants changes hardware behavior directly. Some aliases are duplicated and comments indicate old names, so cleanup can accidentally break compatibility with code that uses either alias. A few masks include semicolons or formatting oddities inherited from vendor-era code.

## Test Signals
Compile coverage, attach chip-revision verification, init/tune register traces, and status/statistic reads are the effective validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/nxt6000_priv.h -->
