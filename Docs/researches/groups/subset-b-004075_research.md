# Research: subset-b-004075

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stb6100.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stb6100.c

## Purpose
`stb6100.c` implements the STB6100 satellite silicon tuner as a Linux DVB tuner driver. It attaches tuner operations to an existing `dvb_frontend`, performs direct I2C register reads/writes to the tuner address, computes PLL divider values for 950-2150 MHz input frequencies, programs low-pass bandwidth, and exposes lock/frequency/bandwidth state through `dvb_tuner_ops`.

## Important APIs, Types, and Functions
- Exported API: `stb6100_attach()` allocates `struct stb6100_state`, binds `fe->tuner_priv`, and installs `stb6100_ops` into `fe->ops.tuner_ops`.
- Tuner ops: `stb6100_init`, `stb6100_sleep`, `stb6100_get_status`, `stb6100_set_params`, `stb6100_get_frequency`, `stb6100_get_bandwidth`, and `stb6100_release`.
- Register helpers: `stb6100_read_regs()`, `stb6100_read_reg()`, `stb6100_write_reg_range()`, and `stb6100_write_reg()` wrap I2C transfers and apply the `stb6100_template` mask/set normalization on writes.
- Tuning helpers: `stb6100_set_frequency()` selects ODIV/OSM/PSD2, computes integer and fractional PLL divisors from `state->reference`, writes VCO/NI/NF/K/G/DLB/test/LPEN/FCCK registers, and waits for lock/stabilization. `stb6100_set_bandwidth()` maps requested Hz to the STB6100 `F` register and toggles the LPF clock/calibration bit.
- Lookup data: `lkup[]` maps frequency ranges in kHz to OSM values; `stb6100_regnames[]` and `stb6100_template[]` support debug output and reserved-bit handling.

## Control Flow
Attach initializes only software state and does not probe the tuner. Runtime setup begins with `.init`, which sets default bandwidth and reference clock. `.set_params` consults `fe->dtv_property_cache`: if `frequency` is nonzero it runs `stb6100_set_frequency()`, and if `bandwidth_hz` is nonzero it runs `stb6100_set_bandwidth()`. Frequency programming first asks the demodulator `.get_frontend` for current properties when available so it can use symbol rate for baseband gain selection. It then enables LPF calibration, powers the tuner core, chooses divider mode, writes PLL divider registers one by one, enables the PLL loop, runs VCO search timing, disables search, and stops calibration.

## State and Persistence Behavior
Persistent driver state lives in `struct stb6100_state`: I2C adapter, immutable config pointer, frontend pointer, cached `frequency`, cached `bandwidth`, `srate`, and reference clock in kHz. Hardware register contents are the authoritative state; getters read registers back and refresh cached values. There is no firmware, disk persistence, workqueue, lock, or shared global state beyond the `verbose` module parameter. `stb6100_sleep()` is a TODO and does not power down hardware.

## Dependencies and Integration Points
The file depends on Linux module/slab/string APIs, `i2c_transfer`, `msleep`, DVB frontend core types, and register/config definitions from `stb6100.h`. It integrates as a tuner behind demodulator drivers through `dvb_tuner_ops`; demodulators may gate I2C access around tuner calls. The source assumes `kzalloc_obj()` is available in this tree's kernel compatibility layer.

## Risks and Edge Cases
- `stb6100_read_reg()` performs the I2C transfer before validating `reg`, and it ignores the transfer return value; invalid offsets are still checked before debug name use but after the bus operation.
- `stb6100_write_reg()` returns `-EREMOTEIO` for an invalid register offset instead of `-EINVAL`.
- Several `msleep()` comments explicitly note concurrency risk if related threads program the same hardware during calibration/search windows; the driver has no mutex around multi-register sequences.
- Attach does not verify device identity, so board code must provide correct config/address.
- `.set_params` ignores return values from frequency and bandwidth setters, so caller-visible success can mask I2C/tuning failures.

## Test Signals
Useful validation is hardware-oriented: attach with a known board, tune boundary frequencies across all `lkup[]` bands, verify `FE_HAS_LOCK` through `STB6100_LD_LOCK`, confirm bandwidth readback after 5/36 MHz clamps, and exercise I2C error injection. Static tests should flag unchecked I2C returns, missing locking around calibration, and the no-op sleep path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stb6100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stb6100.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stb6100.h

## Purpose
`stb6100.h` defines the STB6100 register map, bit masks, config/state structs, and attach prototype used by the STB6100 tuner driver and board drivers.

