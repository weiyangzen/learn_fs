# sources/distributed-fs/ceph-client/sound/soc/codecs/88pm860x-codec.c

Purpose: ASoC codec driver for Marvell 88PM860x PMIC audio. It exposes PCM and I2S codec DAIs, mixer controls, DAPM widgets/routes, bias sequencing, mute and hw_params programming, and headset/microphone/short jack detection through the parent MFD IRQ resources.

Important APIs, types, and functions: `struct pm860x_priv` stores sysclk/dir/filter, component, I2C/regmap handles, MFD chip, detection state, IRQs, and names. `struct pm860x_det` stores jack pointers and report masks. Custom controls include sidetone get/put through `st_table` and inverted output gain handlers. DAPM event handlers `pm860x_rsync_event()` and `pm860x_dac_event()` coordinate RSYNC and DAC mute/modulator bits. DAI ops cover mute, PCM/I2S hw_params, set_fmt, and set_sysclk. Exported `pm860x_hs_jack_detect()` and `pm860x_mic_jack_detect()` configure detection and synchronize jack state. Probe registers component, DAIs, and IRQ handlers.

Control flow: platform probe obtains the parent `pm860x_chip`, selects primary or companion I2C/regmap, reads four IRQ resources, and registers the component with two DAIs. Component probe initializes the regmap and requests four threaded IRQs. Bias STANDBY powers the audio PLL/section and reset sequence; OFF clears those bits. DAI hw_params writes word length and rate codes into PCM or I2S interface registers. Set_fmt validates master/slave direction against `pm860x->dir` and supports I2S mode. Jack IRQ handling reads status and shorts registers, builds headphone/mic/hook/short reports, and calls `snd_soc_jack_report()`.

State and persistence: runtime state is in `pm860x_priv`, ASoC regmap cache/registers, DAPM power state, IRQ registration, and jack report masks. Hardware state persists while the PMIC is powered but there is no filesystem persistence.

Dependencies and integration: depends on the 88PM860x MFD core (`linux/mfd/88pm860x.h`), PM860x register helpers, ALSA SoC component/DAI/DAPM/jack APIs, regmap, platform IRQ resources, and Kconfig symbol `SND_SOC_88PM860X`.

Risks: `pm860x_set_dai_sysclk()` only accepts `PM860X_CLK_DIR_OUT`, while I2S set_fmt has a path for clock input; machine drivers must call sysclk consistently or set_fmt fails. PCM supports only 8/16/32/48 kHz and I2S only common 8..48 kHz rates. Component probe uses non-devm `request_threaded_irq()` and frees on remove; partial failure cleanup is present. Jack handler only reports when a bit is present, so absence transitions rely on `snd_soc_jack_report()` masks during sync paths and should be tested. Register writes mix regmap via component and MFD helper I2C writes.

Test signals: build with `MFD_88PM860X`; probe via MFD child with four IRQ resources; enumerate two DAIs and mixer controls; run PCM/I2S playback/capture at accepted and rejected rates/widths; verify DAPM power sequencing, mute/RSYNC behavior, bias transitions, headset/mic/hook/short IRQ reporting, and remove cleanup.
