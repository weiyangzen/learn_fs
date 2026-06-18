# subset-b-004057 Research

Grouped research for DVB frontend tuner and demodulator driver files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_top.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_top.c

## Purpose
Implements the top-level Linux DVB frontend glue for the Sony CXD2880 SPI-connected DVB-T/DVB-T2 tuner-demodulator. The file adapts DVB core operations to Sony's lower-level `cxd2880_tnrdmd_*`, monitor, integration, SPI-device, and SPI-I/O helper layers. It owns frontend registration, chip identification, power/init/sleep transitions, tuning, status polling, frontend property readback, signal metrics, BER/PER measurement-window setup, and cumulative DVB statistics.

## Important APIs, Types, And Functions
The private state is `struct cxd2880_priv`, which embeds the Sony `struct cxd2880_tnrdmd`, SPI I/O objects, DVB-T and DVB-T2 tune parameter caches, a shared `spi_mutex`, jiffies-based statistic update deadlines/intervals, and the last lock status. `cxd2880_attach()` allocates this state, installs `cxd2880_dvbt_t2_ops` into the caller-provided `dvb_frontend`, initializes SPI wrappers at 55 MHz, reads the chip ID from system bank register `0xfd`, accepts only CXD2880 ES1.0x/ES1.11 IDs, and stores the private pointer in `fe->demodulator_priv`.

Core frontend callbacks are `cxd2880_init()`, `cxd2880_sleep()`, `cxd2880_tune()`, `cxd2880_set_frontend()`, `cxd2880_get_frontend()`, `cxd2880_read_status()`, `cxd2880_read_signal_strength()`, `cxd2880_read_snr()`, `cxd2880_read_ucblocks()`, and `cxd2880_release()`. DVB-T/T2 tuning is split through `cxd2880_dvbt_tune()` and `cxd2880_dvbt2_tune()`, which validate state/bandwidth/profile, call Sony tune phase 1, wait for AGC stabilization, then call tune phase 2. The statistic helpers read raw pre-BER, post-BER, and block error counters for DVB-T and DVB-T2 from demodulator register banks, using `slvt_freeze_reg()` when snapshots span multiple registers.

## Control Flow
Attach-time flow wires the frontend ops and verifies hardware before the DVB adapter exposes the frontend. Init-time flow creates the Sony tuner-demod object if needed, calls `cxd2880_integ_init()`, then sets TS pin current config while holding `spi_mutex`. Tuning starts from DVB property-cache values: `bandwidth_hz` is translated to Sony bandwidth enums, `delivery_system` selects DVB-T or DVB-T2, frequency is converted to kHz, stream ID becomes the DVB-T2 PLP ID, and all statistic counters are reset to `FE_SCALE_NOT_AVAILABLE` before tune.

Status polling checks Sony sync/lock monitors only when the internal tuner-demod state is active. Sync value 6 yields signal/carrier, and the lock bit adds Viterbi/sync/lock. On the first carrier+lock, DVB-T configures BER/PER periods from TPS information, while DVB-T2 first verifies L1-post/data-PLP validity and then computes periods from L1-pre, L1-post, active PLP, and BB header data. `cxd2880_get_stats()` is then called from `read_status()` and updates DVB counter stats only when enough jiffies have elapsed for each measurement period.

## State And Persistence
Persistent driver state is per-frontend heap allocation plus hardware-visible demodulator state. The tune parameter structs preserve the last tuned frequency, bandwidth, profile, PLP ID, and tune-result metadata. The jiffies fields rate-limit register polling and accumulate DVB statistic counters in the frontend property cache. SPI access is serialized with the externally supplied mutex, so this file assumes the board/SPI parent owns mutex lifetime and shares it with any sibling access path.

## Dependencies And Integration Points
The file depends on Linux DVB frontend APIs, SPI device access, `linux/int_log.h` for measurement-window exponent selection, and CXD2880-specific headers for monitor, integration, tune, SPI, and driver-version helpers. Integration points are the SPI parent driver that calls `cxd2880_attach()`, supplies `struct cxd2880_config`, and registers the returned DVB frontend; DVB userspace tools then interact through normal FE_SET_PROPERTY/FE_READ_STATUS/statistics ioctls. The advertised capabilities cover DVB-T and DVB-T2 across 174-862 MHz with 1 kHz steps and common FEC/QAM/guard/transmission-mode auto support.