## Important APIs, Types, and Functions
- Register offsets and masks cover `LD`, `VCO`, `NI`, `NF_LSB`, `K`, `G`, `F`, `DLB`, `TEST1`, `FCCK`, `LPEN`, and `TEST3`.
- `STB6100_NUMREGS` fixes the register window size at 12 bytes.
- `INRANGE` and `CHKRANGE` provide range helpers used by the driver lookup logic.
- `struct stb6100_config` supplies `tuner_address` and `refclock`.
- `struct stb6100_state` stores I2C, config, frontend, tuner ops copy, cached frequency/symbol rate/bandwidth, and reference clock.
- `stb6100_attach()` is declared when `CONFIG_DVB_STB6100` is reachable; otherwise a stub logs that the driver is disabled and returns `NULL`.

## Control Flow
This header has no runtime control flow except the Kconfig-gated inline fallback. Board code includes it to build a `stb6100_config` and call `stb6100_attach()` after creating a demodulator frontend.

## State and Persistence Behavior
The header establishes the software state layout only. Runtime values are in memory and hardware registers, with no persistence outside the frontend lifetime.

## Dependencies and Integration Points
It depends on `<linux/dvb/frontend.h>` and `<media/dvb_frontend.h>`. The public integration point is the attach function and `stb6100_config`; the rest of the register constants are internal-driver-facing but visible to any includer.

## Risks and Edge Cases
The state struct includes a `struct dvb_tuner_ops ops` field that the implementation does not currently use. The attach stub uses `printk`, so including this header in code without kernel logging context would be inappropriate, though normal use is kernel DVB code.

## Test Signals
Compile coverage with `CONFIG_DVB_STB6100=y/m/n` verifies both real and stub attach paths. Driver tests should validate register masks against datasheet expectations because this header is the source of bitfield truth for all STB6100 programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stb6100.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stb6100_cfg.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stb6100_cfg.h

## Purpose
`stb6100_cfg.h` is a small static wrapper layer for board or demodulator code that wants separate get/set frequency and get/set bandwidth helpers while the real tuner API exposes a combined `.set_params` operation.

## Important APIs, Types, and Functions
- `stb6100_get_frequency()` calls `fe->ops.tuner_ops.get_frequency` if present.
- `stb6100_set_frequency()` writes `dtv_property_cache.frequency`, temporarily clears `bandwidth_hz`, calls tuner `.set_params`, then restores bandwidth.
- `stb6100_get_bandwidth()` calls tuner `.get_bandwidth` if present.
- `stb6100_set_bandwidth()` writes `dtv_property_cache.bandwidth_hz`, temporarily clears `frequency`, calls tuner `.set_params`, then restores frequency.

## Control Flow
Each helper reaches through `struct dvb_frontend_ops` to the installed `dvb_tuner_ops`. Setters mutate the frontend property cache before invoking `.set_params` so that the STB6100 driver changes only one dimension. Getters are simple pass-throughs.

## State and Persistence Behavior
State changes are limited to temporary edits of `fe->dtv_property_cache`. On successful `.set_params`, the original untouched field is restored. If `.set_params` returns an error, restoration has already occurred in this header's implementation for both setters.

## Dependencies and Integration Points
The wrapper depends on DVB frontend core headers and is meant to be included into C files rather than compiled as a standalone translation unit. It assumes the frontend already has tuner ops installed, commonly by `stb6100_attach()`.

## Risks and Edge Cases
The functions are `static`, so every includer gets private copies and names may collide with other static helpers in the same C file. There is no I2C gate control here; boards that require the demodulator repeater must use `stb6100_proc.h` or gate externally. Missing tuner callbacks are silently treated as success.

## Test Signals
Unit-style tests can use a fake `dvb_frontend` with stub tuner ops to verify cache mutation/restoration and error propagation. Hardware tests should confirm this wrapper is not used on boards that need explicit I2C repeater enablement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stb6100_cfg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stb6100_proc.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stb6100_proc.h

## Purpose
`stb6100_proc.h` provides alternate static STB6100 wrapper helpers that open and close the demodulator I2C gate around tuner frequency/bandwidth operations.

## Important APIs, Types, and Functions
- `stb6100_get_freq()` and `stb6100_get_bandw()` wrap tuner getter calls with optional `frontend_ops->i2c_gate_ctrl(fe, 1)` before and `i2c_gate_ctrl(fe, 0)` after.
- `stb6100_set_freq()` and `stb6100_set_bandw()` use the same temporary `dtv_property_cache` mutation pattern as `stb6100_cfg.h`, but also gate the bus for `.set_params`.

