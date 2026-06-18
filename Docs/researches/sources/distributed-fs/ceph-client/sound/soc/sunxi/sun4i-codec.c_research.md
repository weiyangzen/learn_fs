# sources/distributed-fs/ceph-client/sound/soc/sunxi/sun4i-codec.c

## Purpose
`sun4i-codec.c` is the main Allwinner internal codec driver for many SoC generations. It combines digital codec FIFO/DMA programming, analog DAPM controls for older integrated codecs, a dummy CPU DAI for DMAengine PCM, and simple-card creation for SoC-specific routing and external analog-control auxiliary devices.

## Important APIs, Types, And Functions
`struct sun4i_codec` stores device, regmap, APB/module clocks, optional reset and GPIOs, regmap fields for variant-specific ADC/DAC FIFOC offsets, and DMA parameters. `struct sun4i_codec_quirks` selects the regmap config, codec component, card factory, FIFO field locations, TX/RX data register offsets, reset requirement, playback-only mode, and DMA maxburst. Core stream callbacks are `sun4i_codec_startup()`, `sun4i_codec_shutdown()`, `sun4i_codec_prepare()`, `sun4i_codec_hw_params()`, and `sun4i_codec_trigger()`. The file defines many ASoC controls, TLV scales, DAPM widgets/routes, card factories such as `sun4i_codec_create_card()`, `sun6i_codec_create_card()`, `sun8i_*_codec_create_card()`, `sun50i_h616_codec_create_card()`, and probe/remove.

## Control Flow
Probe maps registers, fetches quirks from OF compatible data, creates the regmap, enables APB clock, gets the module clock and optional reset, obtains optional speaker/headphone GPIOs, allocates FIFOC regmap fields, fills playback and capture DMA addresses from resource base plus quirk offsets, registers the SoC-specific codec component, registers a dummy CPU DAI component, registers DMAengine PCM, creates a SoC-specific card, stores driver data in the card, and registers the card. PCM startup sets DRQ clear behavior and enables the module clock. `hw_params()` chooses 22.5792 MHz or 24.576 MHz module clock families, maps sample rates to hardware rate codes, programs ADC/DAC sample rate, mono mode, sample-bit mode, FIFO packing, and DMA bus width. Prepare flushes FIFOs and programs trigger levels plus some undocumented SoC tuning. Trigger toggles ADC/DAC DRQ enables. Card initialization can set up headphone jack GPIO reporting, speaker PA GPIO DAPM events, auxiliary analog controls, and device-tree audio routing.

## State And Persistence
State persists in codec registers, regmap fields, DMA parameter structs, clocks, reset line, optional GPIO descriptors, ASoC card/component registration, and DAPM route/control state. Stream state is mostly in ALSA runtime; the driver mutates FIFO mode and DMA width per `hw_params()`. Device-managed resources cover most cleanup, while remove unregisters the card.

## Dependencies And Integration Points
The driver binds many compatibles from `allwinner,sun4i-a10-codec` through `allwinner,sun50i-h616-codec` and `allwinner,suniv-f1c100s-codec`. It depends on MMIO regmap, `apb` and `codec` clocks, optional resets, optional GPIOs `allwinner,pa` and `hp-det`, DMAengine PCM, ASoC component/card APIs, OF audio-routing, and for some sun8i variants the `allwinner,codec-analog-controls` phandle consumed as an auxiliary component.

## Risks And Edge Cases
The static global `aux_dev` is mutated by multiple card factory functions, which risks cross-instance state leakage on systems with more than one matching codec. `sun50i_h616_codec_quirks` sets `reg_adc_fifoc` and `reg_adc_rxdata` absent while `playback_only` is not set in the initializer, so probe still tries to allocate an ADC FIFOC field and configure capture DMA from zeroed fields; this should be verified against the intended local tree state. Several prepare paths program undocumented bits, making regression testing hardware-dependent. Supported rates are explicit, and clock selection rejects unknown rates. Card creation and component registration are tightly coupled; a missing analog-control phandle prevents sun8i cards from probing.

## Test Signals
Build all OF-compatible variants, probe each with valid clocks/resets/DMA, test playback and capture where supported, verify H616 playback-only behavior, exercise S16_LE and S32_LE DMA widths, mono/stereo paths, rate-code mapping for every supported rate, FIFO flush/DRQ trigger behavior, speaker PA and headphone-detect GPIOs, OF audio-routing parsing, auxiliary analog-control binding, and remove/unregister paths.
