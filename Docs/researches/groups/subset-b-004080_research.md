# subset-b-004080 research

This grouped report covers TDA/TUA/TS DVB frontend demodulator and tuner files under `sources/distributed-fs/ceph-client/drivers/media/dvb-frontends`. Each section preserves the original source path so reconciliation can split it into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda10021.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda10021.c

## Purpose
`tda10021.c` implements the Philips TDA10021 DVB-C demodulator frontend used by older cable cards. It exposes a DVB frontend for Annex A/C QAM reception, programs symbol-rate and QAM-specific demodulator registers over I2C, gates tuner access through the demodulator, and reports lock, BER, signal strength, SNR, and uncorrected block counters.

## Important APIs, Types, and Functions
The exported entry point is `tda10021_attach()`, which validates the chip ID, allocates `struct tda10021_state`, copies `tda10021_ops`, and returns a `struct dvb_frontend`. The state stores the I2C adapter, board `tda1002x_config`, frontend object, PWM value, and cached register 0 value. Core helpers include `_tda10021_writereg()`, `tda10021_readreg()`, `lock_tuner()`, `unlock_tuner()`, `tda10021_setup_reg0()`, `tda10021_set_symbolrate()`, `tda10021_init()`, `tda10021_set_parameters()`, `tda10021_get_frontend()`, and the DVB metric callbacks.

## Control Flow
Attach allocates state, caches board config and PWM, reads register `0x1a`, accepts TDA10021-style IDs, explicitly rejects TDA10023 ID `0x7d`, and installs DVB-C frontend callbacks. `init` writes the 0x40-byte initialization table, applies the PWM register, and wakes the PLL. `set_frontend` validates Annex A/C, QAM family, and explicit inversion, asks the tuner to tune through `tuner_ops.set_params`, closes the demod I2C gate, computes the symbol-rate decimation/filter/BDR registers, writes QAM threshold/AGC parameters, selects Annex C roll-off in register `0x3d`, and triggers the acquisition through register 0. Status and metrics are direct register reads with small counter reset writes.

## State and Persistence Behavior
All persistent configuration is board-supplied through `struct tda1002x_config`; the driver itself keeps only volatile state in `tda10021_state`. `state->reg0` is the software mirror for modulation and inversion bits and is later used by `get_frontend()`. `state->pwm` is board PWM output programming reapplied at init/tune time. BER and uncorrected-block reads reset hardware counters, so metric collection is stateful at the device-counter level. Sleep powers down the ADC and places the chip in standby.

## Dependencies and Integration Points
The driver depends on Linux I2C, DVB frontend core APIs, `tda1002x.h`, board-specific tuner callbacks, and the demodulator I2C gate bit in register `0x0f`. It exports `tda10021_attach()` for bridge drivers to bind this demodulator to an adapter and tuner.

## Risks and Edge Cases
`tda10021_set_symbolrate()` clamps rates outside the supported range, so callers may not get an error for too-low or too-high symbol rates. QAM and Annex validation is explicit, but inversion must not be auto. I2C register writes delay 10 ms each, making init and tune sensitive to slow buses. `tda10021_get_frontend()` adjusts frequency from AFC only when carrier lock exists and relies on the cached `p->symbol_rate`. The attach path must distinguish TDA10021 and TDA10023 because their ID high nibbles overlap.

## Test Signals
Useful tests include successful attach with non-`0x7d` `0x70`-family IDs, rejection of TDA10023, init table programming, all supported QAM modes for Annex A and C, invalid delivery/modulation/inversion rejection, tuner gate open/close around external tuner tuning, lock-bit mapping from register `0x11`, BER and UCB counter resets, AFC frequency correction under carrier lock, and standby writes to ADC/standby registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda10021.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda10023.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda10023.c

## Purpose
`tda10023.c` implements the Philips TDA10023 DVB-C demodulator, a later cable demodulator used by Philips CU1216-3 NIM and similar boards. It supports Annex A/C QAM, configurable crystal and PLL setup, board-selectable MPEG TS output mode, symbol-rate programming, tuner I2C gating, and frontend metric callbacks.

## Important APIs, Types, and Functions
The exported API is `tda10023_attach()`. `struct tda10023_state` stores the I2C adapter, `tda10023_config`, frontend, PWM/register cache, and clock fields `xtal`, `pll_m`, `pll_p`, `pll_n`, and computed `sysclk`. Register access is provided by `tda10023_readreg()`, `tda10023_writereg()`, `tda10023_writebit()`, and table interpreter `tda10023_writetab()`. Runtime callbacks include `tda10023_init()`, `tda10023_set_symbolrate()`, `tda10023_set_parameters()`, `tda10023_read_status()`, metric readers, `tda10023_get_frontend()`, `tda10023_sleep()`, and `tda10023_i2c_gate_ctrl()`.

## Control Flow
Attach wakes register 0, checks the demodulator ID high nibble, copies frontend ops, applies default or board-provided clock PLL factors, computes `sysclk`, and updates frontend symbol-rate limits. `init` builds a masked register script, optionally patches `deltaf` and TS output mode from config, programs PLL and demod defaults, performs reset sequences, and enables the MPEG output mode. `set_frontend` validates delivery system and QAM, tunes the external tuner, calculates symbol-rate registers from `sysclk`, writes QAM-specific lock/MSE/AGC/ERAGC thresholds, selects Annex A/C filter mode, and toggles register 0 to start acquisition.

## State and Persistence Behavior
The driver persists no data outside the device. In-memory state caches register 0, PWM, clock factors, and computed `sysclk`. Counter callbacks mutate hardware state: BER read retriggers the bit-error counter, and UCB read resets the uncorrected-block counter sequence. The chip can be put in standby by powering down the ADC and writing register 0 standby bits.

## Dependencies and Integration Points
The file depends on DVB frontend properties, Linux I2C, 64-bit division from `asm/div64.h`, and public declarations in `tda1002x.h`. Bridge drivers provide `tda10023_config` with demod address, optional clock/PLL values, output mode, and baseband offset. The demod gates tuner I2C access through register `0x0f`, and exported `tda10023_attach()` is the bridge integration point.

## Risks and Edge Cases
Clock settings directly determine symbol-rate limits and BDR math; bad board data can tune incorrectly while still attaching. `TDA10023_OUTPUT_MODE_SERIAL` is declared as TODO and not actually implemented. The code accepts only Annex A/C and fixed QAM modes but does not validate inversion in the same strict way as TDA10021. Several register-table operations ignore individual write return values. Signal strength normalization is heuristic and combines IF gain with AGC gain.

## Test Signals
Tests should cover attach with default and custom PLL settings, symbol-rate limit updates from `sysclk`, init with `deltaf` and output-mode overrides, each supported QAM mode on Annex A/C, external tuner gate sequencing, status decoding from register `0x11`, BER/UCB reset behavior, AFC frequency correction, standby mode, and failure paths for invalid delivery or unsupported QAM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda10023.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda1002x.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda1002x.h

## Purpose
`tda1002x.h` is the public board-facing header for the TDA10021 and TDA10023 DVB-C demodulator drivers. It defines board configuration structures, output-mode constants for TDA10023, and Kconfig-gated attach prototypes or inline stubs.

## Important APIs, Types, and Functions
`struct tda1002x_config` contains the TDA10021 demodulator I2C address and inversion flag. `enum tda10023_output_mode` declares three parallel TS modes and a serial placeholder. `struct tda10023_config` adds clock PLL fields, TS output mode, and `deltaf` to the demod address/inversion configuration. The attach APIs are `tda10021_attach()` and `tda10023_attach()`, each returning a `struct dvb_frontend *` or `NULL`.

