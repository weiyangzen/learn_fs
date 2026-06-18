# subset-b-004081 grouped research

Grouped research for ceph-client Linux media DVB frontend, FireDTV FireWire, and V4L2 I2C driver files. Each source file section is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tua6100.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tua6100.h

Purpose: Public attach contract for the Infineon TUA6100 DVB-S PLL tuner. The header lets board/frontend drivers attach the tuner to an existing `struct dvb_frontend` when `CONFIG_DVB_TUA6100` is reachable, while keeping callers buildable when the tuner driver is disabled.

Important APIs/types/functions: `tua6100_attach(struct dvb_frontend *fe, int addr, struct i2c_adapter *i2c)` is the single exported integration point. The disabled-driver inline stub logs a Kconfig warning and returns `NULL`. The header includes Linux I2C and DVB frontend types and uses `IS_REACHABLE(CONFIG_DVB_TUA6100)` so both built-in and module combinations are handled.

Control flow: There is no hardware logic here. Board code passes a frontend, tuner I2C address, and adapter into `tua6100_attach`; if the real implementation is not compiled in, the stub fails immediately. Successful attach is expected to populate `fe->ops.tuner_ops` in the implementation file outside this subset.

State and persistence: The header owns no mutable state. Any tuner state is allocated by the implementation and usually hangs off `fe->tuner_priv`. The only persistence-like behavior is the compile-time Kconfig decision.

Dependencies/integration: Integrates DVB demodulator/board drivers with the TUA6100 tuner module. It depends on `<linux/i2c.h>`, `<media/dvb_frontend.h>`, and the surrounding DVB attach conventions.

Risks and test signals: Build both reachable and disabled Kconfig combinations, including module-to-module attach users. Runtime board tests should verify callers handle `NULL` and do not assume tuner ops are installed when the stub path is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tua6100.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/ves1820.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/ves1820.c

Purpose: Implements the VLSI VES1820 DVB-C Annex A demodulator. It probes the chip over I2C, programs the demodulator register table, sets QAM modulation and symbol-rate parameters, coordinates an attached tuner, reports DVB frontend lock/statistics, and exports `ves1820_attach()`.

Important APIs/types/functions: `struct ves1820_state` owns the I2C adapter, board `ves1820_config`, DVB frontend, cached register 0 value, and PWM value. `ves1820_writereg()` and `ves1820_readreg()` are raw I2C register helpers. `ves1820_set_symbolrate()` derives NDEC, SFIL, BDR, and BDRI values from `config->xin`. `ves1820_setup_reg0()` encodes spectral inversion and QAM register bits. Frontend callbacks include `ves1820_init()`, `ves1820_set_parameters()`, `ves1820_get_frontend()`, `ves1820_read_status()`, BER/strength/SNR/uncorrected-block readers, `ves1820_sleep()`, `ves1820_get_tune_settings()`, and `ves1820_release()`.

Control flow: Attach allocates state, caches config/I2C/PWM, reads register `0x1a` and accepts identities with high nibble `0x70`, then copies `ves1820_ops` into the embedded frontend and sets dynamic symbol-rate bounds from `xin`. Init writes register zero, then the whole `ves1820_inittab`, optionally enables SELAGC mode, and restores PWM register `0x34`. Tuning calls tuner `set_params` if available, closes the demod I2C gate, programs symbol rate, PWM, modulation-dependent gain/timing registers, inversion/QAM bits through reg0, and SELAGC. Status/stat readers map hardware sync/BER/gain/quality/uncorrected counters to DVB API values; `get_frontend()` reports QAM/inversion and applies AFC correction when carrier is recovered.

State and persistence: Runtime state is limited to kernel memory and volatile demod registers. `state->reg0` preserves current modulation/inversion bits across reg0 writes; `state->pwm` preserves attach-supplied AGC PWM. There is no firmware, nonvolatile storage, or suspend persistence beyond reinitialization from static tables.

Dependencies/integration: Depends on Linux I2C, DVB frontend APIs, `do_div()`/`DIV_ROUND_CLOSEST`, and `ves1820.h`. Integrates with board tuner drivers through `fe->ops.tuner_ops.set_params` and optional `fe->ops.i2c_gate_ctrl`. Exported symbol is GPL-only.

Risks and test signals: Exercise attach identity failure, all QAM modes from QAM16 through QAM256, invalid modulation rejection, symbol-rate clamping to 500 ksym/s and `xin/2`, SELAGC selection, PWM restoration, inversion with `config->invert` both ways, AFC correction after lock, counter overflow handling (`0x7f` -> `0xffffffff`), and tuner/I2C failures. Several register writes ignore return values, so I2C errors during tune/init can be hidden.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/ves1820.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/ves1820.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/ves1820.h

Purpose: Public board-driver interface for the VES1820 DVB-C demodulator.

Important APIs/types/functions: Defines `VES1820_SELAGC_PWM`, `VES1820_SELAGC_SIGNAMPERR`, and `struct ves1820_config` with demod I2C address, crystal input frequency `xin`, inversion polarity bit, and SELAGC mode bit. Declares `ves1820_attach(config, i2c, pwm)` when `CONFIG_DVB_VES1820` is reachable and provides a logging `NULL` stub otherwise.

Control flow: Board code constructs a `ves1820_config`, passes it plus an I2C adapter and PWM value to attach, and uses the returned `dvb_frontend` callbacks from `ves1820.c`. The disabled stub returns before any hardware access.

State and persistence: The header has no owned state. Its config struct is read by the implementation for every symbol-rate and inversion calculation, so its lifetime must outlive the attached frontend.

Dependencies/integration: Includes `<linux/dvb/frontend.h>` and participates in DVB frontend attach conventions. Used by PCI/USB bridge board files that provide tuner wiring and crystal details.

Risks and test signals: Compile reachable and disabled Kconfig paths, verify callers keep config storage valid, and test incorrect `xin`, address, `invert`, or `selagc` values because they directly alter register programming and reported symbol-rate limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/ves1820.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/ves1x93.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/ves1x93.c

Purpose: Implements VLSI VES1893/VES1993 DVB-S QPSK demodulators. It identifies chip revision, loads the matching register initialization table, configures inversion/FEC/symbol rate/LNB voltage, exposes an I2C gate for tuner access, and reports lock/statistics through DVB frontend ops.

Important APIs/types/functions: `struct ves1x93_state` owns I2C/config/frontend state, selected init/write tables, demod type, cached inversion, and last tuned frequency. `ves1x93_writereg()`/`ves1x93_readreg()` are I2C register helpers. `ves1x93_set_inversion()`, `ves1x93_set_fec()`, `ves1x93_get_fec()`, and `ves1x93_set_symbolrate()` encode the main tuning parameters. `ves1x93_i2c_gate_ctrl()` toggles reg0 between tuner-gate open and normal states. `ves1x93_attach()` is exported and `ves1x93_ops` supplies the DVB-S frontend methods.

