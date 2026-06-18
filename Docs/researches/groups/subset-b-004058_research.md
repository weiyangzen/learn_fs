# Research: subset-b-004058

Grouped research for DiBcom DVB frontend drivers in `sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dib7000m.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dib7000m.c

## Purpose

`dib7000m.c` is the Linux DVB demodulator driver for DiBcom DiB7000MA/MB/PA/PB/MC-family COFDM chips. It implements a `dvb_frontend_ops` instance for DVB-T reception, handles direct register access over I2C, initializes chip clocks/GPIO/output paths, runs AGC and optional autosearch, tunes a found channel, and exposes helper APIs for downstream tuners or board drivers such as gated I2C access and PID filtering.

The driver is hardware-sequencing code. Most meaningful behavior is encoded as ordered writes to fixed chip registers, with state cached in `struct dib7000m_state` so later tuning, bandwidth, diversity, and stats operations can reuse the previous hardware state.

## Important APIs, Types, And Functions

`struct dib7000m_state` owns the private frontend state: embedded `struct dvb_frontend demod`, copied `struct dib7000m_config`, I2C address/adapter, `dibx000_i2c_master`, revision/register-offset handling, current AGC and bandwidth state, timing frequency (`timf` and default), diversity flags, AGC state-machine cursor, and reusable I2C buffers protected by `i2c_buffer_lock`.

Low-level I2C helpers are `dib7000m_read_word()`, `dib7000m_write_word()`, and `dib7000m_write_tab()`. The read path uses two I2C messages and sets bit 7 in the high register byte; the write path sends a four-byte register/value transaction. `dib7000m_write_tab()` applies run-length encoded default register tables and compensates register addresses 112 through 331 when `reg_offs` is set for 7000MC-like revisions.

Initialization and hardware identity are handled by `dib7000m_attach()`, `dib7000m_identify()`, `dib7000m_demod_reset()`, `dib7000m_reset_pll()`, `dib7000mc_reset_pll()`, `dib7000m_reset_gpio()`, `dib7000m_set_power_mode()`, and `dib7000m_set_adc_state()`. `dib7000m_attach()` allocates state, copies frontend ops, identifies vendor/device IDs, initializes the nested DiBcom I2C master, resets the demod, and returns the embedded frontend.

Tuning functions are `dib7000m_set_frontend()`, `dib7000m_agc_startup()`, `dib7000m_set_agc_config()`, `dib7000m_update_lna()`, `dib7000m_set_channel()`, `dib7000m_autosearch_start()`, `dib7000m_autosearch_is_irq()`, and `dib7000m_tune()`. These convert DVB frontend properties into register fields and run a multi-step AGC sequence before autosearch or final tune.

External helper APIs are exported with symbols: `dib7000m_attach()`, `dib7000m_get_i2c_master()`, `dib7000m_pid_filter_ctrl()`, and `dib7000m_pid_filter()`. A disabled `#if 0` enumeration helper remains in the file for prototype boards but is not compiled.

The `dib7000m_ops` frontend ops advertise `SYS_DVBT` and implement `.init`, `.sleep`, `.set_frontend`, `.get_frontend`, `.get_tune_settings`, and basic status/stat reads.

## Control Flow

Attach starts with `dib7000m_attach()`: allocate zeroed state, copy board config, set I2C metadata, initialize the mutex, cache `timf_default`, identify vendor `0x01b3` and supported revisions `0x4000` through `0x4003`, initialize the proper `dibx000_i2c_master` flavor, then call `dib7000m_demod_reset()`.

Reset powers all blocks, enables VBG, toggles demod reset registers, configures either old PLL or MC PLL layout, resets GPIOs, disables output, unforces diversity-start state, sets 8 MHz bandwidth defaults, calibrates the slow ADC, selects DVB-T output where requested, configures mobile/baseband behavior, writes default register tables, then drops to interface-only power.

