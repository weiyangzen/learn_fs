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
