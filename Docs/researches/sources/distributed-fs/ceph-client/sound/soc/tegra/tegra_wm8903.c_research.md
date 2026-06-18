# sources/distributed-fs/ceph-client/sound/soc/tegra/tegra_wm8903.c

## Purpose
Codec-specific Tegra machine wrapper for WM8903 boards. It supplies WM8903 card/DAI descriptors and mic/MICBIAS handling while delegating generic setup to `tegra_asoc_machine_probe`.

## Important APIs/types/functions
Main functions are `tegra_wm8903_mclk_rate`, `tegra_wm8903_init`, and `tegra_wm8903_remove`. Static policy includes legacy and non-legacy `tegra_asoc_data` and a broad OF compatible table.

## Control flow
Shared probe binds the card. DAI init optionally fixes old HP-detect polarity, calls common init, creates a WM8903 codec-driven mic jack if no mic GPIO exists, calls `wm8903_mic_detect`, and force-enables `MICBIAS`. Remove disables mic detect. MCLK is 128x for high rates, 256x otherwise, then doubled until at least 6 MHz.

## State, dependencies, integration, risks, tests
State is common Tegra machine state, static descriptors, and WM8903 mic detection. Dependencies are WM8903 codec APIs, ASoC jack/DAPM, gpiod polarity, OF, and common Tegra helpers. Risks are legacy polarity quirks, mic GPIO versus codec detect conflicts, and forced MICBIAS. Test legacy compatibles, HP/mic/headset events, suspend/resume, and clock setup.
