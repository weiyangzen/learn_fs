# sources/distributed-fs/ceph-client/sound/soc/qcom/storm.c

Purpose: small machine driver for Google/QTi IPQ806x Storm audio, connecting a DT-specified CPU DAI and codec DAI and programming CPU sysclk as a multiple of I2S bit clock.

Important functions: `storm_ops_hw_params()` computes `sysclk_freq = rate * bitwidth * 2 * STORM_SYSCLK_MULT` and calls `snd_soc_dai_set_sysclk()` on the CPU DAI. `storm_parse_of()` resolves `cpu` and `codec` phandles and mirrors the CPU node to the platform component. `storm_platform_probe()` parses card name, fills a single DAI link, and registers the card.

Control flow: probe allocates an ASoC card, reads `qcom,model`, resolves phandles, and registers. During hw_params, the CPU DAI clock divider receives a stable sysclk derived from the PCM params.

State and persistence: no private mutable state beyond the devm-managed card. DAI link definition is static.

Dependencies and integration: depends on OF phandles, ASoC card registration, and a codec named `HiFi`. Compatible is `google,storm-audio`.

Risks: the DAI link uses `COMP_EMPTY()` placeholders filled by DT; missing phandles fail probe. Sysclk assumes stereo (`* 2`) and no codec system clock requirement. Unsupported PCM formats fail through negative bit width.

Test signals: DT card-name parse, CPU/codec phandle resolution, `snd_soc_dai_set_sysclk()` called with expected rate for 44.1/48 kHz formats, and successful playback through the MAX98357a-style codec path.
