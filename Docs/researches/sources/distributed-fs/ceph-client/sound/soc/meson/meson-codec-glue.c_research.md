# sources/distributed-fs/ceph-client/sound/soc/meson/meson-codec-glue.c

Purpose: provides common helper logic for Meson codec glue blocks that expose multiple input DAIs and one or more output DAIs with propagated runtime constraints.

Important APIs/types/functions: exports `meson_codec_glue_input_get_data`, `meson_codec_glue_input_hw_params`, `meson_codec_glue_input_set_fmt`, `meson_codec_glue_output_startup`, `meson_codec_glue_input_dai_probe`, and `meson_codec_glue_input_dai_remove`. Internal helpers locate DAPM widgets and store per-input `struct meson_codec_glue_input`.

Control flow: input DAI probe allocates glue input state and binds it to the DAI playback widget. Input `hw_params` copies rate/channel/format intervals into that state; input `set_fmt` records the DAI format. Output startup walks source DAPM paths and applies the selected input constraints to the output substream.

State and persistence: state is per-input DAI devm-like allocation controlled by probe/remove, stored as DAI private data and widget private data. It persists while the component is registered and is updated on hw_params.

Dependencies and integration: used by G12A to-acodec and to-hdmitx glue drivers. Depends on ASoC DAPM graph traversal and ALSA runtime constraint APIs.

Risks: constraint propagation depends on correct DAPM source discovery; a missing or inactive source can leave outputs unconstrained or fail startup. The helper stores the last input parameters, so unusual graph changes before output startup need careful sequencing.

Test signals: input probe/remove memory lifecycle, output startup constraints matching active input, route switching across multiple inputs, and rejection of incompatible output params after input hw_params.
