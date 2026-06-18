# sources/distributed-fs/ceph-client/drivers/media/usb/cx231xx/cx231xx-avcore.c

## Purpose

`cx231xx-avcore.c` contains the hardware-control core for cx231xx analog/video/audio paths. It programs the analog front end, video decoder block, DIF/Colibri tuner IF path, I2S audio block, power modes, endpoint stream enable masks, GPIOs, and bit-banged GPIO I2C. It is the shared low-level register layer used by analog V4L2, MPEG 417, ALSA audio, DVB, tuner, and board setup code.

## Important APIs, Types, And Functions

- Register access wrappers: `verve_write_byte()`, `verve_read_byte()`, `afe_write_byte()`, `afe_read_byte()`, `vid_blk_write_byte()`, `vid_blk_read_byte()`, `vid_blk_write_word()`, and `vid_blk_read_word()` route byte/word I2C transactions to VERVE, AFE, and video-block device addresses.
- GPIO firmware-load helpers: `initGPIO()` and `uninitGPIO()` set GPIO direction/state, manipulate VERVE register `0x07`, start/stop VBI capture, and configure EP5/GBULK registers for firmware download.
- AFE setup: `cx231xx_afe_init_super_block()`, `cx231xx_afe_init_channels()`, `cx231xx_afe_setup_AFE_for_baseband()`, `cx231xx_afe_set_input_mux()`, `cx231xx_afe_set_mode()`, `cx231xx_afe_update_power_control()`, `cx231xx_afe_adjust_ref_count()`, and `cx231xx_Setup_AFE_for_LowIF()` tune ADC power, calibration, channel muxes, clamp/preclamp behavior, and reference counts.
- Video path setup: `cx231xx_set_video_input_mux()` selects board inputs and power mode, while `cx231xx_set_decoder_video_input()` programs AFE, video block, DIF/baseband mode, DFE control, output mode, and VBI/raw behavior for composite, S-video, tuner, and cable inputs.
- BT.656 export helpers: `cx231xx_enable656()` and `cx231xx_disable656()` program TS1 pin controls and are exported for the MPEG encoder path.
- Standard/timing helpers: `cx231xx_do_mode_ctrl_overrides()` adjusts VERT/HORIZ timing by NTSC/PAL/SECAM standard; `cx231xx_dif_set_standard()` writes large DIF register profiles by standard.
- Audio decoder helpers: `cx231xx_unmute_audio()`, `cx231xx_set_audio_input()`, and `cx231xx_set_audio_decoder_input()` route line/tuner/mute audio, reset audio firmware, program SRCs, I2S/parallel audio controls, AC97, path volume/thresholds, and SIF enable bits by tuner type.
- Chip/power helpers: `cx231xx_init_ctrl_pin_status()`, `cx231xx_set_agc_analog_digital_mux_select()`, `cx231xx_enable_i2c_port_3()`, and `cx231xx_set_power_mode()` manipulate control pins, tuner/demod I2C routing, and Polaris power bits.
- Stream helpers: `cx231xx_initialize_stream_xfer()`, `cx231xx_capture_start()`, `cx231xx_start_stream()`, and `cx231xx_stop_stream()` configure TS mode registers and set/clear endpoint bits in `EP_MODE_SET`.
- GPIO helpers: `cx231xx_set_gpio_direction()`, `cx231xx_set_gpio_value()`, and the `cx231xx_gpio_i2c_*()` family implement cached GPIO writes and a lock-protected software I2C bus.

## Control Flow

Input selection starts at `cx231xx_set_video_input_mux()`. It inspects the board input type, switches bus-powered boards into external-AV or analog-TV power mode as needed, maps tuner boards to either baseband decoder or DIF tuner mode depending on tuner type/model, then saves `dev->video_input`.

Decoder video setup first adjusts AFE reference count if the pin type changed, then sets AFE input muxes from board `vmux`. Composite and S-video paths force DIF baseband bypass, enable VBI gate and VGA auto, disable auto config, set CVBS or YC input mode, and program chroma/VGA channel selection. Tuner paths either use baseband for XC5000/specific I2C tuner boards or enable and configure the DIF for the current norm, enable AGC output pins, select output mode, and prepare AFE channels for audio.

DIF standard setup is table-like control flow. `cx231xx_dif_set_standard()` chooses a function mode by board model, configures C2HH for low IF, then writes profile constants for baseband, PAL D/I/M/N, SECAM variants, NTSC M, or default PAL BG. It preserves spectral inversion bits, disables `FLD_DIF_AUD_SRC_SEL`, and overrides `DIF_MISC_CTRL` for FM radio mode.

