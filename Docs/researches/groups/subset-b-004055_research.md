# Research group subset-b-004055

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cx24120.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cx24120.c

Purpose: Linux DVB frontend driver for the Conexant CX24120/CX24118 DVB-S/S2 demodulator/tuner, used by boards such as Technisat Skystar S2. It exposes `cx24120_attach()` and a `dvb_frontend_ops` table for satellite tuning, DiSEqC, LNB voltage/tone, status, DVBv3 counters, and DVBv5 statistics.

Important APIs and functions: low-level I2C access is handled by `cx24120_readreg()`, `cx24120_writereg()`, and chunked `cx24120_writeregs()`, honoring `config->i2c_wr_max`. Firmware-mailbox operations use `struct cx24120_cmd`, `cx24120_message_send()`, and `cx24120_message_sendrcv()`. `cx24120_attach()` validates chip revision `0x07` or `0x05`, copies `cx24120_ops`, and stores private state in `frontend.demodulator_priv`. `cx24120_init()` performs cold one-time hardware setup, uploads `dvb-fe-cx24120-1.20.58.2.fw` through the board-supplied firmware callback, starts the tuner, programs VCO/bandwidth/MPEG output, reads firmware version, and initializes statistics. Tuning is via `cx24120_tune()`/`cx24120_set_frontend()`.

Control flow: attach probes the revision register; init uploads firmware and prepares MPEG/BER infrastructure; set frontend validates `SYS_DVBS` or `SYS_DVBS2`, translates inversion/FEC/pilot/symbol-rate into firmware values, sends `CMD_TUNEREQUEST`, and writes clock dividers. `read_status()` maps hardware bits into `FE_HAS_*`; once lock is seen, it programs MPEG clock ratios, enables MPEG output, and clears `need_clock_set`. Statistics are refreshed from firmware/register counters by `cx24120_get_stats()`.

State and persistence: `struct cx24120_state` caches current/next tuning (`dcur`/`dnxt`), cold-init state, MPEG enable state, pending clock setup, last frontend status, BER/PER timing, bitrate, previous BER, and UCB offset. There is no disk persistence; all state is per attached frontend and reset by release.

Dependencies and integration: depends on Linux I2C, firmware loading, `media/dvb_frontend.h`, DVB core status/stat APIs, and the board config from `cx24120.h`. Integration is through legacy attach/export, tuner-contained firmware commands, and DVB SEC callbacks.

Risks and test signals: firmware upload is mandatory and fragile; one error log uses `ret` rather than the final-byte register when firmware verification fails. `cx24120_writeregs()` sets `msg.len` to payload length before copying `max` bytes but allocates `max + 1`, so I2C provider limits and chunk boundaries need coverage. MPEG output is disabled around many commands; regressions show up as lost transport stream after tune/DiSEqC. Test with valid/invalid revisions, missing firmware, DVB-S and DVB-S2 lock, DiSEqC timeout, stats scaling, repeated retune, and `i2c_wr_max` smaller than firmware payload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cx24120.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cx24120.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cx24120.h

Purpose: public configuration header for the CX24120/CX24118 DVB-S/S2 driver. It describes the board-provided parameters needed by `cx24120.c` and conditionally exposes the attach API.

Important APIs and types: `struct cx24120_initial_mpeg_config` carries three board-specific MPEG output bytes used during `CMD_MPEG_INIT`. `struct cx24120_config` contains the demodulator I2C address, crystal frequency in kHz, initial MPEG config, a board-specific `request_firmware()` callback, and `i2c_wr_max` for controllers with limited I2C write sizes. `cx24120_attach()` returns a `struct dvb_frontend *` when `CONFIG_DVB_CX24120` is reachable; otherwise the inline stub warns and returns `NULL`.

Control flow and integration: this header is consumed by board drivers that instantiate the frontend. The implementation reads the config directly during attach, firmware load, VCO setup, MPEG output setup, and chunked firmware writes. The `request_firmware` indirection lets legacy media drivers supply the firmware mechanism rather than requiring direct global firmware access.

State and persistence: the header defines no runtime state itself. The pointed-to `cx24120_config` must remain valid for the lifetime of the frontend because the driver stores the pointer rather than copying the contents.

Dependencies: includes Linux DVB frontend and firmware definitions. Kconfig reachability controls whether callers link to the real attach symbol or receive a build-time-safe stub.

