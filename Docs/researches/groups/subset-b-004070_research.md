# subset-b-004070 research

This grouped report covers Linux DVB frontend demodulator and satellite LNB supply helpers under `sources/distributed-fs/ceph-client/drivers/media/dvb-frontends`. Each section preserves the original source path so the reconciliation lane can split it into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lgdt3306a.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lgdt3306a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lgdt3306a.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lgdt3306a.h

## Purpose
`lgdt3306a.h` is the public board-driver interface for the LGDT3306A ATSC/QAM demodulator. It describes transport-stream output options, IF frequencies, I2C repeater policy, crystal selection, and the attach API.

## Important APIs, Types, and Functions
The header defines `enum lgdt3306a_mpeg_mode`, `enum lgdt3306a_tp_clock_edge`, and `enum lgdt3306a_tp_valid_polarity`. `struct lgdt3306a_config` carries the demod I2C address, QAM/VSB IF frequencies in kHz, repeater-deny and spectral-inversion flags, MPEG/TS polarity settings, supported `xtalMHz` values, and output pointers for the created frontend and muxed tuner adapter. `lgdt3306a_attach()` is declared when `CONFIG_DVB_LGDT3306A` is reachable and replaced with a warning stub otherwise.

## Control Flow
Legacy callers fill this config and call `lgdt3306a_attach()`. I2C-client users provide the same structure as platform data; probe copies it, fills `i2c_addr` from the client, and writes back `fe` and `i2c_adapter` after mux creation.

## State and Persistence
The header itself owns no state. Its config fields determine volatile demodulator register programming at init and tune time, especially IF/NCO setup, TS bus shape, and I2C repeater behavior.

## Dependencies and Integration Points
It depends on `<linux/i2c.h>` and `<media/dvb_frontend.h>`. Integration is with board/card drivers that instantiate the demodulator and downstream tuner on a possibly muxed I2C bus.

## Risks and Edge Cases
Only 24 MHz and 25 MHz crystals are handled by the implementation. The `spectral_inversion` bit is present but the C file mostly applies modulation-specific defaults, so callers should verify board behavior rather than assuming the field fully controls inversion. The `fe` and `i2c_adapter` output pointers must be valid for I2C-client probe mode.

## Test Signals
Compile coverage should include enabled and disabled Kconfig paths. Runtime tests should validate the caller's IF frequencies, TS polarity/mode choices, repeater-deny setting, and returned frontend/tuner adapter pointers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lgdt3306a.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lgdt330x.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lgdt330x.c

## Purpose
`lgdt330x.c` supports LGDT3302 and LGDT3303 ATSC 8VSB / Annex B QAM demodulators. It provides an I2C-client-backed DVB frontend with legacy attach wrapping, chip-specific init/reset sequences, modulation switching, SNR/status/statistics reporting, and tuner integration.

## Important APIs, Types, and Functions
`struct lgdt330x_state` stores the I2C client, copied config, frontend, cached modulation/frequency, SNR, uncorrected-block count, and throttled-stat timestamp. I2C helpers are `i2c_write_demod_bytes()` and `i2c_read_demod_bytes()`. Reset/init paths are `lgdt3302_sw_reset()`, `lgdt3303_sw_reset()`, `lgdt330x_sw_reset()`, and `lgdt330x_init()`. Tuning uses `lgdt330x_set_parameters()` and `lgdt330x_get_frontend()`. Metrics use `calculate_snr()`, `lgdt3302_read_snr()`, `lgdt3303_read_snr()`, `lgdt330x_read_snr()`, `lgdt330x_read_signal_strength()`, `lgdt3302_read_status()`, `lgdt3303_read_status()`, and `lgdt330x_read_ucblocks()`. Driver entry points are `lgdt330x_probe()`, legacy `lgdt330x_attach()`, and `lgdt330x_remove()`.

## Control Flow
Probe allocates state, copies platform config, chooses LGDT3302 or LGDT3303 frontend ops, and verifies I2C communication by reading register 2. Init writes chip-specific register tables, applies LGDT3303 clock-polarity variants, initializes DVB statistic property scales, resets the demodulator, and clears the stat throttle. Set-frontend changes demod mode only when modulation changes, optionally switches an RF input through `pll_rf_set()`, writes LGDT3303 VSB/QAM register tables, combines serial/parallel MPEG output bits, invokes `set_ts_params()`, then asks the tuner to tune and resets the demod. Status callbacks read AGC/carrier/sync/FEC lock registers, update FE_HAS_* flags, and when locked refresh CNR and block counters at most once per second.

## State and Persistence
State is in the I2C chip registers plus software caches for current modulation/frequency, last SNR, `ucblocks`, and `last_stats_time`. The driver has no suspend cache or persistent storage. `release()` unregisters the I2C client for legacy attach users; remove frees the state.

## Dependencies and Integration Points
The driver depends on I2C, DVB frontend core, `intlog10()` fixed-point math, and board callbacks from `struct lgdt330x_config` for RF connector selection and TS parameter setup. It registers I2C id `"lgdt330x"` and exports `lgdt330x_attach()`. The frontends advertise `SYS_ATSC` and `SYS_DVBC_ANNEX_B`.

## Risks and Edge Cases
Several I2C reads in status/SNR paths do not fully propagate errors before consuming buffers. The legacy `lgdt330x_attach()` creates an I2C client from a stack-copied platform-data object; probe copies the data immediately, which is required for correctness. Cached modulation avoids reprogramming mode but frequency is always tracked with a FIXME noting tuner sharing with analog APIs. Block count increments use a fixed placeholder of 10000 and are not true hardware totals.