## Control Flow
Each function checks whether the relevant tuner callback exists. If so, it enables the I2C gate when the demodulator provides `i2c_gate_ctrl`, performs the tuner operation, then disables the gate on success.

## State and Persistence Behavior
Setters temporarily clear the other tuning property (`bandwidth_hz` or `frequency`) so `.set_params` touches only the requested dimension. Hardware state is changed by the underlying tuner op. The demodulator I2C repeater/gate is a transient hardware side effect.

## Dependencies and Integration Points
This include-style helper depends on `struct dvb_frontend_ops`, `struct dvb_tuner_ops`, and the optional demodulator `.i2c_gate_ctrl` callback. It is intended for demodulator/board combinations where the tuner sits behind a gated I2C repeater.

## Risks and Edge Cases
On error paths, the functions return before closing the I2C gate, leaving the repeater enabled. `stb6100_set_freq()` also restores `bandwidth_hz` before checking the error, but does not close the gate if `.set_params` fails; similarly for bandwidth. Missing callbacks are treated as success.

## Test Signals
Fake frontend tests should assert gate open/close ordering for success and should expose the current leak on tuner callback failure. Hardware tests should validate that repeated get/set operations do not leave the bus in an unexpected state after I2C faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stb6100_proc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv0288.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv0288.c

## Purpose
`stv0288.c` implements a Linux DVB-S demodulator driver for the ST STV0288. It handles demodulator I2C register access, default or board-supplied initialization tables, symbol-rate programming, tuner handoff, DiSEqC/tone commands, and DVB frontend status/statistics callbacks.

## Important APIs, Types, and Functions
- `struct stv0288_state` stores I2C/config/frontend, cached tuner frequency, symbol rate, FEC, initialization flag, and error-counter mode.
- Exported API: `stv0288_attach()` allocates state, wakes/probes register `0x00` for ID `0x11`, copies `stv0288_ops`, and returns the embedded frontend.
- I2C helpers: `stv0288_writeregI()`, `stv0288_write()`, and `stv0288_readreg()`.
- Tuning: `stv0288_init()` loads `stv0288_inittab` or `config->inittab`; `stv0288_set_symbolrate()` calculates SFR registers; `stv0288_set_frontend()` validates `SYS_DVBS`, invokes tuner `.set_params`, programs symbol rate, and sweeps carrier offset registers until lock or timeout.
- Satellite control: `stv0288_send_diseqc_msg()`, `stv0288_send_diseqc_burst()`, `stv0288_set_tone()`, and stub `stv0288_set_voltage()`.
- Metrics: `read_status`, `read_ber`, `read_signal_strength`, `read_snr`, and `read_ucblocks`.

## Control Flow
Attach probes the demodulator but does not fully initialize it. `.init` resets and writes the register table. `.set_frontend` is the main tune path: TS parameters are optionally set, the external tuner is programmed, I2C gate is closed, symbol rate is written, carrier lock control is enabled, and a loop adjusts CFR registers while polling Viterbi status register `0x24`. Successful completion caches `frequency`, `symbol_rate`, and `FEC_AUTO`.

## State and Persistence Behavior
The embedded `dvb_frontend` owns state lifetime until `.release`. Cached tuning fields mirror the last requested values, but hardware registers drive lock and metrics. `errmode` selects whether BER/uncorrected-block reads report counters. `sleep` writes standby register `0x41=0x84` and clears `initialised`, though `initialised` is otherwise not used for gating.

## Dependencies and Integration Points
The driver depends on Linux I2C, delay, jiffies, slab, module APIs, and DVB frontend core. It integrates with an external tuner through `fe->ops.tuner_ops.set_params` and optional demodulator `i2c_gate_ctrl`. Board-specific behavior enters through `struct stv0288_config` callbacks and optional init table.

## Risks and Edge Cases
- I2C read errors return the default byte rather than a negative error, so callers can misinterpret bus failures as register values.
- `stv0288_set_frontend()` usually returns 0 even if lock was not achieved; lock failure is only visible through later `read_status`.
- `set_voltage` logs but does not control LNB voltage.
- `debug_legacy_dish_switch` is declared as a module parameter but not used in this driver.
- Carrier sweep timing is fixed and may be fragile across boards/tuners.

## Test Signals
Hardware validation should cover attach ID detection, init table override, DVB-S tuning across symbol-rate bounds, DiSEqC master/burst/tone behavior, and status register transitions. Fault injection should cover I2C transfer failures and verify that tuning failures surface through status even when `.set_frontend` returns success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv0288.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv0288.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv0288.h