Risks and test signals: board data quality is critical. A wrong `xtal_khz` affects VCO and clock ratios, bad MPEG bytes affect transport stream output, a missing firmware callback prevents init, and too-large `i2c_wr_max` assumptions can break firmware upload on constrained adapters. Tests should verify disabled-Kconfig behavior, config lifetime assumptions, and representative board configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cx24120.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cx24123.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cx24123.c

Purpose: legacy DVB-S/QPSK frontend driver for Conexant CX24123 demodulator with CX24109/CX24113 tuner integration. It exposes `cx24123_attach()`, an optional tuner I2C adapter, and DVB callbacks for tuning, status, BER, signal strength, SNR, DiSEqC, tone, and voltage.

Important APIs and functions: `cx24123_i2c_readreg()`/`cx24123_i2c_writereg()` access the demodulator. `cx24123_set_inversion()`, `cx24123_set_fec()`, and `cx24123_set_symbolrate()` program demod acquisition. `cx24123_pll_calculate()`, `cx24123_pll_writereg()`, and `cx24123_pll_tune()` compute and transmit tuner VCA/VGA/band/PLL words unless `dont_use_pll` delegates to external tuner ops. `cx24123_repeater_mode()` and the `cx24123_tuner_i2c_algo` expose a repeater bus for external tuners. `cx24123_initfe()` writes the register default table.

Control flow: attach allocates state, reads revision `0xe1`/`0xd1`, copies `cx24123_ops`, then always creates a child tuner I2C adapter. Init writes defaults and polarity/repeater settings. `set_frontend()` calls board `set_ts_params()`, caches requested frequency/symbol rate, programs inversion/FEC/symbol rate, tunes either internal PLL or external tuner, triggers acquisition reset, and invokes an optional AGC callback. `tune()` optionally calls set-frontend, reads status unless oneshot mode is requested, and returns a 100 ms delay.

State and persistence: private state caches PLL programming words, `demod_rev`, `currentfreq`, and `currentsymbolrate` because the hardware does not easily expose original values. State is in memory only and freed by release after deleting the tuner I2C adapter.

Dependencies and integration: depends on DVB frontend APIs, I2C transfer, jiffies/timeouts, and board config in `cx24123.h`. Module parameters `force_band` and `debug` affect tuning and logging. DiSEqC and LNB control are direct register operations.

Risks and test signals: tuner band boundaries are documented as approximate and `force_band` can override them. Several I2C writes are not checked by callers, so partial hardware failure may surface later as no lock. BER/SNR are raw or approximate. Release always deletes the tuner adapter, so attach-error cleanup and adapter lifetime matter. Test with both internal PLL and external tuner modes, invalid revision, symbol-rate bounds, FEC/inversion auto, DiSEqC queue timeout, tone restart after message/burst, and repeated attach/release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cx24123.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cx24123.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cx24123.h

Purpose: public board-facing header for the CX24123/CX24109 DVB-S frontend driver.

Important APIs and types: `struct cx24123_config` supplies the demodulator I2C address, optional `set_ts_params()` callback, LNB polarity inversion flag, `dont_use_pll` selection for external tuners, and optional AGC callback. When `CONFIG_DVB_CX24123` is reachable, the header exports `cx24123_attach()` and `cx24123_get_tuner_i2c_adapter()`. Disabled-Kconfig stubs print warnings and return `NULL`.

Control flow and integration: board drivers call `cx24123_attach()` with the config and adapter, then optionally call `cx24123_get_tuner_i2c_adapter()` to bind an external tuner behind the demodulator repeater. The implementation reads config fields during init, tuning, status, LNB voltage, and AGC callback dispatch.

State and persistence: no state is defined in the header, but the implementation stores the config pointer, so caller-owned config memory must outlive the frontend.

Dependencies: includes Linux DVB frontend definitions and relies on Kconfig reachability for symbol availability.

Risks and test signals: mismatched `dont_use_pll` and board tuner wiring can leave the frontend without a usable tuner. Incorrect LNB polarity inverts voltage behavior. Tests should cover disabled stubs, attach with internal and external tuner modes, and the presence of `set_ts_params` on DMA-dependent boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cx24123.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2099.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2099.c