## Risks
Register-bank selection and freeze/unfreeze discipline are central: missing an unfreeze on a new error path or reading counters without a coherent snapshot would corrupt metrics or block later monitor reads. BER/PER period math depends on monitored TPS/L1/PLP values and several lookup tables; invalid or zero rates can produce misleading intervals. `cxd2880_post_bit_err_t()` initializes `bit_error` to zero and compares that variable instead of the just-read `*post_bit_err`, so the intended sanity check is ineffective. `cxd2880_attach()` declares its local private pointer as `static`, which is unnecessary and could race under concurrent attaches even though the pointer is copied into each frontend. Hardware access assumes `cfg`, `cfg->spi`, and `cfg->spi_mutex` are valid, but only `fe` is checked. DVB-T2 uses `stream_id` directly as a PLP ID and always selects base profile in `set_frontend()`, so profile-lite or invalid PLP cases rely on later L1-post checks.

## Test Signals
Useful static signals are a successful build with the CXD2880 driver enabled and sparse/smatch coverage over register error paths. Runtime smoke tests should show attach success, correct chip-ID detection, `init`/`sleep` without SPI failures, and successful DVB-T and DVB-T2 locks across 5/6/7/8 MHz, plus 1.7 MHz for DVB-T2. Statistics tests should watch `pre_bit_error`, `post_bit_error`, `block_error`, RF strength, CNR, and uncorrected blocks transition from unavailable to counters only after lock and continue increasing at plausible intervals. PLP tests should include valid and invalid DVB-T2 PLP IDs and verify no deadlock or stale stats after retune.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_top.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dib0070.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dib0070.c

## Purpose
Implements the DiBcom DiB0070 base-band RF tuner driver for the DVB frontend subsystem. It provides I2C register access, board reset/sleep control, revision detection, default register programming, wide-band detector offset calibration, RF/LO tuning, captrim search, LNA matching, bandwidth/filter setup, and exported helper hooks for demodulator drivers that need AGC filter or RF-output control.

## Important APIs, Types, And Functions
`struct dib0070_state` stores the I2C adapter, owning frontend, board config, revision, current RF frequency, tune-state machine variables, captrim search values, selected tuning/LNA table entries, WBD gain/offset data, reusable `i2c_msg` arrays, fixed-size I2C buffers, and `i2c_buffer_lock`. `dib0070_read_reg()` and `dib0070_write_reg()` serialize two-byte register reads and three-byte writes with that mutex.

Public entry points are `dib0070_attach()`, `dib0070_wbd_offset()`, `dib0070_ctrl_agc_filter()`, `dib0070_get_rf_output()`, and `dib0070_set_rf_output()`. DVB tuner ops are installed from `dib0070_ops`, with `.init`, `.sleep`, `.set_params`, `.get_frequency`, and `.release`. The frequency-dependent behavior is driven by `struct dib0070_tuning` and `struct dib0070_lna_match` tables for normal, S-band, and flip-chip variants.

## Control Flow
Attach allocates state, initializes the I2C mutex, temporarily stores it in `fe->tuner_priv`, and calls `dib0070_reset()`. Reset toggles board sleep/reset callbacks, reads revision registers, rejects P1D, writes default register batches from `dib0070_p1f_defaults`, configures crystal mode and clock pad drive, optionally inverts IQ, sets LO5 control according to revision/config, and measures WBD offsets for gains 6 and 7.

Tuning begins in `dib0070_tune()`, which sets `CT_TUNER_START` and repeatedly calls `dib0070_tune_digital()` with sleeps derived from the returned 0.1 ms delay value. The tune state machine adjusts requested frequency for VHF/UHF offsets and ISDB-T segment cases, selects tuning and LNA rows, calculates reference divider, feedback divider, fractional remainder, sigma-delta denominator, and LO register values, writes PLL/tuner enable registers, then runs `dib0070_captrim()` as a binary search around ADC target 400. Final steps program WBD gain/mux, RF switch/LNA registers, AGC/filter registers, and baseband bandwidth selection.

## State And Persistence
The driver keeps only volatile per-tuner state. `current_rf` avoids repeating full PLL programming when retuning to the same kHz value. WBD offsets calibrated at reset are cached in `wbd_offset_3_3[]` and reused by `dib0070_wbd_offset()`. The current tune and LNA table pointers persist across the staged tune loop, and `tune_state` encodes progress through the tuner state machine. Hardware persists register state until reset/sleep/power loss.

