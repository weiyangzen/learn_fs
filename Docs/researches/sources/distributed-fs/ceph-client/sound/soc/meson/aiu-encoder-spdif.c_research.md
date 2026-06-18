# sources/distributed-fs/ceph-client/sound/soc/meson/aiu-encoder-spdif.c

Purpose: Implements the AIU SPDIF encoder DAI ops, including hold/unhold trigger control, IEC958 consumer channel-status programming, sample-width mode selection, SPDIF master-clock setup, and clock enable sequencing.

Important APIs and functions: Exported `aiu_encoder_spdif_dai_ops` supplies `startup`, `shutdown`, `trigger`, `hw_params`, and `hw_free`. Helpers include `aiu_encoder_spdif_divider_enable()`, `aiu_encoder_spdif_hold()`, and `aiu_encoder_spdif_setup_cs_word()`.

Control flow: Startup reparents the SPDIF MCLK selector to the dedicated `spdif_mclk`, then enables the SPDIF clock bulk. `hw_params` disables the divider, validates 16-bit or 32-bit physical widths, programs `AIU_958_MISC`, writes left/right IEC958 channel-status halfwords, sets the internal divider, sets MCLK to `rate * 128 * internal_div`, and enables the divider. Runtime trigger releases or asserts hold depending on start/stop/pause state. `hw_free` disables the divider and shutdown disables clocks.

State and persistence: Channel-status words persist in `AIU_958_CHSTAT_L/R*`; hold state persists in `AIU_958_CTRL`; format and clock divider state persist in `AIU_958_MISC` and `AIU_CLK_CTRL`.

Dependencies and integration points: Depends on ALSA IEC958 helper `snd_pcm_create_iec958_consumer_hw_params()`, AIU clock data, and AIU CPU DAI registration. It is connected through DAPM to the SPDIF FIFO or I2S FIFO via the AIU CPU SPDIF source mux.

Risks: Only PCM/uncompressed mode is configured; non-PCM bits are cleared. Incorrect MCLK parent selection or divider setup breaks SPDIF framing. Width validation excludes unusual containers. Trigger hold behavior must align with FIFO start/stop to avoid underrun noise.

Test signals: SPDIF playback at 32/44.1/48/88.2/96/176.4/192 kHz, S16 and S24/S32 containers, IEC958 status control inspection on receiver, pause/resume behavior, and clock/regmap tracing for `AIU_958_*`.