Control flow: Attach allocates state, reads identity register `0x1e`, selects VES1893 tables for `0xdc`/`0xdd` or VES1993 tables for `0xde`, then returns an initialized frontend. Init iterates the chip-specific write table and writes only marked registers, optionally ORing `invert_pwm` into AGC register `0x05`. Tuning calls the external tuner, closes the I2C gate, writes inversion, FEC, and symbol-rate registers, stores cache values, and for VES1893 pulses the clear bit because VES1993 loses lock if that sequence is used. Status reads retry up to ten times when VES1893 reports inconsistent low sync bits and high lock bits.

State and persistence: No persistent storage exists. State persists only while the frontend is attached: selected chip tables, cached inversion for auto-inversion reporting, and last frequency for AFC-corrected `get_frontend()`. Hardware state is volatile register programming.

Dependencies/integration: Depends on Linux I2C, delays, DVB frontend APIs, and `ves1x93.h`. Integrates with external tuner ops through `set_params`, with board LNB control through `set_voltage`, and with tuner drivers through `i2c_gate_ctrl`.

Risks and test signals: Test identity handling for all supported revisions and unknown IDs, VES1893 versus VES1993 symbol-rate behavior, inversion auto/on/off including the documented I/Q swap, FEC rejection outside 1/2..8/9, voltage writes for 13/18/off, I2C gate open/close, status retry loop, AFC frequency correction, and uncorrected-block reset. `ves1x93_readreg()` returns the negative I2C transfer count in an unsigned byte path on read failure, which can look like a valid register value to callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/ves1x93.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/ves1x93.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/ves1x93.h

Purpose: Public attach and configuration header for VES1893/VES1993 DVB-S demodulators.

Important APIs/types/functions: `struct ves1x93_config` supplies demodulator I2C address, crystal input frequency, and `invert_pwm`. `ves1x93_attach(config, i2c)` is declared under `CONFIG_DVB_VES1X93`; the disabled inline stub warns and returns `NULL`.

Control flow: Board drivers pass a static config and I2C adapter to attach. The implementation detects the exact VES chip and returns a frontend with DVB-S ops or `NULL` on probe failure.

State and persistence: The header has no state; config data must remain alive for the attached frontend because the implementation uses it during initialization and symbol-rate programming.

Dependencies/integration: Includes `<linux/dvb/frontend.h>` and follows the media DVB attach pattern.

Risks and test signals: Verify Kconfig-disabled builds, board handling of `NULL` attaches, and config correctness for I2C address, `xin`, and PWM polarity. Header signature changes affect all old DVB-S board files using VES1x93.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/ves1x93.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/z0194a.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/z0194a.h

Purpose: Board-support header for the Sharp Z0194A DVB-S frontend arrangement using STV0299-style demodulator programming. It provides a symbol-rate callback and static initialization table intended to be included by board drivers.

Important APIs/types/functions: `sharp_z0194a_set_symbol_rate(fe, srate, ratio)` chooses ACLK/BCLK values from symbol-rate bands and writes STV0299 registers `0x13`, `0x14`, and ratio registers `0x1f`..`0x21`. `sharp_z0194a_inittab` is a register/value initialization sequence terminated by `0xff, 0xff`, covering oscillator, DAC, DiSEqC/LNB control, AGC, lock detector, FEC thresholds, Viterbi/search, and RS error control registers.

Control flow: Board code includes the header, passes the table to an STV0299 config, and installs the symbol-rate callback. The callback is invoked by the STV0299 demod driver during tuning after it has calculated the ratio value.

State and persistence: No mutable driver state is owned here. The static inittab encodes volatile hardware reset defaults and is copied/written by the demodulator consumer.

Dependencies/integration: Assumes `struct dvb_frontend` and `stv0299_writereg()` are visible from the including source. Integrates with STV0299-based DVB-S bridge drivers rather than registering a module of its own.

Risks and test signals: Test symbol-rate thresholds at 1.5, 3, 7, 14, 30, and 45 Msym/s, ratio byte ordering and masking, table termination, LNB power/DiSEqC defaults, and FEC threshold values. Because this is a header with `static` data/functions, every including translation unit receives its own copy and missing STV0299 declarations fail at compile time.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/z0194a.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/zd1301_demod.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/zd1301_demod.c

Purpose: Implements the ZyDAS ZD1301 DVB-T demodulator as a platform driver. It exposes a DVB frontend, creates an I2C adapter for downstream tuner access through the demodulator's I2C bridge, programs demod registers for DVB-T bandwidths, and uses parent-supplied register callbacks for hardware access.

Important APIs/types/functions: `struct zd1301_demod_dev` owns the platform device, frontend, child I2C adapter, and cached gain. `zd1301_demod_wreg()`/`zd1301_demod_rreg()` call `zd1301_demod_platform_data` callbacks. Frontend ops include `zd1301_demod_init()`, `zd1301_demod_sleep()`, `zd1301_demod_set_frontend()`, `zd1301_demod_get_tune_settings()`, and `zd1301_demod_read_status()`. Exported helpers `zd1301_demod_get_dvb_frontend()` and `zd1301_demod_get_i2c_adapter()` let the parent/bridge wire demod and tuner together. `zd1301_demod_i2c_master_xfer()` implements limited child I2C transactions.

Control flow: Probe validates platform data and parent driver, allocates state, writes initial sleep/bridge registers, registers an I2C adapter named "ZyDAS ZD1301 demod", copies frontend ops, and stores drvdata. `set_frontend()` requires tuner `set_params` and `get_if_frequency`, accepts only IF 36.15 MHz, maps 6/7/8 MHz bandwidth to register `0x6a50`, then writes a fixed register sequence. The child I2C algorithm supports write-read with one address byte and up to eight read bytes, write with one register byte plus up to eight data bytes, and rejects unsupported transfer shapes. Status polls register `0x6a24`, treats values 1..31 as full lock, and updates gain register `0x6a43` if the module parameter changed.

State and persistence: Runtime state includes the module parameter `gain`, cached per-device gain, the registered child I2C adapter, and volatile demod/bridge registers. No firmware or nonvolatile persistence exists.

Dependencies/integration: Depends on platform devices, parent register callbacks, DVB frontend APIs, Linux I2C adapter registration, jiffies/timeouts, and module parameter handling. It is designed to be instantiated by a USB/bridge driver that owns direct register access and tuner attachment.

Risks and test signals: Test missing platform data, no parent driver, I2C adapter registration failure, fixed IF rejection, bandwidth rejection, tuner callback errors, child I2C length/shape limits, bridge transfer timeouts, gain module parameter changes during status polling, and remove cleanup. The I2C bridge polling loops return success even if `0x6804` never clears before timeout, so transfer-timeout behavior deserves hardware validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/zd1301_demod.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/zd1301_demod.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/zd1301_demod.h

Purpose: Public platform-data and accessor header for the ZD1301 demodulator platform driver.

