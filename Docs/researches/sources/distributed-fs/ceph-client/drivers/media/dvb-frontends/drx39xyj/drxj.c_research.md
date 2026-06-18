# Research: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/drx39xyj/drxj.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-004060`: lines 1-8990, `Docs/researches/chunks/subset-b-004060_research.md`
- `subset-b-004061`: lines 8991-12391, `Docs/researches/chunks/subset-b-004061_research.md`

## Chunk Research

### subset-b-004060: lines 1-8990

# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/drx39xyj/drxj.c lines 1-8990

## Scope

This chunk covers the first 8,990 lines of the DRX39xxJ/DRX3933J DVB frontend implementation. It includes global defaults, register-access helpers, host-interface commands, device capability detection, MPEG transport output setup, UIO/I2C bridge/smart-antenna helpers, SCU command access, ADC/AGC/frequency-shifter setup, 8VSB datapath setup and measurements, QAM power-down/setup/measurement tables, and the beginning of QAM64 auto lock recovery. The chunk ends inside `qam64auto()`, so later frontend callbacks and the completion of QAM auto-lock behavior belong to the following chunk.

## Purpose and Major Responsibilities

- Define the DRXJ firmware name, hardware tuning constants, ATSC/QAM/analog-TV/audio register constants, default demodulator/common/audio state, and helper macros for word-to-byte register payloads.
- Provide the low-level I2C/FASI transport used by the rest of the driver, including short/long DRX address encoding, chunked reads/writes, 16-bit and 32-bit endian conversion, and special handling for audio token-ring registers.
- Implement host-interface and SCU command protocols used for configuration commands, atomic access, bridge control, demod reset/start/stop, and SCU RAM accesses.
- Discover silicon/package capabilities from hardware strap/JTAG state and cache the result in `struct drxj_data`.
- Configure MPEG TS output for 8VSB and QAM standards, including parity insertion, serial/parallel mode, static/dynamic clocking, output inversion, DTO/RCN rates, and pad drive configuration.
- Manage UIO pins, the tuner I2C bridge, smart antenna output, ADC synchronization, RF/IF AGC state, pre-SAW/PGA state, and IQM analog-front-end power.
- Program the 8VSB datapath from reset through IQM/FEC/VSB configuration, fixed coefficient tables, AGC setup, MPEG output enabling, SCU demod start, and VSB signal measurement helpers.
- Program the QAM datapath for Annex A/B/C modes, symbol-rate/frequency-shifter setup, QAM constellation-specific thresholds/tables for QAM16/32/64/128/256, MPEG output enabling, SCU demod start, and early QAM64 sync/spectrum recovery logic.

## Important APIs, Types, and Functions

