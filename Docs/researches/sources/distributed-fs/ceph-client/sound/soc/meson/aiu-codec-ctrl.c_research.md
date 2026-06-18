# sources/distributed-fs/ceph-client/sound/soc/meson/aiu-codec-ctrl.c

Purpose: Implements the AIU HDMI codec control component. It routes AIU PCM or I2S streams into the HDMI codec-facing output and provides DAPM source selection over `AIU_HDMI_CLK_DATA_CTRL`.

Important APIs and functions: `aiu_hdmi_ctrl_register_component()` registers the HDMI control component and its `HDMI I2S IN`, `HDMI PCM IN`, and `HDMI OUT` DAIs. `aiu_codec_ctrl_mux_put_enum()` switches clock and data source fields while temporarily disconnecting the DAPM mux. Input DAIs use `meson_codec_glue_input_*` ops; the output DAI uses `meson_codec_glue_output_startup()`.

Control flow: DAPM source changes first force the mux to disabled, clear clock/data selection fields, then set both fields to the requested PCM or I2S source and restore DAPM power. Codec-glue input `hw_params` records stream parameters for the output side to consume during startup.

State and persistence: Source state persists in `AIU_HDMI_CLK_DATA_CTRL`. Codec-glue per-input state records format, rate, channel, and lane parameters while a route is active.

Dependencies and integration points: Registered by the AIU core for HDMI-capable topologies. Integrates with `meson-codec-glue`, HDMI codec components, device-tree DAI phandle translation through `aiu_of_xlate_dai_name()`, and DAPM routes from AIU encoders or FIFOs to HDMI.

Risks: The reset-then-set sequence is important because switching clock/data source independently could expose mismatched clocks to the HDMI codec. DAI name and component-id phandle translations must match dt-bindings. The component supports up to eight channels, so downstream HDMI codec limits must be negotiated correctly by DPCM.

Test signals: HDMI audio playback using I2S and PCM sources, DAPM mux changes under active/inactive routes, `aplay` multichannel negotiation, and regmap traces for `AIU_HDMI_CLK_DATA_CTRL`.