## Purpose
`stv0288.h` declares the board-facing configuration and attach API for the STV0288 DVB-S demodulator driver.

## Important APIs, Types, and Functions
- `struct stv0288_config` contains `demod_address`, optional `inittab`, `min_delay_ms`, and `set_ts_params` callback.
- `stv0288_attach()` is declared when `CONFIG_DVB_STV0288` is reachable, otherwise a disabled-driver stub returns `NULL`.
- `stv0288_writereg()` is an inline helper that writes one register through `fe->ops.write`.

## Control Flow
The header itself only routes calls by Kconfig. Board drivers pass a populated config and I2C adapter to `stv0288_attach()`, then can use the returned `dvb_frontend` with normal DVB core operations.

## State and Persistence Behavior
No state is stored in the header; it defines configuration consumed by the implementation. The init table pointer must remain valid for the driver's lifetime because the implementation references it from `state->config`.

## Dependencies and Integration Points
It depends on DVB frontend headers. `set_ts_params` lets board code configure transport-stream mode or DMA-adjacent parameters before tuning.

## Risks and Edge Cases
`inittab` is mutable `u8 *` rather than `const u8 *`, and the implementation assumes a `0xff, 0xff` terminator. `min_delay_ms` is declared but this implementation does not expose `.get_tune_settings`, so it is unused here.

## Test Signals
Compile with reachable/unreachable Kconfig modes. Board integration tests should verify init table lifetime, terminator correctness, and that `stv0288_writereg()` properly delegates through `.write`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv0288.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv0297.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv0297.c

## Purpose
`stv0297.c` implements a DVB-C Annex A demodulator driver for the STV0297. It programs QAM mode, symbol rate, sweep/carrier offsets, inversion, AGC/equalizer acquisition, and exposes DVB-C status/statistics through `dvb_frontend_ops`.

## Important APIs, Types, and Functions
- `struct stv0297_state` stores I2C/config/frontend, `last_ber`, and cached `base_freq`.
- Exported API: `stv0297_attach()` allocates state, probes register `0x80` for expected chip bits, copies `stv0297_ops`, and returns the embedded frontend.
- I2C helpers: `stv0297_writereg()`, `stv0297_readreg()`, `stv0297_writereg_mask()`, and `stv0297_readregs()`, with optional STOP-between-write-and-read support from config.
- Tuning helpers: `stv0297_set_symbolrate()`, `stv0297_get_symbolrate()`, `stv0297_set_sweeprate()`, `stv0297_set_carrieroffset()`, `stv0297_set_initialdemodfreq()`, `stv0297_set_qam()`, and `stv0297_set_inversion()`.
- Frontend ops include init/sleep, I2C gate control, set/get frontend, and metric readers.

## Control Flow
`.init` writes the board-supplied register table and clears BER cache. `.set_frontend` validates modulation, derives sweep and timing parameters, applies board inversion policy, reinitializes the chip, programs the external tuner, clears interrupts, configures AGC/STL/deinterleaver/equalizer, writes QAM/symbol/sweep/carrier/inversion settings, starts acquisition, then waits in stages for WGAGC lock, equalizer partial convergence, full convergence, main lock, and stable lock. On success it disables sweep and stores `base_freq`.

## State and Persistence Behavior
State is memory-resident and freed by `.release`. `last_ber` persists the last completed BER counter while hardware measurement is in progress. `base_freq` stores the requested tuned frequency for `get_frontend`. Hardware registers hold current modulation, inversion, symbol rate, and counters. Sleep sets a standby bit in register `0x80`.

## Dependencies and Integration Points
The driver depends on Linux I2C/delay/jiffies/module/slab APIs and DVB frontend core. It integrates with an external cable tuner through `.tuner_ops.set_params` and closes the I2C gate after tuner programming. Board policy is supplied by `struct stv0297_config`: demod address, init table, inversion inversion, and read STOP behavior.

## Risks and Edge Cases
- The debug macro is compiled to unconditional `printk` because `#if 1` is enabled.
- Several helper errors return `-1` instead of standard errno values, and many writes are not checked by higher-level tuning code.
- `.set_frontend` returns 0 even on timeout; acquisition failure must be detected via `read_status`.
- The timeout checks use `time_after(jiffies, timeout)` after loops that exit on `time_before`, which can treat equality imprecisely.
- Symbol-rate arithmetic uses `long`, which is architecture-width sensitive.

## Test Signals
Test with QAM16/32/64/128/256, inversion on/off with `config->invert`, STOP and repeated-start I2C read modes, and symbol-rate min/max. Runtime signals include register `0xDF` lock bit, BER refresh behavior at `0xA0`, and uncorrected-block freeze/clear sequencing through `0xDF`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv0297.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv0297.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv0297.h