`dib7000m_set_frontend()` first disables output, programs bandwidth, calls tuner `.set_params` if present, runs `dib7000m_agc_startup()` until it returns `-1`, optionally launches autosearch when key DVB-T parameters are automatic, reads discovered TPS with `dib7000m_get_frontend()`, runs `dib7000m_tune()`, and finally enables MPEG2 FIFO output.

`dib7000m_agc_startup()` is a cursor in `state->agc_state`. It powers analog/AGC blocks and ADCs, selects a band-specific AGC config, calls optional board `agc_control` before and after startup, handles WBD split search when soft split is not used, lets board LNA updates restart AGC, then applies soft split and exits.

`dib7000m_set_channel()` maps `dtv_frontend_properties` transmission mode, guard interval, modulation, hierarchy, and code rate into chip registers, computes diversity sync wait, enables/disables diversity combination, chooses channel-estimation coefficients by modulation, and sets power for autosearch. `dib7000m_tune()` restarts the demod, powers additional blocks, adjusts loop parameters by FFT mode, updates `timf` on lock, and reapplies bandwidth scaling.

Read operations are simple register decoders: `dib7000m_read_status()` maps lock bits from register 535 to `FE_HAS_*`; BER, uncorrected blocks, and signal strength read fixed counters/registers. `read_snr` is a stub returning zero.

## State And Persistence Behavior

Persistent driver state is memory resident in `dib7000m_state`. Important fields include `revision`, `reg_offs`, `current_band`, `current_bandwidth`, `current_agc`, `timf`, `timf_default`, `internal_clk`, `div_state`, `div_force_off`, `div_sync_wait`, and `agc_state`.

Hardware state is persisted in the demodulator until reset, sleep, or new tuning writes replace it. Power mode, ADC state, PLL configuration, AGC thresholds, output mode, PID filters, timing frequency, and diversity controls are all register-backed. `timf` is learned from lock feedback and reused on later bandwidth programming, making lock history part of future tuning behavior.

The I2C transfer buffers are shared per state and serialized by `i2c_buffer_lock`. There is no filesystem persistence, firmware load, or NVM interaction in this file.

## Dependencies And Integration Points

The file depends on kernel I2C, mutex, allocation, sleep, and DVB frontend APIs. It consumes `dib7000m_config` from `dib7000m.h` and common DiBcom types/macros from `dibx000_common.h`, including AGC configs, bandwidth configs, output-mode constants, ADC states, I2C master helpers, and `BAND_OF_FREQUENCY`/bandwidth conversion macros.

Board drivers integrate by calling `dib7000m_attach()`, supplying tuner callbacks through `fe->ops.tuner_ops`, and optionally supplying `update_lna` and `agc_control` callbacks in config. Tuners behind the demod use `dib7000m_get_i2c_master()`. Transport stream consumers rely on the selected output mode, hardcoded here to FIFO after tuning.

## Risks And Edge Cases

Many register writes ignore individual failure returns, especially reset and power sequencing. `dib7000m_read_word()` returns zero on lock interruption or I2C failure, which can be indistinguishable from a valid hardware value and can alter subsequent register decisions.

Autosearch uses a fixed 800 ms polling loop and returns success/failure by IRQ bits; timeout or failure returns `0` from `set_frontend()`, so callers may need status polling to distinguish no-channel from a successful ioctl path.

The code contains hardcoded hierarchy expressions such as `HIERARCHY_1` and literal conditions that effectively force HP/native choices. Hierarchical DVB-T behavior is only partially represented.

Revision-specific register offsets and special handling for 0x4003/MC revisions are brittle. A missed offset or unsupported revision could corrupt adjacent registers. The driver explicitly rejects DiB7000PC in this driver path.

`read_snr` is not implemented. Signal strength is inverted AGC only, not calibrated dBm. PID filter index bounds are not checked locally.

## Test Signals

Useful validation signals are successful attach/identify logs for each supported revision, I2C transfer success across read/write paths, stable reset and sleep/wakeup cycles, successful tuner `.set_params` plus AGC startup, autosearch success with automatic DVB-T parameters, TPS values returned by `get_frontend()`, `FE_HAS_LOCK` from `read_status()`, nonzero BER/UCB counters on impaired signals, and PID filter register effects on transport output.