## Dependencies And Integration Points
The source depends on Linux I2C, mutex, slab, DVB frontend APIs, `dib0070.h`, and common DiB frequency-band helpers from `dibx000_common.h`. Board integration comes through `struct dib0070_config`: I2C address, reset/sleep GPIO callbacks, crystal clock, offsets, IQ inversion, flip-chip flag, charge pump/filter settings, WBD-gain table, and optional VGA filter value. It integrates with demodulator drivers by filling `fe->ops.tuner_ops` and by exporting AGC/WBD/RF-output helpers.

## Risks
The tune sequence is register-order and delay sensitive; shorter waits or reordered captrim/WBD steps can make PLL or baseband calibration fail intermittently. Revision detection is forced to `DIB0070S_P1A` through the current `#else` path after reading revision logic, so behavior differs from what the surrounding comments imply. Several I2C errors are logged but converted to zero-valued register reads, which can hide hardware faults during identification or tuning. `dib0070_set_rf_output()` masks into a `u16` with a wide constant and clamps output to 1-3, so callers cannot select 0 even if a board expected it. Config callbacks are assumed valid in `HARD_RESET()` for sleep, and `cfg` itself is not deeply validated.

## Test Signals
Static signals include building with `CONFIG_DVB_TUNER_DIB0070` and checking exported symbol users compile against `dib0070.h`. Runtime tests should verify attach/reset on known hardware, I2C register read/write success, WBD calibration values for both gains, successful tuning across VHF/UHF/L-band/S-band table boundaries, ISDB-T segment-offset behavior if enabled, and correct reported frequency from `get_frequency`. RF-output and AGC filter helpers should be tested by demodulator integrations that depend on them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dib0070.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dib0070.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dib0070.h

## Purpose
Declares the public interface and board configuration contract for the DiB0070 RF tuner driver. It allows demodulator or bridge drivers to attach the tuner, provide board-specific reset/sleep/clock/WBD parameters, and call exported helper functions when the tuner is enabled in Kconfig.

## Important APIs, Types, And Functions
`DEFAULT_DIB0070_I2C_ADDRESS` is `0x60`. `struct dib0070_wbd_gain_cfg` maps frequency ranges to WBD gain values. `struct dib0070_config` carries the I2C address, reset and sleep callbacks, VHF/UHF frequency offsets, oscillator buffer and crystal/clock configuration, clock pad drive strength, IQ inversion, crystal-mode override, flip-chip flag, third-order-filter and charge-pump controls, WBD gain table pointer, and optional VGA filter register value.

When `CONFIG_DVB_TUNER_DIB0070` is reachable, the header declares `dib0070_attach()`, `dib0070_wbd_offset()`, `dib0070_ctrl_agc_filter()`, `dib0070_get_rf_output()`, and `dib0070_set_rf_output()`. Otherwise it provides stubs that warn and return `NULL` or zero for the first three declared operations.

## Control Flow
Consumers fill `struct dib0070_config`, call `dib0070_attach(fe, i2c, cfg)`, and then use the frontend's tuner ops for normal init/sleep/tune calls. Helper APIs are called directly when the demodulator needs WBD offset or AGC/RF-output coordination.

## State And Persistence
The header owns no state. Its config struct is retained by the implementation as a pointer, so the caller must ensure the config object and callbacks remain valid for the tuner lifetime.

## Dependencies And Integration Points
The header forward-declares `struct dvb_frontend` and `struct i2c_adapter` and relies on kernel integer typedefs being available to includers. It integrates through Kconfig reachability so bridge drivers can compile even when the tuner module is disabled.

## Risks
The disabled-driver stub set omits `dib0070_get_rf_output()` and `dib0070_set_rf_output()`, despite declaring them in the enabled branch; callers of those helpers need Kconfig dependencies or may hit missing declarations/links in disabled configurations. Because the implementation stores a config pointer, stack-allocated configs are unsafe. Callback semantics are only documented by field names/comments, so board drivers must match the active-low/active-high expectations used by the implementation.

## Test Signals
Build representative bridge drivers with `CONFIG_DVB_TUNER_DIB0070=y`, `m`, and disabled to catch Kconfig/stub coverage. Runtime validation is indirect: attach should consume a stable config, and helper calls should operate only after successful attach.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dib0070.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dib0090.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dib0090.c

## Purpose
Implements the DiBcom DiB0090/Krosus RF tuner driver. It supports direct tuner control and a firmware-backed control variant, detects multiple silicon revisions and SoC-integrated variants, programs PLL and RF/baseband paths across CBAND/VHF/UHF/L-band/S-band tables, performs DC/WBD/temperature/captrim calibration, manages software and PWM AGC ramps, and exports helper APIs used by DiB demodulator integrations.

