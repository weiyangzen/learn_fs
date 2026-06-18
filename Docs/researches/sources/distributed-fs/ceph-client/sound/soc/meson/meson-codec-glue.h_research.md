# sources/distributed-fs/ceph-client/sound/soc/meson/meson-codec-glue.h

Purpose: declares the common Meson codec-glue input state and helper functions used by internal DAC and HDMI glue codecs.

Important APIs/types/functions: `struct meson_codec_glue_input` stores `snd_soc_pcm_stream params` and `fmt`. Declarations cover input data retrieval, input hw_params/set_fmt/probe/remove, and output startup.

Control flow: no executable flow; this is the contract that glue drivers wire into their `snd_soc_dai_ops`.

State and persistence: exposes the state layout that input DAIs use to remember last negotiated stream parameters and format.

Dependencies and integration: includes ALSA ASoC and PCM parameter types; consumed by `g12a-toacodec.c`, `g12a-tohdmitx.c`, and implemented by `meson-codec-glue.c`.

Risks: because drivers can mutate `params` after helper hw_params, callers must preserve invariants expected by output startup. Header changes affect multiple codec glue drivers.

Test signals: compile coverage from all Meson glue drivers and runtime validation that `meson_codec_glue_input_get_data` returns usable state after DAI probe.