Regression tests should cover both 0x4000 and `reg_offs` revisions, baseband versus IF tuner config, hostbus diversity and normal MPEG output, board callbacks that change LNA, and I2C failure handling during attach and tuning.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dib7000m.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dib7000m.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dib7000m.h

## Purpose

`dib7000m.h` is the public interface for the DiB7000M/early DiB7000P DVB-T demodulator driver. It defines board-provided configuration data, default constants, GPIO helper macros, and the externally callable attach/I2C/PID-filter APIs used by bridge and tuner drivers.

## Important APIs, Types, And Functions

`struct dib7000m_config` is the key integration type. It carries demod mode flags (`dvbt_mode`, `mobile_mode`, `hostbus_diversity`, `tuner_is_baseband`), transport output formatting (`output_mpeg2_in_188_bytes`), clocking (`quartz_direct`, `input_clk_is_div_2`), GPIO defaults (`gpio_dir`, `gpio_val`, `gpio_pwm_pos`, `pwm_freq_div`), AGC table pointers/counts, bandwidth config pointer, and optional board callbacks `update_lna()` and `agc_control()`.

GPIO macros define default all-output/all-zero states and nibble placement helpers for four PWM positions. `DEFAULT_DIB7000M_I2C_ADDRESS` is 18, matching the shifted address convention used by the C driver.

When `CONFIG_DVB_DIB7000M` is reachable, the header declares `dib7000m_attach()`, `dib7000m_get_i2c_master()`, `dib7000m_pid_filter()`, and `dib7000m_pid_filter_ctrl()`. Otherwise it provides inline stubs that warn and return `NULL` or `-ENODEV`.

## Control Flow

The header itself contains no runtime control flow beyond Kconfig-gated inline stubs. In enabled builds, board code calls `dib7000m_attach()` with an I2C adapter, device address, and persistent config object. After attach, board code may request the demod-hosted I2C adapter with `dib7000m_get_i2c_master()` or control PID filters.

## State And Persistence Behavior

The config object is copied into private driver state during attach, so callers can usually keep static const board data. Pointers inside the config, such as AGC and bandwidth tables, still need valid lifetime for driver use because the C file copies the pointer values, not deep contents.

No file or kernel-global state is stored by this header. Hardware persistence is driven by the implementation after it consumes these fields.

## Dependencies And Integration Points

The header includes `dibx000_common.h` for common AGC/bandwidth types, I2C interface enums, output modes, ADC states, and DVB frontend declarations. It is included by the driver implementation and by board/bridge modules that instantiate DiB7000M devices.

The callback hooks integrate board-specific LNA and AGC sequencing with generic demod code. GPIO fields let boards define reset-time pin state without custom code.

## Risks And Edge Cases

Config fields are mostly raw hardware knobs with no validation in the header. Invalid AGC counts/pointers, missing bandwidth config, wrong clock flags, or inconsistent GPIO defaults can cause attach failure or bad RF behavior later.

The disabled-driver stubs use `printk(KERN_WARNING ...)`; callers must handle `NULL` or `-ENODEV` gracefully when the module is not built. The TODO block lists historical APIs that are not available through this Linux header.

## Test Signals

Compile coverage should include both reachable and non-reachable Kconfig paths. Runtime validation should verify that board configs with multiple AGC bands, custom LNA callbacks, and GPIO/PWM defaults are correctly reflected in the `dib7000m.c` reset and tune sequences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dib7000m.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dib7000p.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dib7000p.c

## Purpose

`dib7000p.c` is the Linux DVB frontend driver for the second-generation DiBcom DiB7000P/7000PC COFDM demodulator family, with additional DiB7090 SoC support. It implements DVB-T frontend operations, chip reset and tuning, I2C bus and tuner-interface bridging, PID filtering, DVBv5 statistics, and an exported ops-table attachment model used by bridge drivers.

Unlike `dib7000m.c`, this file's public attach entry `dib7000p_attach()` fills a caller-provided `struct dib7000p_ops` table rather than returning a frontend directly. The actual frontend is created later by the populated `ops->init` callback (`dib7000p_init()`).