## Important APIs, Types, And Functions
`struct dib0090_state` is the main direct-control state: I2C adapter, frontend, config pointer, current band/RF/standard, tune state, WBD offset/target, RF gain limit/current gain, gain registers, ramp pointers, DC/captrim variables, selected tuning/PLL table entries, identity data, requested RF, calibration flags, temperature, WBD table state, reusable I2C messages/buffers, and an I2C mutex. `struct dib0090_fw_state` is a smaller firmware-control state that uses the I2C message address as the firmware register selector.

Important external APIs include `dib0090_register()`, `dib0090_fw_register()`, `dib0090_dcc_freq()`, `dib0090_pwm_gain_reset()`, `dib0090_gain_control()`, `dib0090_get_current_gain()`, `dib0090_get_wbd_target()`, `dib0090_get_wbd_offset()`, `dib0090_set_switch()`, `dib0090_set_vga()`, `dib0090_update_rframp_7090()`, `dib0090_update_tuning_table_7090()`, `dib0090_get_tune_state()`, and `dib0090_set_tune_state()`. The file contains many revision-specific ramp, PLL, tuning, WBD-slope, default-register, EFUSE, and DC calibration tables.

## Control Flow
Direct registration allocates state, selects the default or board-provided WBD table, stores state in `fe->tuner_priv`, resets digital hardware, identifies the tuner, writes default register batches, applies EFUSE-derived calibration values, configures crystal mode, marks DC/WBD/temperature calibration pending, and installs `dib0090_ops`. Firmware registration performs a smaller digital reset/identify flow and installs `dib0090_fw_ops`, which intentionally lacks normal tuning callbacks.

Normal tuning starts in `dib0090_set_params()` by setting `CT_TUNER_START` and repeatedly calling `dib0090_tune()` until `CT_TUNER_STOP`, sleeping with an enforced 10 ms granularity. `dib0090_tune()` first runs pending calibration state machines: DC offset calibration, WBD offset calibration, temperature measurement, then captrim search. Once calibrated, it computes the requested RF from DVB cache frequency plus band-specific offset and ISDB-T low-IF adjustments, selects tuning and PLL rows based on band, SoC/P1G identity, force-CBAND settings, and special CBAND module variants, computes VCO frequency, feedback divider, fractional remainder, LO5/LO6 settings, enables the proper RF path, performs captrim, writes final LNA/mixer/load/WBD registers, sets bandwidth, and schedules WBD/temperature recalibration for later.

AGC is separate. `dib0090_gain_control()` runs an AGC tune-state machine that reads WBD and demodulator ADC power, computes WBD and ADC error, updates RF gain limit and total gain through `dib0090_gain_apply()`, and writes gain registers only when values change. `dib0090_pwm_gain_reset()` configures PWM RF/BB ramps and muxing for hardware-assisted AGC, with special SoC and 7090/8090 ramp choices.

## State And Persistence
State is volatile but extensive. The driver caches identity, current RF/standard, current table entries, WBD calibration gain, temperature, calibration flags, gain split, and previous gain-register values to avoid unnecessary writes and to coordinate staged calibration across repeated callbacks. Hardware-visible state includes PLL divider registers, RF path enables, LNA/mixer/load values, baseband filter settings, WBD mux/gain, DC trim registers, AGC ramp tables, and sleep/reset-controlled power state.

## Dependencies And Integration Points
The file depends on Linux I2C, mutex, slab, DVB frontend APIs, `dib0090.h`, and `dibx000_common.h` band helpers. Board-specific behavior is provided through `struct dib0090_config`, including reset/sleep callbacks, PLL/clock configuration, ADC power callback, analog/PWM/SoC flags, low-IF offset table, WBD slopes, CBAND forcing, and pad/drive settings. Demodulators integrate either through tuner ops (`set_params`, `get_frequency`, sleep/init) or through exported AGC/WBD/tune-state helpers.

## Risks
This file is highly state-machine and timing sensitive; incorrect callback pacing, missed calibration flags, or wrong sleep granularity can produce intermittent tuner lock failures. Many register reads return zero after I2C failure, so identity, calibration, and AGC decisions can proceed on bad data. The direct and firmware state structs are different but both use `fe->tuner_priv`; exported direct-control helpers must not be called on a frontend registered through `dib0090_fw_register()`. The gain-control path requires `config->get_adc_power`; a missing callback would crash. Revision/band table selection is complex, so board config flags such as `in_soc`, `force_cband_input`, `is_dib7090e`, and `fref_clock_ratio` must match hardware exactly. Several compile-time feature macros are defined inside the C file, which can make behavior less obvious from Kconfig.