Important APIs/types/functions: `struct zd1301_demod_platform_data` supplies a private callback pointer plus `reg_read()` and `reg_write()` functions for 16-bit register addresses and 8-bit values. When `CONFIG_DVB_ZD1301_DEMOD` is reachable, the header declares `zd1301_demod_get_dvb_frontend()` and `zd1301_demod_get_i2c_adapter()`. Disabled stubs warn and return `NULL`.

Control flow: A parent bridge creates a platform device with this platform data, waits for probe, then calls the exported helpers to get the frontend and child I2C adapter used to attach a tuner. Disabled builds fail early through the stubs.

State and persistence: The header owns no state. Platform data callback lifetime is critical because every hardware register access in the implementation goes through these function pointers.

Dependencies/integration: Includes platform device, DVB frontend, and media DVB frontend headers. It is the coupling point between a parent hardware driver and the ZD1301 demod platform child.

Risks and test signals: Validate callback pointers before instantiation, Kconfig-disabled builds, helper calls before/after probe, and remove ordering so exported pointers are not used after the platform device is gone.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/zd1301_demod.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/zl10036.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/zl10036.c

Purpose: Implements the Zarlink ZL10036 DVB-S silicon tuner. It attaches tuner ops to an existing DVB frontend, initializes tuner registers, calculates PLL divider and baseband filter settings, manages RF loop/gain options, and reports cached tuned frequency.

Important APIs/types/functions: `struct zl10036_state` stores I2C adapter, config, cached frequency, and cached bandwidth filter parameters `br`/`bf`. `zl10036_read_status_reg()` reads the tuner status byte and checks POR/lock bits. `zl10036_write()` writes register sequences. `zl10036_set_frequency()` computes divider from a 10.111 MHz crystal and `_RDIV=10`. `zl10036_set_bandwidth()` clamps requested bandwidth, derives BR/BF, writes only changed values, and toggles RSD. `zl10036_set_gain_params()` encodes charge-pump/gain/RF-loop control. `zl10036_set_params()`, `zl10036_init()`, `zl10036_sleep()`, `zl10036_get_frequency()`, and `zl10036_release()` populate `dvb_tuner_ops`.

Control flow: Attach validates config, allocates state, opens the demod I2C gate, verifies status read, initializes register defaults, closes the gate, installs tuner ops, and stores `fe->tuner_priv`. Init reads status and unconditionally programs defaults. Tuning validates frequency in kHz against frontend bounds, derives bandwidth from symbol rate using DVB-S alpha plus a 3 MHz margin, chooses charge pump by L-band frequency range, opens the I2C gate, writes gain, frequency, and bandwidth, then polls the frequency/phase lock bit up to 20 times.

State and persistence: The tuner stores only runtime cached frequency and BR/BF values. Hardware state is volatile I2C register programming. Module parameter `debug` controls logging.

Dependencies/integration: Depends on Linux I2C, DVB frontend tuner ops, and `zl10036.h`. It relies on a demodulator-provided `i2c_gate_ctrl` when present and assumes frequencies in `dtv_property_cache` are in kHz for its validation/math.

Risks and test signals: Test attach with missing config, absent chip, initialization failures, RF-loop enable/disable, frequency boundaries 950..2175 MHz, symbol-rate-derived filter clamping 8..35 MHz, lock polling, cached frequency rounding, sleep wake paths, and I2C gate closure on every error. `zl10036_init()` returns directly on status-read failure before closing the I2C gate, which is a gate-state risk.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/zl10036.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/zl10036.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/zl10036.h

Purpose: Public configuration and attach header for the Zarlink ZL10036 DVB-S tuner.

Important APIs/types/functions: `struct zl10036_config` contains `tuner_address` and `rf_loop_enable`. `zl10036_attach(fe, config, i2c)` attaches tuner ops to an existing frontend when `CONFIG_DVB_ZL10036` is reachable; otherwise the inline stub warns and returns `NULL`.

Control flow: Board drivers create a config and call attach after demod frontend creation. The implementation updates `fe->tuner_priv` and `fe->ops.tuner_ops` on success.

State and persistence: No state in the header. The config pointer is retained by the implementation and must remain valid while attached.

Dependencies/integration: Includes Linux I2C and media DVB frontend headers. Integrates tuner hardware into demod/board drivers via standard DVB tuner ops.

Risks and test signals: Build reachable and disabled Kconfig combinations, ensure board code handles `NULL`, and verify config lifetime/address/RF-loop values because they directly drive I2C transactions and tuner register bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/zl10036.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/zl10039.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/zl10039.c

Purpose: Implements the Zarlink ZL10039 DVB-S tuner. It validates the chip ID, installs tuner ops, performs reset/sleep, and programs PLL/RF/baseband registers from DVB-S frequency and symbol-rate requests.

Important APIs/types/functions: `struct zl10039_state` stores I2C adapter, address, and chip ID. Register enum names PLL, RF, baseband, LO, and general registers. `zl10039_read()`/`zl10039_write()` provide bounded I2C access, with `MAX_XFER_SIZE` guarding block writes. `zl10039_init()` resets and wakes the tuner. `zl10039_sleep()` writes power-down. `zl10039_set_params()` computes PLL divider, reference divider, RF control, and baseband cutoff then writes them as a six-byte block. `zl10039_attach()` verifies `GENERAL` register low nibble equals `ID_ZL10039`, installs `zl10039_ops`, and stores state in `fe->tuner_priv`.

Control flow: Attach opens the demod I2C gate, reads `GENERAL`, closes the gate, masks the ID, checks it, then copies tuner ops. Init opens the gate, writes reset (`0x40`) and wake (`0x01`) to `GENERAL`, then closes the gate. Tune derives the divider assuming a 10.111 MHz crystal and reference ratio 80, derives baseband filter from symbol rate, opens the gate, enables filter adjustment through `BASE1`, writes PLL0..BASE1 values, disables adjustment, and closes the gate on the success path.

State and persistence: Runtime state is only I2C adapter/address/ID. Programmed tuner registers are volatile. Module parameter `debug` controls logging.

Dependencies/integration: Depends on Linux I2C, DVB frontend tuner ops, and `zl10039.h`. It depends on a demodulator I2C gate when present and is normally attached by a board-specific demod setup.

Risks and test signals: Test chip-ID mismatch, I2C read/write failures, reset write behavior where an error is logged as normal, frequency/symbol-rate calculations for overflow and zero/low symbol rate, gate closure on error paths in init/sleep/tune, and block write bounds. In `zl10039_set_params()` and some init/sleep errors, failures before the success-path gate close can leave the gate open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/zl10039.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/zl10039.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/zl10039.h

Purpose: Public attach header for the Zarlink ZL10039 DVB-S tuner.

Important APIs/types/functions: Declares `zl10039_attach(struct dvb_frontend *fe, u8 i2c_addr, struct i2c_adapter *i2c)` when `CONFIG_DVB_ZL10039` is reachable. The disabled inline stub warns and returns `NULL`.

Control flow: Board code calls attach with a demod frontend, tuner address, and I2C adapter. On success the implementation installs tuner ops on the frontend; on disabled builds the stub performs no hardware access.

State and persistence: No state is owned here. Attached implementation state is stored under `fe->tuner_priv`.

