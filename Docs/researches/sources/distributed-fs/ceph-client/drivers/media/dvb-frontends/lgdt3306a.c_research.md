# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lgdt3306a.c

## Purpose
`lgdt3306a.c` implements an LG Electronics LGDT3306A ATSC 8VSB and ITU-T J.83 Annex B QAM demodulator. It exposes a DVB frontend, controls the demodulator over 16-bit-register I2C transactions, optionally creates a tuner I2C mux/repeater, and handles custom search/tune/status behavior for VSB, QAM64, QAM256, and QAM_AUTO.

## Important APIs, Types, and Functions
`struct lgdt3306a_state` stores the I2C adapter, board config, `dvb_frontend`, cached frequency/modulation, last SNR, and optional `i2c_mux_core`. Low-level helpers are `lgdt3306a_write_reg()`, `lgdt3306a_read_reg()`, `lgdt3306a_set_reg_bit()`, and `lgdt3306a_soft_reset()`. Configuration paths include `lgdt3306a_mpeg_mode()`, `lgdt3306a_mpeg_mode_polarity()`, `lgdt3306a_mpeg_tristate()`, `lgdt3306a_power()`, `lgdt3306a_set_vsb()`, `lgdt3306a_set_qam()`, `lgdt3306a_set_if()`, and `lgdt3306a_i2c_gate_ctrl()`. DVB callbacks are wired through `lgdt3306a_ops`: init/sleep, tune/search, set/get frontend, read status/BER/SNR/signal strength/uncorrected blocks, TS bus control, release, and tune settings. Integration entry points are legacy `lgdt3306a_attach()` plus the I2C-driver `lgdt3306a_probe()`/`lgdt3306a_remove()`.

## Control Flow
Attach allocates state, installs `lgdt3306a_ops`, probes a few reset-default register masks as a weak hardware check, seeds cached tuning state to invalid values, and powers the chip down. Probe copies platform data, attaches, creates a locked one-channel I2C mux adapter for the tuner, disables the frontend's direct gate callback because mux select/deselect now handles it, and returns both the frontend and tuner adapter through platform pointers. Initialization programs common ADC, PLL, IF, AGC, VSB/QAM defaults, transport-stream mode, tristates output, and then sleeps. A tune powers up, calls tuner `set_params()`, programs modulation-specific register sequences, AGC/IF, TS polarity, bus enable, and soft reset. Status reads optionally query tuner RF strength, polls the demodulator's never-lock, sync, FEC, and packet-error/SNR paths, then publishes DVB lock bits and CNR stats.

## State and Persistence
Runtime state is volatile: cached frequency/modulation prevent redundant retunes, `snr` backs legacy signal-strength calculations, and the chip register image holds power, modulation, IF, TS, AGC, and monitor settings. Sleep invalidates the cached frequency, tristates MPEG/IF outputs, and powers down. There is no filesystem persistence; a full init/reprogram sequence is needed after reset or loss of chip state.

## Dependencies and Integration Points
The file depends on Linux I2C, DVB frontend core, tuner callbacks, `linux/int_log.h`-style math support through local log interpolation, `i2c-mux`, and board-supplied `struct lgdt3306a_config`. It registers an I2C device id `"lgdt3306a"` and exports `lgdt3306a_attach()` for legacy board drivers. The frontend advertises `SYS_ATSC` and `SYS_DVBC_ANNEX_B`.

## Risks and Edge Cases
The chip-id check is heuristic and warnings do not abort in several mismatch cases, so a wrong I2C device could be accepted until later I/O fails. The module parameter `forced_manual` changes QAM auto/manual behavior and can affect legacy tuning expectations. Some BER/uncorrected-block comments explicitly note unclear DVB-core scaling and wrap behavior. Error handling often logs and continues through long register sequences, so partial configuration can leave the demodulator in an uncertain state. `deny_i2c_rptr` suppresses repeater operations and must match board topology.

## Test Signals
Useful signals are successful I2C attach/probe and mux creation, init with both 24 MHz and 25 MHz crystals, VSB/QAM/QAM_AUTO retunes, tuner-gate open/close around tuner I2C, TS parallel/serial and polarity output validation, lock acquisition with FE_HAS_* bits, CNR scale changes to decibel only after sync, BER/ucblocks reads, sleep/wake retune invalidation, and removal without mux or state leaks.