## Purpose
`stv0297.h` defines the board-facing config and attach API for the STV0297 DVB-C demodulator.

## Important APIs, Types, and Functions
- `struct stv0297_config` includes `demod_address`, required register-pair `inittab`, `invert` bit, and `stop_during_read` bit.
- `stv0297_attach()` is Kconfig-gated with a disabled-driver inline stub.

## Control Flow
Board code builds a config and calls `stv0297_attach()`. The header's only executable path is the disabled-driver stub when the driver is not built.

## State and Persistence Behavior
The config pointer is retained by the implementation, so the init table and config storage must outlive the frontend. No runtime state is stored by the header itself.

## Dependencies and Integration Points
It depends on Linux DVB frontend headers. `stop_during_read` is an integration quirk for I2C adapters/devices that require a STOP between register address write and data read.

## Risks and Edge Cases
The implementation assumes `inittab` is valid and terminated by `0xff, 0xff`; the header does not encode length. The attach stub logs with `printk`.

## Test Signals
Compile coverage for Kconfig paths and board tests with both STOP/read modes are the main validation signals. Init table terminator errors should be caught by static review or guarded board data tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv0297.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv0299.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv0299.c

## Purpose
`stv0299.c` implements the STV0299 DVB-S demodulator driver. It handles demodulator register I2C access, board init tables, FEC and symbol-rate programming, external tuner coordination, DiSEqC/tone/LNB voltage control, Dish Network legacy switch signaling, status/statistics, and tune settings.

## Important APIs, Types, and Functions
- `struct stv0299_state` stores I2C/config/frontend, cached tuner frequency, symbol rate, FEC, error mode, accumulated uncorrected blocks, and saved MCR low bits.
- Exported API: `stv0299_attach()` probes ID `0xa1` or `0x80`, copies `stv0299_ops`, and returns the embedded frontend.
- I2C helpers: `stv0299_writeregI()`, `stv0299_write()`, `stv0299_readreg()`, and `stv0299_readregs()`.
- Tuning: `stv0299_set_FEC()`, `stv0299_get_fec()`, `stv0299_set_symbolrate()` using board callback `set_symbol_rate`, `stv0299_get_symbolrate()`, `stv0299_set_frontend()`, and `stv0299_get_frontend()`.
- Satellite equipment control: `stv0299_send_diseqc_msg()`, `stv0299_send_diseqc_burst()`, `stv0299_set_tone()`, `stv0299_set_voltage()`, and `stv0299_send_legacy_dish_cmd()`.
- Metrics: status, BER, signal strength, SNR, accumulated UCB, and `stv0299_get_tune_settings()`.

## Control Flow
Attach wakes the demodulator from standby and validates chip ID. `.init` writes MCR and the config init table, preserving `mcr_reg` from register `0x02` entries and applying `op0_off` to register `0x0c`. `.set_frontend` optionally sets TS parameters, validates explicit inversion, applies board inversion policy, programs the tuner and closes the gate, sets FEC, delegates symbol-rate register programming through the board callback, clears derotator registers, and caches requested values.

## State and Persistence Behavior
State lives with the embedded frontend and is freed on release. `ucblocks` accumulates uncorrected block reads when `errmode == STATUS_UCBLOCKS`; default `errmode` is BER, so UCB reads return `-ENOSYS` unless changed internally. `mcr_reg` preserves clock/control low bits across init/sleep. Sleep writes standby state and clears `initialised`; hardware registers remain authoritative for live lock/statistics.

## Dependencies and Integration Points
The file depends on Linux I2C, delay/jiffies/ktime, module/slab/string, `dvb_frontend_sleep_until`, and DVB frontend core. Board callbacks in `struct stv0299_config` are required for symbol-rate programming and optional TS setup. Tuner integration uses standard `.tuner_ops.set_params` plus optional I2C gate control.

## Risks and Edge Cases
- `skip_reinit` exists in the header but is not used in this implementation.
- `readreg` returns a byte even on failed I2C transfer; high-level code may proceed after bus errors.
- Auto inversion is rejected in `.set_frontend`, despite frontend caps advertising no explicit auto inversion capability beyond FEC auto.
- `stv0299_get_frontend()` adjusts `p->frequency` by derotator offset without first restoring cached base frequency, so caller-provided property state matters.
- Dish legacy command timing is sensitive and uses precise sleep-until sequencing; regressions are hardware-visible.