Power mode transitions are sequenced in `cx231xx_set_power_mode()`. It reads `PWR_CTL_EN`, sets groups of bits for external AV, analog TV, or digital mode with sleeps between writes, optionally resets tuner GPIOs, enables reset-out for digital mode, then calls AFE and I2S power update helpers and reads back power state.

Stream start/stop uses media-type mapping. `cx231xx_capture_start()` maps `Raw_Video`, `Audio`, `Vbi`, `Sliced_cc`, `TS1`, or `TS2` to endpoint enable bits from `cx231xx-conf-reg.h`. On start it calls `cx231xx_initialize_stream_xfer()` to program `TS_MODE_REG`/`TS1_CFG_REG`/length registers, then sets the endpoint bit. On stop it clears the endpoint bit.

GPIO I2C flow is explicit bit banging under `dev->gpio_i2c_lock`: start condition, address byte, ACK read with clock-stretch polling, byte reads/writes, ACK/NAK, and stop condition. Direction and value are cached in `dev->gpio_dir` and `dev->gpio_val`.

## State And Persistence

The file mutates core device state rather than persistent storage: `dev->video_input`, `dev->afe_mode`, `dev->afe_ref_count`, `dev->norm`, `dev->active_mode`, `dev->power_mode`, `dev->ctl_ainput`, `dev->gpio_dir`, `dev->gpio_val`, `dev->port_3_switch_enabled`, and `dev->xc_fw_load_done`. Hardware state persists in device registers until reset, power change, or unplug.

`cx231xx_enable_i2c_port_3()` stores the demod/tuner I2C switch state in `dev->port_3_switch_enabled`, and GPIO functions cache direction/value to construct subsequent full-register writes. Power mode changes may reset tuner firmware state with `dev->xc_fw_load_done = 0`.

## Dependencies And Integration Points

This file depends on register and field macros from `cx231xx-conf-reg.h`, video block field macros from the main driver headers, DIF filter data from `cx231xx-dif.h`, V4L2 standard bits, tuner constants, and shared USB/vendor/I2C helpers declared in `cx231xx.h`.

It is called by board/probe setup, analog input selection, MPEG firmware setup and BT.656 export, ALSA open/close through `cx231xx_capture_start(Audio)`, DVB/tuner channel changes, and GPIO-based tuner access. Exported symbols include `cx231xx_enable656()`, `cx231xx_disable656()`, `cx231xx_unmute_audio()`, `cx231xx_enable_i2c_port_3()`, and `cx231xx_capture_start()`.

## Risks And Edge Cases

- Many functions overwrite `status` repeatedly rather than accumulating or short-circuiting errors, so early register failures can be hidden by later successful writes.
- Several loops wait for exact AFE power status values without bounded counters; if hardware never reports the target value, power update can hang.
- `cx231xx_set_power_mode()` sets `dev->power_mode` before verifying hardware writes, so failed transitions can leave software state inconsistent.
- `cx231xx_set_decoder_video_input()` compares `pin_type` with `dev->video_input`, but `dev->video_input` stores an input index elsewhere; this can cause unnecessary or missed AFE reference adjustments.
- `cx231xx_tuner_post_channel_change()` returns success only if `status == sizeof(dwval)`, but helper write return conventions elsewhere may return 0 on success, creating possible false `-EIO`.
- GPIO I2C ACK timeout log says `nInit * 10` msec while the loop sleeps 2 ms per iteration; timeout accounting appears inaccurate.
- GPIO bit shifts depend on board GPIO fields being valid. Some board definitions use `-1` for tuner GPIO I2C pins, so callers must avoid GPIO I2C on those boards.
- Endianness is handled manually in control-register byte arrays and with unaligned-style casts to `__le32 *`; changes should preserve little-endian behavior and alignment assumptions.

## Test Signals

Hardware validation should watch input switching between composite, S-video, tuner, and digital paths; stable video lock after standard changes; correct AFE/DIF register writes for NTSC/PAL/SECAM; successful ALSA and VBI/Video/MPEG `cx231xx_capture_start()` calls; correct endpoint bits in `EP_MODE_SET`; no hangs in power transitions; tuner I2C reachability before and after `cx231xx_enable_i2c_port_3()`; and GPIO I2C ACK/NAK behavior. Fault tests should cover I2C write/read failures, invalid GPIO pins, unsupported media types, full-speed USB fallback, disconnected devices during stream toggles, and board configs with absent tuners or absent GPIO I2C pins.
