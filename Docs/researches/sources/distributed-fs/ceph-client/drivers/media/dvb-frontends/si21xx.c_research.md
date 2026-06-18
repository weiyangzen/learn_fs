<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/si21xx.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/si21xx.c

## Purpose
`si21xx.c` implements a Linux DVB frontend driver for Silicon Laboratories SI2109/SI2110 DVB-S demodulators. It exposes a `struct dvb_frontend` with DVB-S tuning, status, signal metrics, LNB voltage, 22 kHz tone, and DiSEqC master/burst operations. It is intended to be attached by a board driver via `si21xx_attach()`.

## Important APIs, Types, And Functions
The private `struct si21xx_state` stores the I2C adapter, immutable board config, embedded frontend, initialization flag, error counter mode, and selected ADC sampling rate `fs`. Low-level access is through `si21_writereg()`, `si21_writeregs()`, `si21_readreg()`, and `si21_readregs()`, with `si21_write()` exported through `frontend.ops.write` for header helper use. `si21xx_attach()` allocates state, wakes the demodulator, reads revision register `0x00`, accepts only SI2110/SI2109 IDs `0x04` and `0x14`, copies `si21xx_ops`, and returns the embedded frontend. `si21xx_init()` writes `serit_sp1511lhb_inittab`, selects DVB QPSK mode, and configures a parallel, LSB-first, gapped transport stream. `si21xx_set_frontend()` validates `SYS_DVBS`, calculates ADC sampling/coarse/fine tune values, writes PLL/tune registers, stores `state->fs`, and calls `si21xx_setacquire()`. The frontend status and metrics callbacks read lock, AGC, BER/SNR, and uncorrected block registers.

## Control Flow
Attach performs a minimal hardware presence check, then DVB core calls `.init` before tuning. Tuning flows from DVB properties to sample-rate selection, PLL programming, symbol-rate register conversion, code-rate mask setup, blind-scan/QuickLock register setup, and acquisition start. Status polling maps demod lock bits into `FE_HAS_SIGNAL`, `FE_HAS_CARRIER`, `FE_HAS_VITERBI`, `FE_HAS_SYNC`, and `FE_HAS_LOCK`. DiSEqC commands write the LNB FIFO and set the LNB control start bit; mini-burst, tone, and voltage operations modify control bits after waiting for idle where needed.

## State And Persistence
State is in memory only. `state->fs` is recalculated per tune and is required by symbol-rate conversion. `state->errmode` decides whether register pair `0x1d/0x1e` is interpreted as BER or uncorrected blocks; it is initialized to BER and not otherwise switched in this file. `state->initialised` is cleared on sleep but otherwise has little effect because `.init` always writes the register table. Hardware state persists in demodulator registers across calls until reinitialized or powered down.

## Dependencies And Integration Points
The driver depends on the DVB frontend core, Linux I2C transfers, jiffies/time helpers, and `si21xx.h` for board configuration and attach declaration. Board drivers provide the I2C address and optional minimum retune delay. Integration is through `dvb_frontend_ops` and satellite equipment control callbacks. It does not own a tuner; board code must coordinate external RF hardware as needed.

## Risks And Test Signals
Important risks are register-programming fragility, integer scaling errors in sample-rate/symbol-rate math, unsupported delivery systems returning `-EOPNOTSUPP`, and weak I2C read error propagation because `si21_readreg()` returns the last byte even on failed transfer. The `coderates[crate]` indexing assumes DVB core gives a valid `fe_code_rate`; unexpected enums could index out of bounds. DiSEqC waits use short 100-jiffy timeouts and should be validated against real hardware. Test signals are successful attach ID logs, tuning lock on known DVB-S transponders over the 950-2150 MHz range, correct 13/18 V and tone behavior, DiSEqC command execution, sane SNR/strength trends, and clean I2C error handling under cable/device removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/si21xx.c -->
