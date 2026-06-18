# subset-b-004068 research

This grouped report covers two Linux DVB frontend demodulator drivers and their local DRXK register/state headers under `sources/distributed-fs/ceph-client/drivers/media/dvb-frontends`. Each section preserves the original source path so the reconciliation step can split it into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/drxk_hard.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/drxk_hard.c

## Purpose
`drxk_hard.c` implements the Micronas/Trident DRX-K DVB-C and DVB-T demodulator frontend driver. It attaches a `struct dvb_frontend`, initializes DRX-K silicon and optional microcode over I2C, programs transport-stream pins, switches between DVB-C Annex A/C QAM and DVB-T OFDM modes, controls the tuner I2C bridge, and exposes lock/statistics callbacks to the Linux DVB core.

## Important APIs, Types, and Functions
The exported API is `drxk_attach(const struct drxk_config *config, struct i2c_adapter *i2c)`, which allocates `struct drxk_state`, imports board configuration, initializes the demodulator, and returns `&state->frontend`. The frontend operations table `drxk_ops` wires `.release`, `.sleep`, `.i2c_gate_ctrl`, `.set_frontend`, `.get_tune_settings`, `.read_status`, `.read_signal_strength`, `.read_snr`, and `.read_ucblocks`.

Low-level access is concentrated in `drxk_i2c_lock()`, `drxk_i2c_unlock()`, `drxk_i2c_transfer()`, `i2c_read1()`, `i2c_write()`, `i2c_read()`, `read16_flags()`, `read32_flags()`, `write16_flags()`, `write32_flags()`, and `write_block()`. These helpers implement the DRX-DAP/FASI short and long address encodings and honor `single_master` by adding address flags. `write_block()` chunks firmware or coefficient writes according to `state->m_chunk_size`.

Device bring-up is handled by `init_state()`, `power_up_device()`, `drxx_open()`, `get_device_capabilities()`, `init_hi()`, `hi_cfg_command()`, `init_drxk()`, `load_firmware_cb()`, and `download_microcode()`. Hardware command helpers include `hi_command()` for host-interface commands, `scu_command()` for SCU demodulator commands, `dvbt_sc_command()` for OFDM synchronization-controller commands, `bl_chain_cmd()` and `bl_direct_cmd()` for bootloader ROM/direct transfers, and `ConfigureI2CBridge()` for the tuner bridge.

Mode and data-path setup is split across `setoperation_mode()`, `start()`, `shut_down()`, `ctrl_power_mode()`, `power_down_device()`, `power_down_dvbt()`, `power_up_dvbt()`, `power_down_qam()`, and `power_up_qam()`. MPEG/TS output is configured through `mpegts_configure_pins()`, `mpegts_disable()`, `mpegts_stop()`, `mpegts_start()`, `mpegts_dto_init()`, `mpegts_dto_setup()`, and `mpegts_configure_polarity()`.

DVB-T setup uses `set_dvbt_standard()`, `set_dvbt()`, `dvbt_start()`, `dvbt_enable_ofdm_token_ring()`, `dvbt_activate_presets()`, `dvbt_ctrl_set_inc_enable()`, `dvbt_ctrl_set_fr_enable()`, `dvbt_ctrl_set_echo_threshold()`, `dvbt_ctrl_set_sqi_speed()`, and `get_dvbt_lock_status()`. DVB-C setup uses `set_qam_standard()`, `set_qam()`, `qam_reset_qam()`, `qam_set_symbolrate()`, `qam_demodulator_command()`, `set_qam_measurement()`, `set_qam16()`, `set_qam32()`, `set_qam64()`, `set_qam128()`, `set_qam256()`, and `get_qam_lock_status()`.

Signal and error reporting uses `get_signal_to_noise()`, `get_dvbt_signal_to_noise()`, `get_qam_signal_to_noise()`, `get_dvbt_quality()`, `get_dvbc_quality()`, `get_quality()`, `get_strength()`, `dvbtqam_get_acc_pkt_err()`, and `drxk_get_stats()`. Board GPIO/antenna support is in `write_gpio()`, `switch_antenna_to_qam()`, and `switch_antenna_to_dvbt()`.