## Test Signals
Validate both LGDT3302 and LGDT3303 ops, LGDT3303 clock-polarity variants, VSB/QAM64/QAM256 switching, serial and parallel MPEG output, RF-selector callback use, tuner gate close after tuner writes, lock/status mapping, CNR decibel counters after lock, once-per-second stats throttling, and I2C client unregister/free behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lgdt330x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lgdt330x.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lgdt330x.h

## Purpose
`lgdt330x.h` defines the public configuration and attach API for LGDT3302/LGDT3303 demodulators.

## Important APIs, Types, and Functions
`lg_chip_type` enumerates `UNDEFINED`, `LGDT3302`, and `LGDT3303`. `struct lgdt330x_config` selects the demod chip, serial MPEG output bit, optional RF-input callback, optional TS-parameter callback, LGDT3303 clock polarity flip, and a driver-filled `get_dvb_frontend()` callback. `lgdt330x_attach()` creates or returns a frontend when the driver is enabled; otherwise the inline stub warns and returns `NULL`.

## Control Flow
Board code supplies the config to `lgdt330x_attach()`, which wraps I2C-client creation. Probe copies the config, fills `get_dvb_frontend`, selects chip-specific ops, and returns the frontend through that callback.

## State and Persistence
This header defines configuration only. Runtime state is allocated in the C file and the demodulator register state is rebuilt during init and tuning.

## Dependencies and Integration Points
It depends on Linux DVB frontend types and I2C client types. Integration is with older board drivers that still use attach-style frontend construction.

## Risks and Edge Cases
The `serial_mpeg` field is a raw register bit value rather than an enum, and differs between LGDT3302 and LGDT3303 according to implementation comments. `clock_polarity_flip` applies only to LGDT3303 and accepts multiple magic variants.

## Test Signals
Build-test enabled and disabled Kconfig paths, attach with both chip enum values, and verify caller callbacks are preserved after probe copies the config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lgdt330x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lgdt330x_priv.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lgdt330x_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lgs8gl5.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lgs8gl5.c

## Purpose
`lgs8gl5.c` implements a simple Legend Silicon LGS-8GL5 DMB-TH/DTMB OFDM demodulator frontend.

## Important APIs, Types, and Functions
`struct lgs8gl5_state` holds the I2C adapter, config, and DVB frontend. Register helpers are `lgs8gl5_write_reg()`, `lgs8gl5_read_reg()`, `lgs8gl5_update_reg()`, and `lgs8gl5_update_alt_reg()` for an alternate I2C address at `demod_address + 2`. Runtime operations include `lgs8gl5_soft_reset()`, `lgs8gl5_start_demod()`, `lgs8gl5_init()`, `lgs8gl5_set_frontend()`, `lgs8gl5_get_frontend()`, status and metric readers, and `lgs8gl5_attach()`.

## Control Flow
Attach allocates state, saves the config and I2C adapter, checks register `REG_RESET`, installs `lgs8gl5_ops`, and returns the frontend. Init writes a fixed demod setup sequence. Set-frontend accepts only 8 MHz bandwidth, calls tuner `set_params()`, closes any I2C gate, and starts demodulation. Start-demod writes the alternate device, resets, programs OFDM registers, waits for carrier for up to roughly 40 ms, then waits for lock for up to roughly 240 ms and copies register `REG_A2` into `REG_7D` before final reset.

## State and Persistence
Software state is only the allocated frontend wrapper. Hardware register state is rebuilt by init and set-frontend. BER and uncorrected-block metrics are stubbed to zero; signal strength and SNR reuse the register strength level.

## Dependencies and Integration Points
The file depends on I2C and DVB frontend core, is exported by `lgs8gl5_attach()`, and advertises `SYS_DTMB`. It expects an external tuner through standard DVB tuner ops.

## Risks and Edge Cases
`lgs8gl5_update_reg()` reads but ignores the old value and blindly writes the new value. The alternate I2C device is marked with a TODO, so board compatibility depends on undocumented hardware. I2C helpers return `-1` for many failures rather than errno-specific values. Only 8 MHz channels are accepted despite the ops advertising bandwidth auto capability.

## Test Signals
Validate attach at the demod I2C address, init sequence completion, tuner programming, rejection of non-8 MHz bandwidth, carrier/lock polling behavior, FE_HAS_SIGNAL/CARRIER/SYNC/LOCK mapping, and strength/SNR scaling from `REG_STRENGTH`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lgs8gl5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lgs8gl5.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lgs8gl5.h

## Purpose
`lgs8gl5.h` defines the board-facing attach interface for the standalone LGS-8GL5 DTMB demodulator driver.

## Important APIs, Types, and Functions
`struct lgs8gl5_config` contains only the demodulator I2C address. `lgs8gl5_attach()` is declared under `CONFIG_DVB_LGS8GL5` and otherwise replaced with a warning stub.

## Control Flow
Callers provide the config and I2C adapter to attach. The C file reads a reset register at that address before returning a configured `dvb_frontend`.

## State and Persistence
The header defines no mutable state. The address is retained by runtime state and used for every demodulator transaction.

## Dependencies and Integration Points
It depends on `<linux/dvb/frontend.h>` and integrates with board drivers using attach-style DVB frontend setup.

## Risks and Edge Cases
There are no fields for TS mode, IF, or alternate-device address, so those are hard-coded in the C file. Misdescribed board wiring cannot be corrected through this config.

## Test Signals
Build-test both Kconfig paths and verify a board can attach, tune, and read status using only the supplied demod address.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lgs8gl5.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lgs8gxx.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lgs8gxx.c