Purpose: I2C driver for the Sony CXD2099AR Common Interface controller, exposing a `dvb_ca_en50221` interface for CAM attribute memory, IO/control space, slot reset/shutdown, TS enable, polling, and optional data-buffer mode.

Important APIs and functions: the driver registers as an `i2c_driver` named `cxd2099`. `cxd2099_probe()` allocates `struct cxd`, initializes regmap, verifies the device can be read, configures clocks and CAM mode via `init()`, copies `en_templ`, and returns the `dvb_ca_en50221` pointer through `cfg->en`. Low-level helpers are `read_block()`, `write_block()`, `read_reg()`, `write_regm()`, `read_pccard()`, `write_pccard()`, `read_io()`, and `write_io()`. DVB CA callbacks include `read_attribute_mem()`, `write_attribute_mem()`, `read_cam_control()`, `write_cam_control()`, `slot_reset()`, `slot_shutdown()`, `slot_ts_enable()`, `poll_slot_status()`, `read_data()`, and `write_data()`.

Control flow: probe initializes hardware registers based on bitrate, polarity, and clock mode. Attribute and IO callbacks lock the device, select attribute or IO mode with `set_mode()`, perform the PC-card access, and unlock. Slot polling calls `campoll()` to acknowledge interrupts, track CAM present/ready state, and manage data-ready/write-busy flags. TS enable clears bypass and enables buffered CAM mode when available. Remove exits regmap and frees state.

State and persistence: `struct cxd` caches register shadows, last address pointer, mode, CAM mode, ready/data/write flags, slot status, buffers, platform config, regmap, client, and mutex. The state is volatile and per I2C client.

Dependencies and integration: depends on Linux I2C, regmap, mutexes, delays, and DVB CA EN50221. The `buffermode` module parameter decides whether `read_data`/`write_data` callbacks remain enabled.

Risks and test signals: `init()` currently returns `0` even if the internal `status` failed, hiding hardware programming errors. `write_pccard()` uses a 256-byte stack buffer with length type `u8`, which bounds callers but should be preserved. `read_data()` drains oversized frames to avoid device hang. Tests should cover probe with missing device, three clock modes, CAM insertion/removal/ready interrupts, slot reset timing, buffer mode on/off, max-I2C chunking, and concurrent CA callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2099.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2099.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2099.h

Purpose: platform-data header for the CXD2099AR Common Interface controller driver.

Important APIs and types: `struct cxd2099_cfg` carries bitrate, polarity, clock mode, maximum I2C transaction size, and a pointer-to-pointer output slot for the created `struct dvb_ca_en50221`. The implementation copies this config during probe and writes `*cfg->en` to expose the CA interface to the caller.

Control flow and integration: board code supplies this struct as `client->dev.platform_data` when registering the I2C device. The probe path uses timing fields to program TS/CAM clocks and uses `max_i2c` to split raw regmap transfers.

State and persistence: no runtime state is declared here. The `en` output pointer must be valid during probe so the driver can publish the CA handle.

Dependencies: includes `media/dvb_ca_en50221.h`; no Kconfig stubs are provided because this is used through I2C device binding rather than legacy attach.

Risks and test signals: invalid bitrate or clock mode directly changes register programming; a null `cfg` or null `cfg->en` would fail badly because probe does not defensively validate platform data. Tests should instantiate representative platform data and verify `en` publication and max-I2C chunk behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2099.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2820r.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2820r.h

Purpose: public API and platform-data definitions for the Sony CXD2820R DVB-T/T2/C demodulator driver.

Important APIs and types: GPIO mode macros encode enable/input/output/high/low for three demod GPIOs. TS mode macros select serial/parallel and MSB variants. `struct cxd2820r_platform_data` is for I2C-client binding and contains TS mode, clock inversion, IF AGC polarity, spectrum inversion, GPIO base pointer, and `get_dvb_frontend()` callback filled by probe. `struct cxd2820r_config` is the legacy attach config with I2C address and the same core demod settings. `cxd2820r_attach()` is exported when Kconfig is reachable; otherwise a warning stub returns `NULL`.

Control flow and integration: newer users bind an I2C client with platform data and later retrieve the frontend through `get_dvb_frontend`. Legacy users call `cxd2820r_attach()`, which wraps driver-core probing by creating an I2C client and then returns the frontend callback result.