## Test Signals
Build tests should cover direct and firmware registration and exported helper users. Hardware tests need attach/identify for non-SoC, P1G, 7090, 8090, and firmware-backed paths where available; PLL lock across all supported band boundaries; DVB-T and ISDB-T low-IF offset cases; DC/WBD/temp/captrim calibration completion; PWM and software AGC convergence; and sleep/wakeup recovery. Useful live signals are stable `get_frequency()`, plausible WBD target/offset values, non-saturating RF/BB gain splits, and no I2C transfer warnings during retunes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dib0090.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dib0090.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dib0090.h

## Purpose
Declares the public configuration and helper API for the DiB0090 tuner driver. It lets bridge/demodulator drivers describe clocking, reset/sleep, IF offsets, WBD calibration, AGC mode, SoC variants, and optional board tables, then attach either the direct-control or firmware-control tuner path.

## Important APIs, Types, And Functions
`struct dib0090_io_config` describes reference clock, PLL bypass/range/predivider/loop divider, ADC clock ratio, and optional internal PLL loop filter. `struct dib0090_wbd_slope` and `struct dib0090_low_if_offset_table` provide frequency-dependent WBD and low-IF compensation data. `struct dib0090_config` carries callbacks, frequency offsets, ADC power callback, clock output and analog output flags, I2C address, WBD offsets, PWM AGC enable, pad drive settings, SoC and 7090e flags, force-CBAND/crystal settings, and WBD/low-IF table pointers.

When `CONFIG_DVB_TUNER_DIB0090` is reachable, the header declares direct and firmware registration plus helper functions for DCC frequency, PWM gain reset, WBD target/offset, gain control, tune-state access, current gain readback, DC servo, RF switches, VGA, and 7090-specific ramp/tuning-table updates. Disabled stubs warn and return safe failure values for most helpers.

## Control Flow
Consumers create a persistent `dib0090_config`, call `dib0090_register()` for normal control or `dib0090_fw_register()` for firmware-mediated control, then use installed tuner ops and optional helper calls. Some helpers are intended for periodic demodulator-driven loops, especially `dib0090_gain_control()`.

## State And Persistence
The header owns no state. The implementation keeps only a pointer to the supplied config, so config storage and callback targets must outlive the tuner.

## Dependencies And Integration Points
The header forward-declares DVB frontend and I2C adapter types and relies on `enum frontend_tune_state` being visible from the DVB frontend/common include environment. Kconfig reachability gates whether real functions or stubs are compiled into consumers.

## Risks
The disabled stub for `dib0090_fw_register()` takes a non-const config pointer while the enabled declaration takes `const struct dib0090_config *`, which can cause prototype mismatches in disabled builds. Helpers assume direct-control private state in the implementation; callers must avoid using direct helpers with firmware-registered frontends unless specifically safe. Config callbacks such as `get_adc_power` are mandatory for some runtime paths but not marked as such by the type system.

## Test Signals
Compile bridge drivers with the tuner enabled, modular, and disabled to catch prototype/stub issues. Runtime validation should cover both registration APIs and helper calls only after successful attach, with board configs stored in static or device-managed memory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dib0090.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dib3000.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dib3000.h

## Purpose
Provides the public interface for the older DiBcom 3000M-B DVB-T demodulator and shared transfer-control callbacks used by DiB USB/bridge integrations.

## Important APIs, Types, And Functions
`struct dib3000_config` contains the demodulator I2C address. `struct dib_fe_xfer_ops` is filled by the demodulator attach path with PID parsing, FIFO control, PID control, and tuner-pass-through callbacks, allowing the bridge to control MPEG transport filtering and tuner I2C access through the demodulator.

The reachable API is `dib3000mb_attach(const struct dib3000_config *config, struct i2c_adapter *i2c, struct dib_fe_xfer_ops *xfer_ops)`. If `CONFIG_DVB_DIB3000MB` is not reachable, a stub warns and returns `NULL`.

## Control Flow
Bridge drivers call `dib3000mb_attach()`, receive a newly allocated `dvb_frontend`, and use the populated `dib_fe_xfer_ops` for USB bandwidth management and tuner pass-through.

## State And Persistence
The header owns no state. The implementation copies `dib3000_config` into private state, while `dib_fe_xfer_ops` is caller-owned storage populated during attach.

