# Research: subset-b-004073

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/rtl2832.c -->
## sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/rtl2832.c

Purpose: Realtek RTL2832 DVB-T demodulator I2C driver. It exposes a `dvb_frontend`, a tuner I2C mux, PID filter controls, slave transport stream control, and a shared regmap for the companion SDR driver.

Important APIs/types/functions: `rtl2832_probe()` allocates `struct rtl2832_dev`, builds an 8-bit regmap with selector ranges, creates an `i2c_mux_core`, copies `rtl2832_ops`, and stores callbacks in `rtl2832_platform_data`. `rtl2832_rd_demod_reg()` and `rtl2832_wr_demod_reg()` implement bitfield access over the private register table. DVB callbacks include `rtl2832_init()`, `rtl2832_sleep()`, `rtl2832_set_frontend()`, `rtl2832_get_frontend()`, `rtl2832_read_status()`, `rtl2832_read_snr()`, and `rtl2832_read_ber()`. Integration callbacks include `rtl2832_get_dvb_frontend()`, `rtl2832_get_i2c_adapter()`, `rtl2832_slave_ts_ctrl()`, `rtl2832_pid_filter_ctrl()`, and `rtl2832_pid_filter()`.

Control flow: probe validates device access and wires the adapter. init writes a generic demod register script, then a tuner-specific AGC/inversion script from `rtl2832_priv.h`. tuning programs the tuner first, reads tuner IF if available, selects 6/7/8 MHz bandwidth tables, computes resampling and carrier offset ratios from platform clock, then toggles soft reset. status reads FSM stage and updates DVBv5 statistics.

State and persistence: state is in `rtl2832_dev`: `sleeping`, `fe_status`, BER counters, delayed I2C gate work, PID filter bitmap, and `slave_ts`. No on-disk persistence. Regmap cache is disabled because hardware registers are active state.

Dependencies/integration: Linux I2C, regmap, i2c-mux, DVB frontend, tuner ops, delayed work. The USB bridge or board driver supplies `rtl2832_platform_data` and consumes returned frontend, tuner adapter, PID callbacks, and regmap.

Risks: many hardware magic values; unsupported tuner id returns `-EINVAL`; PID bitmap is `unsigned long` but code writes 32 bits; status/stat math depends on undocumented scaling; delayed I2C gate timing can affect tuner transactions; some direct `regmap_bulk_write()` string buffers rely on exact byte lengths.

Test signals: attach log, tuner child devices appearing on mux adapter, successful DVB-T lock for 6/7/8 MHz, valid strength/CNR/BER transitions, PID filter behavior, slave TS enable/disable, suspend/remove without delayed-work use-after-free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/rtl2832.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/rtl2832.h -->
## sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/rtl2832.h

Purpose: Public platform-data contract for the RTL2832 demodulator driver.

Important APIs/types/functions: `struct rtl2832_platform_data` provides `clk`, `tuner`, demod-return callbacks, tuner I2C adapter callback, slave TS callback, PID filter callbacks, and an SDR-private `struct regmap *`. Tuner ids define the board-driver ABI and must remain synchronized with `dvb_usb_rtl28xxu`.

Control flow: board code fills clock and tuner before creating the I2C client. `rtl2832_probe()` fills callback fields and the regmap pointer after successful attach. Consumers call callbacks rather than reaching into private state.

State and persistence: the header itself stores no state, but it defines shared mutable pointers used by bridge, tuner, and SDR modules during device lifetime.

Dependencies/integration: includes DVB frontend and I2C mux declarations. Used by RTL28xx USB bridge code and `rtl2832_sdr`.

Risks: platform data is modified by the demod probe, so lifetime must outlive the I2C client; tuner enum drift breaks tuner-specific init; the regmap field is marked private but is still exposed structurally.

Test signals: compile coverage for all tuner ids, successful callback population after probe, SDR using the populated regmap only after demod attach.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/rtl2832.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/rtl2832_priv.h -->
## sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/rtl2832_priv.h

Purpose: Private RTL2832 driver state, register bitfield identifiers, and tuner-specific initialization data.