State and persistence: this header does not own runtime state. Config/platform-data are consumed at probe; `attach_in_use` is private coordination between the wrapper and core to choose release behavior.

Dependencies: Linux DVB frontend and I2C client declarations, plus Kconfig reachability.

Risks and test signals: the pointer type `int **gpio_chip_base` in platform data is unusual and relies on the wrapper passing `&gpio_chip_base`; misuse can corrupt or lose GPIO base reporting. Tests should exercise both legacy attach and direct I2C binding, GPIO-disabled and GPIO-enabled modes, and disabled-Kconfig stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2820r.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2820r_c.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2820r_c.c

Purpose: DVB-C Annex A support routines for the CXD2820R demodulator, called by `cxd2820r_core.c` based on `delivery_system`.

Important APIs and functions: exports `cxd2820r_set_frontend_c()`, `cxd2820r_get_frontend_c()`, `cxd2820r_read_status_c()`, `cxd2820r_init_c()`, `cxd2820r_sleep_c()`, and `cxd2820r_get_tune_settings_c()` to the core through `cxd2820r_priv.h`.

Control flow: `set_frontend_c()` programs the tuner through `fe->ops.tuner_ops.set_params`, writes the DVB-C mode table when switching systems, stores `SYS_DVBC_ANNEX_A`, clears `ber_running`, requires tuner `get_if_frequency`, calculates IF register value from `CXD2820R_CLK`, writes it to secondary regmap bank `0x0042`, then starts acquisition with registers `0x00ff` and `0x00fe`. `get_frontend_c()` reads symbol rate, modulation, and inversion from bank 1. `read_status_c()` reads sync and TS-lock indicators, maps them to DVB status bits, updates signal strength, CNR, and post-bit-error counters.

State and persistence: updates `priv->delivery_system`, `priv->ber_running`, and cumulative `priv->post_bit_error`; writes DVBv5 stat cache fields in `dtv_frontend_properties`. No persistent storage exists.

Dependencies and integration: depends on regmap bank 1 for DVB-C demod registers, common table writer in core, tuner ops for IF frequency, `intlog2()`, and shared private state.

Risks and test signals: tuning fails if the tuner lacks `get_if_frequency`. BER counting uses a start/read/restart sequence and only accumulates valid windows, so polling cadence matters. CNR formula depends on constellation bits and logarithm constants. Test 6/7/8 MHz cable paths through core, missing IF callback, lock/no-lock stat scales, BER start/read transitions, and sleep clearing system state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2820r_c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2820r_core.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2820r_core.c

Purpose: core CXD2820R driver layer. It owns probing, regmap setup for the two I2C register banks, DVB frontend operation dispatch, custom search behavior, I2C gate control, optional GPIO chip registration, legacy attach wrapping, and resource cleanup.

Important APIs and functions: shared helpers include `cxd2820r_wr_reg_val_mask_tab()` and `cxd2820r_gpio()`. DVB frontend callbacks dispatch to per-system files: `cxd2820r_set_frontend()`, `read_status()`, `get_frontend()`, `sleep()`, and `get_tune_settings()`. `cxd2820r_search()` implements custom DVB-T/T2 fallback. `cxd2820r_probe()` allocates `struct cxd2820r_priv`, initializes regmaps, validates chip ID `0xe1`, creates dummy client for the second I2C address, registers GPIOs if requested, copies `cxd2820r_ops`, and publishes `get_dvb_frontend`.

Control flow: legacy `cxd2820r_attach()` creates an I2C client named `cxd2820r`; normal I2C probing performs hardware validation and frontend setup. Runtime DVB operations switch on `dtv_property_cache.delivery_system`. Search alternates between DVB-T and DVB-T2 after failed locks, waits 1s for T/C or 2s for T2 in 50 ms steps, and returns success/again/error. Release unregisters the primary client for legacy attach; direct I2C users have `release = NULL`.

State and persistence: `struct cxd2820r_priv` tracks clients, regmaps, frontend, config flags, GPIO cache, cumulative BER, active delivery system, and `last_tune_failed`. State is volatile and freed on remove.

Dependencies and integration: Linux I2C, regmap range windows, DVB frontend core, GPIOLIB when enabled, and the per-system C/T/T2 translation units.