## Control Flow
The header has no runtime flow beyond conditional compilation. When the relevant Kconfig symbol is reachable, consumers call the real attach function from the module. Otherwise the inline stub logs that the driver is disabled and returns `NULL`, allowing bridge drivers to compile without the demodulator driver.

## State and Persistence Behavior
No state is owned here. The structures describe immutable board configuration consumed by the `.c` drivers during attach and tuning. Persistence is limited to board-driver static data or platform data that instantiates these structs.

## Dependencies and Integration Points
The header includes `<linux/dvb/frontend.h>` and assumes I2C adapter types are visible to consumers. It is included by `tda10021.c`, `tda10023.c`, and board/bridge drivers that instantiate these demodulators.

## Risks and Edge Cases
The `invert` flag affects spectral inversion semantics differently in callers, so board data must match hardware wiring. `TDA10023_OUTPUT_MODE_SERIAL` is exposed but not implemented by the driver. Kconfig stubs log at runtime and return `NULL`, so bridge drivers must handle attach failure cleanly.

## Test Signals
Compile coverage should include enabled and disabled Kconfig combinations, bridge callers using both config structures, custom TDA10023 PLL fields, output-mode constants, and attach-failure handling through the inline stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda1002x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda10048.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda10048.c

## Purpose
`tda10048.c` implements the NXP TDA10048HN DVB-T OFDM demodulator. It identifies the chip, loads DSP firmware unless disabled by board config, programs PLL/IF/bandwidth and transport stream output mode, drives tuner setup through an I2C gate, and exposes DVB-T TPS/status/quality callbacks.

## Important APIs, Types, and Functions
The exported attach API is `tda10048_attach()`. `struct tda10048_state` stores a cloned config, I2C adapter, frontend, firmware-loaded flag, IF/xtal/PLL/sample-frequency data, and current bandwidth. Key helpers are `tda10048_writereg()`, `tda10048_readreg()`, `tda10048_writeregbulk()`, `tda10048_set_phy2()`, `tda10048_set_wref()`, `tda10048_set_invwref()`, `tda10048_set_if()`, `tda10048_firmware_upload()`, `tda10048_set_inversion()`, `tda10048_get_tps()`, `tda10048_i2c_gate_ctrl()`, `tda10048_output_mode()`, `tda10048_init()`, `tda10048_set_frontend()`, and the metric callbacks.

## Control Flow
Attach allocates state, copies board config, treats `no_firmware` as an already-loaded marker, checks identity register `0x00` for `0x48`, selects default or board PLL factors, applies config defaults, computes an initial 8 MHz IF/sample setup, and closes the gate. Init writes a static register table patched with PLL factors, uploads `dvb-fe-tda10048-1.0.fw` in 50- or 200-byte chunks if needed, selects serial or parallel TS mode, applies inversion, sets default 8 MHz IF/bandwidth, and leaves the I2C gate closed. Set-fronted recomputes IF and timing when bandwidth changes, gates tuner access around external tuner setup, enables TPS auto-detection, and triggers BER acquisition.

## State and Persistence Behavior
The driver maintains volatile state only: firmware-loaded flag, current bandwidth, PLL factors, IF frequency, sample frequency, and a cloned mutable config with defaulted fields. The DSP firmware is loaded from the kernel firmware interface but not persisted by the driver. BER reading caches the last CBER in a static function-local variable updated when the soft interrupt says data is fresh, and then retriggers acquisition. UCB reads clear the hardware counter on saturation.

## Dependencies and Integration Points
The file depends on the Linux firmware loader, DVB frontend APIs, I2C transfers, 64-bit division, and `tda10048.h`. It integrates with board tuners through `fe->ops.tuner_ops.set_params` and the demod I2C gate. Module metadata exports `tda10048_attach()` and advertises firmware filename/size requirements implicitly through upload checks.

## Risks and Edge Cases
Firmware size must exactly match `24878` bytes or init fails. Invalid IF/clock combinations not present in `pll_tab` fail attach or tune. The static CBER cache is shared at function scope rather than per frontend, which is risky for multiple devices. Several register writes in setup ignore return values, so partial I2C failures can surface later as lock failure. `tda10048_set_phy2()` has separate low/high IF math and depends on nonzero sample frequency.

## Test Signals
Test signals include chip ID rejection, config default warnings, accepted IF/clock combinations for 6/7/8 MHz, firmware missing/wrong-size/successful upload, bulk write length selection, serial and parallel TS mode programming, disabled gate behavior, external tuner gate sequencing, DVB-T lock bit mapping, TPS decoding for modulation/FEC/guard/transmission/hierarchy, BER interrupt update and retrigger, UCB saturation reset, and attach with `no_firmware`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda10048.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda10048.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda10048.h

## Purpose
`tda10048.h` defines the board configuration interface for the TDA10048HN DVB-T demodulator and declares the attach API.

## Important APIs, Types, and Functions
`struct tda10048_config` contains demod I2C address, serial/parallel output selection, firmware bulk-write length, spectral inversion, per-bandwidth IF frequencies, clock frequency, gate-disable flag, firmware-bypass flag, and optional PLL factors. Macros define accepted output modes, firmware write chunk sizes, inversion values, IF presets, and clock presets. `tda10048_attach()` returns a DVB frontend when `CONFIG_DVB_TDA10048` is reachable; otherwise the inline stub logs and returns `NULL`.

## Control Flow
The header itself only routes compile-time control through Kconfig. Runtime behavior comes from the `.c` file, which mutates a cloned copy of this config to fill defaults and then uses it during init and tune.

## State and Persistence Behavior
No runtime state is owned by the header. The struct is board configuration; `no_firmware` changes whether the driver uploads firmware, and `set_pll` changes whether PLL factors are taken from config or defaults.

## Dependencies and Integration Points
It includes DVB frontend and firmware headers and is consumed by the TDA10048 driver and board/bridge drivers.

## Risks and Edge Cases
Only IF/clock combinations represented by the driver table are usable. `disable_gate_access` changes tuner integration semantics and must match board wiring. `fwbulkwritelen` accepts only 50 or 200 bytes in the implementation; other values silently default.

## Test Signals
Compile tests should cover enabled/disabled Kconfig attach paths. Runtime configuration tests should cover all IF presets used by board files, firmware bypass, PLL override, serial/parallel TS mode, and gate-disabled boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda10048.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda1004x.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda1004x.c

## Purpose
`tda1004x.c` implements Philips TDA10045H and TDA10046H DVB-T OFDM demodulators. It handles low-level I2C register access, firmware or EEPROM boot, PLL/IF/bandwidth programming, auto/manual DVB-T parameter acquisition, tuner I2C gating, status and quality reporting, sleep, and exported attach functions for both chip variants.

## Important APIs, Types, and Functions
The exported APIs are `tda10045_attach()` and `tda10046_attach()`. Shared state is `struct tda1004x_state` from the header. Low-level helpers include `tda1004x_write_byteI()`, `tda1004x_read_byte()`, `tda1004x_write_mask()`, `tda1004x_write_buf()`, `tda1004x_enable_tuner_i2c()`, and `tda1004x_disable_tuner_i2c()`. Firmware and setup helpers include `tda1004x_do_upload()`, `tda1004x_check_upload_ok()`, `tda10045_fwupload()`, `tda10046_init_plls()`, `tda10046_fwupload()`, `tda10045_init()`, and `tda10046_init()`. Runtime callbacks include `tda1004x_set_fe()`, `tda1004x_get_fe()`, `tda1004x_read_status()`, metrics, `tda1004x_sleep()`, `tda1004x_i2c_gate_ctrl()`, and `tda1004x_get_tune_settings()`.

