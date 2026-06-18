# sources/distributed-fs/ceph-client/sound/soc/amd/yc/pci-acp6x.c

## Purpose
This is the AMD Yellow Carp ACP PCI parent driver. It owns PCI enablement, ACP power/reset/interrupt setup, platform-device creation for PDM DMA, DMIC codec, and machine driver, IRQ fanout to ALSA period notifications, and ACP runtime/system PM.

## Important APIs, Types, And Functions
`struct acp6x_dev_data` stores MMIO base, resource, audio mode, and child platform devices. Important helpers are `acp6x_power_on()`, `acp6x_reset()`, `acp6x_enable_interrupts()`, `acp6x_disable_interrupts()`, `acp6x_init()`, `acp6x_deinit()`, and `acp6x_irq_handler()`. `snd_acp6x_probe()` is the PCI probe path; `snd_acp6x_suspend()`, `snd_acp6x_resume()`, and `snd_acp6x_remove()` manage lifecycle. The PCI ID table matches AMD device `0x15E2` with multimedia-other class.

## Control Flow
Probe first calls external `snd_amd_acp_find_config()` and rejects handled configurations. It filters PCI revisions, enables the PCI device, requests BAR regions, maps BAR0, initializes ACP power/reset/clock/interrupts, then reads `ACP_PIN_CONFIG`. For reserved/non-I2S configurations it creates three child platform devices: `acp_yc_pdm_dma`, `dmic-codec`, and `acp_yc_mach`. It then requests the shared PCI IRQ and enables runtime PM. The IRQ handler checks `ACP_EXTERNAL_INTR_STAT` for `PDM_DMA_STAT`, clears it, and calls `snd_pcm_period_elapsed()` on the child PDM capture stream.

## State And Persistence
Software state persists in `acp6x_dev_data` and registered child devices. Hardware state includes ACP power-gating, reset, clock mux, external interrupt masks/status, pin configuration, and PDM DMA interrupt state. PM suspend deinitializes ACP; resume reinitializes it.

## Dependencies And Integration Points
It depends on PCI core, platform-device core, ASoC PDM and machine drivers, generic `dmic-codec`, `acp6x.h`, and the external AMD ACP configuration detector. It is the integration point that supplies the memory resource consumed by `acp6x-pdm-dma.c`.

## Risks And Test Signals
Risk areas include revision/pin-config gating, shared IRQ handling assuming `pdev[0]` exists when interrupts fire, and cleanup ordering across registered children. Test signals are correct child platform-device registration, valid IRQ period callbacks during capture, runtime suspend/resume survival, and clean removal without leaked children or enabled ACP interrupts.