- `struct drxj_data`, `struct drx_common_attr`, `struct drx_demod_instance`, and `struct drx_aud_data` hold the persistent driver state. This chunk initializes global defaults in `drxj_data_g`, `drxj_default_comm_attr_g`, `drxj_default_demod_g`, and `drxj_default_aud_data_g`.
- `struct drxj_hi_cmd` represents host-interface commands with command plus six 16-bit parameters. `struct drxu_code_block_hdr` describes firmware/microcode block headers for later firmware-loading code.
- `frac28()`, `log1_times100()`, and `frac_times1e6()` provide fixed-point arithmetic for frequency shifters, signal-quality math, and measurement scaling without floating point.
- `drxbsp_i2c_write_read()` is the Linux I2C adapter bridge. It builds one-message read/write operations or two-message write-then-read transfers from `struct i2c_device_addr`.
- `drxdap_fasi_read_block()`, `drxdap_fasi_write_block()`, `drxdap_fasi_read_reg16()`, `drxdap_fasi_read_reg32()`, `drxdap_fasi_write_reg16()`, and `drxdap_fasi_write_reg32()` are the base FASI register access layer.
- `is_handled_by_aud_tr_if()`, `drxj_dap_read_aud_reg16()`, and `drxj_dap_write_aud_reg16()` route selected audio block/bank accesses through the audio token-ring interface and poll FIFO lock/full/read-ready bits.
- `drxj_dap_read_reg16()`, `drxj_dap_write_reg16()`, and `drxj_dap_read_modify_write_reg16()` are the main device-specific register access wrappers used by most of the chunk.
- `drxj_dap_atomic_read_write_block()` and `drxj_dap_atomic_read_reg32()` use HI atomic-copy commands and the HI user RAM window for small atomic accesses. `drxj_dap_scu_atomic_read_write_block()`, `drxj_dap_scu_atomic_read_reg16()`, and `drxj_dap_scu_atomic_write_reg16()` perform similar operations through the SCU command interface.
- `hi_command()`, `hi_cfg_command()`, and `init_hi()` program host-interface parameters, issue HI commands, wait for command completion, and special-case power-down commands where reading the result is not possible.
- `get_device_capabilities()` reads oscillator strap and JTAG/package bits, then sets `has_lna`, `has_oob`, `has_ntsc`, `has_btsc`, `has_smatx`, `has_smarx`, `has_gpio`, `has_irqn`, and `mfx`.
- `power_up_device()` wakes the chip with dummy I2C writes to the wake-up key address and repeated reads from the normal address.
- `ctrl_set_cfg_mpeg_output()`, `set_mpegtei_handling()`, `bit_reverse_mpeg_output()`, and `set_mpeg_start_width()` configure MPEG TS/FEC output behavior.
- `ctrl_set_uio_cfg()`, `ctrl_uio_write()`, `ctrl_i2c_bridge()`, and `smart_ant_init()` manage board integration pins and bridge behavior.
- `scu_command()` is the central SCU mailbox helper, with parameter/result count handling, timeout polling, and SCU error-code translation.
- `adc_sync_measurement()`, `adc_synchronization()`, `init_agc()`, `set_frequency()`, `set_agc_rf()`, `set_agc_if()`, and `set_iqm_af()` prepare the shared IQM/AGC/frequency-shifter path.
- `power_down_vsb()`, `set_vsb_leak_n_gain()`, `set_vsb()`, `get_vsb_post_rs_pck_err()`, `get_vs_bpost_viterbi_ber()`, `get_vs_bpre_viterbi_ber()`, and `get_vsbmer()` cover the 8VSB datapath and measurement helpers.
- `power_down_qam()`, `set_qam_measurement()`, `set_qam16()`, `set_qam32()`, `set_qam64()`, `set_qam128()`, `set_qam256()`, `set_qam()`, `qam_flip_spec()`, and the first part of `qam64auto()` cover QAM setup and early auto-lock remediation.

## Control Flow

Initialization begins from default global structures that point a `struct drx_demod_instance` at default I2C, common, and extended DRXJ attributes. Later attach/open paths outside this chunk copy or reference these defaults and attach Linux frontend state through `struct drx39xxj_state` in `i2c_device_addr.user_data`.

All hardware access flows through `drxbsp_i2c_write_read()` and then through FASI/DAP helpers. A normal register read/write validates parameters, encodes a short or long DRX address with flags, chunks data to `DRXDAP_MAX_*CHUNKSIZE`, and transfers little-endian word payloads over I2C. Audio block accesses are intercepted by `drxj_dap_read_reg16()`/`drxj_dap_write_reg16()` and routed through token-ring RMW transactions. Atomic access paths use HI or SCU mailbox commands to copy a limited number of words through an internal buffer before the host reads or writes the data.

The host-interface flow writes command parameters high-to-low according to command type, writes `SIO_HI_RA_RAM_CMD__A`, waits for the command register to clear, and reads `SIO_HI_RA_RAM_RES__A`. Power-down HI config commands skip the result read because the device may no longer answer. `init_hi()` calculates timing and bridge delays from system/oscillator clocks, stores them in `drxj_data`, then sends the config command.

Capability detection unlocks SIO pad registers, reads oscillator strap configuration, reads the JTAG ID, and maps variant IDs to feature booleans. These booleans gate later UIO, smart antenna, OOB, NTSC/BTSC, LNA, and IRQ behavior.

MPEG output setup is standard-dependent. For enabled output, it validates that the current standard can produce MPEG, programs FEC output FIFO/timing defaults, computes or selects RCN/DTO rates, configures RS parity forwarding, serial/parallel mode, signal inversion, and static/dynamic clocking, then unlocks pad registers and switches MPEG pads to output mode. Disabled output switches those pads back to input/tristate mode and stores the requested `enable_mpeg_output` state in `common_attr->mpeg_cfg`.

The shared RF chain flow powers IQM AF blocks, synchronizes ADC sample edge if needed, initializes AGC loop registers, computes the IQM frequency-shifter offset from IF frequency, tuner residual offset, spectrum mirroring, ADC aliasing, and selected standard, and stores `iqm_fs_rate_ofs`/`pos_image` in `drxj_data`. RF and IF AGC functions can use ordinary DAP or SCU atomic access and update both hardware registers and cached per-standard AGC configs.