Important APIs/types/functions: `struct rtl2832_dev` holds platform data, client, regmap, mux, frontend, status/stat counters, gate work, PID bitmap, and slave TS state. `struct rtl2832_reg_entry` maps symbolic bitfields to start address and bit positions. `struct rtl2832_reg_value` drives generic and tuner register scripts. `enum DVBT_REG_BIT_NAME` names demod fields consumed by `rtl2832.c`.

Control flow: `rtl2832_wr_demod_reg()` indexes the enum into `registers[]` in `rtl2832.c`; `rtl2832_init()` selects one tuner init array by platform tuner id and writes it sequentially.

State and persistence: runtime state lives in `rtl2832_dev`; static register tables are immutable driver data. No persistence beyond hardware register programming.

Dependencies/integration: depends on regmap, math64, bitops, DVB frontend, integer log, and public `rtl2832.h`.

Risks: enum/table alignment is critical because the table is indexed directly; several enum values have no entry in `registers[]` and must not be used with generic accessors unless added; init values are undocumented hardware magic and tuner sensitive.

Test signals: build warnings for missing enum entries are unlikely, so runtime coverage should include every supported tuner path and bitfield write used by init/tune/status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/rtl2832_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/rtl2832_sdr.c -->
## sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/rtl2832_sdr.c

Purpose: V4L2 SDR capture driver for RTL2832U devices, sharing the RTL2832 regmap, tuner, and parent DVB USB streaming path to expose raw IQ samples.

Important APIs/types/functions: `struct rtl2832_sdr_dev` owns V4L2/vb2 state, USB URBs, coherent buffers, control handler, tuner frequencies, sample format, and power flags. Probe registers a V4L2 SDR `video_device`. vb2 callbacks are `queue_setup`, `buf_prepare`, `buf_queue`, `start_streaming`, and `stop_streaming`. `rtl2832_sdr_set_adc()` programs demod ADC/IF/sample-rate registers. V4L2 ioctls handle tuner queries, frequency bands, SDR formats, stream I/O, and controls.

Control flow: streaming powers the parent USB device, enables frontend ADC, wakes tuner, applies RF/ADC settings, allocates coherent USB buffers and URBs, then submits bulk reads on endpoint 0x81. URB completion converts CU8 to CU8 or emulated CU16LE, fills the next vb2 buffer, timestamps it, and resubmits. stop kills/free URBs, returns queued buffers with error, restores ADC/tuner, and powers down.

State and persistence: state is volatile in `rtl2832_sdr_dev`: flags `POWER_ON`/`URB_BUF`, URB lists, queue list, sequence, `udev`, frequencies, format, sample counters, and controls. No persistent storage.

Dependencies/integration: platform device data supplies regmap, DVB frontend, tuner V4L2 subdev, and DVB USB device. Uses V4L2, videobuf2-vmalloc, USB core, regmap, firmware-independent tuner ops, and parent power/frontend callbacks.

Risks: disconnect safety depends on lock ordering and `udev` checks; URB completion runs in interrupt context and resubmits unconditionally after nonfatal errors; tuner-specific ADC register sequences repeatedly overwrite `ret` without checking every write; format changes are blocked only while vb2 is busy; CU16LE is marked emulated and optional.

Test signals: `/dev/swradio*` registration, V4L2 capability/format enumeration, streaming with mmap/read/userptr, frequency/band controls, clean unplug during streaming, no leaked URBs/buffers, sample-rate debug output, and valid IQ data in GNU Radio or rtl-sdr style consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/rtl2832_sdr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/rtl2832_sdr.h -->
## sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/rtl2832_sdr.h

Purpose: Public platform-data contract for the RTL2832 SDR platform driver.

Important APIs/types/functions: `struct rtl2832_sdr_platform_data` supplies clock, tuner id, demod regmap, DVB frontend, optional tuner V4L2 subdev, and parent DVB USB device. Tuner ids mirror RTL2832 ids for SDR-supported tuners.

Control flow: the parent bridge creates the platform device after demod/tuner setup. `rtl2832_sdr_probe()` consumes this structure to bind SDR capture to the same hardware.

State and persistence: no state is stored by the header. It carries borrowed pointers whose lifetime must cover the SDR platform device.

Dependencies/integration: includes I2C, V4L2 subdev, and DVB frontend declarations. Integrates demod, tuner controls, and USB streaming.

Risks: no explicit ownership/refcounting in the struct; tuner id list excludes SI2157 despite demod support; missing `dvb_usb_device` or regmap is fatal in practice.