## Important APIs, Types, And Functions

`struct dib7000p_state` embeds `struct dvb_frontend demod`, copied `struct dib7000p_config`, I2C metadata, `dibx000_i2c_master`, current AGC/bandwidth/timing state, diversity fields, GPIO cache, SoC version, DiB7090 tuner adapter, I2C transfer buffers/mutex, MPEG input-mode state, and DVBv5 stat counters/timers.

Register access is through `dib7000p_read_word()`, `dib7000p_write_word()`, and `dib7000p_write_tab()`. These serialize shared buffers with `i2c_buffer_lock` and treat a failed I2C transfer as debug output plus zero or `-EREMOTEIO`.

Core demod setup is handled by `dib7000p_init()`, `dib7000p_identify()`, `dib7000p_demod_reset()`, `dib7000p_reset_pll()`, `dib7000p_update_pll()`, `dib7000p_set_power_mode()`, `dib7000p_set_adc_state()`, `dib7000p_reset_gpio()`, and `dib7000p_cfg_gpio()`.

Tuning uses `dib7000p_set_frontend()`, `dib7000p_agc_startup()`, `dib7000p_set_agc_config()`, `dib7000p_set_dds()`, `dib7000p_set_channel()`, `dib7000p_autosearch_start()`, `dib7000p_autosearch_is_irq()`, `dib7000p_spur_protect()`, and `dib7000p_tune()`.

Stats and signal reporting include `dib7000p_read_status()`, `dib7000p_read_ber()`, `dib7000p_read_unc_blocks()`, `dib7000p_read_signal_strength()`, `dib7000p_get_snr()`, `dib7000p_read_snr()`, `dib7000p_reset_stats()`, `interpolate_value()`, `dib7000p_get_time_us()`, and `dib7000p_get_stats()`. These fill legacy read callbacks and DVBv5 `dtv_property_cache` counters/scales.

DiB7090-specific integration includes `dib7090_tuner_xfer()`, APB/SERPAR access helpers, `dib7090_get_i2c_tuner()`, `dib7090_set_output_mode()`, `dib7090_set_diversity_in()`, DibStream mux helpers, `dib7090_tuner_sleep()`, `dib7090_get_adc_power()`, and `dib7090_slave_reset()`.

## Control Flow

`dib7000p_attach()` validates the ops pointer and installs callback function pointers. A board driver then calls `ops->init()`, which allocates state, copies config, initializes frontend ops, detects the demod at the I2C address, reads `version`, initializes `dibx000_i2c_master`, registers a synthetic DiB7090 tuner I2C adapter, resets the demod, resets DVBv5 stats, and configures DiB7090 output/diversity defaults when `version == SOC7090`.

Reset powers all blocks, resets the DiBcom I2C master for SOC7090, enables VBG, toggles restart registers, resets PLL and GPIO, disables output, calibrates slow ADC, unforces diversity enumeration state, sets default bandwidth and IQ correction, writes default register table, sets clock drive registers for non-SOC7090, and powers down to interface-only mode.

`dib7000p_set_frontend()` disables output/diversity path, copies the module-level `buggy_sfn_workaround` flag into state, calls tuner `.set_params`, loops through AGC startup until complete, optionally autosearches unknown DVB-T parameters, reads discovered TPS, runs `dib7000p_tune()`, then enables the configured output mode. For SOC7090 it routes through MPEG mux and DibStream paths when needed.

`dib7000p_agc_startup()` is similar to 7000M but includes SOC7090 gain-update period and ADC enable registers plus DDS offset programming based on the tuner-reported actual frequency. The WBD split path and LNA callback path restart AGC as needed.

`dib7000p_tune()` writes channel parameters, restarts the demod, applies SFN workaround loop settings when enabled, waits for initial timing update if needed, adjusts loop parameters by FFT mode, restarts FEC if lock is absent, updates `timf` when lock appears, optionally programs spur-protection notch coefficients, reapplies bandwidth, and resets stats.