8VSB setup in `set_vsb()` stops FEC/VSB/IQM sub-blocks, resets the VSB demod via SCU, writes IQM and VSB equalizer/carrier/clip/FEC settings, pushes large fixed coefficient arrays, initializes measurement counters, enables IQM AF and AGC, configures MPEG output and TEI/bit-order/start-width options, starts the VSB demod via SCU, and marks IQM/VSB/FEC command execution active.

QAM setup in `set_qam()` is operation-mask driven. `QAM_SET_OP_ALL` performs reset, environment/parameter setup, spectrum setup, constellation setup, MPEG output, and demod start. `QAM_SET_OP_CONSTELLATION` updates constellation-dependent symbol-rate, measurement, coefficient, and SCU start pieces. `QAM_SET_OP_SPECTRUM` limits work to frequency-shifter/spectrum-related configuration. Annex B hard-codes supported QAM64/QAM256 symbol-rate settings; Annex A/C compute rate values from `channel->symbolrate`. The constellation-specific helper then writes threshold, loop-control, CMA radius, and signal-power tables for QAM16/32/64/128/256.

`qam_flip_spec()` is a recovery helper used by the auto-lock logic. It temporarily silences QAM acquisition/equalizer/loop control, freezes selected loops, atomically reads current FS rate values, computes the mirrored FS offset, writes it back, toggles `ext_attr->pos_image`, negates imaginary equalizer taps, restores DQ/FQ modes, nudges the QAM FSM target state, polls for state 4 up to 100 reads, then restores control enable bits. The chunk ends while `qam64auto()` is polling lock state and deciding whether to flip sync pattern and mirror spectrum.

## State and Persistence Behavior

- Persistent driver state lives primarily in `struct drxj_data`: feature flags, current standard/constellation/frequency/bandwidth/mirror, AGC/PGA/pre-SAW configs, MPEG quirks, IQM FS/RC offsets, measurement periods, packet-error accumulator state, UIO modes, host-interface config, smart antenna inversion, and OOB/audio-related state.
- `struct drx_common_attr` persists board/frontend-wide settings such as firmware file/verification policy, IF/sys/oscillator clocks, MPEG output config, bridge/tuner settings, current/previous channel and standard, power mode, capabilities, and scan state.
- Hardware state persists in many DRXJ register blocks: SIO/HI, SIO pad config, FEC output controller, IQM analog/front-end/frequency/resampler/channel-filter blocks, SCU RAM, VSB/QAM demod blocks, and audio token-ring registers.
- Measurement state is partly hardware and partly cached. VSB/QAM error counters are reset by writes to SCU/FEC measurement registers. QAM measurement period/prescale and VSB FEC/BER/MER settings are cached in `drxj_data` for later quality calculations.
- `power_up_device()` and HI power-down config affect the device's ability to answer I2C; follow-up code must respect wake-up timing and the wake-up key.
- UIO and MPEG pad changes persist in pad configuration registers after the calls return. Several helpers unlock pad writes with `SIO_TOP_COMM_KEY__A` and then attempt to lock them again, but early error returns before relocking are possible in some paths.
- `set_frequency()` stores the computed FS rate and selected image in `ext_attr`; `qam_flip_spec()` mutates those values during auto-detection. This makes subsequent signal-quality and mirror decisions dependent on earlier acquisition attempts.

## Dependencies and Integration Points

- Linux kernel/DVB dependencies include `i2c_transfer()`, `struct i2c_msg`, `msleep()`, `usleep_range()`, `jiffies`, `time_is_after_jiffies()`, `jiffies_to_msecs()`, `msecs_to_jiffies()`, `pr_*()` logging, `struct dvb_frontend`, and `struct dtv_frontend_properties`.
- Driver-local definitions come from `drx39xxj.h`, `drxj.h`, `drxj_map.h`, and `drx_driver_version.h`. Most register addresses, masks, enums, and structures are external to this file.
- Firmware integration is declared by `DRX39XX_MAIN_FIRMWARE` and `struct drxu_code_block_hdr`; actual firmware loading continues outside this chunk.
- Board integration uses `struct drx39xxj_state` via `i2c_device_addr.user_data` for the Linux I2C adapter and frontend property cache.
- Tuner integration depends on the host I2C bridge (`ctrl_i2c_bridge()`), common tuner AGC polarity settings, IF frequency, residual tuner frequency offset, and mirror settings.
- The VSB/QAM setup routines are not exported here as DVB ops directly in this chunk, but they are core internals that later tuning/set-frontend code calls to acquire channels.
- `ctrl_get_qam_sig_quality()` is forward-declared and used by `qam64auto()` before its definition, which appears in the later chunk.