Test signals: platform data validation through successful SDR probe, tuner-specific control set creation, streaming with each supported tuner id.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/rtl2832_sdr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/s5h1409.c -->
## sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/s5h1409.c

Purpose: Samsung S5H1409 ATSC 8VSB and Annex B QAM demodulator attach-style driver.

Important APIs/types/functions: `struct s5h1409_state` stores I2C/config/frontend, current modulation/frequency/IF, QAM lock and optimization state. `s5h1409_attach()` probes chip id, initializes, opens the I2C gate, and returns `dvb_frontend`. Register helpers use 8-bit register addresses and 16-bit values. Frontend ops cover init, gate control, set/get frontend, status, BER/SNR/signal strength/ucblocks, and release.

Control flow: init wakes and resets the chip, writes `init_tab`, applies HVR-1600 optional tweaks, output mode, inversion, IF, GPIO, MPEG timing, soft reset, and closes gate. tuning soft-resets, selects VSB or QAM IF/mode, calls tuner through gate, resets again, then runs QAM interleave/amhum optimization. status polls lock registers and may continue QAM optimization.

State and persistence: current tuning and QAM state are cached in memory. Counters are read from hardware. No persistent storage.

Dependencies/integration: direct `i2c_transfer`, DVB frontend/tuner ops, board-provided `s5h1409_config`.

Risks: register writes often ignore return values; read errors return whatever buffer contains; QAM optimization has board-specific legacy paths; `s5h1409_writereg()` returns `-1` instead of standard errno; attach leaves I2C gate open by design.

Test signals: attach id 0x0066/0x007f, VSB and QAM64/256 locks, tuner-lock versus demod-lock status modes, HVR-1600 optimized path, SNR table boundaries, gate open/close around tuner calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/s5h1409.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/s5h1409.h -->
## sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/s5h1409.h

Purpose: Public configuration and attach declaration for the S5H1409 demodulator.

Important APIs/types/functions: `struct s5h1409_config` defines demod I2C address, serial/parallel output, GPIO, QAM IF, spectral inversion, status mode, MPEG timing, and HVR-1600 optimization flag. `s5h1409_attach()` is exported when enabled and stubbed otherwise.

Control flow: board drivers fill config and call attach; returned frontend owns callbacks from `s5h1409.c`.

State and persistence: config is immutable board data referenced by driver state.

Dependencies/integration: Linux DVB frontend API and Kconfig reachability.

Risks: config values are macro integers with no type safety; VSB IF is hardcoded in the C file while QAM IF is configurable; incorrect status mode changes frontend lock semantics.

Test signals: build with and without `CONFIG_DVB_S5H1409`, board attach paths, serial/parallel TS output, GPIO and MPEG timing variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/s5h1409.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/s5h1411.c -->
## sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/s5h1411.c

Purpose: Samsung S5H1411 ATSC 8VSB and Annex B QAM demodulator driver, updated from S5H1409 with separate TOP/QAM I2C addresses.

Important APIs/types/functions: `struct s5h1411_state` caches config, frontend, modulation, first-tune flag, frequency, IF, and inversion. `s5h1411_writereg/readreg()` access 16-bit registers through specified I2C address. `s5h1411_attach()` validates chip id 0x0066, initializes, opens gate, sleeps device, and returns frontend. Ops include init/sleep/gate/set/get/status/SNR/BER/strength/ucblocks/release.

Control flow: init powers on, resets registers, writes mixed TOP/QAM `init_tab`, forces first tune, applies output mode, inversion, IF, GPIO, MPEG timing, soft reset, and closes gate. tune resets, sets modulation-specific TOP/QAM mode and IF, tunes external tuner through gate, and resets. status selects QAM or VSB lock registers and optionally augments signal/carrier from tuner status.

State and persistence: in-memory current frequency/modulation/IF/inversion and first-tune guard. No persistent state.

Dependencies/integration: direct I2C transfers, DVB frontend API, tuner ops, board `s5h1411_config`.

Risks: many writes ignore return codes; read errors can be masked; QAM_AUTO is programmed but read status handles only QAM_64/QAM_256; first-tune logic is empirical; powerstate naming uses enable=1 for sleep.

