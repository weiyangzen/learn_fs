# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8195/mt8195-dai-pcm.c

## Purpose
Implements the MT8195 legacy PCM interface DAI named `PCM1`, with playback and capture, DAPM routes to the AFE interconnect, PCM format/clock polarity/master-mode setup, and ASRC/PCMIF clock supplies.

## Important APIs, Types, and Functions
`mt8195_dai_pcm_register()` registers the PCM sub-DAI. `mtk_dai_pcm_set_fmt()` stores ASoC format, inversion, and clock-provider policy in `struct mtk_dai_pcmif_priv`. `mtk_dai_pcm_prepare()` calls `mtk_dai_pcm_configure()` when neither playback nor capture widget is active. `mtk_dai_pcm_mode()` maps supported rates to PCM mode values. The only DAI driver is `PCM1`, symmetric in rate and sample bits, with S16/S24/S32 formats and rates from 8 kHz to 48 kHz.

## Control Flow
Registration allocates a sub-DAI descriptor, attaches the DAI driver, DAPM widgets, DAPM routes, and one private `mtk_dai_pcmif_priv`. `set_fmt` accepts I2S, DSP_A, and DSP_B formats, four LRCK/BCLK inversion combinations, and either codec bit/frame clock provider (`BC_FC`, slave mode) or CPU provider (`BP_FP`, master mode). `prepare` avoids reprogramming while either playback or capture is already active, then configures sync frequency, clock domain, PCM mode, format, sync length, word length, master/slave selection, and clock inversion.

For clock domain selection, rates divisible by 8 kHz use the 26 MHz 48 kHz family and 44.1 kHz-family rates use the 26 MHz 44.1 kHz family. Mode A/B force one-bit sync length; I2S/EIAJ style uses sample bit width. Widths above 16 bits use 24-bit and 64-BCK programming, otherwise 16-bit and 32-BCK.

## State and Persistence
Per-DAI state lives in `mtk_dai_pcmif_priv`: slave mode, LRCK inversion, BCLK inversion, and selected format. Hardware configuration persists in `PCM_INTF_CON1` and `PCM_INTF_CON2` until changed or regcache/runtime PM restores it. DAPM state controls `PCM_EN`, `aud_asrc11`, `aud_asrc12`, and `aud_pcmif`.

## Dependencies and Integration Points
Depends on regmap, ALSA PCM params, MT8195 clock/register definitions, and the AFE private state array. It integrates with memif I/O nodes `I002`, `I003`, `O000`, `O001`, `I000/I001`, and `I070/I071`; the MT8195 machine driver exposes `PCM1_BE` using this DAI.

## Risks
Slave-mode ASRC handling is explicitly left as a TODO, so external-clock PCM capture/playback can be incomplete. `prepare` uses DAPM widget active flags and may skip reconfiguration when simultaneous playback/capture requires a new compatible setup. Only a limited set of rates is mapped by `mtk_dai_pcm_mode()`. Unsupported format variants return `-EINVAL`, which can break machine links if DT/topology uses a different ASoC format constant.

## Test Signals
Signals include `PCM1` BE probe, format negotiation for I2S/DSP_A/DSP_B, master and slave clock polarity validation on pins, playback and capture at 8/16/32/44.1/48 kHz, 16-bit versus 24/32-bit BCK width checks, DAPM enabling `PCM_EN` and ASRC clocks, and simultaneous playback/capture behavior with symmetric constraints.