## Risks and Edge Cases

- The file is hardware-register dense. Many error paths return immediately after unlocking SIO pad writes or after partially programming a datapath, so failed I2C transactions can leave hardware in a half-configured state.
- `drxbsp_i2c_write_read()` returns `0` if `state->i2c` is NULL after logging an error, which can make an absent adapter look like success to upper layers.
- Several helpers perform divisions that rely on validated nonzero inputs: `frac28(N, D)`, `frac_times1e6(N, D)`, QAM symbol-rate calculations, FEC measurement period calculations, and VSB MER math. Some checks exist, but not all denominators are locally guarded.
- `drxj_dap_atomic_read_reg32()` returns `0` when `drxj_dap_atomic_read_write_block()` returns a negative error, which appears to suppress an atomic-read failure instead of propagating it.
- Audio token-ring read/write loops are timeout-based and depend on jiffies millisecond deltas. Wraparound is not handled with `time_after()` style helpers in that path.
- `set_agc_rf()` appears to write IF AGC target registers from RF AGC TOP settings when IF AGC is also auto, which may be intentional coupling but is easy to misconfigure.
- In `init_agc()`, the IF polarity branch writes back to `agc_rf` rather than `agc_if`, so inverted IF AGC polarity may not affect the intended initial IF DAC value.
- QAM Annex B supports only QAM64 and QAM256 in this setup path. Other constellations return errors even though generic constellation helpers exist for Annex A/C.
- Static MPEG output clocking and RCN/DTO values are a mix of formulas and hard-coded constants. Incorrect `sys_clock_freq`, `curr_symbol_rate`, `insert_rs_byte`, or `mpeg_output_clock_rate` settings can produce invalid TS timing.
- `qam_flip_spec()` polls for FSM state 4 without sleeping and does not fail if the target state is never reached; it proceeds to restore control bits as long as register reads succeed.
- This chunk ends mid-`qam64auto()`, so any analysis of final return behavior, post-loop lock status, and integration with frontend tuning must include the next chunk.

## Test Signals

- Build the media frontend driver with DRX39xxJ enabled. Compile errors should catch missing register constants, enum mismatches, `fallthrough` annotations, and local prototype issues.
- Probe hardware and confirm I2C wake-up, HI init, capability detection, and firmware-dependent later initialization can read the expected oscillator/JTAG/package values without `-EIO` or timeout logs.
- Exercise tuner bridge open/close and board UIO paths on variants with and without SMA_TX, SMA_RX, GPIO, and IRQN. Expected signals are correct capability gating and no pad-register writes on unsupported pins.
- Tune known ATSC 8VSB channels and verify the flow reaches SCU DEMOD_START, FEC/VSB/IQM command execution active, MPEG TS output enabled, stable lock, packet-error counters changing, and plausible post-RS, Viterbi BER, and MER readings.
- Tune Annex A/C QAM channels across QAM16/32/64/128/256 and Annex B QAM64/QAM256. Signals include valid symbol-rate programming, constellation-specific table writes, SCU QAM start success, lock, MPEG output timing, and meaningful CNR/BER counters.
- Test mirror/auto-spectrum cases for QAM64 with `DRX_MIRROR_AUTO`; verify `qam_flip_spec()` toggles `pos_image`, writes the mirrored FS offset, and does not destabilize already locked channels.
- Test serial and parallel MPEG output, RS-byte insertion on/off, static clock, dynamic clock, signal inversion, TEI handling disable, bit-reversed MPEG output, and 1-clock vs 8-clock MPEG start width on hardware with a TS analyzer.
- Run I2C fault-injection or unplug/error tests if available. Useful signals are no kernel crashes, no endless polling, correct propagation of `-EREMOTEIO`/`-EIO`/`-ETIMEDOUT`, and sane recovery on the next tune or power cycle.
- Exercise power-up from deep/power-down modes repeatedly. Confirm dummy wake-up transfers, HI reconfiguration, and subsequent register reads succeed after the expected delays.

## Chunk Notes for Merge Lane