Dependencies/integration: Relies on DVB frontend and I2C types being visible from including code. This legacy header does not include those headers itself, so inclusion order matters.

Risks and test signals: Compile users with reachable/disabled Kconfig, verify include dependencies, and ensure callers tolerate `NULL`. Runtime board tests should confirm correct 7-bit/8-bit I2C address usage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/zl10039.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/zl10353.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/zl10353.c

Purpose: Implements the Zarlink ZL10353, Intel CE6230, and Intel CE6231 DVB-T demodulator frontend. It handles I2C register access, hard/soft reset, DVB-T TPS hint programming, tuner interaction through either secondary-bus PLL register writes or external tuner ops, status/statistic reads, and attach probing.

Important APIs/types/functions: `struct zl10353_state` owns I2C, embedded frontend, copied config, cached bandwidth/frequency, and accumulated uncorrected blocks. `zl10353_single_write()`, `zl10353_write()`, and `zl10353_read_register()` implement I2C register access. `zl10353_calc_nominal_rate()` and `zl10353_calc_input_freq()` derive TRL/input-frequency register values from config clock/IF. Frontend ops include `zl10353_init()`, `zl10353_sleep()`, `zl10353_i2c_gate_ctrl()`, `zl10353_set_parameters()`, `zl10353_get_parameters()`, status/BER/strength/SNR/ucblocks readers, and `zl10353_get_tune_settings()`. `zl10353_attach()` probes `CHIP_ID`.

Control flow: Attach allocates state, copies config, reads `CHIP_ID`, accepts ZL10353/CE6230/CE6231 IDs, and returns a frontend. Init optionally dumps registers, adjusts reset attach bytes for parallel TS and board clock overrides, and writes the reset sequence only if key registers differ. Tuning resets the demod, configures AGC/acquisition controls, programs bandwidth-specific MCLK/unknown registers, writes nominal rate and input frequency, validates and encodes TPS hints from code rates/modulation/transmission mode/guard interval/hierarchy, then either calls an external tuner (`no_tuner`) or obtains PLL bytes from tuner `calc_regs` and writes them through the demod. It finally starts either `FSM_GO` or `TUNER_GO`.

State and persistence: Runtime state includes cached requested frequency/bandwidth and cumulative uncorrected-block count. Register programming is volatile and recalculated on init/tune. Module parameters `debug` and `debug_regs` affect logging and full register dumps.

Dependencies/integration: Depends on Linux I2C, DVB frontend APIs, `zl10353.h`, and `zl10353_priv.h`. It can bridge to a tuner on the demod secondary I2C bus via PLL register writes, or coordinate an external tuner through frontend tuner ops.

Risks and test signals: Test accepted and rejected chip IDs, 6/7/8 MHz bandwidth paths, defaulting unsupported bandwidth to 8 MHz, all TPS enum validation branches, `no_tuner` versus `calc_regs` paths, I2C gate disabled mode, parallel TS and clock override config, register dump mode, TPS readback only after FE/TPS lock, accumulated uncorrected blocks, and I2C read/write failures. Several write return values in tuning/init are ignored, so hardware programming failures may not propagate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/zl10353.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/zl10353.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/zl10353.h

Purpose: Public configuration and attach header for the ZL10353-family DVB-T demodulator.

Important APIs/types/functions: `struct zl10353_config` supplies demod I2C address, optional ADC clock and IF2 values in 0.1 kHz units, `no_tuner`, `parallel_ts`, optional I2C gate-disable bit, and clock-control overrides `clock_ctl_1` and `pll_0`. `zl10353_attach(config, i2c)` is declared when `CONFIG_DVB_ZL10353` is reachable; disabled builds use a warning `NULL` stub.

Control flow: Board drivers pass a populated config to attach and then wire tuner ops according to `no_tuner`/secondary-bus expectations. The implementation copies the config, so stack/static lifetime is less fragile than headers that store the pointer.

State and persistence: No mutable header state. Config fields become per-frontend runtime state in `zl10353.c`.

Dependencies/integration: Includes DVB frontend API types and follows DVB demod attach conventions.

Risks and test signals: Validate clock/IF units, `no_tuner` behavior, parallel serial TS selection, gate-disable boards, and Kconfig-disabled build coverage. Incorrect clock values feed fixed-point register calculations and can prevent lock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/zl10353.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/zl10353_priv.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/zl10353_priv.h

Purpose: Private register-map header for the ZL10353-family DVB-T demodulator implementation.

Important APIs/types/functions: Defines supported chip IDs `ID_ZL10353`, `ID_CE6230`, and `ID_CE6231`, byte extraction macros `msb()` and `lsb()`, and `enum zl10353_reg_addr` for interrupt/status/statistics, TPS, clock, reset, AGC, acquisition, TRL, input-frequency, tuner/FSM start, chip ID, and timing registers.

Control flow: This file has no executable logic. `zl10353.c` uses the enum names to address hardware registers during attach, init, tuning, status reads, and statistics reads.

State and persistence: No runtime state. It encodes the stable hardware ABI expected by `zl10353.c`.

Dependencies/integration: Included by the ZL10353 implementation before the public config header. Consumers outside the implementation should not depend on it.

Risks and test signals: Register-address drift causes silent hardware misprogramming. Tests should cover attach ID reads, each status/statistic register path, TPS register encoding/decoding, and clock/reset register overrides so enum changes are caught quickly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/zl10353_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/firewire/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/firewire/Kconfig

Purpose: Kconfig fragment for Digital Everywhere FireDTV/FloppyDTV FireWire DVB adapters.

Important APIs/types/functions: The fragment is active only when `DVB_CORE && FIREWIRE`. `config DVB_FIREDTV` is a tristate that builds the `firedtv` module. Nested `config DVB_FIREDTV_INPUT` is a derived boolean enabling remote-control input support when `INPUT` availability matches the FireDTV build mode.

Control flow: Selecting `DVB_FIREDTV` enables the FireWire DVB driver objects from the Makefile. Selecting or deriving `DVB_FIREDTV_INPUT` adds remote-control input code. The visible comment groups these under FireWire adapters in media configuration.

State and persistence: Kconfig choices determine compile-time module composition and the presence of input support. No runtime state is defined here.

Dependencies/integration: Integrates with the kernel media Kconfig hierarchy, DVB core, FireWire core, and input subsystem. The Makefile consumes `CONFIG_DVB_FIREDTV` and `CONFIG_DVB_FIREDTV_INPUT`.

Risks and test signals: Build matrix should cover disabled, built-in, module, and input-enabled/disabled combinations. The derived input expression must avoid invalid built-in/module combinations where input support would be unavailable to the FireDTV object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/firewire/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/firewire/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/firewire/Makefile

Purpose: Build rules for the FireDTV FireWire DVB driver.