## Purpose
`lgs8gxx.c` is the broader Legend Silicon GB20600/DMB-TH demodulator family driver for LGS8913, LGS8GL5, LGS8G75, and experimental LGS8G42/G52/G54 variants. It programs ADC/IF/TS modes, performs auto-detection of guard interval and transmission parameters, optionally loads LGS8G75 firmware, and exposes DTMB frontend operations.

## Important APIs, Types, and Functions
Core helpers are `lgs8gxx_write_reg()`, `lgs8gxx_read_reg()`, `lgs8gxx_soft_reset()`, and `wait_reg_mask()`. Configuration helpers include `lgs8gxx_set_ad_mode()`, `lgs8gxx_set_if_freq()`, `lgs8gxx_set_mode_auto()`, `lgs8gxx_set_mode_manual()`, `lgs8gxx_set_mpeg_mode()`, `lgs8g75_set_adc_vpp()`, `lgs8913_init()`, and `lgs8g75_init_data()`. Locking paths are `lgs8gxx_wait_ca_lock()`, `lgs8gxx_is_autodetect_finished()`, `lgs8gxx_autolock_gi()`, `lgs8gxx_auto_detect()`, and `lgs8gxx_auto_lock()`. DVB callbacks include init, write, I2C gate control, set frontend, tune settings, status, BER, signal strength, SNR, ucblocks, and release.

## Control Flow
Attach validates config/I2C, allocates state, probes register 0, installs ops, and for LGS8G75 downloads `lgs8g75.fw` into device memory. Init optionally sets LGS8G75 ADC range, configures MPEG output, runs LGS8913-specific setup, writes IF frequency NCO, and configures ADC input mode. Set-frontend invokes the tuner and then `lgs8gxx_auto_lock()`: the driver switches to auto mode, tries guard intervals and CPN combinations with soft resets and lock polling, reads detected parameters, applies product-specific fixes, stores current guard interval, and switches to manual mode. Status checks product-specific lock registers; signal metrics use either LGS8913 CIR scanning/fake signal, LGS8G75 level registers, or generic AGC categories.

## State and Persistence
`struct lgs8gxx_state` retains the config, I2C adapter, frontend, and current guard interval. Device registers and optional downloaded firmware hold the meaningful demodulator state. No suspend cache exists. BER measurement temporarily starts/stops packet counters and reads volatile total/error registers.

## Dependencies and Integration Points
The driver depends on Linux firmware loading, I2C, DVB frontend core, `do_div()` math, product IDs from `lgs8gxx.h`, private mode constants from `lgs8gxx_priv.h`, and external tuner callbacks. It exports `lgs8gxx_attach()`, registers module firmware `lgs8g75.fw`, and advertises `SYS_DTMB`.

## Risks and Edge Cases
Firmware load failure for LGS8G75 is not propagated by attach, so the frontend can be returned after a failed init-data download. Many helper failures return `-1` or are ignored, making root-cause diagnosis harder. `fake_signal_str` defaults on for LGS8913 because real strength scanning is slow. Auto-detect retries are limited and may fail without detailed error propagation. Alternate I2C address selection for non-LGS8G75 registers above `0xC0` must match board routing.

## Test Signals
Test each product id that has board support, LGS8G75 firmware request and register download, IF/baseband and external ADC combinations, serial/parallel TS and clock polarity/gating, tuner I2C gate writes, auto-lock across guard intervals, lock status mapping, BER packet-counter reads, LGS8913 fake and real signal modes, and attach cleanup after I2C probe failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lgs8gxx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lgs8gxx.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lgs8gxx.h

## Purpose
`lgs8gxx.h` is the public configuration header for the Legend Silicon DMB-TH/DTMB demodulator family driver.

## Important APIs, Types, and Functions
It defines product IDs for LGS8913, LGS8GL5, LGS8G42, LGS8G52, LGS8G54, and LGS8G75. `struct lgs8gxx_config` describes product type, demod I2C address, serial/parallel TS mode, TS clock polarity and gating, IF clock/frequency, external ADC and ADC data-format flags, IF sampling/negative-center options, LGS8G75 ADC Vpp selection, and tuner slave address. `lgs8gxx_attach()` is declared under `CONFIG_DVB_LGS8GXX` and stubbed otherwise.

## Control Flow
Board drivers fill this structure and call attach. The C file branches heavily on `prod` to choose register addresses, init sequences, firmware loading, lock checks, and signal metric formulas.

## State and Persistence
The header itself is immutable configuration. Runtime state stores a pointer to the config; therefore board-provided config storage must outlive the frontend.

## Dependencies and Integration Points
It depends on DVB frontend and I2C headers and is consumed by board/card drivers that instantiate the demodulator and tuner.

## Risks and Edge Cases
The config uses raw `u8` flags rather than enums for most booleans, making invalid combinations possible. `tuner_address == 0` disables the demodulator I2C gate in the implementation. IF clock/frequency values directly affect fixed-point NCO calculation, so zero or mismatched clock values can produce invalid tuning.

## Test Signals
Validate enabled/disabled builds, product-specific register behavior, TS output electrical mode, IF/ADC combinations, tuner gate enablement, and LGS8G75 ADC range choices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lgs8gxx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lgs8gxx_priv.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lgs8gxx_priv.h

## Purpose
`lgs8gxx_priv.h` defines private runtime state and bit masks used by the LGS8Gxx family driver.

## Important APIs, Types, and Functions
`struct lgs8gxx_state` contains the I2C adapter, config pointer, DVB frontend, and current guard interval. Macros define detected transmission-parameter fields: sub-carrier modulation (`SC_*`), FEC rate (`LGS_FEC_*`), time interleave (`TIM_*`), control frame (`CF_*`), guard interval (`GI_*`), and TS output flags (`TS_*`).