This is the first of two chunks for `sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/drx39xyj/drxj.c`. Merge should connect these internals to the later chunk that completes `qam64auto()`, signal-quality routines, firmware loading, frontend ops, attach/release paths, and module metadata. The final per-file report should emphasize that this chunk is the hardware-control core: it owns I2C/DAP/HI/SCU access, persistent demod state defaults, MPEG/pad configuration, AGC/IQM setup, and most VSB/QAM acquisition programming.

### subset-b-004061: lines 8991-12391

# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/drx39xyj/drxj.c lines 8991-12391

## Scope

This chunk covers the end of the Micronas DRX39xxj demodulator driver implementation. It starts at the return path of the preceding QAM auto-acquisition helper, then covers QAM channel selection and QAM signal-quality reporting, ATV/audio/OOB shutdown and OOB setup, high-level demodulator controls, driver open/close and firmware upload, Linux DVB frontend callbacks, attach/release, and the exported `dvb_frontend_ops`.

The code is hardware-control heavy. Most routines convert DVB or internal driver state into SCU commands, register writes, and cached DVBv5 statistics in `struct dtv_frontend_properties`.

## Purpose

The chunk is the driver integration layer that turns lower-level DRXJ register and SCU helpers from earlier in the file into a usable Linux DVB frontend for ATSC 8VSB and DVB-C Annex B QAM. Its responsibilities are:

- Acquire QAM64/QAM256 channels, including automatic constellation and spectrum-mirror handling.
- Read and translate demodulator counters into Linux DVB statistics: signal strength, CNR/SNR, BER-style counters, and uncorrected blocks.
- Stop ATV/audio/OOB paths and configure an OOB receiver path when requested by internal control code.
- Select standards and channels, power the chip up or down, and preserve selected state in `struct drxj_data` and `struct drx_common_attr`.
- Upload and optionally verify firmware through the Linux firmware loader.
- Expose the device through `struct dvb_frontend_ops`, including tuning, status reads, sleeping, I2C-gate control, LNA control, and release.

## Important APIs, Types, and Functions

### QAM Acquisition and Quality

- `qam256auto()` polls `ctrl_lock_status()` after a QAM256 setup. Once demod lock is seen and `ctrl_get_qam_sig_quality()` reports CNR above a hard-coded threshold, it waits for FEC lock. If the requested channel mirror mode is `DRX_MIRROR_AUTO`, it sets `ext_attr->mirror = DRX_MIRROR_YES`, calls `qam_flip_spec()`, and restarts the acquisition timer with a reduced timeout.
- `set_qam_channel()` validates the current `ext_attr->standard`, requested constellation, mirror mode, and Annex-specific constraints. For Annex B, explicit QAM64/QAM256 requests go through `set_qam()` and then the matching auto-lock helper. For `DRX_CONSTELLATION_AUTO`, Annex B tries QAM256 first, then forces the QAM FSM back to rate hunting and tries QAM64; Annex C starts from QAM64. Temporary mutation of `channel->constellation` is restored to `DRX_CONSTELLATION_AUTO` on successful auto mode and on error via `auto_flag`.
- `get_qamrs_err_count()` reads the QAM Reed-Solomon and sync-failure counters from FEC registers into `struct drxjrs_errors`. The comment explicitly notes these reads are non-atomic, so one statistic sample can mix counters from adjacent hardware measurement periods.
- `get_sig_strength()` reads IQM IF/RF AGC values and maps them into a 0-100 relative strength using fixed thresholds `DRXJ_AGC_TOP`, `DRXJ_AGC_SNS`, `DRXJ_RFAGC_MAX`, and `DRXJ_RFAGC_MIN`.
- `ctrl_get_qam_sig_quality()` reads QAM MER, Viterbi symbol error, RS error, and sync-failure period registers. It derives CNR in centi-dB via `log1_times100()`, accumulates pre/post bit counts and errors into the DVBv5 stats cache, and records block errors. It uses `ext_attr` measurement constants such as `fec_rs_period`, `fec_rs_prescale`, `fec_rs_plen`, `qam_vd_period`, `qam_vd_prescale`, and `fec_vd_plen`.

### ATV, Audio, and OOB Control