Important APIs/types/functions: `obj-$(CONFIG_DVB_FIREDTV) += firedtv.o` declares the composite module. `firedtv-y` includes `firedtv-avc.o`, `firedtv-ci.o`, `firedtv-dvb.o`, `firedtv-fe.o`, and `firedtv-fw.o`; `firedtv-$(CONFIG_DVB_FIREDTV_INPUT)` conditionally adds `firedtv-rc.o`.

Control flow: Kbuild links the listed objects into one `firedtv` module or built-in object according to Kconfig. Remote-control code is compiled only when input support is enabled.

State and persistence: No runtime state. The object list defines link-time feature composition.

Dependencies/integration: Consumes symbols from the FireDTV source files and Kconfig symbols. The base objects share `firedtv.h` internal APIs.

Risks and test signals: Build with and without `CONFIG_DVB_FIREDTV_INPUT`, and ensure every cross-file symbol remains present in the selected object set. Missing `firedtv-rc.o` must be covered by inline stubs in `firedtv.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/firewire/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/firewire/firedtv-avc.c -->
# sources/distributed-fs/ceph-client/drivers/media/firewire/firedtv-avc.c

Purpose: Implements FireDTV AV/C/FCP command transport and command encoding. It sends tuner, PID filter, LNB, remote-control, conditional-access, and CMP connection commands over FireWire, parses AV/C responses into DVB status/CA data, and serializes access to the shared command/reply buffer.

Important APIs/types/functions: `struct avc_command_frame` and `struct avc_response_frame` map the 512-byte AV/C payload. `avc_write()` sends `fdtv->avc_data` to the FCP command register with retries and waits for `avc_recv()`. Public routines include `avc_tuner_dsd()`, `avc_tuner_set_pids()`, `avc_tuner_get_ts()`, `avc_identify_subunit()`, `avc_tuner_status()`, `avc_lnb_control()`, `avc_register_remote_control()`, CA helpers (`avc_ca_app_info()`, `avc_ca_info()`, `avc_ca_reset()`, `avc_ca_pmt()`, `avc_ca_get_time_date()`, `avc_ca_enter_menu()`, `avc_ca_get_mmi()`), remote re-registration work, and CMP helpers `cmp_establish_pp_connection()`/`cmp_break_pp_connection()`.

Control flow: Command callers lock `fdtv->avc_mutex`, build an AV/C frame in `fdtv->avc_data`, set length, call `avc_write()`, optionally validate the response now stored in the same buffer, then unlock. `avc_recv()` is invoked by the FireWire FCP address handler; it handles remote-control notify frames specially, otherwise copies replies into `avc_data`, marks `avc_reply_received`, and wakes waiters. DVB-S/S2 tuning uses vendor QPSK commands, DVB-C/T tuning uses standard DSD multiplex descriptors plus active PID filters. CA ioctl paths in `firedtv-ci.c` call vendor host2CA/CA2host helpers, including PMT rewriting into a TS PMT object with CRC. CMP helpers use compare-swap locks on output plug control registers.

State and persistence: Shared runtime state lives in `struct firedtv`: `avc_mutex`, wait queue, reply flag, `avc_data_length`, `avc_data`, voltage/tone cache, active PID bitmap, and CA command state. Module parameters `debug` and `fake_ca_system_ids` affect logging and CA-info synthesis. No nonvolatile persistence exists.

Dependencies/integration: Depends on FireDTV FireWire backend functions `fdtv_write/read/lock`, DVB frontend property enums, DVB DiSEqC/CA data shapes, CRC32 for PMT CRC, workqueues for remote control, and `firedtv.h`. It is called by frontend, demux, CI, RC, and bus layers.

Risks and test signals: Test FCP timeout/retry behavior, out-of-order responses, remote-control changed/interim notifications, all frontend type tuning encoders, PID count and full-TS paths, LNB DiSEqC lengths, tuner-status descriptor validation, CA object length parsing, PMT bounds and CRC, fake CA IDs, and CMP compare-swap retry/online/channel cases. Many CA responses are marked FIXME for response/data validation, and all command/reply traffic shares one 512-byte buffer, so malformed device payloads and concurrent notify traffic need careful fuzz/hardware testing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/firewire/firedtv-avc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/firewire/firedtv-ci.c -->
# sources/distributed-fs/ceph-client/drivers/media/firewire/firedtv-ci.c

Purpose: Implements DVB Conditional Access device support for FireDTV. It exposes a DVB CA device, maps CA ioctls to FireDTV AV/C CA commands, parses EN50221 message tags, and reports CI slot capability/status.

Important APIs/types/functions: `fdtv_ca_ready()` and `fdtv_get_ca_flags()` translate tuner-status CA bits. `fdtv_ca_get_caps()`, `fdtv_ca_get_slot_info()`, `fdtv_ca_get_msg()`, and `fdtv_ca_send_msg()` implement CA ioctl operations. `fdtv_ca_pmt()` strips the EN50221 length wrapper and forwards PMT payloads to `avc_ca_pmt()`. `fdtv_ca_ioctl()` dispatches `CA_RESET`, `CA_GET_CAP`, `CA_GET_SLOT_INFO`, `CA_GET_MSG`, and `CA_SEND_MSG`. `fdtv_ca_register()` conditionally registers `DVB_DEVICE_CA`, and `fdtv_ca_release()` unregisters it.

Control flow: During DVB registration, FireDTV queries tuner status and registers CA only when the module is present, initialized, error-free, and marked DVB. Userspace sends CA messages through DVB generic ioctl; the driver stores the last EN50221 tag in `fdtv->ca_last_command`, performs immediate actions for CA PMT/menu/reset, and defers app-info/CA-info response generation until `CA_GET_MSG`. Poll always reports readable.

State and persistence: Per-device state includes `fdtv->cadev`, `ca_last_command`, and `ca_time_interval`. State is runtime only. CA readiness comes from live tuner-status descriptors; no CAM data is persisted.

Dependencies/integration: Depends on Linux DVB CA uAPI, DVB device registration, FireDTV AV/C CA helpers, and `struct firedtv_tuner_status`. Integrated into `fdtv_dvb_register()`/`fdtv_dvb_unregister()`.

Risks and test signals: Test module absent/not-ready cases, slot number validation, CA PMT short/extended length parsing and bounds, unknown message/ioctl rejection, app-info and CA-info request/response ordering, date-time request handling, poll behavior, and unregister when `cadev` is absent. `fdtv_ca_release()` unconditionally calls `dvb_unregister_device(fdtv->cadev)`, so failed CA registration paths should be checked for NULL-safe behavior in the DVB core or guarded by callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/firewire/firedtv-ci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/firewire/firedtv-dvb.c -->
# sources/distributed-fs/ceph-client/drivers/media/firewire/firedtv-dvb.c

Purpose: Registers FireDTV as a DVB adapter/demux/frontend/network device and maps demux feed start/stop events to FireDTV PID filter AV/C commands.

Important APIs/types/functions: Channel helpers `alloc_channel()`, `collect_channels()`, and `dealloc_channel()` manage up to 16 hardware PID channels using `fdtv->channel_active` and `channel_pid`. Public demux callbacks are `fdtv_start_feed()` and `fdtv_stop_feed()`. `fdtv_dvb_register()` creates the DVB adapter, demux, dmxdev, memory/frontend connection, DVB net, frontend, and optional CA device. `fdtv_dvb_unregister()` tears them down.

Control flow: Feed start validates demux feed type and PES type, takes `demux_mutex`, allocates a channel, records the PID, collects all active PIDs, and either requests full TS for PID 8192 or programs the current PID set with `avc_tuner_set_pids()`. Feed stop handles DVB core decoder bookkeeping, clears the channel, recollects PIDs, and updates the device filters. DVB registration performs staged setup with failure labels unwinding in reverse order; unregister mirrors successful setup.

State and persistence: Runtime state includes DVB adapter/demux objects, `demux_mutex`, active-channel bitmap, per-channel PID array, adapter module option `adapter_nr`, and CA registration state. No persistent storage exists.

Dependencies/integration: Depends on DVB core, demux, dmxdev, dvbnet, FireDTV frontend/CA/AVC helpers, and `firedtv.h`. It is called by the FireWire probe/remove path in `firedtv-fw.c`.

Risks and test signals: Test all registration failure labels, adapter numbering, 16-channel exhaustion, PID 8192 full-TS path, section and TS feed types, invalid PES/feed type rejection, start error rollback, stop with decoder/non-packet feeds, and concurrent feed operations. The code relies on feed-private channel indices remaining valid and on `demux_mutex` covering PID bitmap updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/firewire/firedtv-dvb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/firewire/firedtv-fe.c -->
# sources/distributed-fs/ceph-client/drivers/media/firewire/firedtv-fe.c

Purpose: Builds the FireDTV DVB frontend operations table and translates DVB frontend callbacks into AV/C tuner, LNB, and isochronous stream operations.

Important APIs/types/functions: `fdtv_dvb_init()` establishes a FireWire CMP point-to-point connection and starts isochronous reception. `fdtv_sleep()` stops isochronous reception and breaks CMP. `fdtv_diseqc_send_master_cmd()`, `fdtv_set_tone()`, and `fdtv_set_voltage()` update LNB state/commands. Status/stat readers call `avc_tuner_status()`. `fdtv_set_frontend()` calls `avc_tuner_dsd()`. `fdtv_frontend_init()` fills `fdtv->fe.ops` and capabilities for DVB-S, DVB-S2, DVB-C, or DVB-T models.

Control flow: Frontend init is called during DVB adapter registration after the model type was detected. Opening the frontend chooses an isochronous channel from adapter number, establishes CMP on the model subunit, and starts the FireWire ISO context. Tuning encodes current properties into AV/C. Status reads fetch a fresh tuner-status descriptor and map `no_rf` to no lock or otherwise report full lock. Sleep tears down ISO/CMP and resets `isochannel` to -1.

State and persistence: Runtime state includes `fdtv->isochannel`, cached voltage/tone values, frontend ops/info, and model type. Hardware state is live FireWire/CMP and AV/C tuner state.

Dependencies/integration: Depends on DVB frontend APIs, FireDTV AV/C/CMP helpers, and FireWire ISO backend functions. It is the interface between DVB frontend core and the FireDTV transport layer.

Risks and test signals: Test every model type's delsys/caps/frequency limits, init failure when CMP or ISO start fails, sleep after partial init, DiSEqC command forwarding, tone/voltage defaults before first tune, status behavior for `no_rf`, unsupported ucblocks, and model detection failure. Isochannel selection is a FIXME and uses adapter number rather than IRM allocation, so multi-device/channel collision tests matter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/firewire/firedtv-fe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/firewire/firedtv-fw.c -->
# sources/distributed-fs/ceph-client/drivers/media/firewire/firedtv-fw.c

Purpose: Provides the FireDTV FireWire bus backend. It handles FireWire transactions, isochronous MPEG-TS reception, FCP response routing, device probe/remove/update, model detection, DVB/RC registration, and module init/exit address-handler registration.

Important APIs/types/functions: `node_req()` wraps `fw_run_transaction()` for lock/read/write operations exported as `fdtv_lock()`, `fdtv_read()`, and `fdtv_write()`. ISO receive state is `struct fdtv_ir_context`; `queue_iso()`, `handle_iso()`, `fdtv_start_iso()`, and `fdtv_stop_iso()` manage receive buffers and feed TS packets to `dvb_dmx_swfilter_packets()`. `handle_fcp()` routes FCP responses to the matching `struct firedtv` in `node_list`. Probe/remove/update callbacks are `node_probe()`, `node_remove()`, and `node_update()`. Module init registers an FCP response address handler and the FireWire driver.

Control flow: Probe allocates and initializes `struct firedtv`, reads the CSR model string, maps it to a model enum, registers remote control if enabled, adds the node to the global list for FCP routing, identifies the AV/C subunit, registers DVB devices, and registers remote-control notifications. Remove unregisters DVB, removes the node from FCP routing, unregisters RC, and frees state. ISO start creates a FireWire receive context, initializes DMA pages, queues 64 packets, starts matching all tags, and stores the context; the callback strips ISO/CIP/source headers and sends 188-byte MPEG-TS packets to the demux.

State and persistence: Global runtime state is `node_list` protected by `node_list_lock` and one FCP address handler. Per-device state is `struct firedtv`, including workqueue item, mutexes, DVB objects, ISO context pointer, model type, subunit, and channel. No persistent storage exists.

Dependencies/integration: Depends on Linux FireWire core, FireWire CSR constants, DMA page-backed ISO buffers, DVB demux, and all FireDTV internal modules. The device ID table matches Digital Everywhere OUIs/models/specifier/version.

Risks and test signals: Test probe failure unwind at every stage, model string length/matching, FCP routing across bus generation changes, node update while streaming, ISO packet length/header parsing, queue/requeue failures, stop with missing context, remove while work/ISO/FCP callbacks are active, and multiple devices. `fdtv_stop_iso()` assumes `fdtv->ir_context` is valid, and model type defaults to zero if no string matches, so invalid hardware paths require coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/firewire/firedtv-fw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/firewire/firedtv-rc.c -->
# sources/distributed-fs/ceph-client/drivers/media/firewire/firedtv-rc.c

Purpose: Adds optional Linux input support for FireDTV remote-control notifications. It registers an input device, supplies keymaps for current and older remotes, and translates AV/C remote codes into key press/release events.

Important APIs/types/functions: `oldtable` maps older 0x4501..0x451f and 0x4540..0x4542 codes. `keytable` maps 2008-era 0x0300..0x031f and 0x0340..0x0354 codes. `fdtv_register_rc()` allocates and registers `input_dev`, copies the mutable keytable to `idev->keycode`, and sets supported key bits. `fdtv_unregister_rc()` cancels remote work, frees keycode storage, and unregisters input. `fdtv_handle_rc()` maps a received vendor code to a key and emits press/release syncs.

Control flow: FireWire probe registers RC before adding the node to FCP routing. `avc_recv()` handles remote-control changed notifications, calls `fdtv_handle_rc()`, and schedules work to re-register for notify events. Remove cancels that work via unregister. Invalid codes are logged and ignored.

State and persistence: Runtime state is the input device pointer and copied keycode table in `fdtv->remote_ctrl_dev`. Keymaps are not persisted beyond input core runtime configuration.

Dependencies/integration: Depends on Linux input subsystem, workqueues, and `firedtv.h`. Compiled only when `CONFIG_DVB_FIREDTV_INPUT`; otherwise header stubs make callers no-ops.

Risks and test signals: Test allocation failures, input registration failure unwind, keymap mutability via input core, all supported code ranges, invalid code logging, work cancellation during remove, and disabled-input builds. `fdtv_unregister_rc()` assumes registration succeeded and `remote_ctrl_dev` is valid, so caller ordering and failure paths need coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/firewire/firedtv-rc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/firewire/firedtv.h -->
# sources/distributed-fs/ceph-client/drivers/media/firewire/firedtv.h

Purpose: Shared internal interface for the FireDTV FireWire DVB driver. It defines common model/status/device state structures and cross-file function prototypes used by AVC, CI, DVB, frontend, FireWire backend, and remote-control modules.

Important APIs/types/functions: `struct firedtv_tuner_status` is the parsed AV/C tuner-status descriptor with RF, BER, signal, C/N, voltage, and CA bits. `enum model_type` identifies unknown, DVB-S, DVB-C, DVB-T, and DVB-S2 devices. `struct firedtv` aggregates device pointer/list membership, DVB adapter/demux/frontend/net/CA objects, AV/C synchronization and buffer state, remote-control work/input state, model/subunit/isochannel, LNB tone/voltage, demux PID filter state, and a 512-byte AV/C data buffer. Prototypes expose the cross-module FireDTV APIs.

Control flow: FireWire probe allocates `struct firedtv`, initializes locks/work, detects model/subunit, then calls functions declared here to register DVB, RC, CA, AV/C, and ISO components. During runtime DVB frontend/demux/CA callbacks all converge on the shared state and AVC helpers.

State and persistence: This header defines the central per-device runtime state. It is all volatile kernel memory; hardware state lives in FireWire/CMP/AVC transactions and is reconstructed on probe/init/tune.

Dependencies/integration: Includes Linux DVB uAPI, media DVB core, demux, dvbnet, mutex/spinlock/wait/workqueue types, and FireWire matching types. It provides input stubs when `CONFIG_DVB_FIREDTV_INPUT` is disabled.

Risks and test signals: Cross-file changes to `struct firedtv` affect lifetime, locking, and callback assumptions across the whole module. Tests should stress concurrent AV/C commands, demux feed changes, remote notifications, CA ioctls, ISO start/stop, remove/update, and disabled RC builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/firewire/firedtv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/Kconfig

Purpose: Central Kconfig menu for V4L2 media I2C subdevice drivers, including camera sensors, lenses, flash devices, audio/video decoders, video encoders, SDR tuners, helper chips, and serializers/deserializers.

Important APIs/types/functions: The file is gated by `if VIDEO_DEV`. Relevant entries in this subset are `VIDEO_AD5820` under `VIDEO_CAMERA_LENS` with `depends on I2C && GPIOLIB`, `MEDIA_CONTROLLER`, and `VIDEO_V4L2_SUBDEV_API`; `VIDEO_ADP1653` under flash devices with `depends on I2C && GPIOLIB && MEDIA_CAMERA_SUPPORT`; `VIDEO_ADV7170` and `VIDEO_ADV7175` under "Video encoders" with `depends on VIDEO_DEV && I2C`. The file also sources nested Kconfigs such as `ccs`, `et8ek8`, and `cx25840`.

Control flow: Menuconfig symbols group large families and hide ancillary subdrivers when `MEDIA_HIDE_ANCILLARY_SUBDRV` is set. Selecting a tristate here controls Makefile object inclusion and, for some camera/lens symbols, selects media-controller/subdev support needed by the implementation.

State and persistence: Kconfig selections are compile-time state controlling which modules are built and which helper frameworks are selected. No runtime state exists.

Dependencies/integration: Integrated with the media subsystem Kconfig tree, I2C, V4L2, media controller, GPIO, OF, ACPI, regmap, and helper subsystem symbols. `drivers/media/i2c/Makefile` consumes these symbols.

Risks and test signals: Build all relevant symbols as disabled/built-in/module, especially dependency combinations for lens/flash media-controller support and old video encoders. Kconfig dependency mistakes surface as missing types/functions at compile time or unusable menus for board configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/Makefile

Purpose: Kbuild object list for media I2C V4L2 subdevice drivers.

Important APIs/types/functions: Maps Kconfig symbols to objects and subdirectories. Relevant subset mappings are `CONFIG_VIDEO_AD5820 -> ad5820.o`, `CONFIG_VIDEO_ADP1653 -> adp1653.o`, `CONFIG_VIDEO_ADV7170 -> adv7170.o`, and `CONFIG_VIDEO_ADV7175 -> adv7175.o`. It also defines composite `msp3400-objs` and routes large drivers like `adv748x/`, `ccs/`, and `cx25840/` into subdirectories.

Control flow: Kbuild includes each object according to the resolved tristate. Directory entries delegate to nested Makefiles. Object order is mostly a flat list and does not encode runtime ordering.

State and persistence: No runtime state. The file defines link-time module composition.

Dependencies/integration: Consumes the symbols declared in `drivers/media/i2c/Kconfig` and must stay in sync with source filenames and module names.

Risks and test signals: Build with each relevant Kconfig symbol as module and built-in, confirm object names match source files, and audit additions/removals so stale entries do not break allmodconfig or leave Kconfig options without build products.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ad5820.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/ad5820.c

Purpose: V4L2 subdevice driver for AD5820/AD5821 camera voice-coil lens focus DACs. It exposes an absolute-focus control, manages regulator/GPIO power, restores focus state after power transitions, and registers a media-entity lens subdevice.

Important APIs/types/functions: `struct ad5820_device` owns the V4L2 subdev, VANA regulator, control handler, focus/ramp settings, optional enable GPIO, power mutex/count, and standby flag. `ad5820_write()` sends a 16-bit big-endian DAC/status word over I2C. `ad5820_update_hw()` encodes ramp time/mode, focus absolute, and power-down bit. `ad5820_power_on()`/`ad5820_power_off()` manage regulator/GPIO and optional standby write. Controls are initialized in `ad5820_init_controls()` and handled by `ad5820_set_ctrl()`. Probe/remove register/unregister the async subdev and media entity.

Control flow: Probe obtains the VANA regulator and optional enable GPIO, initializes locks and subdev metadata, creates a lens media entity, and asynchronously registers the subdev. Internal `registered` callback creates V4L2 controls. Opening the subdev powers on and restores hardware state; close powers down into standby. `s_power` uses a reference count so multiple opens/users only toggle hardware on 0->1 and 1->0 transitions. PM suspend powers off without standby if active; resume powers on and restores settings.

State and persistence: Runtime state includes cached focus absolute, ramp settings, standby flag, and power_count. Hardware programming is volatile and restored from cached values after power-on/resume. There is no nonvolatile persistence.

Dependencies/integration: Depends on I2C, regulator consumer API, GPIO descriptors, V4L2 controls/subdev/async registration, and media entity APIs. Device matching supports I2C IDs `ad5820`/`ad5821` and OF compatibles `adi,ad5820`/`adi,ad5821`.

Risks and test signals: Test regulator/GPIO probe deferral, async subdev registration failure unwind, open/close power refcounting, suspend/resume while active/inactive, focus control writes with power off/on, I2C write failures, and negative power_count warnings. `ad5820_set_ctrl()` writes hardware without explicitly checking power state, so control access while powered down should be validated against V4L2 core locking/use patterns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ad5820.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/adp1653.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/adp1653.c

Purpose: V4L2 subdevice driver for the Analog Devices ADP1653 LED flash controller. It exposes flash/torch/indicator controls, parses platform data or devicetree limits, handles software strobe, fault reporting/clearing, and simple power control.

Important APIs/types/functions: The main state type `struct adp1653_flash` is defined in `<media/i2c/adp1653.h>` and stores subdev, platform data, controls, fault cache, power lock/count, and control pointers. `adp1653_update_hw()` writes OUT_SEL and CONFIG from current controls. `adp1653_get_fault()` reads/accumulates the fault register and clears faults by disabling output. `adp1653_strobe()` performs software flash strobe. `adp1653_init_controls()` creates V4L2 flash controls. `adp1653_of_init()` parses `flash` and `indicator` child nodes plus enable GPIO. `__adp1653_set_power()` and `adp1653_set_power()` manage platform or GPIO power and power refcounting.

Control flow: Probe allocates state, obtains platform data from DT or legacy board data, initializes the power mutex, initializes an I2C V4L2 subdev with devnode flag, creates controls, initializes a zero-pad flash media entity, and sets function `MEDIA_ENT_F_FLASH`. Opening powers on and initializes the device; close powers off. Control set/get first reads/clears faults; fatal faults can block strobe/intensity/mode changes. Flash mode writes timer config; torch mode writes high-power LED intensity immediately; software strobe toggles the strobe register.

State and persistence: Runtime state includes V4L2 control values, cached fault bits, platform limits, enable GPIO/power callback, and power_count. Fault bits are accumulated until read by the volatile fault control, then cleared in software. Hardware state is volatile and rebuilt on power-on.

Dependencies/integration: Depends on I2C SMBus, V4L2 subdev/control APIs, media entity API, GPIO descriptors, OF parsing, and the ADP1653 media platform header. It supports both DT and legacy platform data.

Risks and test signals: Test DT parsing missing flash/indicator properties, GPIO probe deferral, platform power callback errors, fault bit handling and clear sequence, all V4L2 flash controls, strobe in non-flash mode, timeout/intensity unit conversions, suspend/resume active/inactive, and media entity cleanup. Probe does not call async subdev registration in this file, so integration users should verify expected registration path for this legacy driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/adp1653.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/adv7170.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/adv7170.c

Purpose: V4L2 I2C subdevice driver for Analog Devices ADV7170/ADV7171 analog video encoders. It programs PAL/NTSC register tables, switches between decoder pass-through and playback input modes, and exposes basic media bus format negotiation.

Important APIs/types/functions: `struct adv7170` stores the V4L2 subdev, a 128-byte software register cache, current norm, and input. `adv7170_write()`, `adv7170_read()`, and `adv7170_write_block()` perform SMBus/raw I2C register access; block writes use auto-increment when `I2C_FUNC_I2C` is available and update the cache. `adv7170_s_std_output()` programs NTSC/PAL tables and resets timing. `adv7170_s_routing()` selects pass-through or playback input. Pad ops enumerate/get/set `MEDIA_BUS_FMT_UYVY8_2X8` and `MEDIA_BUS_FMT_UYVY8_1X16`.

Control flow: Probe requires SMBus byte-data support, allocates state, initializes the subdev, defaults to NTSC pass-through, writes the NTSC table, toggles TR0 reset, and reads revision. Standard changes write the matching register table, optionally enable genlock for pass-through, pulse TR0 reset, and cache the norm. Routing writes MR/TR/genlock registers for decoder or ZR36060 source and caches input. Active format set toggles bit `0x40` in register `0x07`; try formats are accepted without hardware writes.

State and persistence: Runtime state is the cached register array plus current norm/input. Hardware state is volatile I2C register programming and is not restored from PM hooks in this file.

Dependencies/integration: Depends on I2C/SMBus, V4L2 subdev/video/pad APIs, media bus format constants, and board drivers that instantiate the I2C client. Module parameter `debug` controls V4L2 debug logging.

Risks and test signals: Test adapters with and without raw I2C, PAL/NTSC switching, invalid standard/input/format rejection, register-cache consistency after failed block writes, pass-through genlock behavior, and remove unregister. Width/height are returned as zero in format get, reflecting legacy encoder behavior; callers must tolerate that.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/adv7170.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/adv7175.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/adv7175.c

Purpose: V4L2 I2C subdevice driver for Analog Devices ADV7175/ADV7176 analog video encoders. It initializes encoder registers, supports PAL/NTSC/SECAM-ish output programming, switches among pass-through/playback/color-bar inputs, controls power, and exposes simple media bus formats.

Important APIs/types/functions: `struct adv7175` stores subdev, current norm, and input. `adv7175_write()`, `adv7175_read()`, and `adv7175_write_block()` perform register I/O with raw-I2C auto-increment fallback to SMBus. `set_subcarrier_freq()` adjusts NTSC subcarrier registers for pass-through stability. `adv7175_init()` writes the common init table. `adv7175_s_std_output()`, `adv7175_s_routing()`, pad format ops, and `adv7175_s_power()` provide the V4L2 behavior.

Control flow: Probe checks SMBus byte-data support, allocates state, initializes the subdev, defaults to NTSC/pass-through, writes `init_common`, pulses TR0 reset, and reads revision for debug. Standard changes write PAL/NTSC tables or PAL-with-genlock-disabled for SECAM input conversion attempts, then reset timing. Routing writes source and genlock/subcarrier controls for decoder pass-through, ZR36060 playback, or color bar. Active format set toggles bit `0x40` in register `0x07`. Power on/off writes register `0x01` to active or low-power values.

State and persistence: Runtime state is current norm/input. Hardware register state is volatile and not restored by PM code here.

Dependencies/integration: Depends on I2C/SMBus, V4L2 subdev core/video/pad APIs, and board-level I2C instantiation. Module parameter `debug` controls logging.

Risks and test signals: Test PAL/NTSC/SECAM paths, all routing inputs, color-bar mode, power toggling, invalid format/input/std rejection, adapters without raw I2C, and write failures in block initialization. Like ADV7170, get_fmt reports zero dimensions; consumers should rely on code/colorspace rather than size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/adv7175.c -->