## Control Flow
The C file uses these masks when interpreting auto-detected parameters, applying the LGS8913 time-interleaver fix, setting guard interval trials, and configuring MPEG/TS output registers.

## State and Persistence
`curr_gi` is software state used mainly by LGS8913 signal-strength scanning. All other macros describe volatile register bitfields.

## Dependencies and Integration Points
It is private to `lgs8gxx.c` and relies on public `struct lgs8gxx_config` from `lgs8gxx.h`.

## Risks and Edge Cases
The guard-interval constants are register encodings, not human-readable interval values; the C file translates them to 420/595/945 for `curr_gi`. Misusing these constants outside their register context would create wrong scan lengths or TS settings.

## Test Signals
Auto-detect should report and apply each guard interval, LGS8913 detected-parameter correction should preserve expected CF/SC/FEC fields, and TS mode bits should produce the configured serial/parallel clock behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lgs8gxx_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lnbh24.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lnbh24.h

## Purpose
`lnbh24.h` provides the public interface and register bit definitions for LNBH24 satellite LNB supply control, implemented through the shared LNBP21/LNBH24 C file.

## Important APIs, Types, and Functions
The header defines system register bits such as `LNBH24_OLF`, `LNBH24_OTF`, `LNBH24_EN`, `LNBH24_VSEL`, `LNBH24_LLC`, `LNBH24_TEN`, `LNBH24_TTX`, and `LNBH24_PCL`. `lnbh24_attach()` accepts a frontend, I2C adapter, override set/clear masks, and I2C address when `CONFIG_DVB_LNBP21` is reachable.

## Control Flow
Callers attach LNBH24 support to an existing satellite frontend. The implementation routes this to `lnbx2x_attach()` with an LNBH24 default config bit, then overrides the frontend SEC voltage/tone callbacks.

## State and Persistence
The header defines bit constants only. Runtime state in `lnbp21.c` keeps one volatile config byte and board override masks.

## Dependencies and Integration Points
It depends on DVB frontend types and is tied to `CONFIG_DVB_LNBP21` because LNBH24 shares that implementation.

## Risks and Edge Cases
The override masks can force bits on or off for every write; incorrect masks can permanently disable tone, power, or protection behavior. The header has no type-safe config structure, only raw masks and address.

## Test Signals
Validate attach through the LNBP21 implementation, 13 V/18 V/off writes at the supplied address, tone callback availability depending on override masks, and Kconfig-disabled stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lnbh24.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lnbh25.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lnbh25.c

## Purpose
`lnbh25.c` drives the ST LNBH25 satellite LNB supply/control IC. It attaches SEC voltage control to an existing DVB frontend, writes DATA1/DATA2 over I2C, and verifies voltage monitor status after enabling output.

## Important APIs, Types, and Functions
`struct lnbh25_priv` stores the I2C adapter, 7-bit I2C address, and a three-byte write buffer starting at DATA1 register `0x02`. `lnbh25_set_voltage()` maps DVB `SEC_VOLTAGE_OFF`, `SEC_VOLTAGE_13`, and `SEC_VOLTAGE_18` to `LNBH25_VSEL_*` values and writes the config. `lnbh25_read_vmon()` reads six status bytes and rejects over-current or voltage-monitor faults. `lnbh25_release()` powers off and frees `sec_priv`; `lnbh25_attach()` allocates state, probes by powering off, and overrides `release_sec` and `set_voltage`.

## Control Flow
Attach converts the supplied 8-bit address to a 7-bit I2C address, seeds config bytes, stores `fe->sec_priv`, and calls `lnbh25_set_voltage(OFF)` as presence detection. Setting voltage writes all three bytes, waits 120 ms for 13/18 V before reading status, or 20 ms for off.

## State and Persistence
State is one allocated `lnbh25_priv` and the last DATA1/DATA2 config bytes. Hardware output state is volatile and explicitly forced off on release. There is no persistent storage.

## Dependencies and Integration Points
The file depends on Linux I2C, delays, module infrastructure, and DVB frontend SEC callbacks. It exports `lnbh25_attach()` for board drivers and uses `struct lnbh25_config` from the header.

## Risks and Edge Cases
Status read is split into two single-message transfers instead of one combined `i2c_transfer()` call; adapters must tolerate that sequence. Only voltage control is implemented, not tone or DiSEqC. Any VMON/OFL bit after the fixed delay is treated as `-EIO`, so slow or heavily loaded hardware may fail attach or voltage changes.

## Test Signals
Test attach/probe at the configured address, off/13 V/18 V transitions, DATA2 option preservation, VMON/OFL fault reporting, release power-off, and frontend SEC callback replacement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lnbh25.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lnbh25.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lnbh25.h

## Purpose
`lnbh25.h` defines board configuration and option bits for the ST LNBH25 LNB supply driver.

## Important APIs, Types, and Functions
It defines DATA2 option bits `LNBH25_TEN`, `LNBH25_LPM`, and `LNBH25_EXTM`. `struct lnbh25_config` carries an I2C address and DATA2 configuration byte. `lnbh25_attach()` is declared under `CONFIG_DVB_LNBH25` and stubbed otherwise.

## Control Flow
Board drivers fill `lnbh25_config`, call attach with an existing frontend and I2C adapter, and the C file installs voltage-control SEC callbacks.

## State and Persistence
The config byte is copied into runtime state and rewritten on each voltage change. No persistent state is defined here.