Test signals: chip id detection, cold first tune, VSB and QAM locks, top/qam address transactions, sleep/resume, tuner-lock and demod-lock status modes, SNR table conversions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/s5h1411.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/s5h1411.h -->
## sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/s5h1411.h

Purpose: Public configuration for the S5H1411 ATSC/QAM demodulator.

Important APIs/types/functions: defines TOP and QAM I2C addresses, IF constants, output/GPIO/MPEG timing/inversion/status macros, `struct s5h1411_config`, and conditional `s5h1411_attach()`.

Control flow: board code selects VSB/QAM IFs and hardware output behavior through this config before attach.

State and persistence: config is referenced by driver state for device lifetime.

Dependencies/integration: DVB frontend API and Kconfig.

Risks: IF defaults are board-sensitive; wrong I2C address constants would break all access; status mode changes how lock bits are interpreted by DVB core.

Test signals: compile with disabled-driver stub, attach on boards using each IF option, serial/parallel output validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/s5h1411.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/s5h1420.c -->
## sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/s5h1420.c

Purpose: DVB-S QPSK demodulator driver for Samsung S5H1420 and PnpNetwork PN1010, including DiSEqC, tone, LNB voltage, and tuner I2C repeater support.

Important APIs/types/functions: `struct s5h1420_state` holds config, frontend, tuner I2C adapter, cached `CON_1`, post-lock flag, clock/tune/FEC/symbol state, and register shadow. `s5h1420_attach()` probes chip id, initializes shadow, creates frontend and a tuner I2C adapter. Exported `s5h1420_get_tuner_i2c_adapter()` returns the repeater adapter. Frontend ops include satellite controls, set/get frontend, tune settings, status, BER/strength/ucblocks, init/sleep, and release.

Control flow: set_frontend performs fast retune when only frequency drift changes within allowed range; otherwise it resets, picks PLL/fclk by symbol rate, configures loop/filter/MPEG/FEC/DiSEqC/tuner registers, programs symbol rate and FEC/inversion, starts QPSK, and clears postlock. read_status maps monitor bits to FE status, fixes a FEC 5/6 inversion edge case, and on first lock programs MPEG clock and loop values from actual symbol/FEC rate.

State and persistence: cached tuning parameters, symbol rate, FEC, `postlocked`, register shadow, and tuner adapter live in memory. Hardware state is reprogrammed on tune/init.

Dependencies/integration: I2C core, DVB-S frontend API, DiSEqC structures, tuner ops through repeater adapter, jiffies/timeouts.

Risks: `s5h1420_readreg()` may return raw transfer count on failure as `u8`; shadow workaround depends on previous writes; fast-tune gate handling is asymmetric; DiSEqC receive code has FIXME uncertainty; arithmetic can overflow if unexpected symbol rates/clocks are used.

Test signals: chip id 0x03, tuner adapter registration, symbol-rate range coverage, fast and full retunes, lock/postlock MPEG output, DiSEqC send/receive/burst timeout behavior, 13/18V and tone control.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/s5h1420.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/s5h1420.h -->
## sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/s5h1420.h

Purpose: Public configuration and exported entry points for the S5H1420/PN1010 DVB-S driver.

Important APIs/types/functions: `struct s5h1420_config` contains demod I2C address and bitfields for inversion polarity, repeated-start workaround, MPEG clock polarity, and serial MPEG output. Declares `s5h1420_attach()` and `s5h1420_get_tuner_i2c_adapter()` with disabled-driver stubs.

Control flow: board drivers attach demod, then use returned tuner I2C adapter for tuner clients if needed.

State and persistence: config is immutable per board; no runtime state in header.

Dependencies/integration: DVB frontend API, Kconfig reachability.

Risks: bitfield layout is compact but ABI-sensitive for in-kernel users; repeated-start workaround must match host I2C controller capability; disabled stub for tuner adapter silently returns NULL.

Test signals: board configs using serial/parallel MPEG, inverted/non-inverted IF, repeated-start workaround on affected adapters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/s5h1420.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/s5h1420_priv.h -->
## sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/s5h1420_priv.h

Purpose: Private symbolic register map for S5H1420/PN1010.

Important APIs/types/functions: `enum s5h1420_register` names demod control, PLL, QPSK, loop, NCO, monitor, FEC, Viterbi, sync, MPEG, DiSEqC, RF, and error registers used by `s5h1420.c`.

