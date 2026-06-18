# sources/distributed-fs/ceph-client/include/linux/platform_data/asoc-pxa.h

Purpose: declares PXA2xx audio/AC97 platform operations and setup hooks used by legacy PXA board files and ASoC drivers.

Important APIs and types: `pxa2xx_audio_ops_t` contains PCM lifecycle callbacks (`startup`, `shutdown`, `suspend`, `resume`), private data, `reset_gpio`, and per-codec `codec_pdata[AC97_BUS_MAX_DEVICES]`. `pxa_set_ac97_info()` registers the ops, and `pxa27x_configure_ac97reset()` controls whether the PXA27x AC97 reset line is routed through GPIO.

Control flow: board code initializes audio ops through `pxa_set_ac97_info()`. The AC97/ASoC driver invokes lifecycle callbacks around PCM use and configures reset behavior, including the PXA27x reset-line workaround.

State and persistence: platform ops are static function/data pointers. Runtime PCM streams, AC97 bus devices, reset GPIO state, and suspend state live in audio drivers and hardware.

Dependencies and integration points: includes ALSA core, PCM, and AC97 codec headers. Integrates PXA board code, ASoC platform drivers, AC97 bus, GPIO reset handling, and codec-specific platform data.

Risks and test signals: risks include callback lifetime issues, wrong reset GPIO defaults, codec platform-data array bounds, and suspend/resume ordering bugs. Test AC97 reset on PXA27x, playback/capture callbacks, suspend/resume, multi-codec pdata, and no-reset-gpio configurations.