## Dependencies and Integration Points
It depends on Linux I2C and DVB frontend headers. Integration is limited to satellite SEC voltage-control setup.

## Risks and Edge Cases
The I2C address is expected in the board convention used by the C file, which shifts it right by one. Supplying an already 7-bit address would address the wrong chip.

## Test Signals
Build both Kconfig paths, verify address handling on target boards, and check that DATA2 option bits are present in every LNBH25 write.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lnbh25.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lnbh29.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lnbh29.c

## Purpose
`lnbh29.c` drives the STMicroelectronics LNBH29 LNB supply/control IC. It attaches a voltage-control SEC helper to an existing DVB frontend and validates output voltage through status reads.

## Important APIs, Types, and Functions
`struct lnbh29_priv` stores the I2C adapter, 7-bit address, and two-byte DATA register write buffer. `lnbh29_set_voltage()` updates only the `LNBH29_VSEL_MASK` bits for off, 13 V, or 18 V and writes register `0x01`. `lnbh29_read_vmon()` reads two status bytes from register `0x00` and treats OLF or VMON as failures. `lnbh29_release()` powers off and frees state; `lnbh29_attach()` allocates state, probes with voltage off, and installs SEC callbacks.

## Control Flow
Attach shifts the configured address, seeds the DATA register byte from board config, stores `sec_priv`, and powers off to detect the chip. Voltage changes perform one I2C write, wait 6-20 ms for soft-start, and read status unless turning off.

## State and Persistence
The driver keeps a mutable cached DATA byte so board option bits survive voltage changes while VSEL bits change. Release forces off. No persistent storage or suspend cache exists.

## Dependencies and Integration Points
It depends on Linux I2C, DVB frontend SEC operations, bit macros, and `struct lnbh29_config`. It exports `lnbh29_attach()`.

## Risks and Edge Cases
Only voltage control is implemented. Status bits for over-temperature, power-not-good, and power-down are defined but only OLF/VMON are used for failure decisions. Address shifting has the same 8-bit-vs-7-bit board convention risk as LNBH25.

## Test Signals
Validate attach, DATA option preservation, off/13/18 V writes, status-fault propagation, release power-off, and callback replacement on an existing frontend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lnbh29.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lnbh29.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lnbh29.h

## Purpose
`lnbh29.h` defines the public configuration interface for the LNBH29 LNB supply driver.

## Important APIs, Types, and Functions
It defines `LNBH29_DATA_COMP` for the DATA register compensation option. `struct lnbh29_config` carries the I2C address and initial DATA register configuration. `lnbh29_attach()` is declared when `CONFIG_DVB_LNBH29` is reachable and stubbed otherwise.

## Control Flow
Board code supplies config to attach; the implementation copies the DATA option byte, installs `set_voltage`, and probes with output off.

## State and Persistence
The header owns no state. The DATA config becomes a mutable runtime cache in `fe->sec_priv`.

## Dependencies and Integration Points
It depends on Linux I2C and DVB frontend headers and integrates with satellite frontend SEC setup.

## Risks and Edge Cases
Only the compensation option is named publicly; other DATA register bits may need board-specific values in `data_config` without symbolic documentation here. The implementation shifts `i2c_address` right by one.

## Test Signals
Build-test Kconfig enabled/disabled paths and verify board-provided DATA bits survive voltage changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lnbh29.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lnbp21.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lnbp21.c

## Purpose
`lnbp21.c` implements SEC helper support for ST LNBP21 and LNBH24 LNB supply/control ICs. It attaches to an existing DVB frontend and overrides voltage, high-voltage compensation, tone, and release callbacks.

## Important APIs, Types, and Functions
`struct lnbp21` stores one config byte, force-set/force-clear masks, I2C adapter, and I2C address. `lnbp21_set_voltage()` maps DVB off/13 V/18 V to EN/VSEL bits, applies overrides, and writes one byte. `lnbp21_enable_high_lnb_voltage()` toggles LLC. `lnbp21_set_tone()` toggles TEN. `lnbp21_release()` powers off and frees `sec_priv`. The shared `lnbx2x_attach()` handles allocation, default config, override masks, presence probe, and callback installation. Public wrappers are `lnbh24_attach()` and `lnbp21_attach()`.

## Control Flow
LNBH24 attach calls the shared helper with the caller-supplied I2C address and `LNBH24_TTX` as default config. LNBP21 attach uses address `0x08` and `LNBP21_ISEL` as default config. The shared helper powers off as a presence probe, installs callbacks, and suppresses `set_tone` when the LNBH24 TEN bit is forced clear.

## State and Persistence
Runtime state is one mutable config byte plus override masks. Every SEC operation re-applies overrides before I2C write. Release powers off and frees state. There is no persistent storage or fault-status polling.

## Dependencies and Integration Points
The file depends on DVB frontend SEC callbacks, Linux I2C, and bit definitions from `lnbp21.h` and `lnbh24.h`. It exports both attach functions for board drivers.

## Risks and Edge Cases
The presence probe only checks that an I2C write succeeds; read-only fault bits are never inspected. Incorrect override masks can force power/tone/protection bits into unsafe states. If attach fails, `fe->sec_priv` is not explicitly cleared in the shared helper after freeing. Tone callback installation depends on an LNBH24 bit even when using the shared helper.

## Test Signals
Validate LNBP21 and LNBH24 attach paths, off/13/18 V writes, LLC toggle, TEN tone toggle or suppression, override set/clear behavior, release power-off, and failed I2C probe cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lnbp21.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lnbp21.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lnbp21.h

## Purpose
`lnbp21.h` defines LNBP21 system-register bits and the attach API for the LNBP21 LNB supply driver.