## Control Flow
Attach starts by allocating `struct drxk_state`, copying `struct drxk_config` options such as I2C address, transport-stream width, clocking mode, antenna GPIO, microcode name, chunk size, and QAM command parameter count, then installing `drxk_ops` and defaulting internal state with `init_state()`. If a microcode file is configured, the file is requested and passed to `load_firmware_cb()`; otherwise `init_drxk()` runs immediately. The callback still calls `init_drxk()` when firmware is missing, relying on internal ROM/microcode compatibility instead of failing attach at the firmware callback boundary.

`init_drxk()` is the main hardware initialization sequence. It takes exclusive I2C segment ownership, wakes the device, validates identity/capabilities, computes host-interface bridge timing from the oscillator, initializes the HI block, disables MPEG output and side processes, starts the bootloader, optionally downloads microcode, toggles the OFDM token-ring path for upload, starts SCU briefly to expose version data, powers to the OFDM-down baseline, writes driver version BCD values into SCU RAM, initializes FEC/MPEG DTO defaults, configures TS polarity and pins, writes configured GPIOs, sets the state to stopped or powered down, and fills `frontend.ops.delsys` dynamically from detected DVB-C/DVB-T capabilities.

Tune requests enter `drxk_set_parameters()`. The driver opens the tuner I2C gate, calls the tuner `.set_params`, closes the gate, snapshots `dtv_property_cache` into `state->props`, and switches operation mode when the delivery system changes. DVB-C Annex A/C transitions call `setoperation_mode()` with `OM_QAM_ITU_A` or `OM_QAM_ITU_C`; DVB-T uses `OM_DVBT`. The tuner must expose `.get_if_frequency`; that IF is passed to `start()`, which dispatches to `set_qam()` for DVB-C or `mpegts_stop()`, `set_dvbt()`, and `dvbt_start()` for DVB-T.

The DVB-T path resets/stops OFDM, writes transmission mode, guard interval, hierarchy, modulation, high-priority stream, code rate, bandwidth-specific noise/receiver parameters, IQM resampling values, and frequency shifter settings. It then starts SCU/OFDM, sends a demod-start SCU command, writes OFDM synchronization-controller preference parameters with auto-detection flags, and updates SQI speed when appropriate. `dvbt_start()` starts lock tracking, MPEG output synchronization, and FEC execution.

The QAM path resets FEC/QAM blocks, computes symbol-rate dependent IQM/loop-controller parameters, maps DVB modulation to DRX-K constellations, sends the firmware-specific QAM demodulator parameter command using either the configured 2/4-parameter count or auto-probing, sets frequency shifter and BER measurement windows, writes common loop defaults, halts SCU for safe direct register writes, applies modulation-specific equalizer/slicer/FSM/loop coefficients, restarts SCU, configures MPEG DTO timing, starts FEC/QAM/IQM blocks, and sends the final QAM demod-start command.

Status reads call `drxk_get_stats()`, which gets lock state, maps it to DVB `FE_HAS_*` bits, estimates relative strength from RF/IF AGC state, reports CNR in decibel scale when demod lock exists, and when FEC lock exists updates DVBv5 block, pre-bit, and post-bit counters from OFDM/FEC/SCU registers. Legacy `.read_signal_strength`, `.read_snr`, and `.read_ucblocks` expose the current cached or direct values.

## State and Persistence
All persistent runtime state is per-frontend in `struct drxk_state`: I2C adapter/address, mutex, initialization state, current operation mode, power mode, demod properties, detected silicon capabilities, host-interface timing, MPEG output configuration, AGC presets, QAM/DVB-T tuning data, GPIO/antenna bits, firmware pointer, and cumulative DVBv5 statistics. Hardware state lives in volatile DRX-K registers and SCU RAM defined by `drxk_map.h`; there is no filesystem persistence beyond loading firmware from the kernel firmware API. `release_firmware(state->fw)` and `kfree(state)` clean up on frontend release.

Synchronization is mixed: the host-interface command path, SCU commands, bootloader chain commands, and HI configuration use `state->mutex`; I2C segment locking is used during initialization and can route transfers through `__i2c_transfer()` while locked. The tuner I2C bridge is stateful and can be disabled by `config->no_i2c_bridge`; powerdown may open the bridge first when `m_b_p_down_open_bridge` is set.

## Dependencies and Integration Points
The driver depends on Linux I2C, firmware loading, `dvb_frontend`, DVBv5 property/stat APIs, kernel delay/jiffies helpers, `intlog10()`, and local headers `drxk.h`, `drxk_hard.h`, and `drxk_map.h`. It integrates with board drivers through `struct drxk_config`, tuner callbacks (`set_params`, `get_if_frequency`), I2C gate control, Kconfig `CONFIG_DVB_DRXK`, and the module symbol `drxk_attach`.