## Dependencies And Integration Points
It includes `linux/dvb/frontend.h` for frontend types and Kconfig helpers. Integration is primarily with legacy DiB USB bridge drivers that need demodulator-managed PID/FIFO/tuner-gate functions.

## Risks
The API is narrow and legacy; callers must pass a valid, writable `xfer_ops` pointer because the implementation writes through it unconditionally. The header covers only the MB variant; MC/P devices use `dib3000mc.h`.

## Test Signals
Build with `CONFIG_DVB_DIB3000MB` enabled and disabled. Runtime attach should verify vendor/device IDs and populate all transfer callbacks before the bridge uses them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dib3000.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dib3000mb.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dib3000mb.c

## Purpose
Implements the DiBcom 3000M-B DVB-T COFDM demodulator frontend. It handles I2C register access, chip identification, frontend initialization, DVB-T parameter programming, optional autosearch, TPS readback, lock/statistic reads, sleep, PID filtering, FIFO control, and tuner I2C pass-through for legacy DiB bridge devices.

## Important APIs, Types, And Functions
The private `struct dib3000_state` is defined in `dib3000mb_priv.h` and stores the I2C adapter, copied config, frontend, timing state, and last tuned bandwidth/frequency fields. The C file's low-level accessors are `dib3000_read_reg()` and `dib3000_write_reg()`, wrapped by private-header macros such as `rd`, `wr`, and `wr_foreach()`.

The main frontend callbacks are `dib3000mb_fe_init_nonmobile()`, `dib3000mb_sleep()`, `dib3000mb_set_frontend_and_tuner()`, `dib3000mb_get_frontend()`, `dib3000mb_read_status()`, BER/strength/SNR/uncorrected-block readers, and `dib3000mb_release()`. `dib3000mb_attach()` verifies DiBcom vendor ID `0x01b3` and device ID `0x3000`, copies `dib3000mb_ops`, and fills `struct dib_fe_xfer_ops` with PID/FIFO/tuner-pass callbacks.

## Control Flow
Initialization powers up the demodulator, resets hardware, programs clock/electrical output, default DDS/timing/bandwidth values, impulse noise, AGC, phase-noise, lock masks, filter coefficients, mobile/multi-demod values, output/FIFO/MPEG2/PID defaults, and disables diversity input. Set-frontend first lets the tuner tune through `fe->ops.tuner_ops.set_params`, closes the I2C gate if present, programs bandwidth-specific timing/filter tables, then translates DVB property-cache transmission mode, guard, inversion, modulation, hierarchy, and FEC into demodulator registers.

For auto parameters, the driver computes an autosearch sequence index from auto FFT/guard/inversion flags, inhibits ISI, restarts autosearch, polls IRQ/lock status up to 100 ms, reads TPS values with `dib3000mb_get_frontend()` on success, and recursively reprograms without tuner retune. Otherwise it restarts the control path directly. Status and metrics read dedicated monitoring registers and translate lock bits into `FE_HAS_*` flags.

## State And Persistence
Most persistent behavior is in hardware registers. Driver heap state persists the config, frontend, I2C pointer, and unused/legacy timing fields. PID filter state is written into hardware PID registers beginning at `DIB3000MB_REG_FIRST_PID`; FIFO and PID parser state persist in the demodulator until changed. The implementation does not serialize I2C access with a local mutex.

## Dependencies And Integration Points
The file depends on Linux module/delay/slab APIs, DVB frontend APIs, `dib3000.h`, and the private register-map header. It integrates with an external tuner through frontend tuner ops and I2C gate control, and with bridge drivers through the `dib_fe_xfer_ops` callbacks for PID filtering, FIFO control, and tuner pass-through. It exports only `dib3000mb_attach()`.

## Risks
The driver relies heavily on magic register constants and batch tables; wrong values can silently degrade lock or transport output. I2C read failures return zero after debug logging, which can be confused with valid lock/status values. Recursive reprogramming after autosearch can re-enter large parts of set-frontend and needs the property cache to be coherent. The mapping for `DIB3000_FEC_5_6` in `get_frontend()` assigns `FEC_4_5`, which appears inconsistent with the debug text and other mappings. `xfer_ops` is written without a null check, and no local locking protects concurrent frontend callbacks.

## Test Signals
Build with `CONFIG_DVB_DIB3000MB` and exercise attach ID checks. Runtime tests should cover init, sleep, 6/7/8 MHz tuning, all-auto and fixed DVB-T parameters, TPS readback after autosearch, lock-bit progression, BER/strength/SNR/uncorrected-block reads, PID filter enable/disable, FIFO enable/disable, and tuner pass-through register behavior on bridge hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dib3000mb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dib3000mb_priv.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dib3000mb_priv.h