## Important APIs, Types, and Functions
The header documents status and control bits: OLF, OTF, EN, VSEL, LLC, TEN, ISEL, and PCL. `lnbp21_attach()` accepts an existing frontend, I2C adapter, and override set/clear masks under `CONFIG_DVB_LNBP21`, with a warning stub otherwise.

## Control Flow
Board drivers call attach to install SEC voltage/tone callbacks. The implementation writes a default config byte, applies override masks on every operation, and probes by powering off.

## State and Persistence
No state is declared here. Bit definitions describe the single volatile system register cached by `lnbp21.c`.

## Dependencies and Integration Points
It depends on DVB frontend types and is used by satellite board drivers that need LNB power control.

## Risks and Edge Cases
The API exposes raw override masks instead of a structured config, so caller mistakes directly alter every hardware write. Read-only fault flags are defined but not consumed by the implementation.

## Test Signals
Build enabled/disabled paths, confirm voltage/tone behavior with override masks, and validate the default current-limit selection on target boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lnbp21.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lnbp22.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lnbp22.c

## Purpose
`lnbp22.c` implements a simple LNBP22 LNB supply/control helper. It attaches voltage and high-voltage compensation callbacks to an existing DVB frontend and writes a four-byte I2C config frame.

## Important APIs, Types, and Functions
`struct lnbp22` stores a four-byte config array and I2C adapter. `lnbp22_set_voltage()` resets byte 3 to power-down base `0x60`, then applies EN/VSEL for off/13 V/18 V and writes to fixed I2C address `0x08`. `lnbp22_enable_high_lnb_voltage()` toggles LLC in byte 3. `lnbp22_release()` powers off and frees state. `lnbp22_attach()` seeds default bytes, probes with voltage off, and installs SEC callbacks.

## Control Flow
Attach allocates state, initializes four undocumented/default bytes, stores `fe->sec_priv`, calls set-voltage off as detection, and then overrides `release_sec`, `set_voltage`, and `enable_high_lnb_voltage`. Voltage and LLC operations write all four bytes each time.

## State and Persistence
The config array is volatile runtime state. Release powers off and frees it. No fault status is read and no persistent storage exists.

## Dependencies and Integration Points
The file depends on Linux I2C, module parameters for debug output, and DVB frontend SEC callbacks. It exports `lnbp22_attach()`.

## Risks and Edge Cases
The I2C address is hard-coded to `0x08`, unlike newer helpers that take a config address. Tone control is not implemented. The first three config bytes are marked unknown in comments, and byte 3 is reset on every voltage change, which can discard prior LLC state unless LLC is set after voltage.

## Test Signals
Validate attach/probe at address `0x08`, off/13/18 V writes, LLC toggle persistence across expected call order, release power-off, and debug/error behavior on I2C failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lnbp22.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lnbp22.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lnbp22.h

## Purpose
`lnbp22.h` defines LNBP22 control bits and the attach API for the LNBP22 SEC helper.

## Important APIs, Types, and Functions
It defines `LNBP22_EN`, `LNBP22_VSEL`, and `LNBP22_LLC`. `lnbp22_attach()` accepts an existing frontend and I2C adapter under `CONFIG_DVB_LNBP22`, with a disabled-driver warning stub otherwise.

## Control Flow
Board drivers call attach after demodulator/frontend creation. The C file installs voltage and high-voltage callbacks and uses a fixed I2C address.

## State and Persistence
The header contains no state. The control bits map to byte 3 of the runtime four-byte config array.

## Dependencies and Integration Points
It depends on DVB frontend types and integrates with satellite frontend SEC setup.

## Risks and Edge Cases
The comment mentions override masks, but the actual attach signature has no override parameters. Callers cannot configure address or default bytes through this header.