Risks and test signals: probe depends on platform data and a valid `gpio_chip_base` indirection. The legacy attach path must handle `i2c_new_client_device()` failures. Search mutates `delivery_system` to alternate T/T2, so frontend cache semantics are important. Test chip-ID rejection, second-client creation failure, GPIO registration/fallback, direct vs legacy release, I2C gate bit toggling, dispatch for invalid delivery systems, and T/T2 retry behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2820r_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2820r_priv.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2820r_priv.h

Purpose: private shared header for CXD2820R core and delivery-system implementation files.

Important APIs and types: `struct reg_val_mask` represents register, value, and mask table entries used by mode programming. `CXD2820R_CLK` defines the 41 MHz demod clock used in IF calculations. `struct cxd2820r_priv` contains the two I2C clients/regmaps, parent adapter, DVB frontend, TS/AGC/spectrum config, DVBv3/DVBv5 BER state, GPIO cache and optional `gpio_chip`, current delivery system, and `last_tune_failed`. The header declares core register/GPIO helpers and all DVB-C/T/T2 per-system entry points.

Control flow and integration: this header is the internal ABI across `cxd2820r_core.c`, `cxd2820r_c.c`, `cxd2820r_t.c`, and `cxd2820r_t2.c`. Per-system files rely on the private state layout and helper prototypes to write shared registers and update common counters.

State and persistence: defines all persistent in-memory state for the demodulator. The state persists for the life of the frontend/I2C client only.

Dependencies: DVB frontend internals, integer log helpers, GPIO driver API, math64, regmap, and the public `cxd2820r.h`.

Risks and test signals: duplicate declaration of `cxd2820r_wr_regs()` suggests header drift. Changes to struct layout or helper prototypes affect all split translation units. Test signals include compile coverage with and without `CONFIG_GPIOLIB`, all delivery-system files included, and BER/GPIO state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2820r_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2820r_t.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2820r_t.c

Purpose: DVB-T support routines for the CXD2820R demodulator.

Important APIs and functions: exports `cxd2820r_set_frontend_t()`, `cxd2820r_get_frontend_t()`, `cxd2820r_read_status_t()`, `cxd2820r_init_t()`, `cxd2820r_sleep_t()`, and `cxd2820r_get_tune_settings_t()`.

Control flow: `set_frontend_t()` validates bandwidth 6/7/8 MHz, programs the tuner, writes the DVB-T initialization table when switching into T mode, stores `SYS_DVBT`, clears BER running, requires tuner IF frequency, writes IF registers, timing-recovery bandwidth tables, bandwidth selector, latency values, and start registers. `get_frontend_t()` decodes modulation, transmission mode, guard interval, hierarchy, HP/LP code rates, and inversion from demod registers. `read_status_t()` reads sync and TS-lock, maps status bits, then updates relative strength, dB CNR, and post-bit-error counters. `sleep_t()` clears active mode registers and marks the system undefined.

State and persistence: updates shared `priv->delivery_system`, `priv->ber_running`, cumulative `post_bit_error`, and DVBv5 statistic fields. No durable state.

Dependencies and integration: uses regmap bank 0, common register table writer, tuner `set_params`/`get_if_frequency`, and `intlog10()` for CNR.

Risks and test signals: unsupported bandwidth returns `-EINVAL`. IF callback absence breaks tuning. BER counters are restart-driven and require polling under sync. Test all bandwidths, invalid bandwidth, lock partial states, CNR edge cases around zero/large register values, and core search switching between T and T2.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2820r_t.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2820r_t2.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2820r_t2.c

Purpose: DVB-T2 support routines for CXD2820R, including PLP filtering and T2-specific metrics.

Important APIs and functions: exports `cxd2820r_set_frontend_t2()`, `cxd2820r_get_frontend_t2()`, `cxd2820r_read_status_t2()`, `cxd2820r_sleep_t2()`, and `cxd2820r_get_tune_settings_t2()`. The private header also declares `cxd2820r_init_t2()`, but this file does not define it; the core initializes T2 through `cxd2820r_init_t()`.