## Test Signals
Validation should cover attach IDs, init table programming, board `set_symbol_rate` ratio values, all FEC modes, inversion policy, tuner gate sequencing, DiSEqC FIFO/idle timeout handling, tone and 13/18/off voltage register effects, and legacy Dish timing with `debug_legacy_dish_switch`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv0299.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv0299.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv0299.h

## Purpose
`stv0299.h` defines constants, board configuration, attach API, and a register-write inline helper for STV0299 DVB-S demodulator integrations.

## Important APIs, Types, and Functions
- Constants define lock output modes (`STV0299_LOCKOUTPUT_*`) and 13V output selection (`STV0299_VOLT13_OP0`, `STV0299_VOLT13_OP1`).
- `struct stv0299_config` includes demod address, init table, master clock, inversion policy, reinit flag, lock output selection, LNB voltage output policy, minimum delay, required `set_symbol_rate` callback, and optional `set_ts_params`.
- `stv0299_attach()` is Kconfig-gated with a disabled-driver stub.
- `stv0299_writereg()` writes one register through `fe->ops.write`.

## Control Flow
Board code passes config and I2C adapter to `stv0299_attach()`. The inline write helper builds a two-byte buffer and delegates to the frontend `.write` op if present.

## State and Persistence Behavior
The config pointer is retained by the implementation; the init table and callbacks must remain valid for the frontend lifetime. The header itself has no persistent runtime state.

## Dependencies and Integration Points
It depends on DVB frontend headers. The `set_symbol_rate` callback is a required board/chip-family integration point because symbol-rate register details vary by board support code.

## Risks and Edge Cases
`skip_reinit` is declared but unused by the implementation. `inittab` has no explicit length and must be `0xff, 0xff` terminated. `stv0299_writereg()` silently returns success when `.write` is absent.

## Test Signals
Compile both Kconfig paths. Board-level tests should verify callback presence, valid init table termination, voltage output policy, and inline register write delegation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv0299.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv0367.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv0367.c

## Purpose
`stv0367.c` implements a multi-mode STV0367 demodulator driver for DVB-T, DVB-C Annex A, and Digital Devices hybrid DVB-C/T hardware. It provides 16-bit register I2C access, register-bitfield helpers, default table loading, PLL setup, transport-stream mode setup, terrestrial OFDM acquisition, cable QAM acquisition, metrics, and three exported attach paths.

## Important APIs, Types, and Functions
- State types: `struct stv0367_state` owns the embedded frontend, I2C/config, chip ID, mode flags, active demod selector, and pointers to `stv0367ter_state`/`stv0367cab_state`; mode-specific structs hold acquisition state, clocks, cached counters, bandwidth, inversion, and lock results.
- Exported attach APIs: `stv0367ter_attach()`, `stv0367cab_attach()`, and `stv0367ddb_attach()`.
- Core register helpers: `stv0367_writereg()`, `stv0367_readreg()`, `extract_mask_pos()`, `stv0367_writebits()`, `stv0367_setbits()`, `stv0367_readbits()`, `stv0367_write_table()`, and `stv0367_pll_setup()`.
- Shared helpers: `stv0367_get_if_khz()`, `stv0367_get_tuner_freq()`, `stv0367_get_tune_settings()`, and `stv0367_release()`.
- DVB-T path: gate control, IIR coefficient setup, AGC reset/lock detection, `stv0367ter_lock_algo()`, TS/clock mode setup, standby/init, `stv0367ter_algo()`, set/get frontend, read status/BER/SNR/UCB.
- DVB-C path: gate control, MCLK/ADC clock reads, QAM-specific register setup, derotator and symbol-rate programming/readback, FSM-to-signal mapping, standby/init, `stv0367cab_algo()`, set/get frontend, RF level/strength, SNR, and UCB.
- DDB hybrid path: `stv0367ddb_setup_ter()`, `stv0367ddb_setup_cab()`, mode-dispatching set/get/status/sleep, DVBv5 stat population, and `stv0367ddb_init()`.

## Control Flow
The generic terrestrial and cable attach paths allocate only the relevant mode state, read chip ID `0x50`/`0x60`, choose generic default tables, and return a frontend with mode-specific ops. Their `.set_frontend` methods optionally reinitialize on each tune, gate the tuner I2C bus, call tuner `.set_params`, then run the mode acquisition algorithm.

For DVB-T, `.set_frontend` maps DVB properties to internal bandwidth/mode/guard/sense, then tries one or two spectrum senses for auto inversion. `stv0367ter_algo()` programs IF/IQ mode, AGC/IIR coefficients for bandwidth, hierarchy, nominal timing and derotator increments, resets counters, calls `stv0367ter_lock_algo()`, records mode/guard/AGC, applies carrier and timing offset corrections, and restarts the core if final lock drops.