## Test Signals
Build both Kconfig paths and verify control bits produce expected voltage/LLC writes in `lnbp22.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lnbp22.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/m88ds3103.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/m88ds3103.c

## Purpose
`m88ds3103.c` drives Montage M88DS3103, M88DS3103B/C, and M88RS6000 DVB-S/S2 demodulators. It is a regmap-backed I2C driver with legacy attach wrapping, firmware cold/warm handling, tuner I2C mux creation, TS/clock programming, status/statistics reporting, DiSEqC, and LNB voltage/tone control.

## Important APIs, Types, and Functions
Register helpers are `m88ds3103_update_bits()`, `m88ds3103_wr_reg_val_tab()`, and the M88DS3103B/C internal clock-device accesses `m88ds3103b_dt_write()`/`m88ds3103b_dt_read()`. Public helpers are `m88ds3103_get_agc_pwm()` and legacy `m88ds3103_attach()`. Core frontend callbacks include `m88ds3103_init()`, `m88ds3103_sleep()`, `m88ds3103_set_frontend()`, `m88ds3103_get_frontend()`, `m88ds3103_read_status()`, `m88ds3103_read_snr()`, `m88ds3103_read_ber()`, `m88ds3103_set_tone()`, `m88ds3103_set_voltage()`, `m88ds3103_diseqc_send_master_cmd()`, `m88ds3103_diseqc_send_burst()`, and tune settings. Probe/remove manage `m88ds3103_dev`, regmap, chip-id detection, dummy internal tuner/clock I2C client, and `i2c_mux_core`.

## Control Flow
Probe copies platform data into local config, initializes regmap, reads chip id, validates clock-out and TS clock config, sleeps the device, creates a tuner I2C mux, installs frontend ops and callbacks, and for B/C variants enables an internal repeater and creates a dummy internal-device client. Init wakes the chip, resets demod/FEC/DiSEqC blocks, checks firmware status, downloads the chip-specific firmware if cold, verifies warm firmware, initializes stats, and performs B/C/C-specific TS and clock setup. Set-frontend requires warm firmware, resets the demod, tunes the external tuner, derives actual tuner frequency when possible, computes MCLK/TS clock choices, selects the correct DVB-S or DVB-S2 register table, applies symbol-rate, spectrum, AGC, TS, and carrier-offset programming, and records the delivery system. Status reads chip-specific lock bits, updates FE_HAS_* status, computes CNR, and accumulates post-bit error/count counters. DiSEqC commands write message bytes and poll TX-ready with timeouts.

## State and Persistence
`struct m88ds3103_dev` retains config, frontend, regmap, chip id/type, warm/cold firmware state, current delivery system, last frontend status, MCLK, DVBv3 BER, and cumulative DVBv5 post-bit counters. Firmware and register state are volatile; sleep clears status/delivery-system state and powers down blocks. There is no filesystem persistence beyond requesting firmware files from userspace.

## Dependencies and Integration Points
The driver depends on I2C, regmap, firmware loading, I2C mux, DVB frontend core, math/log helpers, tuner ops, and platform data from `m88ds3103.h`. It registers I2C ids for `"m88ds3103"`, `"m88rs6000"`, `"m88ds3103b"`, and `"m88ds3103c"`, exports legacy attach and AGC PWM helper APIs, and declares required firmware blobs.

## Risks and Edge Cases
Firmware absence makes init fail and leaves the demod cold. `m88ds3103_wr_reg_val_tab()` rejects tables longer than 86 entries even though its local buffer is 83 bytes, so batch sizing relies on `i2c_wr_max` and table grouping. Some B/C internal-device reads return negative errno through an `int` function otherwise used as a byte. The legacy attach path depends on probe immediately copying stack platform data. TS clock, symbol-rate, and chiptype branches are dense and board misconfiguration can silently produce invalid transport output. Remove unregisters `dt_client` even when it may be NULL for non-B/C variants, which relies on helper tolerance.

## Test Signals
Test probe for each chip id/type, invalid TS clock rejection, firmware download and warm re-init, tuner mux open transactions, DVB-S and DVB-S2 tuning across low/high symbol rates, serial/parallel/CI TS modes and polarity, external tuner actual-frequency carrier-offset correction, CNR/BER counter updates, sleep/wake behavior, DiSEqC message/burst timeouts, LNB voltage/tone polarity options, AGC PWM export, legacy attach, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/m88ds3103.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/m88ds3103.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/m88ds3103.h

## Purpose
`m88ds3103.h` is the public configuration and attach header for Montage M88DS3103/M88RS6000 DVB-S/S2 demodulators.

## Important APIs, Types, and Functions
`enum m88ds3103_ts_mode` selects serial, serial on D7, parallel, or CI TS output. `enum m88ds3103_clock_out` controls crystal clock output. `struct m88ds3103_platform_data` is the I2C-client binding contract, with clock, I2C max write size, TS mode/clock/polarity, spectrum and AGC polarity/config, DiSEqC envelope mode, LNB pin polarities, and driver-filled callbacks. `struct m88ds3103_config` is the legacy attach equivalent. The header declares `m88ds3103_attach()` and `m88ds3103_get_agc_pwm()` when enabled, or stubs otherwise.

## Control Flow
Modern users instantiate an I2C client with platform data; probe copies it and fills callback pointers. Legacy users call `m88ds3103_attach()`, which builds platform data and an I2C client, then retrieves the frontend and muxed tuner adapter through callbacks.

## State and Persistence
The header defines configuration only. The implementation copies config into device state and uses it for volatile clock, TS, AGC, spectrum, DiSEqC, and LNB-pin programming.

## Dependencies and Integration Points
It depends on DVB frontend types and I2C client types. It integrates demodulator, tuner-I2C adapter, SEC tone/voltage, and optional tuner AGC-PWM consumers.

## Risks and Edge Cases
The legacy config comments say several fields have no defaults and must be set; the C file rejects missing `ts_clk`. Platform data `attach_in_use` is private and should not be set by normal I2C-client users. `ts_clk` units differ internally: platform data is kHz, while the driver converts to Hz.

## Test Signals
Build enabled/disabled configurations, instantiate I2C-client and legacy attach paths, verify returned frontend/tuner adapter callbacks, TS mode and clock output choices, and AGC PWM availability for tuner drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/m88ds3103.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/m88ds3103_priv.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/m88ds3103_priv.h

## Purpose
`m88ds3103_priv.h` defines private firmware names, chip IDs/types, runtime state, register-value table format, and chip/system-specific initialization tables for the M88DS3103 driver.

## Important APIs, Types, and Functions
Firmware macros name `dvb-demod-m88ds3103b.fw`, `dvb-demod-m88ds3103c.fw`, `dvb-demod-m88ds3103.fw`, and `dvb-demod-m88rs6000.fw`. Chip macros define IDs for DS3103, RS6000, and DS3103C plus logical chiptypes. `struct m88ds3103_dev` carries I2C clients, regmap, config, frontend, status, firmware warmth, mux, chip identity, MCLK, BER counters, and internal-device address. `struct m88ds3103_reg_val` backs static register tables for DS3103 DVB-S, DS3103 DVB-S2, RS6000 DVB-S, RS6000 DVB-S2, and DS3103C initialization.

## Control Flow
`m88ds3103.c` selects one of these register tables during set-frontend based on delivery system and chip id, then writes it through `m88ds3103_wr_reg_val_tab()`. The firmware name macros are selected in init when the chip is cold. The state structure is allocated at probe and freed at remove.

## State and Persistence
The state structure holds all runtime software state for the driver. Register tables and firmware names are static constants; hardware state remains volatile and is restored by init/tune paths.

## Dependencies and Integration Points
The header includes DVB frontend, public M88DS3103 config, integer log/math, firmware, I2C mux, and regmap headers. It is private to the driver implementation.

## Risks and Edge Cases
Large static tables are hardware magic values; an incorrect chip/table pairing would produce tuning failures that are hard to diagnose. The private state contains both copied config and a config pointer, so code must keep them synchronized through `dev->cfg = &dev->config`.

## Test Signals
Firmware selection should match chip type, register table selection should match DVB-S/DVB-S2 and chip id, state counters should initialize and accumulate correctly, and probe/remove should handle internal dummy clients and mux state for all chip variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/m88ds3103_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/m88rs2000.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/m88rs2000.c

## Purpose
`m88rs2000.c` implements a DVB-S frontend for the Montage M88RS2000 demodulator/tuner family. It performs direct I2C register programming, tuner coordination, DVB-S symbol/FEC/carrier setup, status/stat reads, DiSEqC/tone/voltage control, and I2C gate control.

## Important APIs, Types, and Functions
`struct m88rs2000_state` stores the I2C adapter, config, frontend, no-lock retry count, cached tuner frequency/symbol rate/FEC, tuner level, and error mode. I/O helpers are `m88rs2000_writereg()` and `m88rs2000_readreg()`. Tuning helpers include `m88rs2000_get_mclk()`, `m88rs2000_set_carrieroffset()`, `m88rs2000_set_symbolrate()`, `m88rs2000_set_fec()`, `m88rs2000_get_fec()`, and table executor `m88rs2000_tab_set()`. SEC helpers are `m88rs2000_send_diseqc_msg()`, `m88rs2000_send_diseqc_burst()`, `m88rs2000_set_tone()`, and `m88rs2000_set_voltage()`. DVB ops include init/sleep, set/get frontend, status/BER/strength/SNR/ucblocks, tune settings, I2C gate control, and release.

## Control Flow
Attach allocates state, installs ops, and returns the frontend. Init executes either a caller-provided init table or the built-in setup table; sleep executes the shutdown table. Set-frontend only accepts `SYS_DVBS`, calls tuner `set_params()`, uses tuner actual frequency when available to compute carrier offset, adjusts MCLK near problematic frequency multiples, resets and programs demod tables, sets FEC and symbol rate, triggers acquisition, then polls lock up to 25 times while toggling a register bit after repeated no-lock attempts. On lock it caches detected FEC and requested tune parameters.

## State and Persistence
The driver caches the last frequency, symbol rate, and FEC for `get_frontend()`, and tracks no-lock retries during acquisition. Register state is volatile and rebuilt through setup/reset/trigger tables. Release frees only software state; sleep writes shutdown registers.

## Dependencies and Integration Points
The file depends on DVB frontend core, I2C, jiffies/delay helpers, and optional board callbacks in `struct m88rs2000_config`, including custom init table and TS-parameter callback. It exports `m88rs2000_attach()` and advertises `SYS_DVBS`.

## Risks and Edge Cases
`m88rs2000_readreg()` returns zero on I2C failure without separately returning errno, which can mask hardware faults. DiSEqC burst is marked TODO and does not actually implement mini-command differences. `set_tone()` silently ignores invalid enum values. Attach performs no chip presence check. Voltage bit handling is terse and should be validated against board polarity. Custom init tables rely on sentinel encoding and are cast from `u8 *` to `struct inittab *`.

## Test Signals
Validate default and custom init tables, sleep table, DVB-S-only rejection of other systems, tuner set/get frequency paths, symbol rates across threshold bands, FEC auto/manual programming, acquisition polling and no-lock bit toggle, BER/ucblocks reset behavior, DiSEqC master command timing, tone/voltage outputs, I2C gate writes, and get_frontend cached values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/m88rs2000.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/m88rs2000.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/m88rs2000.h

## Purpose
`m88rs2000.h` defines the board-facing configuration and attach API for the M88RS2000 DVB-S demodulator driver.

## Important APIs, Types, and Functions
`struct m88rs2000_config` contains the demodulator I2C address, optional custom init table, minimum delay, and optional `set_ts_params()` callback. It defines callback reason constants `CALL_IS_SET_FRONTEND` and `CALL_IS_READ`, crystal constant `RS2000_FE_CRYSTAL_KHZ`, and init-table commands `DEMOD_WRITE` and `WRITE_DELAY`. `m88rs2000_attach()` is declared under `CONFIG_DVB_M88RS2000` and stubbed otherwise.

## Control Flow
Board drivers call attach with this config and an I2C adapter. The C file stores the config pointer directly, executes the optional init table during frontend init, and invokes `set_ts_params()` from status read after lock.

## State and Persistence
The header provides static configuration and command encodings only. Runtime state stores a pointer to config, so the config and optional init table must remain valid for the frontend lifetime.

## Dependencies and Integration Points
It depends on DVB frontend headers and integrates with board-specific tuner/TS setup and optional custom demod initialization tables.

## Risks and Edge Cases
The `inittab` field is typed as `u8 *` even though the implementation casts it to `struct inittab *`, so callers must provide correctly packed table entries and sentinel values. `min_delay_ms` is present but the implementation computes tune delays from symbol rate instead.

## Test Signals
Build enabled/disabled paths, validate attach with and without custom init tables, verify TS callback reason values, and confirm the crystal constant drives expected MCLK calculations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/m88rs2000.h -->
