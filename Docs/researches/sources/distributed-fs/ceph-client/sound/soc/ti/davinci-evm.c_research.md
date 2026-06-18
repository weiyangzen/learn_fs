# sources/distributed-fs/ceph-client/sound/soc/ti/davinci-evm.c

## Purpose
Machine driver for TI DaVinci EVM boards using TLV320AIC3X codec and McASP. It wires DT phandles into a card, manages optional MCLK, and sets codec/CPU sysclk.

## Important APIs/types/functions
`struct snd_soc_card_drvdata_davinci` stores MCLK and sysclk. Important functions are `evm_startup`, `evm_shutdown`, `evm_hw_params`, `evm_aic3x_init`, and `davinci_evm_probe`. Static descriptors are `evm_dai_tlv320aic3x` and `evm_soc_card`.

## Control flow
Probe matches the DAI link, parses codec and McASP phandles, assigns CPU/platform/codec nodes, parses model, obtains optional MCLK, derives sysclk from `ti,codec-clock-rate` or clock rate, then registers the card. Startup/shutdown enable/disable MCLK. `hw_params` sets codec and CPU sysclk. Codec init installs widgets/routes and disables unconnected pins.

## State, dependencies, integration, risks, tests
The static card/link are mutated with DT phandles; drvdata stores clock state. Dependencies are OF, ASoC, clocks, TLV320AIC3X, and McASP. Risks include static-card multi-instance issues, node reference cleanup, clock mismatch, and DT/legacy route divergence. Test phandle failures, MCLK behavior, sysclk setup, and playback routes.
