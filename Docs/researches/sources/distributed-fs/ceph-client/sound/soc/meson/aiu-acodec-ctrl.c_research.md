# sources/distributed-fs/ceph-client/sound/soc/meson/aiu-acodec-ctrl.c

Purpose: Implements the AIU internal analog codec control component for GXL-class SoCs. It routes AIU I2S or PCM data into the internal DAC path, constrains the DAC-facing output to two channels, and exposes DAPM controls plus a lane-select mixer control.

Important APIs and functions: `aiu_acodec_ctrl_register_component()` registers the component and three DAIs: `ACODEC I2S IN`, `ACODEC PCM IN`, and `ACODEC OUT`. `aiu_acodec_ctrl_mux_put_enum()` safely switches the source mux by disconnecting DAPM before rewriting LRCLK/BCLK source fields. `aiu_acodec_ctrl_input_hw_params()` wraps `meson_codec_glue_input_hw_params()` and limits advertised channel min/max to `AIU_ACODEC_OUT_CHMAX`. Component probe `aiu_acodec_ctrl_component_probe()` programs DIN skew.

Control flow: Input DAIs use codec-glue probe/remove/hw_params/set_fmt callbacks to capture format data. The DAPM mux selects disabled/I2S/PCM, updates both data LRCLK and BCLK/MCLK source fields, then reconnects the selected route. The output DAI uses codec-glue output startup to enforce the parameters captured from the selected input.

State and persistence: Codec-glue input data persists per DAI and is mutated during hw_params. AIU control register bits persist in `AIU_ACODEC_CTRL`, including source selection, DIN enable, DIN skew, and lane source.

Dependencies and integration points: Depends on AIU register definitions, dt-bindings component IDs, `meson-codec-glue`, ALSA DAPM, and AIU platform probe, which calls this registration only when `has_acodec` is true.

Risks: The DIN skew write is documented as required to avoid output saturation but not fully understood. Source switching must remain DAPM-disconnected while register fields change to avoid glitches. Channel narrowing to two channels assumes only one of four glue lanes reaches the DAC.

Test signals: GXL internal DAC playback through I2S and PCM sources, DAPM route changes for `ACODEC SRC`, lane-select control changes, 1/2-channel negotiation, and regmap checks of `AIU_ACODEC_CTRL`.