- `power_down_atv()` stops the ATV SCU standard, disables CVBS/SIF outputs, stops ATV and IQM execution registers, conditionally stops either the primary IQM path or the secondary IQM subblocks, and then calls `power_down_aud()`.
- `power_down_aud()` stops `AUD_COMM_EXEC` and marks `ext_attr->aud_data.audio_is_active = false`.
- `set_orx_nsu_aox()` toggles the ORX NSU/AOX standby bits for ADC, amplifier, bias, PLL, detector, AGC, and filter blocks.
- `ctrl_set_oob()` is both the OOB off path and the OOB setup path. With `oob_param == NULL`, it issues an OOB DEMOD_STOP SCU command, powers down NSU/AOX, stops ORX execution, and clears `ext_attr->oob_power_on`. With a valid `struct drxoob`, it validates a 70-130 MHz OOB frequency, computes an internal frequency and tracking-filter value from `ext_attr->oob_trk_filter_cfg`, stops/resets OOB, sends SET_ENV with data-rate and inversion selection, configures SIO OOB pin drive, ORX AGC/DDC/NSU registers, target mode, frequency-gain correction, lock thresholds, prefilter coefficients, Nyquist coefficients, starts ORX/SCU, enables NSU/AOX, writes pre-SAW threshold, and sets `ext_attr->oob_power_on = true`.

### High-Level Demodulator Controls

- `ctrl_set_channel()` validates the active standard, normalizes bandwidth for 8VSB and Annex B, derives Annex A/C bandwidth from symbol rate and rolloff, optionally drives UIO1 as a SAW switch, activates SCU execution, and dispatches to `set_vsb()` plus `set_frequency()` or to `set_qam_channel()`. It sets `ext_attr->reset_pkt_err_acc = true` after channel programming.
- `ctrl_sig_quality()` is the standard-agnostic stats entry. It always tries `get_sig_strength()` first. For 8VSB, it only exposes BER/block/CNR stats when lock is present and uses VSB-specific helper functions; for QAM standards, it delegates to `ctrl_get_qam_sig_quality()`.
- `ctrl_lock_status()` sends a standard-specific SCU DEMOD_GET_LOCK command and maps SCU result thresholds to `DRX_NOT_LOCKED`, `DRXJ_DEMOD_LOCK`, `DRX_LOCKED`, or `DRX_NEVER_LOCK`. For VSB it adjusts the demod-lock threshold with `demod_lock |= 0x6`.
- `ctrl_set_standard()` powers down the previous standard, stores the new standard in `ext_attr->standard`, and runs standard-specific setup. QAM standards currently perform a dummy SCU RAM version read; VSB calls `set_vsb_leak_n_gain()`. On failure it deliberately sets the standard cache to `DRX_STANDARD_UNKNOWN`.
- `drxj_reset_mode()` rebuilds default AGC, PGA, RF AGC, and pre-SAW shadow settings for QAM and VSB, with separate defaults depending on `ext_attr->has_lna`.
- `ctrl_power_mode()` maps internal power modes to SIO clock/power-down levels, powers the device up if needed, resets analog defaults when returning to `DRX_POWER_UP`, or powers down the active standard before deeper sleep. It updates the SIO power-down registers, configures host-interface sleep for non-up modes, and finally updates `common_attr->current_power_mode`.
- `ctrl_set_cfg_pre_saw()` and `ctrl_set_cfg_afe_gain()` are configuration setters that write hardware only when the relevant standard family is active and always update the shadow copy in `ext_attr`.

### Lifecycle, Firmware, and Frontend Operations

- `drxj_open()` is the heavy initialization path used by attach and resume. It powers up the device, reads capabilities, soft-resets SYS/OSC clock domains, powers down unused analog/OOB/audio blocks, initializes the host interface, disables MPEG output pins, uploads and optionally verifies firmware, starts SCU execution, initializes scan timeout and default mode state, initializes smart antenna support, stamps the driver version into SCU RAM, disables OOB, resets audio defaults, marks the instance opened, and disables the LNA.
- `drxj_close()` powers the device up enough to access it, starts SCU execution, then transitions to `DRX_POWER_DOWN` and clears the opened flag.
- `drx_u_code_compute_crc()` computes the firmware block CRC over big-endian 16-bit words using the DRX polynomial residue logic.
- `drx_check_firmware()` validates the firmware block table, extracts the auxiliary firmware version block into `DRX_ATTR_MCRECORD(demod)`, and detects truncated images.
- `drx_ctrl_u_code()` requests the firmware named by `mc_info->mc_file`, validates the magic word and block count, checks block CRCs, uploads blocks via `drxdap_fasi_write_block()`, or verifies blocks by reading device memory with `drxdap_fasi_read_block()` and `memcmp()`.
- `drxj_set_lna_state()` configures UIO1 as read/write and writes the requested LNA GPIO state.
- `drx39xxj_attach()` allocates `struct drx39xxj_state`, `struct drx_demod_instance`, I2C address, common attributes, and extended attributes from defaults, wires the pointers, sets firmware name `DRX39XX_MAIN_FIRMWARE`, initial IF and power state, calls `drxj_open()`, installs `drx39xxj_ops`, and initializes DVBv5 stat lengths/scales.
- `drx39xxj_ops` advertises `SYS_ATSC` and `SYS_DVBC_ANNEX_B`, 51-858 MHz tuning, QAM64/QAM256/8VSB capability, and hooks for init, sleep, tuning, I2C gate, status/stat readback, LNA control, and release.

