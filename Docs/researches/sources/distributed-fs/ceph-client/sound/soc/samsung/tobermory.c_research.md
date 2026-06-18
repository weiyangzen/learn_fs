# sources/distributed-fs/ceph-client/sound/soc/samsung/tobermory.c

## Purpose
ASoC machine driver for the Tobermory board with Samsung I2S and a WM8962 codec. It provides a single CPU-codec link, board routes for headphone, speaker, headset mic, analog mic, and digital mic, headset detection, and bias-level FLL clock management.

## APIs, Types, and Functions
Registers a `platform_driver` named `tobermory`. The main card hooks are `tobermory_set_bias_level()`, `tobermory_set_bias_level_post()`, `tobermory_hw_params()`, `tobermory_late_probe()`, and `tobermory_probe()`. `sample_rate` is a file-scope setting captured from `hw_params` and later used in bias transitions. The DAI link uses `samsung-i2s.0` to `wm8962.1-001a` with I2S normal polarity and codec bit/frame master. Jack state is held in `tobermory_headset` and `tobermory_headset_pins`.

## Control Flow, State, and Persistence
Probe assigns the card device and registers the static card. Late probe sets the codec SYSCLK to 32.768 kHz MCLK input, creates the headset jack, and enables `wm8962_mic_detect()`. `hw_params` records the stream sample rate globally. On PREPARE from STANDBY, the codec FLL is started from 32.768 kHz to `sample_rate * 512` and SYSCLK is switched to the FLL. In post-bias STANDBY, SYSCLK is switched back to MCLK and the FLL is stopped. DAPM routes remain static, with fully routed card policy.

## Dependencies and Integration
Depends on ASoC card/DAI/DAPM/jack APIs and the WM8962 codec helper `wm8962_mic_detect()`. Like the older board files, it uses fixed component names instead of OF matching and relies on platform device registration under alias `platform:tobermory`.

## Risks and Test Signals
Risks include a global `sample_rate` shared across any theoretical instances, FLL configuration before `hw_params` using the default 44.1 kHz rate, a headset jack pin entry for `Headphone` with microphone mask that looks suspicious, and hard-coded DAI link indexes in bias hooks. Test signals are probe and late-probe success, headset button/mic reporting, FLL start/stop across playback/capture at several rates, DAPM route validation for AMIC/DMIC/headset/speaker/headphone, and suspend/resume through `snd_soc_pm_ops`.
