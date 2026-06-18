<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stb0899_algo.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stb0899_algo.c

## Purpose
`stb0899_algo.c` contains the acquisition algorithms for the STB0899 multistandard satellite demodulator. It implements separate DVB-S/DSS and DVB-S2 lock procedures used by `stb0899_drv.c` custom frontend search.

## Important APIs, Types, And Functions
The exported functions are `stb0899_dvbs_algo()`, `stb0899_dvbs2_algo()`, and `stb0899_carr_width()`. DVB-S support includes symbol-rate programming (`stb0899_set_srate()`), first/subsequent search range calculation, timing lock checks/search (`stb0899_check_tmg()`, `stb0899_search_tmg()`), carrier detection/search, data lock search, and range validation. DVB-S2 support configures UWP/CSM thresholds, BTR symbol-rate and loop bandwidth, CRL carrier nominal frequency, acquisition step geometry, timing-loop reset, reacquire triggers, demod lock polling, FEC lock polling, manual CSM tuning for specific modcod/pilot cases, and measured parameter storage.

## Control Flow
For DVB-S/DSS, the driver sets the SFR registers, optimizes loop constants by symbol rate, resets the stream merger, computes a tuner subrange, tunes the external tuner through the I2C gate, waits for AGC/timing, then searches timing, carrier, data, and final range in a zigzag pattern. On success it switches loops from acquisition to tracking and applies puncture-rate-specific Viterbi/carrier loop settings. For DVB-S2, it tunes the external tuner, sets acquisition AGC, initializes UWP/CSM/BTR/CRL, sets IQ inversion, triggers acquisition, waits for UWP+CSM demod lock, waits for packet/FEC lock, retries false locks using measured carrier offset, flips IQ inversion if needed, optionally reconfigures manual CSM for low master-clock/symbol-rate ratios, then stores final offset, symbol rate, modcod, pilots, frame length, and AGC tracking settings.

## State And Persistence
The algorithms mutate `state->internal`: current frequency, symbol rate, search range, tuner bandwidth, derotator frequency, inversion, FEC/modcod, lock status, timing constants, and DVB-S2 measured parameters. The code also writes many demodulator, S2 demod, and S2 FEC registers; those register settings persist until the next tune, sleep, or init. No data is persisted outside the frontend instance.

## Dependencies And Integration Points
This file depends on `stb0899_priv.h` state definitions, `stb0899_drv.h` config callbacks, and `stb0899_reg.h` register/bitfield definitions. It calls the low-level read/write helpers and `stb0899_i2c_gate_ctrl()` from `stb0899_drv.c`, and it relies on board-provided tuner callbacks in `struct stb0899_config`.

## Risks And Test Signals
The highest risks are integer scaling/overflow in loop and NCO calculations, divide-by-zero if symbol rate or master clock are invalid, fragile timing sleeps, false locks, and bad state carryover between DVB-S and DVB-S2. The comment in DVB-S warns that status reads during acquisition can break lock, so instrumentation must be careful. Test signals are successful locks for DVB-S, DSS, and DVB-S2 across low/high symbol rates, IQ inversion recovery, false-lock retries that converge, correct reported final frequency/symbol rate, stable reacquisition after failed searches, and no I2C gate leaks around tuner calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stb0899_algo.c -->
