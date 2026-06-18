# sources/distributed-fs/ceph-client/sound/soc/tegra/tegra_asoc_machine.c

## Purpose
Shared Tegra ASoC machine-driver implementation for many older Tegra boards/codecs. It centralizes jack GPIOs, DAPM widgets/controls, clock programming, phandle binding, and codec-specific card descriptors.

## Important APIs/types/functions
Exports `tegra_asoc_machine_probe` and `tegra_asoc_machine_init`. `tegra_machine_hw_params` selects PLLA/PLLA_OUT0/MCLK rates and calls codec `set_sysclk`. Static `tegra_asoc_data` objects describe WM8753, WM9712, MAX98090/98088, SGTL5000, TLV320AIC23, RT5677/RT5640/RT5632/RT5631, and CPCAP cards.

## Control flow
Probe gets GPIOs, parses model/routes, assigns AC97 or I2S/codec phandles, installs optional common controls/widgets/ops, obtains clocks, handles legacy clock parent fallback, enables MCLK, and registers the card. Init creates headphone/headset/mic jacks according to GPIO availability and policy flags.

## State, dependencies, integration, risks, tests
`struct tegra_machine` stores clocks, cached rates, GPIO descriptors, and jack pointers. File-static jack objects imply one active card instance. Dependencies are ASoC, gpiod, clocks, OF, and codec drivers. Risks include global jack state, legacy clock quirks, widget-name coupling, and codec clock mismatch. Test compatibles, jack events, DAPM GPIOs, AC97/I2S probe, sample-rate changes, and suspend/resume.