Control flow: C code uses these constants in tuning, status, DiSEqC, and output configuration instead of raw numeric addresses.

State and persistence: no state; symbolic constants only.

Dependencies/integration: includes `asm/types.h`.

Risks: constants must match silicon documentation; enum names cover only low register range used by the driver, while raw addresses still appear in code.

Test signals: compile coverage plus functional tests of every code path that touches PLL, DiSEqC, MPEG, and Viterbi registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/s5h1420_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/s5h1432.c -->
## sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/s5h1432.c

Purpose: Samsung S5H1432 DVB-T demodulator driver, apparently minimal and partially implemented.

Important APIs/types/functions: `struct s5h1432_state` stores I2C/config/frontend, modulation, first_tune, current frequency, IF, and inversion. Helpers read/write 8-bit registers through the fixed TOP address. `s5h1432_attach()` allocates state and returns a DVB-T frontend. Ops include init, sleep, set_frontend, tune_settings, status/stat stubs, and release.

Control flow: init writes a fixed demod script, sets default IF, serial mode bits, and soft-resets. set_frontend skips retuning when frequency is unchanged; otherwise it calls tuner `set_params`, sleeps, sets bandwidth and IF, soft-resets, and repeats bandwidth/IF/reset sequence. Metric callbacks return zero without populating values.

State and persistence: current frequency and config-derived inversion are cached. No persistence and no meaningful stats state.

Dependencies/integration: I2C transfers, DVB frontend/tuner ops, board `s5h1432_config`.

Risks: no chip-id verification; `kmalloc_obj` leaves fields potentially uninitialized beyond explicit assignments; most callbacks are stubs; bandwidth is initially set before `dvb_bandwidth` is updated; repeated duplicated tuning sequence; write failures ignored in init/tune.

Test signals: only basic attach/init/tune and transport output can be trusted; status, BER, SNR, signal strength, and ucblocks need hardware validation or implementation before relying on DVB monitoring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/s5h1432.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/s5h1432.h -->
## sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/s5h1432.h

Purpose: Public configuration for the S5H1432 DVB-T demodulator.

Important APIs/types/functions: defines fixed top I2C address, common IF frequency constants, output/GPIO/MPEG timing/IF/inversion/status macros, `struct s5h1432_config`, and conditional `s5h1432_attach()`.

Control flow: board code passes config to attach, although the C implementation uses only a subset of fields.

State and persistence: config lifetime is external to driver state.

Dependencies/integration: DVB frontend API and Kconfig.

Risks: default IF macros reference lowercase names (`s5h1432_IF_44000`) that do not match defined uppercase constants; many config fields are currently unused by the C file; comments mention VSB/QAM while driver is DVB-T.

Test signals: compile all users of default macros, attach stub behavior, board configs that expect GPIO/MPEG timing to be honored.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/s5h1432.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/s921.c -->
## sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/s921.c

Purpose: Sharp VA3A5JZ921/S921 ISDB-T one-seg frontend driver for a Brazilian SBTVD device.

Important APIs/types/functions: `struct s921_state` stores I2C/config/frontend and cached frequency. Static register arrays initialize the chip and bracket PLL retuning. `s921_attach()` returns frontend ops. `s921_pll_tune()` selects band register and PLL offset from requested RF frequency. Ops include init, set/get frontend, status, signal strength, tune, frontend algo, and release.

Control flow: init writes the full `s921_init` register script. tuning computes band from frequency table, writes pre-frequency registers, programs PLL high/low and band switch, writes post-frequency registers, polls debug status registers, and caches frequency. tune optionally retunes then reads status unless oneshot. status reads registers 0x81/0x82 and maps coarse magic values to FE flags.

State and persistence: only current frequency is cached. Hardware scripts are static; no persistent storage.

Dependencies/integration: direct I2C, DVB frontend API, `do_div` for PLL math, board `s921_config`.

Risks: debug defaults to enabled despite parameter description; status and strength are approximate; no BER/SNR/ucblocks ops; PLL band comments note uncertain bounds; read helper has macro/function name collision style that is hard to read; many values are reverse-engineered magic.

Test signals: ISDB-T lock over all band table ranges, PLL offset correctness, status register captures, one-seg stream output, debug disabled by module parameter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/s921.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/s921.h -->
## sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/s921.h