## Control Flow
Attach allocates state, selects demod type, reads chip ID, validates `0x25` for TDA10045 or `0x46` for TDA10046, and copies the corresponding frontend ops. Init performs firmware validation and upload if needed, then programs demod-specific ADC, PLL, AGC, transport stream, output clock, and measurement registers. TDA10045 always loads host firmware if needed. TDA10046 wakes the chip, configures GPIO/PLL/ADC, tries internal EEPROM boot first, and falls back to firmware file loading. Set-fronted gates the external tuner for frequency tuning, forces TDA10045 to auto mode for unreliable manual paths, programs manual or automatic FEC/QAM/hierarchy/guard/transmission settings, writes bandwidth tables, applies inversion with board inversion correction, and starts acquisition via reset or auto bits.

## State and Persistence Behavior
The driver stores only volatile per-frontend state and uses board config callbacks for firmware requests. Firmware is loaded from files or EEPROM into the demodulator DSP but not persisted by this driver. Hardware counters are read and reset in BER/UCB paths. Sleep powers down ADCs or tristates outputs and can invert configured GPIO states for sleep mode on TDA10046. No user-visible persistent settings are written.

## Dependencies and Integration Points
Dependencies include Linux I2C, firmware loading via board `request_firmware`, DVB frontend core, jiffies/timeouts, and `tda1004x.h`. Integration is through frontend ops, board tuner callbacks, the `write` callback used by `tda1004x_writereg()`, and exported attach functions used by bridge drivers and board headers such as `tdhd1.h`.

## Risks and Edge Cases
Firmware boot has multiple timing-sensitive paths and bus-locking requirements; TDA10046 EEPROM boot warns that concurrent I2C traffic can leave the chip unstable. Many register writes ignore return values, so failed initialization can be latent. TDA10045 manual tuning is intentionally avoided because it is unreliable. Bandwidth and IF tables are discrete and reject unsupported bandwidths. Several hardware-bug workarounds require dummy reads of BER reset/LUT registers. GPIO sleep inversion must match board hardware.

## Test Signals
Tests should cover attach ID validation for both variants, firmware already loaded, missing firmware, EEPROM boot success/failure, TDA10046 4/16 MHz xtal and 48/53 MHz sample-clock IF modes, AGC configuration variants, serial/parallel TS output and inverted output clock, 6/7/8 MHz bandwidth tables, auto and manual DVB-T tuning, status fallback using CBER/VBER when not locked, BER/UCB counter reset behavior, tuner gate control, and sleep GPIO/ADC state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda1004x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda1004x.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda1004x.h

## Purpose
`tda1004x.h` is the public configuration and shared-state header for the TDA10045H/TDA10046H DVB-T demodulator driver. It exposes board configuration enums, state layout, attach prototypes, and a small register-write convenience wrapper.

## Important APIs, Types, and Functions
The header defines `enum tda10046_xtal`, `enum tda10046_agc`, `enum tda10046_gpio`, `enum tda10046_if`, and `enum tda10046_tsout`. `struct tda1004x_config` describes demod address, inversion flags, TS mode, crystal, IF, AGC, GPIOs, tuner address/switch data, optional external I2C gate address, and firmware request callback. `enum tda1004x_demod` and `struct tda1004x_state` are shared by the implementation. Public attach functions are `tda10045_attach()` and `tda10046_attach()`. `tda1004x_writereg()` calls the frontend `.write` op for board helpers.

## Control Flow
The header has Kconfig-gated attach declarations or inline stubs. Runtime flow is in `tda1004x.c`; the inline `tda1004x_writereg()` is a thin wrapper that sends a two-byte register write through the frontend op if present.

## State and Persistence Behavior
The header declares volatile runtime state but owns no persistence. Board configuration values are static inputs that drive firmware selection, hardware polarity, GPIO sleep behavior, and IF/AGC programming.

## Dependencies and Integration Points
It includes DVB frontend and firmware interfaces and is used by the demodulator implementation and board-specific helpers such as `tdhd1.h`. The firmware callback allows bridge drivers to provide custom firmware retrieval behavior.

## Risks and Edge Cases
Board config is dense and hardware-specific; incorrect IF, GPIO, xtal, or AGC enum values can produce attach success but no lock. `tda1004x_writereg()` silently returns zero when `.write` is absent, so callers must only use it on frontends with the driver-installed write op. Kconfig stubs require bridge drivers to handle `NULL`.