## Purpose
Provides the private register map, helper macros, default tables, and private state definition used by `dib3000mb.c`. It is the hardware-description companion for the DiB3000M-B demodulator implementation.

## Important APIs, Types, And Data
The header defines I2C helper macros `rd`, `wr`, `wr_foreach`, `set_or`, and `set_and`, debug macro `dprintk`, DVB-T numeric constants, tuner-write enable/disable encodings, vendor/device IDs, and `struct dib3000_state`. The state contains the I2C adapter, copied `dib3000_config`, `dvb_frontend`, timing-offset fields, and last tuned bandwidth/frequency.

Most of the file is register and table data: restart/control registers, FFT/guard/QAM/FEC/hierarchy fields, DDS/timing registers, bandwidth tables for 6/7/8 MHz, impulse-noise values, AGC gains/bandwidths, phase-noise values, lock masks, mobile/diversity/output/FIFO/PID parser registers, filter coefficients, power/clock/electrical-output registers, tuner pass-through register, and monitoring/TPS/BER/PER/lock/IRQ registers.

## Control Flow
The macros are expanded throughout `dib3000mb.c`. `wr()` returns `-EREMOTEIO` from the caller on failed writes, which shapes error handling in initialization and tuning. `wr_foreach()` writes register/value arrays in order and logs if array sizes differ.

## State And Persistence
The header's state struct is embedded in the implementation's heap allocation. Static tables live for module lifetime and are read-only in normal operation, although they are not declared `const`. Hardware persistence is represented by the register constants and values programmed by the C file.

## Dependencies And Integration Points
It depends on `dib3000.h` definitions, `struct i2c_adapter`, `struct dvb_frontend`, and the implementation-provided `debug`, `dib3000_read_reg()`, and `dib3000_write_reg()` symbols/macros. It is private to the MB implementation and should not be included by other drivers.

## Risks
Because this header defines non-const static arrays, including it in more than one C file would create duplicate mutable table copies. The `wr` macro contains control flow that returns from the containing function, so it is easy to misuse in contexts that need cleanup. Register names with `UNK` values document uncertainty; changing them without hardware validation is risky. `wr_foreach()` only logs size mismatch and then iterates over the register array length, so mismatched tables can still perform out-of-bounds reads of the value array.

## Test Signals
Compilation of `dib3000mb.c` is the main static test. Runtime signals are successful default initialization table writes, correct bandwidth table selection, valid monitoring register reads, and no `wr()` error returns during tune/init paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dib3000mb_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dib3000mc.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dib3000mc.c

## Purpose
Implements the DiBcom DiB3000MC/P DVB-T COFDM demodulator frontend. It supports identification of 3000MC and 3000P devices, board-configured AGC/PWM setup, bandwidth/timing programming, output-mode control, autosearch, final tune, status/statistic reads, PID parsing/filtering helpers, tuner I2C master access, and multi-demodulator I2C address enumeration.

## Important APIs, Types, And Functions
`struct dib3000mc_state` embeds a `dvb_frontend`, points to `struct dib3000mc_config`, stores 8-bit wire I2C address, adapter, `dibx000_i2c_master`, timing frequency cache, current bandwidth, device ID, and SFN workaround flag. Register access is through `dib3000mc_read_word()` and `dib3000mc_write_word()`, which allocate a 4-byte buffer per transfer.

Public/exported APIs are `dib3000mc_attach()`, `dib3000mc_i2c_enumeration()`, `dib3000mc_get_tuner_i2c_master()`, `dib3000mc_pid_control()`, `dib3000mc_pid_parse()`, and `dib3000mc_set_config()`. Frontend ops cover init, sleep, set/get frontend, tune settings, status, BER, signal strength, SNR placeholder, uncorrected blocks, and release.

## Control Flow
Attach allocates state, stores config/I2C/address, copies ops, verifies vendor ID `0x01b3` and device ID `0x3001` or `0x3002`, initializes a `dibx000_i2c_master` for tuner access, writes a clock config register, and returns the embedded frontend. Init performs a demod restart, power/mobility setup, clock setup, phase-noise and AGC programming from `cfg->agc`, timing/lock/search/default bandwidth setup, spurious/FEC/diversity/impulse-noise/output setup, and closes the tuner I2C gate.