## Risks and Edge Cases
The hardware sequencing is order-sensitive: SCU must be held for direct RAM/register writes, token-ring state must match firmware/tap upload needs, FEC resets are restricted after MPEG DTO setup, and power-mode transitions can implicitly stop active demodulators. Missing or incompatible microcode may not fail attach immediately, but later QAM commands can fail; `qam_demod_parameter_count` mitigates firmware command ABI differences. `drxk_set_parameters()` ignores return values from some mode-start helpers, so failures can leave partially programmed hardware while returning success. The code assumes a tuner IF callback is present and returns `-EINVAL` without it.

I2C transfer chunk size, FASI address encoding, `single_master` flags, and bridge configuration are board-sensitive. The QAM/DVB-T setup tables contain many magic register constants; changing register definitions or modulation tables risks silent hardware misconfiguration. Statistics share counters across reads and clear accumulated packet failures, so polling cadence affects observed deltas. `state->frontend.ops.delsys` is filled dynamically during init, so callers must handle `-EAGAIN` while firmware/init is incomplete.

## Test Signals
Useful validation signals include successful attach with and without external microcode, correct detected type/spin/xtal logs, populated delivery systems matching hardware capabilities, tuner I2C gate open/close behavior, stable DVB-C Annex A/C and DVB-T locks, valid MPEG TS output in serial and parallel modes, antenna GPIO switching for DVB-C versus DVB-T, no I2C errors during bootloader/microcode block writes, QAM 2- versus 4-parameter command auto-probing, graceful sleep/powerdown/wake transitions, increasing DVBv5 counters only after lock, and correct `-EAGAIN`/`-ENODEV` behavior for uninitialized or failed devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/drxk_hard.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/drxk_hard.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/drxk_hard.h

## Purpose
`drxk_hard.h` is the private hardware-state header for `drxk_hard.c`. It collects DRX-K version constants, power/lock/status enumerations, modulation and DVB-T/QAM configuration enums, AGC/pre-SAW helper structs, SCU command containers, the full `struct drxk_state`, and lock-status constants used by the DRX-K driver implementation.

## Important APIs, Types, and Functions
This header does not export callable functions; its main API is data shape. Important definitions include `DRXK_VERSION_MAJOR/MINOR/PATCH`, host-interface timing constants, `DRXK_MAX_RETRIES`, DRX JTAG IDs, `DRX_UNKNOWN`, `DRX_AUTO`, SCU result codes, MPEG bitrate constants, and IQM adjustment constants.

Core enums are `enum operation_mode` (`OM_NONE`, DVB-C Annex A/B/C QAM, DVB-T), `enum drx_power_mode`, `enum agc_ctrl_mode`, `enum e_drxk_state`, `enum e_drxk_coef_array_index`, `enum e_drxk_sif_attenuation`, `enum e_drxk_constellation`, `enum e_drxk_interleave_mode`, spin revision values, `enum drxk_cfg_dvbt_sqi_speed`, `enum drx_fftmode_t`, `enum drxmpeg_str_width_t`, and `enum drx_qam_lock_range_t`.

Configuration structs include `struct drxk_cfg_dvbt_echo_thres_t`, `struct s_cfg_agc`, `struct s_cfg_pre_saw`, and `struct drxk_ofdm_sc_cmd_t`. `struct drxk_state` embeds the `struct dvb_frontend`, cached DVB properties, device and I2C handles, mutex, chip capability flags, HI timing, current mode/state, AGC presets for VSB/ATV/QAM/DVB-T, MPEG/TS output flags, QAM and DVB-T tuning state, GPIO configuration, microcode/firmware state, bridge and board options from `struct drxk_config`, frontend status, and QAM command ABI tracking.

## Control Flow
The header shapes control flow by providing the state machine values consumed by `drxk_hard.c`. Initialization moves `m_drxk_state` through uninitialized, stopped, started, powered down, or no-device states. `m_operation_mode` selects QAM versus DVB-T paths. `m_current_power_mode` controls transitions through power-up, OFDM-down, core-down, PLL-down, or oscillator-only modes. Lock constants `NEVER_LOCK`, `NOT_LOCKED`, `DEMOD_LOCK`, `FEC_LOCK`, and `MPEG_LOCK` normalize hardware-specific lock readings for DVB callbacks.