The DiB7090 tuner adapter maps selected tuner I2C register addresses either to APB demod registers or to SERPAR register numbers, waits for FIFO overflow/empty conditions, and returns the requested I2C transfer count on emulated success.

## State And Persistence Behavior

The driver maintains memory state for current band, current AGC table, bandwidth, learned `timf`, diversity status, GPIO direction/value, SoC version, saved tuner-enable state, input MPEG mode, and DVBv5 counter timers. Hardware state persists in demod registers and DiB7090 mux/APB/SERPAR blocks until reset or rewritten.

`wbd_ref` overrides the AGC table WBD value after `set_wbd_ref()`. `timf` is learned from registers 427/428 and reused by later `set_bandwidth()` calls. DVBv5 counters are cumulative in `dtv_property_cache`; the driver updates them on jiffies-based intervals and resets them on tuning.

The DiB7090 tuner I2C adapter is registered in `dib7000p_init()` and removed in `dib7000p_release()`. The `i2c_master` is initialized at attach/init and torn down in release.

## Dependencies And Integration Points

The file depends on kernel I2C, allocation, mutex, division helpers, `intlog10`, jiffies timing, and DVB frontend APIs. It consumes `dib7000p.h` and `dibx000_common.h` for config, ops, AGC/bandwidth structures, output modes, and common I2C master support.

Bridge drivers integrate through `struct dib7000p_ops`, not direct symbols for every helper. Tuners integrate via frontend `tuner_ops`, DiBcom gated I2C adapters, or the DiB7090 synthetic tuner adapter. Board policy enters through config callbacks `update_lna` and `agc_control`, GPIO defaults, spur-protect flag, output-mode choices, PLL/table settings, and diversity delay.

## Risks And Edge Cases

Busy waits for PLL lock and tuner SERPAR status can spin up to fixed loop counts and in PLL cases may spin indefinitely if hardware never reports lock. Many reset/tune writes ignore per-register errors.

`dib7000p_get_adc_power()` computes a LUT index from measured mantissa without explicit bounds checking; unexpected raw power values could index outside the table. The DiB7090 I2C emulation often returns `num` for ignored registers, which may hide unsupported tuner operations.

Autosearch timeout and no-channel paths return zero from `set_frontend()`, relying on later status to expose lack of lock. The module-level `buggy_sfn_workaround` affects all devices.

Signal strength dBm is empirical and board-specific. The comment notes the calibration may differ across devices and inputs. DVBv5 block-error accounting appears to add UCB deltas and then later add the current absolute value in the same PER window, which deserves scrutiny if counters look inflated.

PID filter index bounds are not checked. I2C read failure returns zero, which can be consumed as a real register value.

## Test Signals

Validation should include successful ops-table population, `ops->init()` attach on DiB7000PC and SOC7090 variants, reset/sleep/wakeup, tuner adapter registration/removal, GPIO updates, PLL update behavior, AGC startup with and without WBD split, DDS offset when tuner-reported frequency differs, spur-protection enabled, automatic and manual DVB-T parameter tuning, SFN workaround enabled, output modes for smooth block and DiB7090 MPEG mux, DVBv5 stat scale/counter updates, PID filtering, and multi-demod I2C enumeration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dib7000p.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dib7000p.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dib7000p.h

## Purpose

`dib7000p.h` defines the board-facing interface for the DiB7000P/7000PC DVB-T demodulator driver and its DiB7090-adjacent helper operations. It provides the configuration structure consumed by `dib7000p_init()` and an ops table populated by `dib7000p_attach()`.

## Important APIs, Types, And Functions

`struct dib7000p_config` contains output formatting, hostbus diversity, tuner/baseband behavior, optional `update_lna` callback, AGC tables, bandwidth config, GPIO defaults, PWM divider, clock/direct crystal flag, spur-protect flag, optional `agc_control` callback, output mode, sample-and-hold/current-mirror flags, diversity delay, default I2C address, and MPEG output enable flag.