## Test Signals
Compile coverage should include enabled/disabled Kconfig, consumers of both attach functions, board configs for GPIO inversion and TS modes, firmware callback wiring, and external users of `tda1004x_writereg()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda1004x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda10071.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda10071.c

## Purpose
`tda10071.c` implements the NXP TDA10071 plus Conexant CX24118A DVB-S/S2 demodulator/tuner as a modern I2C client driver. It loads firmware, initializes the demodulator and internal tuner through firmware commands, handles DVB-S/S2 tuning, DiSEqC, tone and voltage controls, and reports both DVBv3 callbacks and DVBv5 statistics.

## Important APIs, Types, and Functions
The driver registers an `i2c_driver` named `tda10071` and exposes the frontend through platform-data callback `get_dvb_frontend`. `tda10071_probe()` validates chip ID/type/version and installs `tda10071_ops`; `tda10071_remove()` frees state. Important helpers are `tda10071_wr_reg_mask()`, `tda10071_cmd_execute()`, `tda10071_init()`, `tda10071_set_frontend()`, `tda10071_get_frontend()`, `tda10071_read_status()`, metric callbacks, DiSEqC send/receive helpers, `tda10071_set_tone()`, `tda10071_set_voltage()`, and `tda10071_sleep()`.

## Control Flow
Probe builds a regmap, copies platform data into `struct tda10071_dev`, validates registers `0xff`, `0xdd`, and `0xfe`, and gives the bridge a frontend getter. Init has warm and cold branches. In cold state it requests `dvb-fe-tda10071.fw`, writes boot registers, downloads firmware in chunks bounded by `i2c_wr_max`, checks firmware status/version, then sends firmware commands for demod init, tuner init, MPEG TS config, LNB config, and BER control. In warm state it writes wake registers and sends sleep-mode off. `set_frontend` validates inversion, delivery, rolloff, pilot, modulation/FEC via `TDA10071_MODCOD`, programs symbol-rate-dependent dividers, sends `CMD_CHANGE_CHANNEL`, and records the active delivery system. Status reads hardware lock bits and, when locked or partially locked, updates strength, CNR, BER, PER/UCB counters through firmware commands.

## State and Persistence Behavior
State is in `struct tda10071_dev`: platform clock/TS/spectrum/tuner settings, warm flag, last frontend status, delivery system, BER measurement count, DVBv3 BER, and cumulative post-bit and block error counters. Firmware is loaded into the chip at runtime and `warm` records whether it is running. The driver initializes DVBv5 stat lengths/scales on init and updates counters cumulatively. Sleep sends a firmware sleep command and writes standby register masks.

## Dependencies and Integration Points
The driver depends on I2C client binding, regmap, firmware loader, DVB frontend core, platform data in `tda10071.h`, and private tables/macros in `tda10071_priv.h`. It integrates with bridge drivers by setting `pdata->get_dvb_frontend`, and with satellite control APIs through DiSEqC, tone, and voltage frontend ops.

## Risks and Edge Cases
Most runtime commands fail with `-EFAULT` if firmware is not warm, so callers must run init successfully before tune/SEC operations. Firmware command execution uses a single mutex and polls register `0x1f` up to 1000 iterations; timeouts block tuning and satellite control. Platform `i2c_wr_max` must be greater than one for firmware download chunking to make progress. `CMD_BER_UPDATE_COUNTERS` is skipped when `meas_count` has not changed, so polling cadence affects stats freshness. Rolloff auto is rejected for DVB-S2. DiSEqC send/receive waits can take seconds on hardware that never reports ready.

## Test Signals
Useful tests include probe ID/type/version rejection, firmware missing and successful cold boot, warm resume path, firmware command timeout, all supported MODCOD mappings, invalid rolloff/pilot/FEC/modulation combinations, low versus high symbol-rate divider selection, DVB-S and DVB-S2 stats update, cumulative BER/UCB behavior, DiSEqC master/reply/toneburst length validation and timeout, tone/voltage controls, sleep/wake, and platform TS/tuner address variations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda10071.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda10071.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda10071.h

## Purpose
`tda10071.h` defines the platform-data contract for the TDA10071 DVB-S/S2 I2C client driver.

## Important APIs, Types, and Functions
`struct tda10071_platform_data` provides clock frequency, maximum I2C write size, TS mode (`TDA10071_TS_SERIAL` or `TDA10071_TS_PARALLEL`), spectrum inversion flag, PLL multiplier, CX24118A tuner I2C address, and a driver-filled `get_dvb_frontend` callback.

## Control Flow
The bridge creates an I2C client with this platform data. During probe the driver copies configuration fields into private state and stores a frontend getter in the same platform data, which the bridge later calls to retrieve the initialized `struct dvb_frontend`.

## State and Persistence Behavior
The header owns no runtime state. The config fields are board-specific constants; `get_dvb_frontend` is mutable callback state filled by the driver after successful probe.

## Dependencies and Integration Points
It includes the DVB frontend header and is included by `tda10071_priv.h` and board/bridge code that instantiates the I2C client.

## Risks and Edge Cases
There are no defaults in the header; invalid `clk`, `i2c_wr_max`, PLL, TS mode, or tuner address values are consumed by probe/init and can break firmware download or tuning. `get_dvb_frontend` is valid only after successful probe.

## Test Signals
Compile coverage should include board users of serial and parallel TS modes. Runtime tests should verify platform-data propagation into probe/init, frontend getter installation, and failure behavior when platform data fields are invalid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda10071.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda10071_priv.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda10071_priv.h

## Purpose
`tda10071_priv.h` contains private state, MODCOD mapping, register-mask helper structures, firmware filename, command IDs, and command-buffer layout for the TDA10071 implementation.

## Important APIs, Types, and Functions
`struct tda10071_dev` is the driver state: frontend, I2C client, regmap, command mutex, platform settings, measurement counters, cached frontend status, delivery system, warm flag, and cumulative DVBv5 error counters. `TDA10071_MODCOD[]` maps delivery/modulation/FEC combinations to firmware mode bytes. `struct tda10071_reg_val_mask` supports masked register scripts. `struct tda10071_cmd` holds up to `TDA10071_ARGLEN` command bytes. Macros define `TDA10071_FIRMWARE` and all firmware command IDs.

## Control Flow
The header has no standalone flow. `tda10071.c` uses the MODCOD table during tune validation, uses command IDs for firmware RPCs, and uses the state fields across probe/init/tune/status/sleep.

## State and Persistence Behavior
It declares volatile runtime state only. `warm` records firmware-running state, `meas_count` suppresses repeated metric updates, and `post_bit_error`/`block_error` accumulate software counters over time.

## Dependencies and Integration Points
It includes DVB frontend, public `tda10071.h`, firmware, and regmap interfaces. It is private to `tda10071.c`.

## Risks and Edge Cases
`TDA10071_MODCOD` defines the accepted tuning matrix; unsupported but theoretically valid combinations will be rejected. `TDA10071_ARGLEN` must cover every command sequence; adding longer firmware commands requires changing this bound. The table is not `const`, so accidental writes would alter tune validation globally.

## Test Signals
Tests should cover all MODCOD entries, command buffer lengths for each firmware command, metric counter accumulation, and initialization paths that transition `warm` from false to true.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda10071_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda10086.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda10086.c

## Purpose
`tda10086.c` implements the Philips TDA10086 DVB-S demodulator. It programs PLL, ADC, AGC, Viterbi, carrier recovery, SEC/DiSEqC registers, drives external tuner setup, supports DVB-S QPSK tuning, and exposes DVB frontend status and metric callbacks.

## Important APIs, Types, and Functions
The exported API is `tda10086_attach()`. `struct tda10086_state` stores I2C adapter, config, frontend, last requested frequency/symbol rate, and a `has_lock` flag used to switch to stable reception settings after first lock. Key functions are `tda10086_write_byte()`, `tda10086_read_byte()`, `tda10086_write_mask()`, `tda10086_init()`, `tda10086_set_inversion()`, `tda10086_set_symbol_rate()`, `tda10086_set_fec()`, `tda10086_set_frontend()`, `tda10086_get_frontend()`, `tda10086_read_status()`, metric callbacks, `tda10086_i2c_gate_ctrl()`, DiSEqC helpers, `tda10086_set_tone()`, and `tda10086_sleep()`.

## Control Flow
Attach allocates state, reads register `0x1e`, validates ID `0xe1`, and copies frontend ops. Init resets the chip, writes fixed demod/PLL/TS/ADC/AGC/Viterbi/carrier/SEC defaults, selects PLL factors based on 4 MHz or 16 MHz xtal, and programs the 22 kHz tone divisor. Set-fronted resets acquisition state, calls the external tuner, asks the tuner for actual tuned frequency, computes demod frequency offset, writes inversion, symbol-rate and FEC registers, then soft-resets and disables TS output until lock. `read_status` maps lock bits from register `0x0e`; on first lock it clears register `0x02` to stabilize reception. `get_frontend` reconstructs frequency, inversion, symbol rate, and FEC from hardware registers plus cached requested values.

## State and Persistence Behavior
Only volatile state is kept. The cached requested frequency and symbol rate are required for `get_frontend()` correction calculations. `has_lock` prevents repeatedly writing the stable reception register after lock. BER and UCB reads consume hardware counters; UCB read resets the counter. Sleep sets a powerdown bit.

## Dependencies and Integration Points
The file depends on DVB frontend APIs, Linux I2C, jiffies/timeouts, and `tda10086.h`. It integrates with external satellite tuners through `tuner_ops.set_params`, `get_frequency`, and the demod I2C gate. DiSEqC/tone operations are exposed through frontend SEC callbacks.

## Risks and Edge Cases
Symbol-rate calculations assume `SACLK` is 96 MHz. `set_tone()` and `send_burst()` do not reject invalid enum values explicitly in all switch paths. `set_frontend()` closes the I2C gate twice around tuner frequency retrieval, which is harmless for this driver but sensitive to gate implementations. DiSEqC wait times out after 200 ms but still restores registers and returns success. Return values from many writes are ignored.

## Test Signals
Tests should cover ID validation, 4 MHz and 16 MHz xtal init paths, tone-with-carrier configuration, symbol-rate thresholds and bypass mode, all supported FEC values plus invalid rejection, external tuner frequency-offset correction, first-lock stabilization, get_frontend corrections, BER/UCB/SNR/strength reads, I2C gate control, DiSEqC master and mini-burst behavior, and sleep/release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda10086.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda10086.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda10086.h

## Purpose
`tda10086.h` defines the board configuration and attach interface for the Philips TDA10086 DVB-S demodulator.

## Important APIs, Types, and Functions
`enum tda10086_xtal` identifies 16 MHz and 4 MHz reference crystals. `struct tda10086_config` contains demod I2C address, spectrum inversion wiring flag, DiSEqC tone-carrier mode, and xtal frequency. `tda10086_attach()` is declared when the driver is reachable; otherwise an inline stub logs that the driver is disabled and returns `NULL`.

## Control Flow
There is no runtime flow except Kconfig-gated attach selection. The implementation reads the config during attach/init/tune/SEC control.

## State and Persistence Behavior
The header owns no state. Config fields are board constants that determine PLL setup, inversion interpretation, and tone-register programming.

## Dependencies and Integration Points
It includes DVB frontend and firmware headers and is consumed by bridge drivers and `tda10086.c`.

## Risks and Edge Cases
Wrong xtal or inversion settings can produce valid attach but failed lock. Kconfig stubs require callers to handle `NULL` attach results.

## Test Signals
Compile tests should cover enabled and disabled driver configs; runtime board tests should cover both xtal values, inversion wiring, and DiSEqC tone-carrier choices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda10086.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda18271c2dd.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda18271c2dd.c

## Purpose
`tda18271c2dd.c` implements a Digital Devices variant of the NXP TDA18271C2 terrestrial/cable tuner. It attaches tuner ops to an existing frontend, initializes fixed tuner contents, calibrates RF tracking filters, tunes DVB-T/T2 and DVB-C channels, reports IF frequency, and maintains a register/cache and calibration model in memory.

## Important APIs, Types, and Functions
The exported API is `tda18271c2dd_attach()`. `struct tda_state` stores I2C address/adapter, current RF frequency and IF, IF level settings, standby/EP registers, master/slave mode, register cache, per-band RF calibration curve data, calibration temperature, and FM-input mode. Low-level helpers include `i2c_readn()`, `i2c_write()`, `WriteRegs()`, `WriteReg()`, `Read()`, `ReadExtented()`, `UpdateRegs()`, and `UpdateReg()`. Mapping/calibration helpers include `SearchMap1..4()`, `ThermometerRead()`, `CalcMainPLL()`, `CalcCalPLL()`, `PowerScan()`, `CalibrateRF()`, `RFTrackingFiltersInit()`, `CalcRFFilterCurve()`, `FixedContentsI2CUpdate()`, `InitCal()`, `RFTrackingFiltersCorrection()`, and `ChannelConfiguration()`. Tuner callbacks are `set_params()`, `sleep()`, `release()`, `get_if_frequency()`, and `get_bandwidth()`.

## Control Flow
Attach allocates `tda_state`, installs `tuner_ops`, calls `reset()` to initialize software defaults, and immediately runs `InitCal()`. Initialization writes fixed register contents, performs image-rejection calibration for low/mid/high bands, scans and calibrates RF tracking filters for all seven RF bands, reads calibration temperature, and enters standby. During tuning, `set_params()` chooses a standard based on delivery system and bandwidth, applies temperature-aware RF tracking correction for the target frequency, then runs `ChannelConfiguration()` to select filters, RF band, IF level, PLL source, and channel PLL values, followed by AGC settling delay.

## State and Persistence Behavior
The driver has rich volatile state but no persistence. `m_Regs[]` mirrors the hardware register file and is the source for range writes. Calibration results are stored in `m_RF*`, `m_RF_A*`, `m_RF_B*`, and `m_TMValue_RFCal` arrays and reused for later RF tracking corrections. `state->IF` is updated from the standard table and returned by `get_if_frequency()`. Sleep transitions the cached register set and hardware to standby.

## Dependencies and Integration Points
The file depends on DVB frontend tuner ops, Linux I2C, division helpers, and calibration maps from `tda18271c2dd_maps.h`. It is attached by bridge/demod drivers to fill `fe->ops.tuner_ops` and uses the frontend property cache for frequency, delivery system, and bandwidth.

## Risks and Edge Cases
`MAX_XFER_SIZE` limits bulk writes to 63 payload bytes; longer ranges are rejected. Calibration is long, timing-sensitive, and mostly fails fast on I2C errors. `RFTrackingFiltersCorrection()` appears to initialize `RF2` and `RF3` from `m_RF1`, which may be intentional fallback or a bug affecting piecewise correction. Attach ignores the return value of `InitCal()`, so a failed calibration can still return an attached tuner. `get_bandwidth()` is a stub returning zero status without setting a value.

## Test Signals
Tests should cover attach and failed calibration handling, fixed-content writes, power scan for each RF band, RF calibration with map lookup failures, thermometer compensation, DVB-T 6/7/8 MHz, DVB-T2, DVB-C bandwidth choices, IF frequency reporting, standby transition, I2C write-size rejection, and tuning across RF band boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda18271c2dd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda18271c2dd.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda18271c2dd.h

## Purpose
`tda18271c2dd.h` declares the attach interface for the Digital Devices TDA18271C2 tuner driver.

## Important APIs, Types, and Functions
The public API is `tda18271c2dd_attach(struct dvb_frontend *fe, struct i2c_adapter *i2c, u8 adr)`. When `CONFIG_DVB_TDA18271C2DD` is not enabled, the inline stub logs that the driver is disabled and returns `NULL`.

## Control Flow
The header only selects the real attach function or stub at compile time. The real attach installs tuner ops into the supplied frontend.

## State and Persistence Behavior
No state is defined here. Runtime state is allocated by the implementation and stored in `fe->tuner_priv`.

## Dependencies and Integration Points
It depends on DVB frontend and I2C types from including code. Bridge drivers include this header to attach the tuner to a demodulator frontend.

## Risks and Edge Cases
The API mutates the caller's frontend in place; callers must not overwrite `tuner_ops` afterward unless intentionally replacing the tuner. Disabled Kconfig stubs require `NULL` handling.

## Test Signals
Compile tests should cover reachable and unreachable Kconfig paths. Runtime tests should confirm attach mutates `fe->tuner_priv` and `fe->ops.tuner_ops` and that attach failure does not leave stale tuner state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda18271c2dd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda18271c2dd_maps.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda18271c2dd_maps.h

## Purpose
`tda18271c2dd_maps.h` supplies the static standard, frequency, PLL, RF calibration, gain, thermometer, and band maps used by the TDA18271C2DD tuner implementation.

## Important APIs, Types, and Functions
The header defines `enum HF_S` standards such as analog TV, FM, ATSC, DVB-T 6/7/8 MHz, DVB-C 6/7/8 MHz, and digital max markers. Static tables include `m_StandardTable`, `m_BP_Filter_Map`, `m_RF_Cal_Map`, `m_KM_Map`, `m_Main_PLL_Map`, `m_Cal_PLL_Map`, `m_GainTaper_Map`, `m_RF_Cal_DC_Over_DT_Map`, `m_IR_Meas_Map`, `m_CID_Target_Map`, `m_RF_Band_Map`, and two thermometer maps.

## Control Flow
There is no executable flow; `tda18271c2dd.c` searches these sorted sentinel-terminated maps with `SearchMap*()` helpers to choose calibration constants, PLL divisors, filter settings, RF bands, and standard IF/bandwidth values.

## State and Persistence Behavior
All data is static read-mostly table data. The implementation uses it to derive volatile register values and calibration curves; it does not modify the tables.

## Dependencies and Integration Points
The header relies on struct definitions declared earlier in `tda18271c2dd.c`, so it is implementation-private and included only after those type definitions. It is not a standalone public header.

## Risks and Edge Cases
Map ordering and sentinel rows are essential because the search helpers stop at the first frequency ceiling or zero terminator. Incorrect table ranges can reject tuning or select bad PLL/filter parameters. Because the file is included into a C file after type declarations, moving it or including it elsewhere would fail unless those structs are visible.

## Test Signals
Tests should cover map lookup at lower/upper boundaries, sentinel failure behavior above supported ranges, every RF band row, standard selection for DVB-T and DVB-C bandwidths, and calibration output stability across representative frequencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda18271c2dd_maps.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda665x.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda665x.c

## Purpose
`tda665x.c` implements a simple TDA665x terrestrial/cable tuner ops provider. It attaches to an existing frontend, programs PLL divider and band/current-selection bytes over I2C, reports cached frequency and PLL lock status, and exposes tuner metadata from board config.

## Important APIs, Types, and Functions
The exported API is `tda665x_attach()`. `struct tda665x_state` stores the parent frontend, I2C adapter, config, cached frequency, and bandwidth. Helpers include `tda665x_read()`, `tda665x_write()`, `tda665x_get_frequency()`, `tda665x_get_status()`, `tda665x_set_frequency()`, `tda665x_set_params()`, and `tda665x_release()`.

## Control Flow
Attach allocates state, stores config/I2C/frontend pointers, installs `tda665x_ops`, and copies tuner info from config. `set_params()` calls `tda665x_set_frequency()` with the frontend cached frequency. Frequency programming validates range, converts RF frequency through board offset/reference divider/multiplier, writes PLL bytes, selects low/mid/high band and charge-pump current based on frequency, waits 20 ms, checks PLL lock, and caches frequency on lock.

## State and Persistence Behavior
The driver keeps only volatile cached frequency and board config pointer. No standby callback is provided. PLL lock status is read from the tuner status byte, and cached frequency is updated only when lock is observed.

## Dependencies and Integration Points
It depends on DVB frontend tuner ops, Linux I2C, and `tda665x.h`. Board config supplies tuner name, I2C address, frequency limits, offset, and reference parameters.

## Risks and Edge Cases
The frequency range check appears inverted: it rejects when `new_frequency < frequency_max` or `new_frequency > frequency_min`, which would reject most normal values if min/max are conventional. `tda665x_set_frequency()` declares a 4-byte buffer but calls `tda665x_write()` with length 5, which is an out-of-bounds read risk. Several frequency thresholds use values like `1040000000` and `1250000000` in a path labeled VHF-L, likely typo-scale errors. The driver returns success even if lock is not achieved.

## Test Signals
Tests should explicitly cover frequency-range validation, buffer length under sanitizers, PLL programming bytes for VHF-L/VHF-H/UHF, lock and no-lock behavior, I2C read/write errors, tuner info propagation from config, and detach release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda665x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda665x.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda665x.h

## Purpose
`tda665x.h` defines board configuration and attach declarations for the TDA665x tuner driver.

## Important APIs, Types, and Functions
`struct tda665x_config` provides tuner display name, I2C address, min/max frequency, frequency offset, reference multiplier, and reference divider. `tda665x_attach()` attaches tuner ops to an existing frontend when the driver is reachable; otherwise an inline stub logs disabled Kconfig and returns `NULL`.

## Control Flow
The header contributes only compile-time attach selection. The config is consumed by `tda665x.c` during attach and frequency programming.

## State and Persistence Behavior
No runtime state is declared here; config data is board-owned and read by the tuner implementation.

## Dependencies and Integration Points
The header is used by bridge drivers and `tda665x.c`; it expects DVB frontend and I2C types from the build context.

## Risks and Edge Cases
Min/max and offset semantics must match the implementation, which has suspicious validation and buffer behavior. Name length is fixed at 128 and copied into tuner info.

## Test Signals
Compile tests should include enabled/disabled Kconfig paths; runtime config tests should validate frequency limits, offset/divider math, and name propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda665x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda8083.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda8083.c

## Purpose
`tda8083.c` implements the Philips TDA8083 DVB-S QPSK demodulator. It initializes a fixed register table, supports FEC and symbol-rate programming, controls tone/voltage/DiSEqC, tunes through an external tuner, and reports DVB-S lock and quality metrics.

## Important APIs, Types, and Functions
The exported API is `tda8083_attach()`. `struct tda8083_state` stores I2C adapter, config, and frontend. Important helpers include `tda8083_writereg()`, `tda8083_readregs()`, `tda8083_readreg()`, `tda8083_set_inversion()`, `tda8083_set_fec()`, `tda8083_get_fec()`, `tda8083_set_symbolrate()`, `tda8083_wait_diseqc_fifo()`, SEC helpers, `tda8083_init()`, `tda8083_set_frontend()`, `tda8083_get_frontend()`, status/metric callbacks, sleep, and release.

## Control Flow
Attach allocates state, validates register `0x00` equals `0x05`, and copies frontend ops. Init writes 44 default registers and toggles reset/acquisition. Set-fronted tunes the external tuner, closes the gate, accepts only automatic inversion, programs FEC mask and symbol-rate ratio/filter, then restarts acquisition. DiSEqC operations write message bytes or toneburst commands, wait for FIFO readiness, then reset the frontend. Status maps signal from inverted register `0x01` and sync bits from register `0x02`, including timeout and full-lock conditions.

## State and Persistence Behavior
The driver stores no cached tune state beyond private pointers. Hardware counters are read directly; UCB `0xff` is translated to `0xffffffff`. Sleep writes a power/reset register. No persistent state is maintained.

## Dependencies and Integration Points
It depends on DVB frontend APIs, Linux I2C, jiffies, and `tda8083.h`. It integrates with external tuners through `tuner_ops.set_params` and optional demod I2C gate callback.

## Risks and Edge Cases
`tda8083_set_inversion()` only accepts `INVERSION_AUTO`; other modes return `-EINVAL`, despite `get_frontend()` reporting on/off. `tda8083_send_diseqc_msg()` does not validate `msg_len`, so callers outside DVB core bounds could overflow the six message registers. `tda8083_set_symbolrate()` returns `1` on success rather than `0`, but callers ignore it. Several read helpers return a byte even after read failure.

## Test Signals
Tests should cover attach ID validation, init table write, symbol-rate clamps and ratio math, automatic and invalid inversion behavior, FEC mask programming, status bit mapping including timeout, DiSEqC master/toneburst/tone/voltage operations, BER/SNR/strength/UCB reads, external tuner integration, and sleep.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda8083.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda8083.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda8083.h

## Purpose
`tda8083.h` defines the board configuration and attach API for the Philips TDA8083 DVB-S demodulator.

## Important APIs, Types, and Functions
`struct tda8083_config` contains the demodulator I2C address. `tda8083_attach()` attaches the demodulator to an I2C adapter when Kconfig allows it; otherwise the inline stub logs a disabled-driver warning and returns `NULL`.

## Control Flow
Only Kconfig-gated attach selection occurs here. The implementation consumes the demod address for all I2C register access.

## State and Persistence Behavior
No state is owned here. The config is static board data.

## Dependencies and Integration Points
It includes DVB frontend and I2C-facing types from the build environment and is used by board/bridge drivers and `tda8083.c`.

## Risks and Edge Cases
The minimal config means all hardware behavior is fixed in the implementation; boards with different inversion or SEC wiring cannot express that here. Disabled Kconfig stubs require attach failure handling.

## Test Signals
Compile coverage should include enabled/disabled Kconfig paths; runtime tests should confirm demod address selection and bridge behavior on `NULL` attach.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda8083.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda8261.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda8261.c

## Purpose
`tda8261.c` implements the TDA8261 8PSK/QPSK satellite tuner. It attaches tuner ops to an existing frontend, programs PLL divider/reference step settings over I2C from frontend frequency, reads PLL lock status, and caches the successfully locked frequency.

## Important APIs, Types, and Functions
The exported API is `tda8261_attach()`. `struct tda8261_state` stores the parent frontend, I2C adapter, config, cached frequency, and bandwidth. Helpers include `tda8261_read()`, `tda8261_write()`, `tda8261_get_status()`, `tda8261_get_frequency()`, `tda8261_set_params()`, and `tda8261_release()`. Divider tables `div_tab[]` and `ref_div[]` map `enum tda8261_step` values to channel spacing and register bits.

## Control Flow
Attach allocates state, stores config/I2C/frontend pointers, sets `fe->tuner_priv`, installs `tda8261_ops`, and sets tuner frequency step from config. `set_params()` validates 950000 to 2150000 kHz, computes divider `N` from configured step size, writes four PLL/control bytes, sleeps 20 ms, checks lock through `get_status()`, and caches the frequency on lock.

## State and Persistence Behavior
Only volatile cached frequency/bandwidth and config pointers are stored. Frequency cache updates only on PLL lock. There is no sleep callback, so power state is not actively managed by this tuner.

## Dependencies and Integration Points
It depends on DVB frontend tuner ops, Linux I2C, and `tda8261.h`. It is used by satellite demod bridge paths that provide frequency in kHz in the property cache.

## Risks and Edge Cases
`config->step_size` is used as an array index without validation; invalid board data can read past `div_tab`/`ref_div`. The driver returns success even when PLL lock is not achieved. I2C helpers return raw transfer counts, so callers treat some positive nonstandard results as success. `bandwidth` state is unused.

## Test Signals
Tests should cover all step sizes, invalid step-size board data, frequency min/max rejection, PLL byte generation, lock and no-lock paths, I2C errors, frequency cache behavior, tuner info step reporting, and release cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda8261.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda8261.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda8261.h

## Purpose
`tda8261.h` defines board configuration and attach declarations for the TDA8261 satellite tuner.

## Important APIs, Types, and Functions
`enum tda8261_step` lists reference/channel spacing options from 2000 kHz to 125 kHz. `struct tda8261_config` contains the tuner I2C address and step size. `tda8261_attach()` attaches tuner ops to an existing frontend when reachable; otherwise a stub logs disabled Kconfig and returns `NULL`.

## Control Flow
The header only gates the attach symbol through Kconfig. The implementation uses the enum value as an index into divider tables.

## State and Persistence Behavior
No runtime state is declared here. The config is board-owned and read by the driver.

## Dependencies and Integration Points
It is included by `tda8261.c` and bridge drivers that attach this tuner to satellite demodulators.

## Risks and Edge Cases
The enum must remain aligned with implementation arrays. Callers must provide a valid enum value; the implementation does not validate it.

## Test Signals
Compile tests should include both Kconfig paths. Runtime tests should cover every step enum and attach failure handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda8261.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda8261_cfg.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda8261_cfg.h

## Purpose
`tda8261_cfg.h` provides small static wrapper callbacks around frontend tuner ops, likely for demodulator configurations that expect separate get/set frequency and get bandwidth helpers.

## Important APIs, Types, and Functions
It defines `tda8261_get_frequency()`, `tda8261_set_frequency()`, and `tda8261_get_bandwidth()` as static functions. The first calls `fe->ops.tuner_ops.get_frequency` when present; the second calls `set_params` using the frontend property cache; the third returns a fixed `40000000` Hz bandwidth.

## Control Flow
Callers include this header into a C file and use the static functions as callbacks. Frequency set ignores its `frequency` argument and relies on `fe->dtv_property_cache.frequency` already being populated before calling tuner `set_params()`.

## State and Persistence Behavior
The header owns no state. It delegates to the tuner's own `tuner_priv` state and returns a constant bandwidth placeholder.

## Dependencies and Integration Points
It depends on DVB frontend ops and Linux logging macros from the include context. It is not a standalone public API; it is intended for inclusion in driver code that needs these callback symbols.

## Risks and Edge Cases
Because the set wrapper ignores its explicit `frequency` parameter, callers that do not update the property cache first will tune the wrong frequency. `get_bandwidth()` is a FIXME constant and may mislead demods that need actual tuner bandwidth. Static definitions in a header can create multiple private copies and naming conflicts if included broadly.

## Test Signals
Tests should cover delegation when tuner callbacks exist or are absent, error propagation from tuner callbacks, cache-dependent set frequency behavior, and consumers that rely on the fixed 40 MHz bandwidth.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda8261_cfg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda826x.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda826x.c

## Purpose
`tda826x.c` implements Philips TDA8262/TDA8263 DVB-S silicon tuners. It attaches tuner ops to an existing frontend, detects tuner presence, programs LO and baseband filter settings based on frequency and symbol rate, supports loop-through power handling, and reports cached tuned frequency.

## Important APIs, Types, and Functions
The exported API is `tda826x_attach()`. `struct tda826x_priv` stores I2C address, adapter, loop-through flag, and cached frequency. Tuner callbacks include `tda826x_sleep()`, `tda826x_set_params()`, `tda826x_get_frequency()`, and `tda826x_release()`.

## Control Flow
Attach opens the frontend I2C gate, performs a zero-length write followed by a two-byte read to detect tuner status bit `0x80`, allocates private state, installs tuner ops, and stores `tuner_priv`. Set-params opens the gate, computes integer MHz divider from requested frequency, computes baseband bandwidth from symbol rate with rolloff assumptions and clamps it to 5 to 36 MHz, writes an 11-byte register block, closes the gate, and caches the rounded frequency. Sleep writes a two-byte powerdown command that differs depending on loop-through presence.

## State and Persistence Behavior
Only volatile tuner private state is stored. The cached frequency is the rounded programmed LO value in kHz. Sleep changes hardware power state but is not persisted across attach.

## Dependencies and Integration Points
It depends on DVB frontend tuner ops, Linux I2C, optional demod `i2c_gate_ctrl`, and `tda826x.h`. It is used by DVB-S demod bridge drivers that need a legacy attach API.

## Risks and Edge Cases
The attach detection uses a zero-length write message, which not all I2C adapters support. Return values from gate control are ignored. Bandwidth math assumes rolloff 0.35 and adds margin; unusual symbol rates can over/under-filter. The sleep command changes loop-through power, so incorrect `has_loopthrough` board data affects RF pass-through.

## Test Signals
Tests should cover attach detection success/failure, I2C adapters that reject zero-length writes, loop-through and no-loop-through sleep bytes, frequency rounding, low/high symbol-rate bandwidth clamps, gate open/close sequencing, write errors, and release cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda826x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda826x.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda826x.h

## Purpose
`tda826x.h` declares the legacy attach interface for Philips TDA8262/TDA8263 DVB-S tuners.

## Important APIs, Types, and Functions
The public API is `tda826x_attach(struct dvb_frontend *fe, int addr, struct i2c_adapter *i2c, int has_loopthrough)`. When `CONFIG_DVB_TDA826X` is not reachable, an inline stub logs disabled Kconfig and returns `NULL`.

## Control Flow
The header gates the attach function at compile time. The real attach mutates the provided frontend by installing tuner ops and private state.

## State and Persistence Behavior
No state is declared here; runtime tuner state is allocated in the implementation and stored under `fe->tuner_priv`.

## Dependencies and Integration Points
It includes Linux I2C and DVB frontend headers and is consumed by satellite board/bridge drivers.

## Risks and Edge Cases
The in-place attach API requires callers to handle partial tuner setup ordering carefully. The `has_loopthrough` integer affects power state in sleep and should match board RF wiring.

## Test Signals
Compile tests should cover both Kconfig paths. Runtime tests should verify attach mutation of frontend ops, loop-through configuration, and caller handling of `NULL` attach.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda826x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tdhd1.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tdhd1.h

## Purpose
`tdhd1.h` provides board-specific support data for the ALPS TDHD1-204A tuner/demodulator combination using the TDA10046 DVB-T demodulator.

## Important APIs, Types, and Functions
It forward-declares `alps_tdhd1_204_request_firmware()` and defines static `alps_tdhd1_204a_config`, a `struct tda1004x_config` with demod address `0x8`, inverted spectrum, 4 MHz crystal, default AGC, 36.17 MHz IF, and board firmware request callback.

## Control Flow
The header has no standalone flow. Including board code uses the static config when calling `tda10046_attach()` and supplies the declared firmware callback elsewhere.

## State and Persistence Behavior
The static config is compile-time board data. No runtime state or persistence is owned by the header.

## Dependencies and Integration Points
It includes `tda1004x.h` and is integrated by board drivers that know how to request TDHD1 firmware.

## Risks and Edge Cases
Because the config is `static` in a header, each including translation unit gets its own copy. The firmware callback is only declared here; missing or mismatched definition causes build/link problems in consumers. Board-specific hard-coded IF/xtal/inversion values must match the ALPS module.

## Test Signals
Compile tests should cover the board file that includes this header and defines the firmware callback. Runtime signals include successful TDA10046 attach/init with 4 MHz xtal, 36.17 MHz IF, inverted spectrum, and firmware request through the board callback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tdhd1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/ts2020.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/ts2020.c

## Purpose
`ts2020.c` implements Montage Technology TS2020/TS2022 satellite silicon tuners. It supports both legacy `ts2020_attach()` and I2C-driver probing, uses regmap with custom I2C-gate locking, initializes clock/loop-through options, tunes PLL and low-pass filters, polls tuner gain statistics, and exposes RF strength in DVBv3/v5 forms.

## Important APIs, Types, and Functions
The exported legacy API is `ts2020_attach()`, while `ts2020_probe()`/`ts2020_remove()` implement the I2C driver. `struct ts2020_priv` stores I2C client, regmap, regmap mutex/config, frontend, delayed stat work, AGC callback, legacy I2C fields, loop-through/clock/polling config, divider switch frequency, cached LO frequency, and tuner model. Major functions include `ts2020_init()`, `ts2020_sleep()`, `ts2020_set_params()`, `ts2020_tuner_gate_ctrl()`, `ts2020_set_tuner_rf()`, `ts2020_get_frequency()`, `ts2020_get_if_frequency()`, `ts2020_read_tuner_gain()`, `ts2020_get_tuner_gain()`, `ts2020_stat_work()`, and `ts2020_read_signal_strength()`.

## Control Flow
Legacy attach creates a temporary I2C board info with platform data and calls `i2c_new_client_device()`, expecting probe to bind immediately. Probe validates platform data, allocates private state, creates a regmap whose lock opens the demod I2C gate for the full operation, reads chip ID, distinguishes TS2020 from TS2022, applies default divider-switch frequency, programs TS2022 clock output and loop-through defaults, puts the chip to sleep, installs tuner ops, and records client data. Init programs model-specific defaults, configures clock output/loop-through, initializes DVBv5 strength stats, and starts polling by calling the stat worker. Tuning computes an integer-N PLL in kHz, selects output divider, writes PLL registers, performs gate control pulses, configures RF/LPF bandwidth from frontend bandwidth, waits for settling, and caches the actual LO frequency.

## State and Persistence Behavior
Runtime state includes cached actual LO frequency, tuner model, loop-through and clock output settings, frequency divider threshold, and delayed statistics work. DVBv5 strength is updated periodically from tuner gain if polling is enabled or on demand when `dont_poll` is true. Sleep cancels polling and powers down the tuner. Legacy release unregisters the I2C client, and remove cancels work, exits regmap, and frees state.

## Dependencies and Integration Points
The driver depends on DVB frontend tuner ops, I2C client core, regmap, delayed work, math64, and `ts2020.h`. It integrates with demodulators through optional `fe->ops.i2c_gate_ctrl` and through an optional `get_agc_pwm()` callback used for gain estimation.

## Risks and Edge Cases
Legacy attach depends on immediate driver binding; if `i2c_new_client_device()` returns a client without this driver, attach returns `NULL`. Regmap locking wraps every I2C access with gate open/close, so reentrant gate callbacks or sleeping constraints matter. LPF calculation has an explicit FIXME that the filter is almost always too wide for low symbol rates. Polling work must be canceled before freeing state. Clock output values are validated only for TS2022 in probe. Signal strength is derived from empirical gain formulas and AGC callback availability.

## Test Signals
Tests should cover TS2020 and TS2022 chip IDs, legacy attach and direct I2C binding, missing platform data, clock output modes, loop-through mode, `dont_poll`, AGC callback present/absent, PLL divider switch below/above threshold, LPF clamps, RF gain formulas, sleep canceling work, remove cleanup, gate open/close serialization, and get_if_frequency returning zero-IF.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/ts2020.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/ts2020.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/ts2020.h

## Purpose
`ts2020.h` defines platform/legacy configuration for the Montage TS2020/TS2022 tuner driver and declares the legacy attach API.

## Important APIs, Types, and Functions
`struct ts2020_config` contains tuner I2C address, optional divider switch frequency, loop-through flag, clock output mode, clock divider, polling suppression flag, frontend pointer for I2C-driver binding, private `attach_in_use` flag, and optional `get_agc_pwm()` callback. Macros define clock output disabled, enabled, and XTALOUT modes. `ts2020_attach()` is declared when reachable; otherwise a stub logs disabled Kconfig and returns `NULL`.

## Control Flow
Legacy callers pass this config to `ts2020_attach()`, which creates an I2C client and forwards the config as platform data. Direct I2C users provide the same platform data to probe. The header notes that new users should prefer I2C bindings over `ts2020_attach()`.

## State and Persistence Behavior
The config fields are board-owned inputs. `attach_in_use` is driver-private and marks legacy attach so the driver can own release/unregister behavior. No persistent state is stored here.

## Dependencies and Integration Points
It includes DVB frontend types and is used by bridge drivers and `ts2020.c`. The `get_agc_pwm` hook integrates demodulator AGC readings into tuner gain statistics.

## Risks and Edge Cases
Clock divider is a 5-bit field documented as 1-31; invalid zero or out-of-range values can misprogram clock output. `fe` is mandatory for I2C-driver probe. New callers should avoid legacy attach to reduce client lifetime complexity.

## Test Signals
Compile tests should cover both Kconfig paths. Runtime tests should cover platform-data validation, legacy `attach_in_use` release behavior, clock modes/dividers, loop-through, `dont_poll`, frequency-divider defaults, and AGC callback integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/ts2020.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tua6100.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tua6100.c

## Purpose
`tua6100.c` implements the Infineon TUA6100 DVB-S tuner. It detects and attaches the tuner to an existing frontend, programs three tuner register groups over I2C using PLL divider math, controls sleep, and reports cached frequency.

## Important APIs, Types, and Functions
The exported API is `tua6100_attach()`. `struct tua6100_priv` stores I2C address, adapter, and cached frequency. Tuner callbacks are `tua6100_sleep()`, `tua6100_set_params()`, `tua6100_get_frequency()`, and `tua6100_release()`.

## Control Flow
Attach opens the frontend I2C gate, writes a probe byte and reads one byte, then allocates private state and installs tuner ops. Set-params selects register 0/1/2 flags based on requested frequency in kHz, computes the PLL predivider and divider using fixed `_R_VAL`, `_P_VAL`, and `_ri`, stores the rounded programmed frequency, opens the gate, writes register groups 0, 2, and 1, then closes the gate. Sleep writes register 0 to zero through the gate.

## State and Persistence Behavior
The only runtime state is the cached rounded frequency plus I2C details. Sleep powers the tuner down but no persistent settings are written.

## Dependencies and Integration Points
The driver depends on DVB frontend tuner ops, Linux I2C, optional demod I2C gate control, and module export infrastructure. It is a legacy in-place tuner attach module for satellite frontends.

## Risks and Edge Cases
Several gate-open calls in `set_params()` occur before each write but the gate is only closed at the end; if an intermediate write fails, the function returns immediately without closing the gate. There is no explicit frequency range validation before programming. The probe only checks I2C transfer success, not chip identity contents. PLL constants are hard-coded and may not suit board variants.

## Test Signals
Tests should cover attach probe success/failure, gate close on all error paths, low/mid/high frequency register branches, PLL divider and cached frequency calculation, I2C errors for each register group, sleep behavior, and get_frequency after tuning.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tua6100.c -->