## Control Flow

The normal attach path is `drx39xxj_attach()` -> `drxj_open()` -> firmware upload/verify -> SCU start -> stats initialization. Failure during allocation or open unwinds allocated memory and returns `NULL`.

The normal tune path is `drx39xxj_set_frontend()`. It wakes the demodulator via `drx39xxj_set_powerstate()`, lets the tuner program RF parameters through `fe->ops.tuner_ops.set_params()`, reads the tuner IF if available, maps DVB delivery system/modulation to `DRX_STANDARD_8VSB` or `DRX_STANDARD_ITU_B` plus DRX constellation, calls `ctrl_set_standard()`, builds a default 6 MHz `struct drx_channel`, and calls `ctrl_set_channel()`. For Annex B auto modulation, `set_qam_channel()` tries QAM256 first and QAM64 second.

The status-read path is `drx39xxj_read_status()` -> `ctrl_lock_status()` -> DVB `enum fe_status` bits. It then calls `ctrl_sig_quality()` every time, so stat cache refresh is coupled to status polling rather than to the individual `read_ber`, `read_signal_strength`, `read_snr`, or `read_ucblocks` accessors. Those accessors only translate cached values from `fe->dtv_property_cache`.

Power and standard transitions are explicit. `ctrl_set_standard()` powers down the previous active demod standard before storing the new standard. `ctrl_power_mode()` also powers down the active standard when leaving full power and then resets `ext_attr->standard` to unknown.

## State and Persistence Behavior

The central persistent state is split between:

- `struct drx_common_attr`: opened flag, current power mode, firmware path, verification flag, intermediate frequency, MPEG output config, scan timeout, desired lock status, and firmware version record.
- `struct drxj_data`: active standard, constellation, mirror mode, AGC/PGA/pre-SAW shadow settings, OOB configuration tables and flags, audio state, LNA capability, UIO mode, packet-error reset flag, and measurement constants used by QAM stats.
- `struct drx39xxj_state`: Linux frontend object, I2C adapter pointer, demod pointer, and cached I2C-gate-open state.
- `struct dtv_frontend_properties`: DVBv5 stat counters/scales. This chunk writes stat scales and accumulates counters rather than returning raw hardware values directly.

Several routines intentionally mutate input or cached state. `set_qam_channel()` temporarily changes `channel->constellation` during auto-detection. `ctrl_set_channel()` may normalize `channel->bandwidth`. `ctrl_set_standard()` changes `ext_attr->standard` before completing setup and resets it to unknown on failure. `ctrl_power_mode()` resets mode defaults on power-up and clears the active standard on power-down. `drxj_open()` temporarily marks `common_attr->is_opened = true` during firmware upload so common microcode control can run, then restores it before final success.

Firmware metadata is not persisted outside memory except for the driver version stamp written into SCU RAM. The Linux firmware blob is requested on demand and released before returning from `drx_ctrl_u_code()`.

## Dependencies and Integration Points

This chunk depends on lower-level helpers and constants defined earlier in `drxj.c` and generated register headers:

- Register access: `drxj_dap_read_reg16()`, `drxj_dap_write_reg16()`, `drxdap_fasi_write_block()`, `drxdap_fasi_read_block()`.
- SCU command transport: `scu_command()`, `struct drxjscu_cmd`, and `SCU_RAM_COMMAND_*` constants.
- Standard setup/teardown helpers: `set_vsb()`, `set_frequency()`, `power_down_vsb()`, `power_down_qam()`, `set_qam()`, `qam_flip_spec()`, `set_iqm_af()`, `init_hi()`, `hi_cfg_command()`, `smart_ant_init()`.
- VSB stats helpers: `get_vsb_post_rs_pck_err()`, `get_vs_bpre_viterbi_ber()`, `get_vs_bpost_viterbi_ber()`, `get_vsbmer()`.
- DVB core interfaces: `struct dvb_frontend`, `struct dvb_frontend_ops`, `struct dtv_frontend_properties`, `enum fe_status`, `SYS_ATSC`, `SYS_DVBC_ANNEX_B`, `FE_SCALE_*`, and tuner/i2c-gate callbacks.
- Linux kernel infrastructure: `request_firmware()`, `release_firmware()`, `kmemdup()`, `kfree()`, `msleep()`, `jiffies_to_msecs()`, `do_div()`, endian helpers, `EXPORT_SYMBOL_GPL()`, and module metadata macros.

