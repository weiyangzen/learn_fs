# sources/distributed-fs/ceph-client/sound/pci/oxygen/xonar_wm87x6.c

## Purpose

This file implements the Oxygen/CMI8788 model support for Asus cards using Wolfson WM8776 and WM8766 codecs: Xonar DS/DSX and Xonar HDAV1.3 Slim. It defines board-specific initialization, suspend/resume, GPIO handling, codec register programming, ALSA mixer controls, HDMI integration for the Slim model, and model selection based on PCI subdevice IDs.

## Important APIs, Types, And Functions

- `struct xonar_wm87x6` extends the generic Xonar model data with cached WM8776/WM8766 register arrays, control pointers for mutually exclusive ADC mux controls, limiter/ALC control pointers, an optional headphone jack, and HDMI state.
- `wm8776_write_spi()`, `wm8776_write_i2c()`, `wm8776_write()`, and `wm8776_write_cached()` abstract codec writes and keep `wm8776_regs[]` synchronized for controls and resume.
- `wm8766_write()` and `wm8766_write_cached()` do the same for the WM8766 surround DAC over SPI.
- `xonar_ds_init()`, `xonar_hdav_slim_init()`, cleanup, suspend, and resume callbacks become the `oxygen_model` lifecycle hooks.
- `update_wm8776_volume()`, `update_wm87x6_volume()`, `update_wm8776_mute()`, `update_wm87x6_mute()`, and `update_wm8766_center_lfe_mix()` are the callbacks consumed by the common Oxygen PCM/mixer code.
- Mixer callbacks implement headphone volume/switch, ADC input volume, ADC mux, ADC high-pass filter, WM8776 limiter/ALC mode and parameters, HDMI output switch, and DS-specific front/mic/line/aux capture controls.
- `get_xonar_wm87x6_model()` maps PCI subdevices `0x838e`, `0x8522`, and `0x835e` to the DS, DSX, and HDAV Slim models.

## Control Flow

During probe, the common Oxygen driver calls `get_xonar_wm87x6_model()` and then the selected model's `init` callback. DS initialization sets anti-pop/output GPIO metadata, initializes both codecs, configures GPIO direction/data/interrupts for input routing and headphone detect, enables output, creates the headphone jack, reports the current jack state, and registers codec component names. HDAV Slim initialization initializes WM8776, configures HDMI/firmware GPIO pins, initializes HDMI support, enables output, and adds the WM8776 component.

PCM parameter callbacks are light. The WM8776 ADC path changes master-rate control when capture exceeds 48 kHz. HDAV Slim DAC params delegate to `xonar_set_hdmi_params()`. The normal Oxygen mixer invokes the file's DAC volume/mute callbacks, which update cached codec registers and use codec master-update bits so stereo or multi-channel volume changes latch coherently.

GPIO interrupts call `xonar_ds_gpio_changed()`, which re-reads headphone detect under `chip->mutex`, routes front L/R output between speaker and headphone paths, mutes or unmutes the WM8766 surround codec, and reports `SND_JACK_HEADPHONE`.

Mixer creation adds static control templates, captures pointers to the line and mic mux controls, and adds the limiter/ALC dependent controls. The "Level Control" enum toggles WM8776 limiter/ALC enable and changes the active/inactive access state of the mode-specific controls.

## State And Persistence

The persistent runtime state is in `struct xonar_wm87x6` and the shared `struct oxygen`. Codec register caches are authoritative for ALSA control reads, change detection, and resume reprogramming. `chip->dac_volume[]` and `chip->dac_mute` remain common Oxygen state. GPIO routing and HDMI state are hardware-backed and restored through resume callbacks. There is no disk persistence; settings live only while the ALSA card instance exists.

## Dependencies And Integration Points

This file integrates with the Oxygen PCI framework through `struct oxygen_model`. It depends on common Xonar helpers (`xonar_enable_output()`, GPIO bit control callbacks, HDMI helpers), Oxygen bus helpers (`oxygen_write_spi()`, `oxygen_write_i2c()`, GPIO register helpers), ALSA control/jack/proc APIs, and Wolfson register definitions from `wm8776.h` and `wm8766.h`.

## Risks

- Cached register correctness is critical. If a write path forgets to mask update bits or update the cache, future ALSA reads and resume restore stale values.
- The DS line and mic mux controls are mutually exclusive and notify each other manually; changes in control names or missing pointer capture break notification.
- GPIO polarity is board-specific. Headphone detect is active low, while Slim HDMI disable is inverted through the generic GPIO control helper.
- Limiter/ALC controls reuse `private_value` both as cached user value and bit-field metadata, so invalid masks or mode flags can silently program the wrong WM8776 field.
- The DS volume update path appears to compare right DAC volume against `WM8776_DACLVOL` when forming `to_change`; this should be reviewed if volume updates are suspected to skip the right channel.

## Test Signals

Useful validation includes probe on each subdevice, suspend/resume with register dumps, ALSA control read/write coverage for all WM8776 fields, headphone jack plug/unplug interrupt tests, capture mux exclusivity checks, 96 kHz capture validation for ADC over-sampling, multi-channel playback volume/mute tests, and HDAV Slim HDMI audio/control tests.