## State and Persistence
`struct drxk_state` is allocated per attached frontend and is the driver's in-memory persistence boundary. It keeps board configuration, runtime hardware state mirrors, statistics status, and firmware pointer for the life of the frontend. The header itself stores no data, but changing fields or defaults affects every mode setup and statistics path in `drxk_hard.c`.

## Dependencies and Integration Points
The header includes `drxk_map.h` and relies on kernel/DVB types made available by the C file and public `drxk.h`. It is private to the DRX-K implementation, with `struct drxk_state` matching register definitions and command helpers in `drxk_hard.c`.

## Risks and Edge Cases
The large `struct drxk_state` mixes board configuration, hardware capability, cached frontend properties, firmware, counters, and mode state; field initialization order is important. Several comments note board-specific defaults that likely belong in `struct drxk_config`, so using the header values across different hardware designs can be fragile. Enum sentinel values use `DRX_UNKNOWN` and `DRX_AUTO` aliases, and code must not treat them as normal low-range enum entries.

## Test Signals
Header-level validation is mostly compile and runtime-coverage based: `drxk_hard.c` should build without mismatched fields, all configured board options should land in expected `drxk_state` fields, state transitions should reject uninitialized/no-device states, and DVB-C/DVB-T capability detection should populate delivery-system support consistently with the capability flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/drxk_hard.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/drxk_map.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/drxk_map.h

## Purpose
`drxk_map.h` is the DRX-K register-address and bitfield map used by `drxk_hard.c`. It defines symbolic addresses, masks, bit positions, reset/preload values, and command constants for the audio, FEC, IQM, OFDM, QAM, SCU, SIO host interface, bootloader, power, pad, GPIO, and token-ring blocks.

## Important APIs, Types, and Functions
The file contains only preprocessor constants. Major register families include `AUD_COMM_EXEC__A`, `FEC_*`, `IQM_*`, `OFDM_*`, `QAM_*`, `SCU_RAM_*`, `SCU_COMM_EXEC__A`, `SIO_TOP_*`, `SIO_HI_RA_RAM_*`, `SIO_CC_*`, `SIO_OFDM_SH_*`, `SIO_BL_*`, and `SIO_PDR_*`. Field constants use suffixes such as `__A` for address, `__M` for mask, `__B` for bit shift, and `__PRE` for preset/default values.

Notable command and state constants include SCU demodulator commands (`SCU_RAM_COMMAND_CMD_DEMOD_RESET`, `SET_ENV`, `SET_PARAM`, `START`, `GET_LOCK`, `STOP`), standard selectors (`SCU_RAM_COMMAND_STANDARD_QAM`, `STANDARD_OFDM`), OFDM synchronization-controller commands and auto flags, QAM lock encodings, bootloader modes, host-interface bridge command parameters, power-domain levels, and MPEG pad inversion/drive masks.

## Control Flow
The map is a compile-time dependency for all DRX-K hardware control flow. `drxk_hard.c` uses these constants to format I2C reads/writes, send HI/SCU/OFDM commands, load firmware and ROM tap tables, configure QAM and OFDM blocks, control MPEG output, poll lock state, compute statistics, and manage power. The `scu_command()` implementation explicitly asserts that `SCU_RAM_PARAM_0__A - SCU_RAM_PARAM_15__A == 15`, so the relative layout of SCU parameter registers is part of the executable contract.

## State and Persistence
The header defines addresses for volatile device state rather than storing state itself. State touched through these symbols includes FEC measurement periods and counters, IQM rate offsets, OFDM lock parameters, QAM loop coefficients and signal powers, SCU command/result RAM, pad drive configuration, bootloader transfer descriptors, and power/reset control. There is no persistent storage in the file.

## Dependencies and Integration Points
`drxk_map.h` is included by `drxk_hard.h`, which is included by `drxk_hard.c`. Its constants encode the DRX-K hardware ABI; changing names, masks, or addresses directly impacts I2C register transactions and firmware command semantics.

## Risks and Edge Cases
The map has no include guard in the visible source and is intended for single private inclusion through `drxk_hard.h`. Incorrect address, mask, or bit constants can compile cleanly but break hardware sequencing. Several constants are paired across low/high register words or mask/shift definitions, so partial edits can corrupt frequency-offset, AGC, QAM, or MPEG configuration. Generated-style names are long and similar across OFDM/QAM/SCU families, making copy/paste mistakes likely.

