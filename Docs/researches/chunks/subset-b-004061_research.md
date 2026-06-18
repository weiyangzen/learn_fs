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
