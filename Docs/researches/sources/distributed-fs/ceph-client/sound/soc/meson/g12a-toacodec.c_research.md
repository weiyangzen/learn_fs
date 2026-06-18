# sources/distributed-fs/ceph-client/sound/soc/meson/g12a-toacodec.c

Purpose: implements the Amlogic G12A/SM1 glue codec routing block from internal I2S/TDM sources to the internal analog codec output.

Important APIs/types/functions: private state is `struct g12a_toacodec` with regmap fields for data, LRCLK, and BCLK source selection. Key functions are `g12a_toacodec_mux_put_enum`, `g12a_toacodec_input_hw_params`, component probes for G12A/SM1, and `g12a_toacodec_probe`. It reuses `meson_codec_glue_input_*` and `meson_codec_glue_output_startup`.

Control flow: probe resets the device, maps registers, allocates SoC-specific regmap fields, and registers four DAIs: three inputs and one output. When the DAPM mux changes, it temporarily disconnects the mux, writes data/LRCLK/BCLK selectors to the same source, updates MCLK selector, then restores DAPM power. Input hw_params stores source stream constraints via codec glue and clamps output channels to the two-channel internal DAC lane.

State and persistence: mux selection, lane selection, enable, and static clock inversion bits live in `TOACODEC_CTRL0`. Runtime stream constraints are stored in per-input glue data associated with DAIs.

Dependencies and integration: depends on Meson TDM format definitions, `meson-codec-glue`, dt-bindings IDs, reset controller, regmap, and ASoC DAPM controls. It is selected by `amlogic,g12a-toacodec` or `amlogic,sm1-toacodec`.

Risks: the code assumes I2S A/B/C map to matching MCLK sources; a FIXME notes this may be wrong for future clock topologies. Source switches must update data and clocks atomically enough to avoid DAPM routing glitches. Output is limited to one lane/two channels even if input streams advertise more.

Test signals: successful component probe initializes clock inversion bits, mux changes produce matching data/LRCLK/BCLK fields, lane select works for both bit layouts, and internal DAC playback works for all three I2S sources.
