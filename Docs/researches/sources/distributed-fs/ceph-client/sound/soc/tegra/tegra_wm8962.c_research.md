# sources/distributed-fs/ceph-client/sound/soc/tegra/tegra_wm8962.c

## Purpose
Tegra machine wrapper for WM8962 codec boards, using the common Tegra machine helper plus WM8962-specific MCLK and mic-detect setup.

## Important APIs/types/functions
Main functions are `tegra_wm8962_mclk_rate`, `tegra_wm8962_init`, and `tegra_wm8962_remove`. Static descriptors are `tegra_wm8962_dai`, `snd_soc_tegra_wm8962`, `tegra_wm8962_data`, and the `nvidia,tegra-audio-wm8962` match entry.

## Control flow
Shared probe registers the card. DAI init calls common init, creates a codec mic jack when external mic GPIO is absent, invokes `wm8962_mic_detect`, and force-enables `MICBIAS`. Remove unregisters codec mic detect. MCLK maps 48 kHz-family rates to 12.288 MHz, 44.1 kHz-family rates to 11.2896 MHz, and other rates to 12 MHz.

## State, dependencies, integration, risks, tests
State is common Tegra machine data, static card/DAI descriptors, and WM8962 mic-detect registration. Dependencies are WM8962 codec APIs, ASoC jack/DAPM, OF, and Tegra common helpers. Risks include unsupported rates falling back to 12 MHz and forced MICBIAS. Test probe, common rates, mic detection, GPIO fallback, and card removal.
