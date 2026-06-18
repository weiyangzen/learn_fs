# sources/distributed-fs/ceph-client/sound/soc/amd/vangogh/pci-acp5x.c

## Purpose
This is the Vangogh ACP5x PCI parent driver. It initializes ACP5x hardware, chooses legacy driver binding based on AMD audio configuration and SOF availability, creates I2S DMA/DAI and machine platform children in I2S mode, and handles PM/remove cleanup.

## Important APIs, Types, And Functions
Private state is `struct acp5x_dev_data`. Hardware helpers are `acp5x_power_on()`, `acp5x_reset()`, `acp5x_enable_interrupts()`, `acp5x_disable_interrupts()`, `acp5x_init()`, and `acp5x_deinit()`. PCI callbacks are `snd_acp5x_probe()`, `snd_acp5x_suspend()`, `snd_acp5x_resume()`, and `snd_acp5x_remove()`.

## Control Flow
Probe calls `snd_amd_acp_find_config()` and rejects the device unless legacy is selected, or SOF is selected but the SOF Vangogh driver is not enabled. It accepts PCI revision `0x50`, enables PCI, requests regions, maps BAR0, initializes ACP, reads `ACP_PIN_CONFIG`, and in I2S mode registers four platform devices: `acp5x_i2s_dma`, two `acp5x_i2s_playcap` DAIs for SP and HS, and `acp5x_mach`. It enables runtime PM autosuspend. Suspend deinitializes ACP; resume reinitializes it; remove unregisters children and disables PCI resources.

## State And Persistence Behavior
Parent state stores MMIO base, audio mode, resource array, and child platform devices. ACP init powers on, sets `ACP_CONTROL`, resets, selects clock mux `0x03`, and enables external interrupts. Deinit disables interrupts, resets, clears clock mux, and clears control.

## Dependencies And Integration Points
It depends on PCI, platform devices, runtime PM, `acp5x.h`, and `../mach-config.h`. It creates children consumed by `acp5x-pcm-dma.c`, `acp5x-i2s.c`, and `acp5x-mach.c`.

## Risks And Edge Cases
The config gate has nuanced interaction with SOF: legacy binds for `FLAG_AMD_LEGACY`, and can bind for `FLAG_AMD_SOF` only when SOF Vangogh support is not enabled. Probe ignores non-I2S pin modes after hardware init and PM setup. Error unwind unregisters only already-created children by decrementing `i`, which is safer than some older drivers. No MSI path is used; IRQ is shared.

## Test Signals
Test revision filtering, legacy versus SOF config combinations, I2S pin mode child creation, runtime/system suspend/resume, remove cleanup, and DMI-specific machine card binding downstream. Successful I2S mode should show `acp5x_i2s_dma.0`, `acp5x_i2s_playcap.0`, `acp5x_i2s_playcap.1`, and `acp5x_mach.0`.
