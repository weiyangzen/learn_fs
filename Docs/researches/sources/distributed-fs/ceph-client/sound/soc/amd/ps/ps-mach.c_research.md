# sources/distributed-fs/ceph-client/sound/soc/amd/ps/ps-mach.c

## Purpose
This is the simple ASoC machine driver for Pink Sardine DMIC capture. It connects the ACP PDM CPU DAI to the generic `dmic-codec` codec through the `acp_ps_pdm_dma` platform component.

## Important APIs, Types, And Functions
The file defines DAI link components with `SND_SOC_DAILINK_DEF()`, one `struct snd_soc_dai_link` named `acp63_dai_pdm`, one `struct snd_soc_card` named `acp63_card`, and a platform probe `acp63_probe()` that registers the card with `devm_snd_soc_register_card()`.

## Control Flow
The PCI parent registers a platform device named `acp_ps_mach` when DMIC is present without SoundWire. The platform probe attaches `acp63_card` to the platform device, associates null private machine data, and registers the card. The card has a single capture-only link named `acp63-dmic-capture`.

## State And Persistence Behavior
The only persistent state is the static card and DAI-link description. No runtime stream state, GPIO state, jack state, or codec clock state is maintained here. Power management delegates to `snd_soc_pm_ops` through the platform driver.

## Dependencies And Integration Points
It depends on the `acp_ps_pdm_dma.0` CPU/platform DAI provided by `ps-pdm-dma.c` and the generic `dmic-codec.0`/`dmic-hifi` codec platform device created by `pci-ps.c`. It includes `acp63.h` for local machine type declarations.

## Risks And Edge Cases
Because the card is static, concurrent multiple device instances would share one global card object; this matches typical single-ACP hardware assumptions. Registration fails if either the PDM DMA DAI or `dmic-codec` component is missing. No constraints are added here, so stream format constraints come from the PDM component and codec.

## Test Signals
Expected runtime signals are an ASoC card named `acp63`, one capture PCM for `DMIC capture`, successful bind of platform device `acp_ps_mach`, and no playback devices from this machine driver. Suspend/resume coverage should ensure `snd_soc_pm_ops` does not disturb the PDM DMA restore path.