`struct dib7000p_ops` is the exported integration surface. It includes callbacks for WBD reference, AGC value reads, AGC minimum changes, PLL updates, GPIO, timing-frequency control, device detection, gated I2C master access, PID filtering, I2C enumeration, DiB7090 tuner adapter access, tuner sleep, ADC power, slave reset, and frontend initialization.

The only exported attach declaration is `void *dib7000p_attach(struct dib7000p_ops *ops)`. When the driver is disabled by Kconfig, an inline stub warns and returns `NULL`.

## Control Flow

Enabled callers allocate or embed a `struct dib7000p_ops`, call `dib7000p_attach(&ops)`, then use the populated callbacks. The actual frontend allocation is performed by `ops.init(i2c_adap, i2c_addr, cfg)`, not by `dib7000p_attach()` itself. Helper callbacks remain accessible through the same ops table for board/tuner coordination.

## State And Persistence Behavior

The config is copied into private state by `dib7000p_init()` while pointer fields such as AGC and bandwidth tables continue to reference caller-owned storage. The ops table is mutated in place by `dib7000p_attach()` and must remain available to the caller.

This header stores no runtime state. Runtime state is in `struct dib7000p_state` inside the C file and in chip registers.

## Dependencies And Integration Points

The header depends on `dibx000_common.h` for shared DiBcom types and macros. It is consumed by bridge drivers that support DiB7000P/DiB7090 hardware and by the driver implementation.

The ops-table pattern lets one module publish many helper hooks without exporting each helper symbol. It also supports SoC-specific functions such as synthetic tuner I2C access and slave reset.

## Risks And Edge Cases

Because `dib7000p_attach()` mutates a caller-provided table, callers must check the returned pointer and not assume callbacks are valid when Kconfig disables the driver. Missing config pointers or invalid output-mode/default-address combinations are not validated in the header.

Several bitfields and flags are hardware-specific; wrong settings can silently produce bad output routing or analog behavior. `default_i2c_addr` semantics differ from the plain default constant and are interpreted by enumeration code.

## Test Signals

Compile tests should cover enabled and disabled Kconfig paths. Runtime integration tests should verify that every ops callback expected by a board driver is non-NULL after attach, that `ops.init()` can create and release a frontend, and that config fields for output mode, spur protection, GPIO, and diversity delay are reflected in register programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dib7000p.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dib8000.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dib8000.c

## Purpose

`dib8000.c` is the Linux DVB frontend driver for DiBcom DiB8000-family ISDB-T demodulators, including DiB8096P support. It implements ISDB-T tuning for 13-segment and sound-broadcasting modes, per-layer parameter programming and stats, diversity chains across up to six frontends, DiB8096P tuner/mux bridging, I2C enumeration, PID filtering, and an ops-table attachment model.

This is the most complex file in the group because ISDB-T carries layered modulation/FEC/interleaving state, TMCC-discovered parameters, optional manual mode, subchannel PRBS handling, and multi-demod diversity coordination.

## Important APIs, Types, And Functions

`struct dib8000_state` owns copied `dib8000_config`, an `i2c_device` wrapper, `dibx000_i2c_master`, WBD/AGC/timing state, diversity and AGC cursors, revision, tune state/status, up to `MAX_NUMBER_OF_FRONTENDS` frontend pointers, I2C buffers/mutex, DiB8096P tuner adapter, segment masks, layer metadata, autosearch state, found FFT/guard, subchannel/symbol-duration/timeouts, output mode, and DVBv5 stat timers.

I2C helpers include `dib8000_i2c_read16()`, `__dib8000_read_word()`, `dib8000_read_word()`, `dib8000_read32()`, `dib8000_i2c_write16()`, and `dib8000_write_word()`. The `i2c_device` form is used for temporary enumeration and normal state-backed access.

Hardware setup functions include `dib8000_init()`, `dib8000_identify()`, `dib8000_reset()`, `dib8000_set_power_mode()`, `dib8000_set_adc_state()`, `dib8000_reset_pll()`, `dib8000_update_pll()`, `dib8000_reset_gpio()`, `dib8000_set_gpio()`, `dib8000_sad_calib()`, and `dib8090p_init_sdram()`.

