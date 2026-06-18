# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv0900_sw.c

## Purpose

`stv0900_sw.c` implements the software acquisition, lock validation, blind-search, result extraction, and post-lock optimization logic for the STV0900 satellite demodulator frontend. It is the high-level demodulator search engine layered over the register map in `stv0900_reg.h` and lower-level I2C/register/tuner helpers from `stv0900_priv.h`. The file is responsible for taking the desired search parameters stored in `struct stv0900_internal` and driving the hardware through DVB-S1, DSS, DVB-S2, warm-start, cold-start, and blind-search flows until it returns an `enum fe_stv0900_signal_type` such as `STV0900_RANGEOK`, `STV0900_NOCARRIER`, `STV0900_NOAGC1`, or `STV0900_NODATA`.

## Important APIs and Functions

`shiftx()` is exported to the register header and shifts packed register or field identifiers for demodulator 1. It is a small helper, but the entire `REGx()`/`FLDx()` alias model relies on it.

`stv0900_check_signal_presence()` reads carrier frequency registers and AGC2 integrator registers, compares the carrier offset against the configured search range and master clock, and returns a boolean-style `no_signal` result. It is used inside software carrier scanning and after failed lock attempts.

`stv0900_algo()` is the primary entry point in this file. It configures hardware resets, symbol-rate registers, bandwidth, tuner state, search-standard enable bits, IQ inversion, rolloff controls, and Viterbi/FEC parameters. It then runs one of three acquisition strategies: `stv0900_blind_search_algo()`, `stv0900_get_demod_cold_lock()`, or `stv0900_get_demod_lock()` for warm starts. After demodulator lock it extracts signal parameters, optimizes tracking, waits for FEC/TS lock, updates `intp->result[demod].locked`, and applies a DVB-S1 IQ workaround on older chips when appropriate.

The carrier and symbol-rate helpers include `stv0900_get_sw_loop_params()`, `stv0900_search_carr_sw_loop()`, and `stv0900_sw_algo()` for fallback carrier scanning; `stv0900_get_symbol_rate()`, `stv0900_set_symbol_rate()`, `stv0900_set_max_symbol_rate()`, and `stv0900_set_min_symbol_rate()` for fixed-point conversions between register values and hertz; `stv0900_get_timing_offst()` for timing-error correction; and `stv0900_carrier_width()` for bandwidth calculation from symbol rate and rolloff.

Lock and result helpers include `stv0900_check_timing_lock()`, `stv0900_get_demod_cold_lock()`, `stv0900_get_lock_timeout()`, `stv0900_get_fec_lock()`, `stv0900_wait_for_lock()`, `stv0900_get_standard()`, `stv0900_get_carr_freq()`, `stv0900_get_tuner_freq()`, and `stv0900_get_signal_params()`. Optimization and standard setup are handled by `stv0900_set_dvbs2_rolloff()`, `stv0900_set_viterbi_tracq()`, `stv0900_set_viterbi_acq()`, `stv0900_set_viterbi_standard()`, `stv0900_get_vit_fec()`, `stv0900_set_dvbs1_track_car_loop()`, `stv0900_track_optimization()`, and `stv0900_set_search_standard()`.

Blind-search support is implemented by `stv0900_blind_check_agc2_min_level()`, `stv0900_search_srate_coarse()`, `stv0900_search_srate_fine()`, and `stv0900_blind_search_algo()`. These routines use AGC2 thresholds, timing-lock quality, KREF timing sweeps, symbol-rate scans, and tuner retuning to discover a usable carrier without a precise starting symbol rate.

## Control Flow

The top-level flow starts in `stv0900_algo()`. It resets hardware algorithm state, chooses correlation thresholds based on `chip_id` and symbol rate, computes demodulator and FEC timeouts with `stv0900_get_lock_timeout()`, and configures either blind-search mode or a bounded known-symbol-rate mode. Known-symbol-rate setup writes timing, AGC2, symbol-rate initial/up/low registers, and bandwidth. Blind-search setup forces a broad bandwidth and initializes a 1 Msymbol/s starting point.

The tuner is then programmed through either the embedded-auto tuner path (`tuner_type == 3`) or normal DVB tuner callbacks. The code checks AGC1 and IQ power before attempting a search. If front-end power is absent it returns `STV0900_NOAGC1`; otherwise it writes spectrum inversion, manual rolloff mode, and standard-specific DVB-S1/DSS/DVB-S2 enable bits. Non-blind searches call `stv0900_start_search()`.

Warm starts simply wait for demodulator lock. Cold starts first wait for lock, then for low symbol rates may step tuner frequency or carrier offset in a bounded zig-zag pattern. If a cold start fails and timing appears locked on higher-symbol-rate carriers, the code invokes `stv0900_sw_algo()` as a software carrier-search fallback. Blind search first rejects channels with insufficient AGC2 evidence, then sweeps timing reference values and performs coarse/fine symbol-rate detection before waiting for demod lock.

