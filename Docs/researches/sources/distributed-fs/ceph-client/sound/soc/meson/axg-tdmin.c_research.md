# sources/distributed-fs/ceph-client/sound/soc/meson/axg-tdmin.c

Purpose: Implements the AXG/G12A/SM1 TDM input formatter. It selects one of 16 TDM input pins, resolves the capture TDM stream through DAPM graph traversal, prepares input skew/format/slot/channel-mask registers, and delegates lifecycle management to the shared TDM formatter framework.

Important APIs and functions: The platform driver probes through `axg_tdm_formatter_probe()` with `axg_tdmin_drv` match data. Formatter ops are `axg_tdmin_get_tdm_stream()`, `axg_tdmin_prepare()`, `axg_tdmin_enable()`, and `axg_tdmin_disable()`. DAPM includes 16 AIF inputs, a `SRC SEL` mux, a `DEC` PGA with `axg_tdm_formatter_event()`, and an `OUT` AIF output.

Control flow: DAPM route traversal in `axg_tdmin_get_be()` walks upstream paths until it finds a backend DAI output and returns that DAI's capture stream. Formatter power-up in the common code attaches to that stream. Prepare computes bit skew from a SoC quirk plus format-specific adjustment, sets I2S-mode versus DSP behavior, compensates LRCLK inversion, programs slot width, clears LSB-first behavior so first received bit lands at bit 31, writes a static swap mask, and calls `axg_tdm_formatter_set_channel_masks()` for `TDMIN_MASK0..3`. Enable applies output/input reset sequencing and sets `TDMIN_CTRL_ENABLE`; disable clears it.

State and persistence: Static match data supplies a skew offset of 3 and the regmap range through `TDMIN_MUTE3`. Runtime state is held by the common formatter object. Selected input source, skew, mode, slot width, swap, and masks persist in TDMIN registers.

Dependencies and integration points: Depends on `axg-tdm-formatter` common code, `axg-tdm.h` polarity helpers, ASoC DAPM graph functions, and AXG card TDM links that expose capture streams.

Risks: Recursive DAPM graph traversal assumes a sane route graph and connected source paths. Skew programming is format-sensitive and includes a hardware quirk; wrong values cause bit misalignment. Channel masks depend on stream parameters having been validated by the interface before formatter prepare. The same driver data is used for AXG, G12A, and SM1 compatibles, so any SoC-specific divergence would need new match data.

Test signals: TDM capture from each input mux source, I2S/left-justified/DSP_A/DSP_B formats, LRCLK inversion variants, multi-lane masks, 8/16/24/32-bit slots, DAPM power transitions around `DEC`, and repeated start/stop checking channel alignment.