Control flow: `set_frontend_t2()` accepts 5/6/7/8 MHz, programs the tuner, writes a large T2 initialization table when switching systems, sets `SYS_DVBT2`, reads tuner IF frequency, programs T2 IF registers, enables or disables PLP filtering based on `stream_id > 255`, writes timing-recovery bandwidth registers, and starts acquisition. `get_frontend_t2()` reads transmission mode, guard interval, FEC, modulation, and inversion. `read_status_t2()` reads T2 sync/lock, maps DVB status, updates signal strength, CNR, and post-bit-error counters from T2 monitor registers. `sleep_t2()` cancels T2 mode and sets delivery system undefined.

State and persistence: uses shared `priv->delivery_system` and cumulative `post_bit_error`; T2 does not use `ber_running` in the same way as T/C. DVB stats are stored in the frontend cache.

Dependencies and integration: regmap bank 0, common register table writer, tuner IF callback, DVB stream ID semantics for PLP, and core custom search.

Risks and test signals: PLP filtering behavior changes at stream IDs above 255, so multistream tests are important. Header declaration drift for `cxd2820r_init_t2()` is a build/API smell. Test each bandwidth, invalid bandwidth, PLP disabled/enabled, lock wait duration, T2 CNR formula, and sleep after active T2.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2820r_t2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2841er.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2841er.c

Purpose: multi-standard Sony demodulator driver for CXD2837/2838/2841/2843/2854ER families, covering DVB-S/S2, DVB-T/T2, DVB-C Annex A/C, and ISDB-T depending on chip ID and attach mode. It exports `cxd2841er_attach_s()` for satellite and `cxd2841er_attach_t_c()` for terrestrial/cable.

Important APIs and functions: low-level I2C helpers are `cxd2841er_write_regs()`, `write_reg()`, `read_regs()`, `read_reg()`, and `set_reg_bits()`, addressing SLVX and SLVT derived from config I2C address. State transitions are explicit: shutdown, sleep-S, active-S, sleep-TC, active-TC. Satellite activation uses `cxd2841er_sleep_s_to_active_s()`, symbol-rate programming, `set_frontend_s()`, `tune_s()`, and DiSEqC/tone/burst helpers. Terrestrial/cable activation uses `sleep_tc_to_active_t()`, `*_t2()`, `*_c()`, `*_i()`, bandwidth subroutines, PLP/profile helpers, `set_frontend_tc()`, and `tune_tc()`. Metrics are read through status, carrier-offset, BER, packet-error, SNR, and AGC helpers.

Control flow: attach allocates state, computes SLVX/SLVT addresses, reads chip ID, mutates operation names/delivery systems based on chip family, and copies either S/S2 or T/C ops. Init forces a sane shutdown-to-sleep transition and configures AGC/TS defaults. Set frontend may tune the tuner early or late based on flags, transitions from sleep to active or retunes while active, writes bandwidth/IF/TS/filter recipes for the selected system, runs `tune_done()` to reset and enable TS output, optionally waits for lock, and later the tune callback applies carrier-offset correction and retunes once. `get_frontend()` refreshes strength whenever active and throttles expensive SNR/BER/UCBLOCK reads to once per second after lock.

State and persistence: `struct cxd2841er_priv` stores frontend, I2C adapter, two slave addresses, config pointer, state, active system, crystal, caps/flags, and stats throttle jiffies. DVBv5 stat counters live in `dtv_property_cache`; there is no durable persistence.

Dependencies and integration: depends on DVB frontend core, Linux I2C, integer-log/math helpers, and public/private headers for flags, crystal values, chip IDs, and CNR lookup tables. Tuner integration uses optional gate control and `set_params`/`get_if_frequency` controlled by flags such as `CXD2841ER_USE_GATECTRL`, `AUTO_IFHZ`, `ASCOT`, `EARLY_TUNE`, and `NO_WAIT_LOCK`.

Risks and test signals: many register writes ignore return values, so I2C failures may be latent. The global mutable `cxd2841er_t_c_ops` is edited during attach for chip-specific names and delivery systems, creating possible cross-instance side effects. State-machine functions return errors on invalid transitions, so mixed S vs TC attach/use must be tested. Bandwidth/crystal support is uneven, especially ISDB-T 7/8 MHz requiring 24 MHz. Test chip-ID matrix, S/S2 DiSEqC and carrier correction, T/T2/C/ISDB bandwidths, PLP auto/manual, stats throttling, gate-control tuner calls, no-wait-lock flag, invalid transition sleeps, and concurrent multiple attachments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2841er.c -->