Purpose: Public attach/config header for the Sharp S921 frontend.

Important APIs/types/functions: `struct s921_config` contains demod I2C address. Declares `s921_attach()` and `s921_get_tuner_i2c_adapter()` when enabled, with disabled stubs.

Control flow: board code supplies address and receives a DVB frontend from attach. The declared tuner adapter function is not implemented in `s921.c`.

State and persistence: no runtime state in header.

Dependencies/integration: DVB frontend API and Kconfig.

Risks: exported declaration for `s921_get_tuner_i2c_adapter()` has no matching implementation in the source shown; disabled stub prints warning. Minimal config leaves all hardware variant behavior hardcoded in C.

Test signals: link/build with CONFIG enabled, board attach, absence of unresolved tuner-adapter symbol users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/s921.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/si2165.c -->
## sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/si2165.c

Purpose: Regmap-based I2C driver for Silicon Labs Si2161 DVB-T and Si2165 DVB-C/T demodulators.

Important APIs/types/functions: `struct si2165_state` stores client, regmap, frontend, config, chip id/rev, derived clocks, BER previous value, capability flags, and firmware state. Register helpers read/write 8/16/24/32-bit little-endian values. `si2165_probe()` identifies chip, builds frontend delsys/name, and returns it through platform data. DVB ops include init, sleep, set_frontend, read_status, read_snr, read_ber, and tune settings.

Control flow: probe validates platform clock/mode, powers up, reads revision/type, powers down, sets capabilities. init powers the chip, configures AGC/RSSI, initializes PLL, waits init done, sets BER period, optionally uploads revision-D firmware with CRC validation, and configures TS output. set_frontend calculates IF shift, applies DVB-T or DVB-C specific PLL/oversampling/register list, tunes external tuner, recalculates IF, resets DSP, rewrites ADC values, and starts synchronization.

State and persistence: derived clocks and BER counters are cached; firmware_loaded records successful upload only in memory. No persistence.

Dependencies/integration: I2C client driver, regmap, request_firmware, DVB frontend/tuner ops, integer log for CNR, platform data.

Risks: firmware missing prevents revision-D init; platform-data comment has a likely typo for 24 MHz value; `get_if_frequency` is mandatory for tuning; CNR only implemented for DVB-C; many register names remain unknown; frontend release is NULL so I2C driver lifetime owns state.

Test signals: detection of Si2161/Si2165, firmware request/CRC path, DVB-T bandwidths, DVB-C constellations and symbol rates, IF inversion, BER/CNR counters, sleep/init cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/si2165.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/si2165.h -->
## sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/si2165.h

Purpose: Public platform data for the Si2165/Si2161 I2C demodulator driver.

Important APIs/types/functions: mode constants `SI2165_MODE_OFF`, `SI2165_MODE_PLL_EXT`, `SI2165_MODE_PLL_XTAL`; `struct si2165_platform_data` returns a frontend pointer and supplies chip mode, reference frequency, and spectrum inversion.

Control flow: board code passes platform data to the I2C client; probe stores the returned frontend in `*fe`.

State and persistence: platform data is an attach-time contract with borrowed frontend pointer output.

Dependencies/integration: DVB frontend API.

Risks: comment lists `240000000` where code supports `24000000`; no explicit tuner/TS config here, so integration relies on frontend tuner ops and private defaults.

Test signals: platform data validation for 4-27 MHz clock range, mode selection, returned frontend pointer population.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/si2165.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/si2165_priv.h -->
## sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/si2165_priv.h

Purpose: Private Si2165 configuration, firmware name, statistics constants, and register address map.

Important APIs/types/functions: `SI2165_FIRMWARE_REV_D` names firmware. `struct si2165_config` mirrors platform data plus I2C address. `STATISTICS_PERIOD_*` defines BER accumulation scale. `REG_*` constants cover chip mode, PLL, DSP control, AGC, DVB standard, firmware DCOM, counters, FEC lock, TS output, and RSSI registers.

Control flow: `si2165.c` uses these constants for probe, init, firmware upload, DVB-T/C setup, stats, and TS configuration.

State and persistence: constants only; no runtime state.

Dependencies/integration: private to SI2165 driver.