Set-frontend disables output, records bandwidth, applies bandwidth tables, enables the optional SFN workaround, lets the tuner tune, performs autosearch when transmission/guard/modulation/FEC are auto, reads back TPS on success, and then calls `dib3000mc_tune()`. The final tune path programs channel config, optional SFN registers, adaptive config based on modulation, 2K/8K timing coefficients, timing-offset correction if indicated by lock register bit `0x80`, and then enables MPEG2 FIFO output. Status maps bits from register 509 to DVB lock flags.

## State And Persistence
Driver state persists the current bandwidth, cached timing frequency `timf`, selected config pointer, device ID, and SFN workaround state. `dib3000mc_set_config()` can replace the config pointer after attach, so config lifetime and synchronization are caller responsibilities. Hardware state persists output mode, PID parser/filter registers, I2C gate/master behavior, AGC/PWM settings, timing, and demodulator lock state.

## Dependencies And Integration Points
The file depends on Linux I2C/slab/kernel APIs, DVB frontend APIs, `dib3000mc.h`, and `dibx000_common.h` through the header. Board integration is via `struct dib3000mc_config`, especially AGC config, phase/impulse noise modes, PWM3 settings, max-time/ADC levels, AGC command bits, mobile mode, and MPEG2 packet-size preference. It integrates with tuners through `dib3000mc_get_tuner_i2c_master()` and with bridges through PID parser/control exports.

## Risks
I2C read/write allocate memory on every transfer, so memory pressure can turn reads into zero and writes into `-ENOMEM`; many callers do not propagate read failures distinctly. The config pointer is not copied and may be replaced at runtime, so dangling or concurrently changed configs can corrupt register programming. Several channel-config expressions appear hardcoded or suspicious, such as `switch (HIERARCHY_1)` and `(ch->hierarchy == 0 || 1 == 1)`, meaning hierarchy handling is effectively fixed. Autosearch returns success/failure by register polling but a not-found path returns 0 rather than an error. The module parameter `buggy_sfn_workaround` affects global behavior for all instances.

## Test Signals
Build with `CONFIG_DVB_DIB3000MC`. Runtime tests should cover attach to both MC and P IDs, I2C enumeration of multi-demod boards, init/sleep, tuner I2C master gated and ungated access, fixed and auto DVB-T tuning, 5/6/7/8 MHz bandwidths, SFN workaround on/off, output modes, PID parser/filter writes, and status/BER/uncorrected/strength reads after lock. Memory-failure or fault-injection tests around I2C buffer allocation would expose weak error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dib3000mc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dib3000mc.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dib3000mc.h

## Purpose
Declares the board configuration and public API for the DiBcom DiB3000MC/P demodulator driver.

## Important APIs, Types, And Functions
`struct dib3000mc_config` provides AGC configuration, phase and impulse noise modes, PWM3 inversion/use/value, max timing and low-noise ADC levels, AGC command bits, mobile-mode flag, and MPEG2 188-byte output preference. Default I2C addresses are `DEFAULT_DIB3000MC_I2C_ADDRESS` 16 and `DEFAULT_DIB3000P_I2C_ADDRESS` 24.

When `CONFIG_DVB_DIB3000MC` is reachable, the header declares `dib3000mc_attach()`, `dib3000mc_i2c_enumeration()`, and `dib3000mc_get_tuner_i2c_master()`. Disabled stubs warn and return `NULL` or `-ENODEV`. Regardless of Kconfig block, it declares exported helpers `dib3000mc_pid_control()`, `dib3000mc_pid_parse()`, and `dib3000mc_set_config()`.

## Control Flow
Bridge drivers call enumeration for multi-demod address assignment when needed, call attach for each demodulator, then use the returned frontend and optional tuner I2C master. PID helper calls control demodulator-side TS filtering.

## State And Persistence
The header owns no state. The implementation stores a pointer to the config rather than copying it, so the config and nested `agc` object must persist for the frontend lifetime unless intentionally replaced through `dib3000mc_set_config()`.

## Dependencies And Integration Points
It includes `dibx000_common.h` for AGC config and I2C master interfaces. Integration is with DiB bridge drivers, tuner drivers behind the demodulator I2C gate, and DVB frontend registration.

## Risks
The PID helper declarations remain visible even when the main driver is disabled; callers need proper Kconfig/link dependencies. Bitfield config values are compact but not self-validating, so invalid board data can program nonsensical AGC/PWM registers. The config pointer lifetime contract is implicit.

## Test Signals
Compile users with the demodulator enabled and disabled. Runtime validation should confirm default address handling, enumeration address reassignment, stable config storage, and availability of the tuner I2C master after attach.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dib3000mc.h -->
