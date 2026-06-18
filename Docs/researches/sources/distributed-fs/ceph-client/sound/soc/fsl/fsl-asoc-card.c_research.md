# sources/distributed-fs/ceph-client/sound/soc/fsl/fsl-asoc-card.c

## Purpose
`fsl-asoc-card.c` is the generic Freescale i.MX ASoC machine-card driver for boards that connect an SSI/ESAI/SAI/SPDIF CPU DAI to one or two codecs, optionally through an ASRC DPCM front-end/back-end path. It converts Device Tree board descriptions into `snd_soc_card`, `snd_soc_dai_link`, DAPM routes/widgets, jack detection, AUDMUX wiring, codec clock/PLL setup, and ASRC backend rate/format constraints.

## Important APIs, Types, and Functions
- `struct codec_priv` stores per-codec MCLK, free-running fallback frequency, MCLK/FLL/PLL IDs used with `snd_soc_dai_set_sysclk()` and `snd_soc_dai_set_pll()`.
- `struct cpu_priv` stores CPU DAI sysclk IDs, directions, static rates, sample-rate ratios, and optional TDM slot shape.
- `struct fsl_asoc_card_priv` is card state: three DAI links, jacks, CPU/codec private data, current stream mask, current sample rate/format, ASRC backend rate/format, DAI format, and generated card name.
- `fsl_asoc_card_hw_params()` records active stream parameters, sets CPU sysclk/TDM slots, and starts codec PLL/FLL paths when a codec profile declares PLL and FLL IDs.
- `fsl_asoc_card_hw_free()` clears the active stream bit and, when the last stream stops, switches codecs back to MCLK/free frequency and stops FLL/PLL.
- `be_hw_params_fixup()` forces ASRC backend DPCM parameters to the ASRC output rate and format parsed from the ASRC node.
- `fsl_asoc_card_audmux_init()` programs i.MX AUDMUX port routing based on CPU/codec clock-provider format or AC97 mode.
- `fsl_asoc_card_spdif_init()` handles new and legacy SPDIF bindings, including dummy codec fallback and playback/capture-only route pruning.
- `fsl_asoc_card_late_probe()` applies codec sysclk after card registration and handles an AC97 S/PDIF slot quirk.
- `fsl_asoc_card_probe()` is the main DT parser and card constructor.

## Control Flow
Probe allocates private state, resolves `audio-cpu` or legacy CPU phandles, looks up up to two codecs, optionally resolves `audio-asrc`, samples codec MCLK rates, and initializes three predeclared links: normal link, ASRC FE, and ASRC BE. It then selects a board-specific profile from the machine compatible string, filling codec DAI names, DAI format, PLL/FLL IDs, stream direction limits, TDM width, CPU sysclk direction/ratio, and DAPM route variants.

After profile selection, DT can override `mclk-id` and DAI clock provider/format. CPU-specific setup configures AUDMUX for SSI, reads ESAI `extal` clock and IDs, or sets SAI master clock IDs. The card is named from `model` or a fallback, routes/widgets are attached, ASRC-only route halves are dropped when no ASRC node exists, and `audio-routing` can replace/extend routing via standard ASoC parsing.

Normal link components are bound to CPU and codec nodes. AC97 uses `cell-index` to synthesize an `ac97-codec.N` component name. When ASRC is present, links 1 and 2 are enabled as FE/BE DPCM links, codec components are copied to the BE link, and ASRC fixed output rate/format are read from `fsl,asrc-rate` plus `fsl,asrc-format` or legacy `fsl,asrc-width`.

Runtime `hw_params` sets CPU and codec clocks per stream. Runtime `hw_free` tears down shared codec FLL/PLL only when no streams remain. Jack setup happens after `devm_snd_soc_register_card()` and registers notifiers to disable speaker on headphone insertion and DMIC on analog mic insertion.

## State and Persistence
All state is kernel runtime state owned by the platform device and ASoC card. `priv->streams` is a bitmask protecting shared PLL teardown while playback/capture overlap. `sample_rate` and `sample_format` are updated from the latest stream and used for PLL ratios. `asrc_rate` and `asrc_format` persist from DT and feed DPCM backend fixups. No disk persistence exists.

Device Tree is the persistent configuration source. The driver consumes both current and legacy properties: `audio-cpu`, `ssi-controller`, `spdif-controller`, `audio-codec`, `audio-asrc`, `mclk-id`, `model`, `audio-routing`, `mux-int-port`, `mux-ext-port`, old SPDIF booleans, and deprecated GPIO names.

## Dependencies and Integration Points
The driver integrates with ASoC core card/link/component APIs, simple-card jack helpers, codec-specific clock IDs from several codec headers, CPU DAI definitions from FSL ESAI/SAI, i.MX AUDMUX, AC97 support when enabled, and the ASRC DAI exposed by `fsl_asrc.c`. DPCM integration depends on the ASRC platform exposing FE CPU/platform DAIs and on `fsl_asrc_dma.c` providing the component DMA operations.

## Risks and Edge Cases
- The profile table hard-codes many board/codec assumptions; new compatibles must fill all clock, format, and route details correctly.
- `codec_dai_name[]` and `codec_dev_name[]` are profile-dependent and can be uninitialized if a branch fails to assign names for all active codec slots.
- The stream bitmask is not locked; ASoC serializes most runtime callbacks, but concurrent open/close behavior should still be considered when modifying clock teardown.
- PLL output ratios are fixed at 256x or 384x depending on S24_LE only, which may not match every codec or packed 24-bit variant.
- AUDMUX setup is sensitive to master/slave interpretation and legacy AC97 special casing.
- ASRC route pruning assumes ASRC routes remain in the second half of each route array.
- SPDIF old-binding dummy-codec handling intentionally suppresses DAPM routes; changes can break old device trees.

## Test Signals
- Probe succeeds for each compatible string with representative DTs, including one/two-codec SPDIF, AC97, SSI AUDMUX, ESAI, SAI, and ASRC/non-ASRC variants.
- `aplay`/`arecord` exercise `hw_params`, `trigger`, and `hw_free` for playback-only, capture-only, and duplex profiles without clock errors.
- ASRC DPCM playback/capture reports BE parameters fixed to `fsl,asrc-rate` and `fsl,asrc-format`.
- Jack GPIO insertion toggles DAPM pins `Ext Spk` and `DMIC` as expected.
- Runtime logs lack `failed to set sysclk`, `failed to start FLL`, `failed to init audmux`, and probe defer loops after dependencies bind.