## Test Signals
The strongest signals are hardware-level: successful device initialization, firmware/tap loading, DVB-C and DVB-T lock, correct MPEG TS output polarity/format, valid BER/SNR/statistics, working I2C bridge and power transitions, and absence of `SCU not ready`, `SIO not ready`, or I2C register errors. Build-time validation should also catch the SCU parameter register layout assertion in `scu_command()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/drxk_map.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/ds3000.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/ds3000.c

## Purpose
`ds3000.c` implements the Montage Technology DS3000 DVB-S/DVB-S2 satellite demodulator frontend driver. It detects the demodulator over I2C, loads firmware on initialization, programs DVB-S or DVB-S2 register tables per tune, coordinates with an external tuner, controls LNB voltage/tone and DiSEqC messaging, and exposes DVB frontend status/statistics callbacks.

## Important APIs, Types, and Functions
The exported attach point is `ds3000_attach(const struct ds3000_config *config, struct i2c_adapter *i2c)`. It allocates `struct ds3000_state`, probes register `0x00`, logs chip version registers, installs `ds3000_ops`, sets `frontend.demodulator_priv`, and turns LNB voltage off as a safe attach default.

`struct ds3000_state` stores the I2C adapter, immutable config pointer, `struct dvb_frontend`, and the previous DVB-S2 uncorrected-block counter. Register access helpers are `ds3000_writereg()`, `ds3000_readreg()`, `ds3000_i2c_gate_ctrl()`, and `ds3000_writeFW()`. Firmware handling uses `DS3000_DEFAULT_FIRMWARE`, `ds3000_firmware_ondemand()`, and `ds3000_load_firmware()`.

Frontend callbacks include `ds3000_initfe()`, `ds3000_set_frontend()`, `ds3000_tune()`, `ds3000_get_algo()`, `ds3000_read_status()`, `ds3000_read_ber()`, `ds3000_read_signal_strength()`, `ds3000_read_snr()`, `ds3000_read_ucblocks()`, `ds3000_set_voltage()`, `ds3000_set_tone()`, `ds3000_send_diseqc_msg()`, `ds3000_diseqc_send_burst()`, `ds3000_set_carrier_offset()`, and `ds3000_release()`. Two static initialization tables, `ds3000_dvbs_init_tab` and `ds3000_dvbs2_init_tab`, provide register/value programming sequences for each delivery system.

## Control Flow
Attach probes for a DS3000 by reading register `0x00` and expecting the upper bits to match `0xe0`. Initialization (`ds3000_initfe()`) performs a hard reset through register `0x08`, waits briefly, then calls `ds3000_firmware_ondemand()`. Firmware on demand reads register `0xb2`, requests `dvb-fe-ds3000.fw` from the kernel firmware loader, writes it to register `0xb0` in 32-byte chunks while `0xb2` is asserted, and releases the firmware.

Tune setup (`ds3000_set_frontend()`) optionally calls board `set_ts_params`, then tuner `.set_params`. It resets the demodulator, selects and writes the DVB-S or DVB-S2 init table, adjusts a few mode-specific registers, enables 27 MHz clock output and AC coupling, validates symbol-rate range, programs symbol-rate performance parameters across several ranges, writes normalized symbol rate, disables co-channel cancellation/equalizer, applies CI-mode register choices, releases software/uC reset, asks the tuner for actual frequency if available, computes carrier offset, and polls lock up to roughly 300 ms.

Status reads are delivery-system specific: DVB-S locks when register `0xd1` low three bits are all set, while DVB-S2 locks when register `0x0d` matches mask `0x8f`. BER, SNR, and uncorrected block logic also split on DVB-S versus DVB-S2 and read different register families. `ds3000_tune()` delegates to set-frontend on retune, sets a 200 ms delay, and returns current status. `ds3000_get_algo()` reports `DVBFE_ALGO_HW`.

Satellite equipment control is register-driven. `ds3000_set_voltage()` updates register `0xa2` for 13 V, 18 V, or off. `ds3000_set_tone()` toggles 22 kHz tone via registers `0xa1`/`0xa2`. DiSEqC master commands write message bytes to `0xa3+`, start send mode through `0xa1`, poll completion, and restore idle state; tone bursts use the same control register with fixed mini-A/mini-B modes.

## State and Persistence
The driver has one heap `ds3000_state` per frontend and no persistent on-disk state. Firmware is requested and written at init time and not cached in `ds3000_state`. The previous DVB-S2 uncorrected-block counter is retained across reads to report deltas. Hardware registers hold current demodulator mode, symbol-rate setup, DiSEqC/LNB state, and counters. Optional board callbacks can maintain external LED or TS/DMA state outside this file.

## Dependencies and Integration Points
The file depends on Linux I2C, firmware loading, DVB frontend APIs, module parameters, and local headers `ds3000.h` and `ts2020.h`. It integrates with an external tuner through `fe->ops.tuner_ops.set_params`, `get_frequency`, and `get_rf_strength`, with board code through `struct ds3000_config` callbacks `set_ts_params` and `set_lock_led`, and with userspace through the DVB frontend ops table advertising `SYS_DVBS` and `SYS_DVBS2`.

## Risks and Edge Cases
`ds3000_writeFW()` always sends 32-byte chunks and assumes firmware length alignment suitable for that loop. `ds3000_readreg()` returns the raw I2C transfer result on failure, which can be positive and must be treated as failure by callers that expect register bytes. Several tune-time register writes ignore individual errors, so an I2C failure can leave partially configured hardware. SNR math includes negative assignment into an unsigned `u16` output path for weak DVB-S2 readings. `ds3000_set_frontend()` computes `offset_khz` from unsigned frequency values into an `s32`, so large mismatches need care.

The attach path disables LNB voltage to avoid interfering with Unicable/SCR setups, which is safe but can surprise boards expecting power to remain on across reprobe. DiSEqC send waits are fixed and can timeout if the demodulator status bit does not clear. The lock LED callback is called from status/get-algo/release paths and should be safe in those contexts.

## Test Signals
Useful test signals include successful probe and version log, firmware load of `dvb-fe-ds3000.fw`, locks on both DVB-S and DVB-S2 transponders across low and high symbol rates, correct tuner frequency offset compensation, DiSEqC master and mini-burst completion without timeout, 13 V/18 V/off LNB voltage behavior, 22 kHz tone on/off behavior, lock LED updates, RF strength delegated to tuner, and stable BER/SNR/UC block readings for both delivery systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/ds3000.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/ds3000.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/ds3000.h

## Purpose
`ds3000.h` is the public integration header for the Montage DS3000 DVB-S/S2 demodulator driver. It defines board configuration data and the conditional attach API used by bridge/card drivers.

## Important APIs, Types, and Functions
`struct ds3000_config` contains the demodulator I2C address, CI mode flag, optional `set_ts_params(struct dvb_frontend *fe, int is_punctured)` callback for board TS/DMA setup, and optional `set_lock_led(struct dvb_frontend *fe, int offon)` callback. When `CONFIG_DVB_DS3000` is reachable, `ds3000_attach()` is declared as an external function; otherwise an inline stub logs that the driver is disabled and returns `NULL`.

## Control Flow
Bridge drivers include this header, fill `struct ds3000_config`, and call `ds3000_attach(config, i2c)`. The Kconfig conditional controls whether the call links to the real driver or the disabled-driver stub. Runtime tuning and status behavior are implemented in `ds3000.c`.

## State and Persistence
The header stores no state. The config structure is passed by pointer into `ds3000.c`, which keeps it in `struct ds3000_state`; callers should ensure the config storage remains valid for the frontend lifetime.

## Dependencies and Integration Points
The header depends on `<linux/dvb/frontend.h>` for `struct dvb_frontend` and on the I2C adapter type through the attach prototype context. It is the primary integration point for board-specific TS setup, lock LED behavior, and demodulator address selection.

## Risks and Edge Cases
Because `ds3000_state` stores `const struct ds3000_config *`, stack-allocated configs in caller code would become dangling after attach. The disabled-driver stub uses `printk(KERN_WARNING, ...)`, so callers should handle `NULL` without assuming probe failure means missing hardware. Callback implementations must tolerate being called from frontend control paths and release/status paths.

## Test Signals
Compile coverage should verify both reachable and disabled Kconfig cases. Runtime tests should confirm board callbacks are invoked as expected, the configured I2C address matches hardware, CI mode changes register programming in `ds3000_set_frontend()`, and callers handle `NULL` attach cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/ds3000.h -->