Risks: several registers are marked unknown and may be silicon/firmware sensitive; mismatch between register widths and helper choice would silently program wrong values.

Test signals: firmware upload, register-list execution, stats period behavior, TS output after init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/si2165_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/si2168.c -->
## sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/si2168.c

Purpose: Firmware-command I2C driver for Silicon Labs Si2168 DVB-T/T2/C demodulators.

Important APIs/types/functions: `cmd_init()` prepares `struct si2168_cmd`; `si2168_cmd_execute()` serializes command I/O, polls firmware ready/error bits, and enforces timeout. `si2168_probe()` identifies chip revision, chooses firmware, creates tuner I2C mux, and returns frontend/adapter through config. DVB ops include init, sleep, resume, set_frontend, read_status, and tune settings. `si2168_ts_bus_ctrl()` manages transport stream output/tristate.

Control flow: probe sends boot commands, queries chip id, maps A20/A30/B40/D60 to firmware, allocates mux, and publishes frontend. init boots or resumes firmware, downloads old or new firmware format, queries firmware version, sets TS mode, and initializes stats. set_frontend validates delivery/bandwidth, tunes external tuner, sends a sequence of firmware properties for standard, PLP, bandwidth, DVB-C symbol rate, inversion, and TS clock, then starts acquisition and enables TS. status sends standard-specific status command, maps lock bits, and accumulates CNR/BER/UCB counters.

State and persistence: `si2168_dev` caches active/warm/initialized flags, chip id, firmware version/name, delivery system, status, TS flags, and mux. No persistent state; warm controls whether firmware reload is skipped.

Dependencies/integration: I2C, firmware loader, i2c-mux, DVB frontend, tuner ops, platform config.

Risks: firmware files are mandatory for cold init; command sequences are opaque and firmware-version sensitive; sleep invalidates warm state for newer B firmware; status returns `-EAGAIN` when inactive; TS clock flags alter multiple properties and need board validation.

Test signals: chip identification for all supported ids, firmware load old/new formats, resume without first init, DVB-T/T2/C locks, PLP stream id selection, BER/UCB counter increments, muxed tuner access, TS tristate on sleep.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/si2168.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/si2168.h -->
## sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/si2168.h

Purpose: Public configuration for the Si2168 I2C demodulator.

Important APIs/types/functions: `struct si2168_config` returns frontend and tuner I2C adapter pointers and supplies TS mode plus clock inversion, gapped clock, and spectral inversion flags. TS mode macros define parallel, serial, tristate, and manual clock behavior.

Control flow: bridge code passes this platform data; probe populates `*fe` and `*i2c_adapter` after creating the mux and stores TS flags in private state.

State and persistence: no state in header; config pointers and flags shape private runtime behavior.

Dependencies/integration: DVB frontend API and I2C adapter type declarations through included headers.

Risks: note hardcodes I2C address 0x64; bad TS mode/clock flags can produce no transport stream despite demod lock; output pointers must remain valid during probe.

Test signals: returned mux adapter works for tuner probe, TS output in serial/parallel/manual/gapped modes, inversion flag lock behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/si2168.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/si2168_priv.h -->
## sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/si2168_priv.h

Purpose: Private SI2168 firmware names, runtime state, chip ids, and command buffer definition.

Important APIs/types/functions: firmware macros map A20, A30, B40, and D60 chips to file names. `struct si2168_dev` stores command mutex, mux, frontend, delivery/status, chip id/version, firmware name, TS mode, and active/warm/initialized/clock/inversion flags. `struct si2168_cmd` contains a 30-byte argument buffer and write/read lengths.

Control flow: `si2168.c` uses this state for probe, firmware loading, TS setup, tune/status commands, mux gate commands, sleep, and resume.

State and persistence: all runtime state is memory resident and reset by remove; firmware state is represented by `warm` and `initialized`.

Dependencies/integration: public `si2168.h`, DVB frontend, firmware loader, I2C mux, kernel helpers.

Risks: fixed `SI2168_ARGLEN` must exceed every firmware command; chip-id macros encode ASCII/numeric bytes and must match firmware query layout; warm-state logic depends on firmware version encoding.

Test signals: command length validation through firmware load, chip-id matching, resume/sleep warm transitions, mux creation/destruction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/si2168_priv.h -->