The attach function exports the driver entry point with `EXPORT_SYMBOL_GPL(drx39xxj_attach)`. The frontend integrates with an external tuner via `fe->ops.tuner_ops`; tuner IF is copied into `demod->my_common_attr->intermediate_freq`.

## Risks and Edge Cases

- QAM RS counters are read non-atomically, so derived BER/block samples can be internally inconsistent.
- `ctrl_get_qam_sig_quality()` reuses variables `e` and `m` across calculations. Later counter updates use the most recent exponent value, which makes the correctness sensitive to the exact calculation order.
- The QAM auto path mutates the caller's `struct drx_channel`; error paths restore only `channel->constellation` when `auto_flag` is true.
- `qam256auto()` uses CNR threshold `> 26800` from the cached DVB stat value after calling `ctrl_get_qam_sig_quality()`. This couples acquisition behavior to the stat conversion formula and cache update semantics.
- `ctrl_set_oob()` has many sequential hardware writes with no rollback if a later write fails. Partial OOB configuration can remain in hardware after an error.
- OOB frequency validation returns `-EIO` for out-of-range input rather than `-EINVAL`, unlike many other argument checks in this chunk.
- `drx39xxj_set_powerstate()` logs a power-state-change failure but still returns 0, so callers may proceed after a failed power transition.
- `drx39xxj_read_status()` calls `ctrl_sig_quality()` even if `ctrl_lock_status()` failed; `lock_status` is not initialized before the failed call path assigns status 0.
- Firmware parsing uses unaligned big-endian loads through casts such as `*(__be16 *)` and `*(__be32 *)`; this is common in older kernel code but can be architecture-sensitive if not tolerated by the platform.
- Firmware block processing in `drx_ctrl_u_code()` validates CRC and size fields but, unlike `drx_check_firmware()`, the upload/verify loop itself does not visibly re-check that each block payload remains inside `fw->size` before advancing `mc_data`.
- The LNA helper comment says "user-I/O #3" while the code uses `DRX_UIO1`, indicating stale documentation or a board-specific naming mismatch.
- Attach failure after `drxj_open()` succeeds jumps to allocation cleanup without calling `drxj_close()`, so hardware may remain initialized if a post-open setup failure is ever added before return.

## Test Signals

Useful validation signals for this chunk include:

- Attach succeeds only when firmware `DRX39XX_MAIN_FIRMWARE` is loadable, has the expected DRX microcode magic, nonzero block count, valid block CRCs, and passes optional readback verification.
- `drx39xxj_ops` exposes only `SYS_ATSC` and `SYS_DVBC_ANNEX_B`; unsupported delivery systems in `set_frontend` should return `-EINVAL`.
- ATSC tuning should call the external tuner, set `DRX_STANDARD_8VSB`, program a 6 MHz channel, and eventually report `FE_HAS_LOCK` through `read_status()` when `ctrl_lock_status()` returns `DRX_LOCKED`.
- Annex B QAM64 and QAM256 tuning should map DVB modulation to the matching DRX constellation; other modulation values should trigger QAM auto-detection.
- DVBv5 stat cache behavior should be tested through the sequence `read_status()` followed by `read_ber()`, `read_signal_strength()`, `read_snr()`, and `read_ucblocks()`, because the latter accessors depend on the cache populated by status polling.
- Power management tests should cover attach/open, sleep, init after resume (`fe->exit == DVB_FE_DEVICE_RESUME`), and release with both ordinary removal and `DVB_FE_DEVICE_REMOVED`.
- I2C-gate tests should verify duplicate enable/disable calls are no-ops and that successful `ctrl_i2c_bridge()` calls update `state->i2c_gate_open`.
- LNA tests should verify unsupported devices reject `c->lna = true` and supported devices drive UIO1 through `ctrl_set_uio_cfg()` and `ctrl_uio_write()`.
