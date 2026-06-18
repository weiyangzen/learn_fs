# sources/distributed-fs/ceph-client/sound/soc/amd/renoir/rn-pci-acp3x.c

## Purpose
This is the Renoir ACP PCI parent driver for DMIC/PDM support. It initializes the ACP block, gates device creation through config, PCI revision, ACPI `_WOV`, DMI quirks, and module parameters, and creates PDM DMA, DMIC codec, and machine platform devices.

## Important APIs, Types, And Functions
Private state is `struct acp_dev_data`. Module parameters are `acp_power_gating` and `dmic_acpi_check`. Hardware functions are `rn_acp_power_on()`, `rn_acp_power_off()`, `rn_acp_reset()`, `rn_acp_enable_interrupts()`, `rn_acp_disable_interrupts()`, `rn_acp_init()`, and `rn_acp_deinit()`. PCI callbacks are `snd_rn_acp_probe()`, `snd_rn_acp_suspend()`, `snd_rn_acp_resume()`, and `snd_rn_acp_remove()`.

## Control Flow
Probe first rejects systems configured for another AMD ACP stack via `snd_amd_acp_find_config()` and rejects non-Renoir revision `0x01`. It enables PCI, requests regions, attempts MSI, maps BAR0, initializes ACP, checks DMIC policy (`dmic_acpi_check`), evaluates ACPI `_WOV` in auto mode, applies DMI quirks that suppress DMIC on listed Lenovo systems, allocates two resources, and registers three platform devices: `acp_rn_pdm_dma`, `dmic-codec`, and `acp_pdm_mach`. PM suspend deinitializes ACP; resume reinitializes it.

## State And Persistence Behavior
Parent state persists MMIO base, resource array, and three child platform devices. `acp_power_gating` controls whether deinit powers off the block after reset. MSI enable state is persisted in PCI core and disabled during remove/error paths. Runtime PM autosuspend is enabled after successful child creation.

## Dependencies And Integration Points
It depends on Linux PCI, ACPI, DMI, runtime PM, the shared AMD machine-config helper `snd_amd_acp_find_config()`, and `rn_acp3x.h` register definitions. The children bind to Renoir PDM DMA, generic DMIC codec, and Renoir machine drivers.

## Risks And Edge Cases
`dmic_acpi_check=0` forces probe failure even if hardware exists; auto mode can fail if `_WOV` is absent. DMI quirks suppress DMIC for listed Lenovo systems by using entries with null `driver_data`. Error unwind unregisters all `ACP_DEVS` children even after partial registration, which may encounter uninitialized entries. Optional power gating changes hardware state across suspend and should be validated per platform.

## Test Signals
Test revision filtering, `snd_amd_acp_find_config()` interaction, MSI and shared IRQ paths, `_WOV` present/absent/false, each `dmic_acpi_check` setting, DMI-quirked Lenovo systems, runtime/system suspend/resume, and remove/error unwind. Expected successful platforms show three child platform devices.
