# sources/distributed-fs/ceph-client/sound/soc/meson/axg-tdmout.c

Purpose: implements the Amlogic AXG/G12A/SM1 TDM output formatter component. It turns selected TDM input streams into a formatted serial output, programs slot/sample geometry, gain/mute/mask registers, and exposes DAPM routes for ASoC graph routing.

Important APIs/types/functions: registers through `axg_tdm_formatter_probe` using `axg_tdm_formatter_driver` instances. Key helpers are `axg_tdmout_get_be`, `axg_tdmout_get_tdm_stream`, `axg_tdmout_prepare`, `axg_tdmout_enable`, and `axg_tdmout_disable`. It depends on `struct axg_tdm_stream`, `struct axg_tdm_formatter_ops`, `axg_tdm_formatter_set_channel_masks`, and `axg_tdm_formatter_event`.

Control flow: DAPM powers the `"ENC"` PGA, which calls the generic formatter event path. The driver recursively follows enabled sink paths to find the backend DAI, obtains its playback TDM stream, prepares `TDMOUT_CTRL0/CTRL1` from the stream format/slot geometry/physical width, writes swap and channel masks, then deasserts resets and enables the block. Disable clears `TDMOUT_CTRL0_ENABLE`.

State and persistence: state is hardware register state in the MMIO regmap. Per-SoC differences are immutable match-data quirks: AXG uses skew offset 1, G12A/SM1 use skew offset 2, and SM1 has five input mux choices plus a different gain-enable bit.

Dependencies and integration: integrates with ASoC DAPM, ALSA controls for lane volumes/gain enable/input mux, device-tree compatibles `amlogic,axg-tdmout`, `amlogic,g12a-tdmout`, and `amlogic,sm1-tdmout`, and shared Meson TDM formatter infrastructure.

Risks: only I2S, left-justified, DSP_A, and DSP_B timing are accepted; unsupported physical widths fail at prepare time. Incorrect DAPM graph wiring can make backend stream discovery return null. Clock polarity is corrected by re-inverting LRCLK, so mistakes in `dai_fmt` propagate directly to bad framing.

Test signals: probe success for each compatible, mixer visibility for lane gain/mux controls, DAPM route power-up of `"ENC"`, playback with 8/16/32-bit physical widths, and audible/channel-mask validation across AXG/G12A/SM1 boards.