ISDB-T channel programming is centered on `dib8000_set_layer()`, `dib8000_adp_fine_tune()`, `dib8000_update_ana_gain()`, `dib8000_load_ana_fe_coefs()`, `dib8000_get_init_prbs()`, `dib8000_set_13seg_channel()`, `dib8000_set_sb_channel()`, `dib8000_small_fine_tune()`, and `dib8000_set_isdbt_common_channel()`.

Tuning is split across `dib8000_set_frontend()`, `dib8000_agc_startup()`, `dib8000_tune()`, `dib8000_autosearch_start()`, `dib8000_autosearch_irq()`, `is_manual_mode()`, `dib8000_get_frontend()`, and helpers for DDS offset, loop parameters, demod restart, sync wait, timeouts, tune state, and lock reads.

DiB8096P-specific helpers mirror the DiB7090 style: host-bus drive, DibStream Tx/Rx config, MPEG mux config, host/DibTx mux selection, diversity input routing, output mode selection, SERPAR/APB tuner I2C emulation, tuner sleep, ADC/DC power helpers, and synthetic tuner adapter creation.

Stats functions include `dib8000_read_status()`, `dib8000_read_ber()`, `dib8000_read_unc_blocks()`, `dib8000_read_signal_strength()`, `dib8000_get_snr()`, `dib8000_read_snr()`, `dib8000_get_time_us()`, and `dib8000_get_stats()`, with per-layer register tables for BER/PER counters.

The exported public entry is `dib8000_attach()`, which fills a caller-supplied `struct dib8000_ops`. The actual frontend allocation occurs through the populated `ops->init` callback.

## Control Flow

`dib8000_attach()` fills an ops table with helper functions for initialization, PLL, GPIO, PWM AGC reset, tuner access, diversity slave frontends, tune-state access, I2C enumeration, PID filtering, timing-frequency control, ADC/DC power, and WBD reference.

`dib8000_init()` allocates private state and a separate `struct dvb_frontend`, copies config, wires the `i2c_device` buffers, sets output default to FIFO unless a supported explicit output is provided, installs frontend ops, identifies the chip, initializes the DiBcom I2C master, registers the DiB8096P tuner adapter, resets the demod, sets BER RS length, and returns the frontend.

`dib8000_reset()` identifies revision `0x8000`, `0x8001`, `0x8002`, or `0x8090`, resets the DiBcom I2C master, powers all blocks, toggles reset registers, configures pad drives and PLL, resets GPIO/output, writes default register table, clears ISDB-T loaded state, unforces diversity enumeration state, sets 6 MHz default bandwidth, calibrates ADC/SAD, configures BER length, enters interface-only power, and resets stats.

`dib8000_set_frontend()` synchronizes the requested `dtv_property_cache` to all linked frontends, configures diversity and output modes for each chip, calls each tuner `.set_params`, runs AGC startup across master and slave frontends until all reach `CT_AGC_STOP`, then runs the demod tune state machine on every frontend until the master and all slaves stop. If any frontend succeeds during autosearch, it reads TMCC parameters and restarts the others with those discovered parameters.

`dib8000_tune()` is a nonblocking-style state machine driven by `frontend_tune_state`. It resets stats, initializes SDRAM for 0x8090, decides manual versus auto mode, sets DDS offset and bandwidth, runs FFT and guard autosearch when needed, programs ISDB-T channel and loop parameters, restarts the demod, waits for COFF/CPIL/lmod4 locks with symbol-derived timeouts, handles diversity input fallback, starts Viterbi/channel decoder, waits for MPEG/data locks by layer/interleaver depth, and for some SB modes iterates PRBS subchannels.

`dib8000_get_frontend()` reads TMCC-derived ISDB-T parameters only after sync is present, preferring a slave frontend with TMCC lock if available. It synchronizes discovered mode, guard, inversion, partial reception, and per-layer segment/interleaving/FEC/modulation data across all frontend caches.

## State And Persistence Behavior