Once demod lock is present, `stv0900_get_signal_params()` reads standard, tuner frequency, carrier offset, symbol rate plus timing offset, FEC, MODCOD, pilots, frame length, rolloff, spectrum inversion, and modulation. It validates the discovered carrier against the configured search range and carrier width. `stv0900_track_optimization()` then rewrites tracking-loop, FEC, equalizer, bandwidth, and error-counter settings for the locked standard. Final lock validation goes through `stv0900_wait_for_lock()`, which requires demodulator lock, FEC lock, and TS FIFO line OK before marking the result locked.

## State and Persistence Behavior

The main mutable software state is `struct stv0900_internal`, reached through `fe->demodulator_priv`. The file reads search inputs from `intp->symbol_rate[demod]`, `intp->srch_range[demod]`, `intp->srch_standard[demod]`, `intp->srch_algo[demod]`, `intp->srch_iq_inv[demod]`, `intp->fec[demod]`, `intp->freq[demod]`, `intp->rolloff`, `intp->mclk`, `intp->chip_id`, `intp->demod_mode`, and `intp->tuner_type[demod]`. It writes derived state to `intp->bw[demod]`, updates `intp->freq[demod]` during blind or low-symbol-rate discovery, and fills `intp->result[demod]` with lock status, standard, frequency, symbol rate, FEC, MODCOD, pilot, frame length, rolloff, spectrum, and modulation.

Hardware state persists through many register writes: demodulator mode, carrier frequency init, symbol-rate bounds, AGC references, timing thresholds, Viterbi thresholds, FEC masks, MODCOD activation, transport-stream FIFO settings, error counters, and tuner registers. There is no file-backed persistence. Timing behavior is explicit through `msleep()` calls and lock polling loops; these sleeps are part of the hardware sequencing contract and affect acquisition latency.

## Dependencies and Integration Points

This file depends on `stv0900.h` for public enums and frontend state, `stv0900_reg.h` for register/field aliases, and `stv0900_priv.h` for private helpers and constants. It calls register primitives such as `stv0900_read_reg()`, `stv0900_write_reg()`, `stv0900_get_bits()`, and `stv0900_write_bits()`, plus hardware helpers such as `stv0900_get_demod_lock()`, `stv0900_start_search()`, `stv0900_set_tuner()`, `stv0900_set_bandwidth()`, `stv0900_set_tuner_auto()`, `stv0900_get_freq_auto()`, `stv0900_get_optim_carr_loop()`, `stv0900_get_optim_short_carr_loop()`, `stv0900_activate_s2_modcod()`, `stv0900_activate_s2_modcod_single()`, and `stv0900_stop_all_s2_modcod()`.

It integrates with the Linux DVB frontend model through `struct dvb_frontend`, `fe->demodulator_priv`, `fe->ops.tuner_ops.get_frequency`, and tuner programming callbacks. It also uses kernel timing and utility primitives such as `msleep()`, `abs()`, and integer types. The result of this algorithm is consumed by higher frontend operations that report tuning success, signal parameters, and lock state to DVB userspace.

## Risks

The code is hardware-revision sensitive. Many register constants differ for `chip_id` values below `0x20`, equal to `0x10`/`0x12`, at or below `0x20`, and at or above `0x30`. A behavior change that appears harmless for one STV0900 cut can regress another. Integer fixed-point conversions are another risk: symbol-rate, carrier-offset, timeout, and bandwidth calculations rely on shifts and divisions by scaled `mclk`, and several branches clamp values to avoid overflow or unreasonable loops.

Acquisition loops are bounded but latency-sensitive. Mistuned timeout constants, sleep intervals, AGC thresholds, or carrier steps can create false no-signal results, long tune times, or unstable locks. Some functions temporarily modify hardware thresholds and restore them later, such as `stv0900_check_timing_lock()`; early returns or future edits in those regions could leave hardware in a degraded state. The demodulator-selection aliasing also depends on every function passing the correct `demod` value for register macros.

There is limited explicit error handling around tuner callbacks and register I/O. `stv0900_get_tuner_freq()` logs invalid tuner frequency reads but returns `0`, which can feed range checks. The top-level algorithm mutates `intp->result[demod].locked` in several branches, so regressions can present as stale or contradictory lock state if a new path misses a reset.

## Test Signals

The strongest test signals are hardware or hardware-in-loop tuning tests across DVB-S1, DSS, DVB-S2, warm start, cold start, low symbol rate, high symbol rate, blind search, both demodulators, and multiple chip revisions. Tests should confirm that `stv0900_algo()` returns the expected signal type, updates `intp->result[demod]` coherently, and leaves TS FIFO/FEC lock stable after `stv0900_wait_for_lock()`.

Targeted regression tests should exercise symbol-rate conversion round trips, carrier-width and timeout calculations near thresholds (1, 2, 5, 10, 20, and 60 Msymbol/s), no-AGC detection, AGC2 no-signal rejection, old-chip DVB-S1 IQ workaround behavior, and tuner retuning during cold and blind search. Debug traces from `dprintk()` around lock acquisition, coarse/fine blind search, found standard, MODCOD, and final range classification are useful operational signals when comparing behavior across changes.
