# sources/distributed-fs/ceph-client/sound/soc/amd/renoir/acp3x-rn.c

## Purpose
This is the Renoir DMIC ASoC machine driver. It binds the Renoir PDM DMA CPU/platform DAI to the generic DMIC codec and registers a one-link capture-only sound card.

## Important APIs, Types, And Functions
It defines `SND_SOC_DAILINK_DEF()` entries for `acp_rn_pdm_dma.0`, `dmic-codec.0`/`dmic-hifi`, and platform `acp_rn_pdm_dma.0`, then defines `acp_dai_pdm`, `acp_card`, and platform probe `acp_probe()`.

## Control Flow
The Renoir PCI parent creates platform device `acp_pdm_mach`. Probe assigns `acp_card.dev`, stores card data on the platform device, associates null machine private data, and registers the card. The single DAI link is capture-only and named `acp3x-dmic-capture`.

## State And Persistence Behavior
The file uses static card/link structures and does not hold runtime stream state. Power management uses `snd_soc_pm_ops`.

## Dependencies And Integration Points
It depends on `acp_rn_pdm_dma.0` from `acp3x-pdm-dma.c`, `dmic-codec.0` from the PCI parent, and `rn_acp3x.h` declarations. It is included only when `CONFIG_SND_SOC_AMD_RENOIR_MACH` is enabled.

## Risks And Edge Cases
The global static card assumes a single Renoir ACP card instance. If the machine-driver Kconfig is disabled, the PCI parent-created `acp_pdm_mach` device will not produce a sound card. No extra constraints or DAPM widgets are provided beyond component defaults.

## Test Signals
Expected signals are card name `acp`, one capture PCM named `DMIC capture`, successful component binding to `acp_rn_pdm_dma.0`, and no playback device from this card. Build coverage should include the machine Kconfig symbol.
