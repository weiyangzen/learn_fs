# sources/distributed-fs/ceph-client/sound/soc/meson/g12a-tohdmitx.c

Purpose: implements the G12A HDMI transmitter audio glue codec, routing internal I2S and SPDIF sources to HDMI-facing output DAIs.

Important APIs/types/functions: key mux callbacks are `g12a_tohdmitx_i2s_mux_put_enum` and `g12a_tohdmitx_spdif_mux_put_enum`. DAI ops are built from `meson_codec_glue_input_*` and `meson_codec_glue_output_startup`. `g12a_tohdmi_component_probe` initializes static clock capture inversion.

Control flow: probe resets the block, maps a 32-bit regmap, and registers seven DAIs: three I2S inputs, one I2S output, two SPDIF inputs, and one SPDIF output. DAPM mux writes keep data and clock selectors in sync while temporarily disconnecting the path. DAPM switches gate the shared output enable bit for the active path.

State and persistence: source selection, clock selection, inversion, and output enable are all in `TOHDMITX_CTRL0`. Per-input hardware parameters are cached by `meson-codec-glue` for constraint propagation to output startup.

Dependencies and integration: uses ASoC DAPM, Meson codec glue, dt-bindings IDs, reset control, regmap, and the `amlogic,g12a-tohdmitx` compatible.

Risks: I2S and SPDIF output switches share the same enable bit, so DAPM sequencing matters. Source mux callbacks assume matching data and clock source indices. SPDIF and I2S support different PCM format masks; mismatched routes should be rejected through constraints but need coverage.

Test signals: DAPM routes for all I2S/SPDIF paths, successful HDMI audio playback from each source, mixer source changes without stale clocks, and format/rate constraints for SPDIF versus I2S outputs.
