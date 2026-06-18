# sources/distributed-fs/ceph-client/sound/pci/ca0106/ca0106_mixer.c

## Purpose

`ca0106_mixer.c` implements ALSA mixer/control surfaces for the CA0106 driver. It maps user controls to CA0106 pointer registers, GPIO mode bits, I2C ADC source/attenuation registers, SPI DAC mute bits, SPDIF IEC958 status words, and virtual master controls. It also cleans up and renames AC97 controls to match the CA0106 signal path.

## Important APIs, Types, and Functions

Hardware routing helpers include `ca0106_spdif_enable()`, `ca0106_set_capture_source()`, `ca0106_set_i2c_capture_source()`, `ca0106_set_capture_mic_line_in()`, and `ca0106_set_spdif_bits()`.

Control callbacks include shared SPDIF switch get/put, digital capture source enum get/put, I2C analog capture source enum get/put, shared mic/line or line/side enum get/put, SPDIF default/stream/mask get/put, pointer-register volume get/put, I2C volume get/put, and SPI mute get/put.

Macros `CA_VOLUME()` and `I2C_VOLUME()` define repeated controls with TLV dB scales. `snd_ca0106_volume_ctls[]` defines analog and IEC958 playback volumes, capture feedback volume, IEC958 controls, SPDIF switch, and capture source controls. `snd_ca0106_volume_i2c_adc_ctls[]` adds per-source ADC capture volumes. `snd_ca0106_volume_spi_dac_ctl()` dynamically creates analog playback switches for SPI-DAC boards.

`snd_ca0106_mixer()` is the exported setup entry point. Under PM sleep, `snd_ca0106_mixer_suspend()` and `snd_ca0106_mixer_resume()` save and restore key volume/routing state.

## Control Flow

Mixer setup removes many generic AC97 controls that do not match this hardware path and renames AC97 playback controls to capture-oriented names. It adds CA0106-specific volume/SPDIF/capture controls, conditionally adds I2C ADC controls and a GPIO shared-jack selector, conditionally adds SPI DAC mute controls, creates a virtual `Master Playback Volume` with follower controls, and for SPI boards creates a virtual `Master Playback Switch`.

When users toggle IEC958 playback, `ca0106_spdif_enable()` switches `SPDIF_SELECT1/2`, updates capture control bit `0x1000`, and adjusts GPIO bits. Capture source controls update `CAPTURE_SOURCE` nibble fields or I2C ADC mux/attenuation. Volume controls translate ALSA 0..255 values to inverted CA0106 attenuation bytes and write all four byte lanes. SPI mute controls update cached DAC registers and send one SPI command.

On suspend, selected pointer-register volumes are saved. On resume, volumes are restored, SPDIF mode and capture source are re-applied, I2C source/volume is forced, all SPDIF status words are rewritten, and shared input GPIO is restored for I2C ADC boards.

## State and Persistence Behavior

The mixer relies on state cached in `struct snd_ca0106`: `spdif_enable`, `capture_source`, `i2c_capture_source`, `i2c_capture_volume`, `capture_mic_line_in`, `spdif_bits`, `spdif_str_bits`, `spi_dac_reg`, and `saved_vol`. Controls return cached values for software-owned state and read pointer registers for hardware volume state.

Default SPDIF writes deliberately mirror default and stream status for older alsa-lib compatibility. I2C source switching mutes the ADC before changing attenuation and mux. SPI mute uses cached register images because DAC register readback is not available through this path.

## Dependencies and Integration Points

The file depends on `ca0106.h`, ALSA control/TLV APIs, AC97 controls already created by `ca0106_main.c` on AC97-capable boards, and the low-level pointer/I2C/SPI accessors from `ca0106_main.c`. It exposes user-visible ALSA mixer and PCM IEC958 controls.

## Risks and Edge Cases

Control removal/renaming is name-based, so upstream AC97 naming changes can leave stale controls or fail to rename expected controls. Several controls update global hardware fields and can affect active streams. `snd_ca0106_proc_i2c_write()` is separate, but mixer I2C writes still assume the ADC transaction helper succeeds. Dynamic SPI controls trust `details->spi_dac` channel-to-DAC mapping; a wrong table entry mutes the wrong channel. Resume unconditionally calls `ca0106_set_i2c_capture_source()` even though only some boards have I2C state initialized, but the later shared-jack restore is guarded.

## Test Signals

Test all mixer controls with `amixer`: analog/IEC958 volumes, capture feedback, IEC958 switch, digital and analog capture source enums, I2C per-source capture volumes, shared mic/line or line/side selector, SPI DAC playback switches, and virtual master followers. Confirm register changes through proc dumps, verify SPDIF status defaults and stream overrides, test resume restoration, and test active playback/capture while controls change.