For DVB-C, `.set_frontend` maps QAM modulation, reinitializes if configured, programs tuner, applies QAM-specific equalizer/FSM settings, writes symbol-rate/derotator values, and launches `stv0367cab_algo()`. The cable algorithm computes acquisition timeouts from symbol rate/modulation/search range, holds TRL reset until AGC setup is ready, disables sweep/modulus mapping, polls QAM FSM states until demod lock, then polls FEC lock and caches symbol rate/spectrum inversion/lock status.

The DDB attach path allocates both mode states, uses DDB default tables, disables external I2C gate control, enables automatic IF query from tuner ops, initializes both register banks, and dispatches operations based on `dtv_property_cache.delivery_system`.

## State and Persistence Behavior
Driver state is memory-resident and freed in `stv0367_release()`. Hardware registers are reset from static default tables during init or reinit. DVB-T state persists previous bandwidth (`pBW`) to avoid unnecessary IIR reloads, previous BER/UCB values, first-lock sense, AGC value, and acquisition mode/guard. DVB-C state persists MCLK/ADC clock, search range, derot offset, lock state, found symbol rate, spectrum inversion, and which status bit indicates QAM/FEC lock. DDB state persists `activedemod` to avoid redundant OFDM/QAM setup and to route metric reads.

## Dependencies and Integration Points
The file depends on kernel I2C, module, slab/string, `linux/int_log.h`, DVB frontend core, `stv0367.h`, `stv0367_defs.h`, `stv0367_regs.h`, and `stv0367_priv.h`. It integrates with board tuners via `.tuner_ops.set_params`, `.get_frequency`, and optionally `.get_if_frequency`. Transport stream output mode and clock polarity come from `struct stv0367_config`.

## Risks and Edge Cases
- Many register writes are unchecked; I2C failures can leave partial hardware programming while higher layers still see success.
- DVB-C `stv0367cab_algo()` divides by `p->symbol_rate`; the DDB dispatcher guards zero symbol rate, but the generic cable path does not.
- Acquisition routines often return 0 even when no lock was obtained, relying on later `read_status`.
- `stv0367_get_tuner_freq()` returns a `u32` but uses negative `-1`/errno-style values; callers sometimes cast/check in ways that can be confusing.
- DDB mode switching shares one chip between OFDM and QAM register banks; incorrect `activedemod` or partial setup can misroute metrics.
- Some capability flags include raw `0x400` for QAM4 rather than a named macro, increasing maintenance risk.

## Test Signals
Key tests are hardware and integration tests: attach ID detection for all three paths, DVB-T 6/7/8 MHz tuning with auto and fixed inversion, DVB-C QAM16/32/64/128/256 with low/high symbol rates, DDB delivery-system switching, tuner gate and IF-frequency interactions, and read_status/stat population. Fault injection should exercise I2C errors, zero symbol rate on generic cable set_frontend, and missing tuner callbacks. Static checks should cover unchecked writes, unsigned negative returns, and table bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv0367.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv0367.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv0367.h

## Purpose
`stv0367.h` declares the public configuration and attach APIs for the STV0367 DVB-T/DVB-C demodulator driver.

## Important APIs, Types, and Functions
- Clock constants: `STV0367_ICSPEED_53125` and `STV0367_ICSPEED_58000`.
- `struct stv0367_config` carries demod I2C address, crystal frequency, IF frequency in kHz, IF/IQ mode, transport-stream mode, and clock polarity.
- Attach APIs: `stv0367ter_attach()`, `stv0367cab_attach()`, and `stv0367ddb_attach()`, each Kconfig-gated with disabled-driver stubs.

## Control Flow
Board drivers select the appropriate attach function for terrestrial-only, cable-only, or DDB hybrid operation. The header's only runtime path is the disabled-driver stub logging when `CONFIG_DVB_STV0367` is unreachable.

## State and Persistence Behavior
The implementation stores a pointer to this config, so config storage must outlive the frontend. No persistent state is held in the header.

## Dependencies and Integration Points
It depends on DVB frontend headers. The config values drive PLL setup, IF derotator math, I2C demod addressing, and TS output configuration in `stv0367.c`.

## Risks and Edge Cases
The config fields `if_iq_mode`, `ts_mode`, and `clk_pol` are plain `int` rather than typed enums, so invalid board data reaches runtime switch statements. Disabled stubs use `printk`.

