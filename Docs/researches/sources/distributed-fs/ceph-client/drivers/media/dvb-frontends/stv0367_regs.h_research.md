# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv0367_regs.h

### Purpose
`stv0367_regs.h` is the static register and bitfield catalog for the STV0367 DVB-T/DVB-C demodulator driver. It does not execute logic; it gives the companion driver code symbolic names for every memory-mapped/I2C-accessed hardware register and field used to configure terrestrial COFDM and cable QAM operation.

### Important APIs, Types, And Functions
The file exports preprocessor constants only. Register constants use the `R367TER_*` and `R367CAB_*` prefixes, while bitfield constants use `F367TER_*` and `F367CAB_*`. The encoded field format places the 16-bit register address in the high part and the field mask in the low byte, for example `F367TER_I2CT_ON` is tied to `R367TER_I2CRPT` and mask `0x80`. This matches common ST frontend helper patterns where code extracts the target register from `field >> 16` and the mask from `field & 0xff`.

### Control Flow
There is no runtime control flow. The file is organized as a long register map. The first region is the terrestrial core around addresses `0xf000` and covers chip ID, I2C repeater, top control, GPIO/IO configuration, AGC, derotator, timing recovery, TPS/FFT/SYR/CHC controls, equalizer, Viterbi/FEC, Reed-Solomon, transport stream output, and error counters. The later cable region uses `R367CAB_*`/`F367CAB_*` names around the `0xf4xx` range and covers QAM demodulation, AGC, equalizer, carrier/timing recovery, FEC, Reed-Solomon counters, BERT, output formatting, and TSMF/status registers.

### State, Persistence, And Dependencies
The header has no state and no persistence behavior. The persistent effect happens only when a driver uses these constants to perform I2C register writes to the STV0367 chip. Its only dependency is C preprocessor inclusion through an include guard. Driver code that includes it depends on the exact numeric values matching the STV0367 datasheet and the helper encoding convention.

### Integration Points
This file integrates with the STV0367 DVB frontend implementation in the same media driver directory. Register-level helper functions in that driver can use `R367*` constants for full-byte reads/writes and `F367*` constants for masked bit updates. The terrestrial/cable prefix split is the key integration boundary: wrong prefix use can program the wrong functional block or address range.

### Risks
The largest risk is silent hardware misconfiguration from an incorrect address or mask. Because these are macros, the compiler cannot validate register ownership, field width, or valid values. The shared encoded-field convention is also implicit; if helper code interprets `F367*` values differently, masked writes will target bad registers. The file contains hundreds of constants, so copy/paste drift, duplicate bit names, or datasheet revision differences are practical maintenance risks.

### Test Signals
Useful validation signals are successful STV0367 probe/chip-ID reads, correct I2C repeater behavior, lock acquisition for both DVB-T and DVB-C channels, stable AGC readings, correct BER/uncorrected block counters, transport-stream output under serial/parallel modes, and regression tests or hardware traces confirming that masked field writes preserve unrelated bits.