Important persistent memory state includes chip `revision`, `current_agc`, `current_band`, learned `timf`, `timf_default`, `diversity_onoff`, `differential_constellation`, `tune_state`, `status`, linked `fe[]` pointers, `seg_mask`, `seg_diff_mask`, `mode`, per-layer segment counts, autosearch phase, found FFT/guard, SB subchannel, symbol duration, timeout, longest interleaver layer, output mode, tuner-enable cache, and DVBv5 stat timers.

Hardware persistence is register-backed. PLL, ADC, power, GPIO, output mux, MPEG/DibStream routing, AGC, DDS offset, ISDB-T layer descriptors, segment masks, PRBS seed, lock masks, loop parameters, interleaver/SDRAM, PID filters, and stat counters live in chip registers until reset or reprogramming.

Multi-frontend chains persist through `state->fe[]`; `dib8000_set_slave_frontend()` appends slave frontend pointers, and release detaches slave frontends before freeing master state. `dtv_property_cache` is explicitly copied across linked frontends to keep diversity chips coherent.

DVBv5 counters are cumulative and jiffies-throttled. `init_ucb` stores an offset for uncorrected-block counters; BER timers exist for all layers and per layer. There is no filesystem persistence or firmware load in this file.

## Dependencies And Integration Points

The driver depends on kernel I2C, mutex, allocation, jiffies/sleep timing, division helpers, `intlog10`, DVB frontend APIs, `dib8000.h`, and `dibx000_common.h`.

Board/bridge drivers integrate through `struct dib8000_ops` populated by `dib8000_attach()`. They then call `ops.init()` to obtain a frontend, optionally chain frontends with `set_slave_frontend()`, control PLL/GPIO/WBD/PID filters, access gated I2C, use the DiB8096P tuner adapter, and monitor tune state.

Tuners integrate through normal frontend `tuner_ops` and through DiB8096P APB/SERPAR emulated I2C. Board callbacks `update_lna` and `agc_control` customize AGC behavior. Config fields control output routing, hostbus diversity, pad drives, GPIO defaults, ref clock selection, MPEG output muxing, PLL tables, and diversity delay.

## Risks And Edge Cases

The tuning state machine is timing-sensitive and relies on jiffies, symbol-duration calculations, fixed sleeps, and hardware lock bits. Incorrect frontend cache values or partial manual parameters force auto mode or can make manual mode fail to lock.

Multiple paths return success while failing to lock, exposing failure only through frontend status. I2C read failures return zero and can be misinterpreted as real register state. Many register writes during reset/tune ignore return values.

Revision-specific register offsets and alternate 0x8090 behavior are widespread. A new chip revision or wrong `is_dib8096p` enumeration flag could program the wrong APB, mux, ADC, or lock registers.

The multi-frontend chain assumes shared configuration and synchronous progression. A bad slave can delay or alter master tuning, and release recursively detaches slave frontends, so ownership must be clear to board drivers.

DiB8096P tuner emulation trusts message lengths in several paths less defensively than normal I2C clients. SERPAR/APB mappings silently ignore unsupported registers by returning `num`.

Stats are empirical and timing-derived. Signal dBm tables are board-specific; per-layer block counting uses estimated bitrate and may not match all ISDB-T modes. Some C expressions around deeper interleaver selection use layer 0's interleaving while iterating layers, which is a risk signal if timeout behavior looks wrong.

## Test Signals

Key validation signals include attach/init/reset on 0x8001, 0x8002, and 0x8090 hardware; I2C enumeration across multiple demods; slave frontend chaining; sleep/wakeup propagation to slaves; tuner `.set_params` calls on every frontend; AGC progression to `CT_AGC_STOP`; auto mode finding FFT/guard/TMCC and synchronizing caches; manual mode lock with full per-layer parameters; 13-seg and 1/3-seg sound-broadcasting modes; PRBS subchannel iteration; diversity input/output routing; DiB8096P MPEG mux and DibStream output modes; PID filter programming; per-layer BER/PER stat increments; and calibrated signal/SNR changes under RF impairment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dib8000.c -->