## Test Signals
Compile all Kconfig paths and board configurations for each attach variant. Runtime tests should verify that each enum-like config field maps to the intended register programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv0367.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv0367_defs.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv0367_defs.h

## Purpose
`stv0367_defs.h` is the static register-default database for the STV0367 driver. It defines the table format, table selectors, generic terrestrial/cable defaults, Digital Devices OFDM/QAM/base defaults, and the combined `stv0367_deftabs` lookup used by `stv0367.c`.

## Important APIs, Types, and Functions
- Table selectors: `STV0367_DEFTAB_GENERIC`, `STV0367_DEFTAB_DDB`, `STV0367_TAB_TER`, `STV0367_TAB_CAB`, `STV0367_TAB_BASE`, and max constants.
- `struct st_register` pairs a 16-bit register address with an 8-bit value.
- Default arrays: `def0367ter[]`, `def0367cab[]`, `def0367dd_ofdm[]`, `def0367dd_qam[]`, and `def0367dd_base[]`.
- `stv0367_deftabs[STV0367_DEFTAB_MAX][STV0367_TAB_MAX]` maps a default-table family and mode to the relevant register array; generic base is `NULL`, DDB base is present.

## Control Flow
This header has no executable logic beyond static data initialization. `stv0367_write_table()` in `stv0367.c` walks a selected array until it reaches `{0x0000, 0x00}` and writes each register/value pair over I2C.

## State and Persistence Behavior
The arrays are compile-time constants. They define the reset/programming baseline that hardware receives during init/reinit. No runtime mutation occurs.

## Dependencies and Integration Points
The header depends on `stv0367_regs.h` for `R367TER_*` and `R367CAB_*` addresses. It is directly included by `stv0367.c`, not a standalone public API. Values encode board-family assumptions such as generic xc5000-related comments and Digital Devices Cine/Flex settings.

## Risks and Edge Cases
- Table termination relies on register address `0x0000` as sentinel; a real need to write address zero would be impossible through this format.
- The header contains large static arrays, so including it outside one C file would duplicate data.
- Register defaults are hardware- and board-sensitive; incorrect table selection can break clocking, ADC, AGC, TS output, or acquisition.
- `stv0367_deftabs` permits `NULL` base table for generic mode, so callers must check before writing base tables; DDB init does this.

## Test Signals
Validation should compare default tables against known-good register dumps for generic and DDB boards. Init tests should verify sentinel termination, table selection, no out-of-bounds table indices, and expected writes for terrestrial, cable, and base setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv0367_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv0367_priv.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv0367_priv.h

## Purpose
`stv0367_priv.h` provides private macros, byte helpers, and internal enums/structs shared by `stv0367.c` for terrestrial and cable acquisition state classification.

## Important APIs, Types, and Functions
- Boolean and utility macros: `TRUE`, `FALSE`, `NULL`, `MAX`, `MIN`, `INRANGE`, `MAKEWORD`, `LSB`, `MSB`, and `MMSB`.
- Terrestrial enums: `stv0367_ter_signal_type`, `stv0367_ts_mode`, `stv0367_clk_pol`, `stv0367_ter_bw`, `stv0367_ter_mode`, `stv0367_ter_hierarchy`, `stv0367_ter_if_iq_mode`, and `stv0367_ter_force`.
- Cable enums: `stv0367cab_mod` and `stv0367_cab_signal_type`.
- `struct stv0367_cab_signal_info` describes lock, frequency, symbol rate, modulation, inversion, RF power, C/N, and BER fields for cable monitoring-style data.

## Control Flow
The header has no runtime control flow. Its enum values are used by `stv0367.c` switch statements, status mapping, and config interpretation.

## State and Persistence Behavior
No state is stored here. The enums define values persisted in `stv0367ter_state` and `stv0367cab_state` during frontend lifetime.

## Dependencies and Integration Points
This is a private header for the STV0367 implementation. Public board configuration in `stv0367.h` uses integer fields that are expected to correspond to `stv0367_ts_mode`, `stv0367_clk_pol`, and `stv0367_ter_if_iq_mode` values defined here.

## Risks and Edge Cases
The header redefines `NULL` if not already defined and defines `MAX` only inside `#ifndef MIN`, which can produce surprising macro availability depending on prior includes. Several historical enums are inside `#if 0`, so maintainers must avoid relying on commented-out types. Public config fields are not strongly typed to these enums.

## Test Signals
Compile-time coverage should catch macro conflicts with kernel headers. Runtime validation should exercise all enum-backed config values and acquisition result mappings, especially cable FSM state to `FE_HAS_*` status conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv0367_priv.h -->
