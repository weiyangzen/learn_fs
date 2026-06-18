# sources/distributed-fs/ceph-client/sound/soc/amd/raven/pci-acp3x.c

## Purpose
This is the Raven ACP3x PCI parent driver. It powers and resets the ACP3x block, reads the I2S pin configuration, creates child platform devices for I2S DMA and CPU DAIs, and owns top-level runtime/system PM and cleanup.

## Important APIs, Types, And Functions
The private parent state is `struct acp3x_dev_data`. Hardware helpers include `acp3x_power_on()`, `acp3x_reset()`, `acp3x_enable_interrupts()`, `acp3x_disable_interrupts()`, `acp3x_init()`, and `acp3x_deinit()`. PCI callbacks are `snd_acp3x_probe()`, `snd_acp3x_suspend()`, `snd_acp3x_resume()`, and `snd_acp3x_remove()`.

## Control Flow
Probe accepts only PCI revision `0x00`, enables PCI, requests BAR regions, maps BAR0, saves `ACP_PME_EN`, initializes hardware, reads `mmACP_I2S_PIN_CONFIG`, and when in I2S mode creates four platform devices: one `acp3x_rv_i2s_dma` with MMIO and IRQ resources and three `acp3x_i2s_playcap` DAI devices for SP/BT windows. It then enables runtime PM autosuspend. Suspend deinitializes ACP; resume reinitializes it.

## State And Persistence Behavior
Parent state stores MMIO base, audio mode, resources, child platform devices, and saved PME enable value. Power-on restores saved PME state because ACP power-on clears `ACP_PME_EN`. Platform children persist until remove or probe-error unwind.

## Dependencies And Integration Points
It depends on PCI device `0x15e2` class multimedia other, `acp3x.h` register helpers, and Kbuild entries in the Raven Makefile. It passes IRQ flags as platform data to the DMA component and MMIO resources to both DMA and DAI children.

## Risks And Edge Cases
The platform-device unwind loop unregisters all four child slots even after a partial registration failure, which may include uninitialized pointers. Probe silently ignores non-I2S pin modes after initializing hardware and PM. Runtime suspend returns 0 even if deinit failed. MSI is not used; IRQ is shared.

## Test Signals
Bind on Raven revision `0x00`, confirm four child platform devices in I2S mode, validate PME register restoration after power-on, runtime suspend/resume cycles, remove-path child unregistering, and non-I2S pin mode behavior. Probe-error injection around child registration is useful for unwind validation.
