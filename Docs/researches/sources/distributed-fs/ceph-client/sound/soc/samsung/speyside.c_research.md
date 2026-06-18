# sources/distributed-fs/ceph-client/sound/soc/samsung/speyside.c

## Purpose
ASoC machine driver for the Wolfson/Samsung Speyside board. It binds the Samsung I2S CPU DAI, WM0010 DSP, WM8996 codec, WM1250 baseband codec, and WM9081 auxiliary speaker amp into one card with board-specific DAPM routes, headset detection, GPIO polarity handling, and low-power clock transitions.

## APIs, Types, and Functions
The module registers a `platform_driver` named `speyside` with `speyside_probe()`. Important card hooks are `speyside_set_bias_level()`, `speyside_set_bias_level_post()`, and `speyside_late_probe()`. Link init functions are `speyside_wm0010_init()` and `speyside_wm8996_init()`, and the auxiliary amp init is `speyside_wm9081_init()`. Jack state is represented by `speyside_headset`, `speyside_headset_pins`, `speyside_hpsel_gpio`, and `speyside_jack_polarity`; `speyside_set_polarity()` is passed to `wm8996_detect()`. The card uses three DAI links: CPU-DSP, DSP-CODEC, and Baseband, plus an aux device with prefix `Sub`.

## Control Flow, State, and Persistence
Probe installs a legacy GPIO lookup table for the WM8996 `hp-sel` line, registers a devm cleanup action, and registers the static `snd_soc_card`. WM8996 init sets the codec initially to the 32.768 kHz MCLK2 path, requests `hp-sel`, creates the headset jack, and enables WM8996 detection. Bias transitions affect only the WM8996 DAPM context: standby switches SYSCLK back to MCLK2 and stops the FLL, while prepare from standby starts the FLL from 32.768 kHz to `512 * 48000` and switches SYSCLK to the FLL. Headset polarity is persistent global board state and controls both GPIO output and the DAPM route predicate selecting MICB1 versus MICB2. Late probe marks playback/capture and external board pins as ignore-suspend.

## Dependencies and Integration
Depends on ASoC card, DAI link, DAPM, jack, GPIO descriptor and lookup APIs, and the WM8996/WM9081 codec helpers. It relies on fixed legacy component names such as `samsung-i2s.0`, `spi0.0`, `wm8996.1-001a`, `wm1250-ev1.1-0027`, and `wm9081.1-006c`, so it is tightly coupled to board registration rather than device tree.

## Risks and Test Signals
Risks include hard-coded DAI link indexes in bias hooks, static global jack/GPIO polarity state, missing NULL checks if `snd_soc_get_pcm_runtime()` cannot find a link, duplicate-looking `IN1RN` routes, and reliance on a GPIO lookup table that must match legacy board device names. Test signals are card probe, GPIO lookup cleanup on probe failure/remove, WM8996 FLL start/stop across DAPM bias changes, headset polarity flips rerouting MICB1/MICB2, suspend audio continuity for ignore-suspend paths, and working streams on CPU-DSP, DSP-CODEC, Baseband, and WM9081 speaker paths.
