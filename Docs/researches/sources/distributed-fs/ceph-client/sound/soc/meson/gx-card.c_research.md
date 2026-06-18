# sources/distributed-fs/ceph-client/sound/soc/meson/gx-card.c

Purpose: provides the Amlogic GX machine driver that turns sound-card device-tree child nodes into ASoC DPCM frontend/backend links.

Important APIs/types/functions: local state `struct gx_dai_link_i2s_data` stores `mclk_fs`. Important functions are `gx_card_add_link`, `gx_card_parse_i2s`, `gx_card_i2s_be_hw_params`, and `gx_card_cpu_identify`.

Control flow: generic `meson_card_probe` calls match-data `gx_card_add_link` for each DT child. FIFO CPU DAIs become dynamic frontend links. Other links become backend links; AIU codec-control links get codec-to-codec parameters, while I2S encoder links also parse DAI format and `mclk-fs` for sysclk setup during hw_params.

State and persistence: per-link I2S data is devm allocated and stored in `meson_card.link_data[index]`; card/link arrays are managed by common Meson card utilities. Runtime clock configuration is derived from PCM params and `mclk_fs`.

Dependencies and integration: integrates with `meson-card-utils.c`, AIU compatible names, ASoC DPCM, DT child link descriptions, and the `amlogic,gx-sound-card` compatible.

Risks: CPU DAI role detection uses string matching on DAI names such as `"FIFO"`, `"CODEC CTRL"`, and `"I2S Encoder"`, making it sensitive to naming changes. Missing `mclk-fs` silently skips sysclk programming.

Test signals: card registration from DT, correct FE/BE split, codec-to-codec link creation, I2S sysclk setting on hw_params, and playback/capture through GX AIU FIFO and encoder paths.
