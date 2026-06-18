# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic79xx_osm_pci.c

## Purpose

`aic79xx_osm_pci.c` is the Linux PCI-driver glue for AIC790x Ultra320 controllers. It exposes the Linux `pci_driver`, matches supported PCI IDs, handles probe/remove and power management callbacks, negotiates DMA masks, maps device registers, requests interrupts, and delegates hardware-specific configuration to `aic79xx_pci.c`.

## Important APIs, Types, and Functions

- `ahd_linux_pci_id_table[]` lists known adapters and generic AIC7901/AIC7902 probes using ID macros from `aic79xx_pci.h`.
- `aic79xx_pci_driver` provides `.probe`, `.remove`, `.id_table`, and SIMPLE_DEV_PM_OPS.
- `ahd_linux_pci_dev_probe()` performs identity lookup, softc allocation, `pci_enable_device()`, bus mastering, DMA mask selection, core PCI configuration, multi-function BIOS flag inheritance, driver-data storage, and host registration.
- `ahd_linux_pci_dev_remove()` removes the SCSI host, disables interrupts under lock, and frees the softc.
- `ahd_linux_pci_dev_suspend()` and `ahd_linux_pci_dev_resume()` sequence core suspend/resume with PCI state save/restore.
- `ahd_pci_map_registers()` prefers memory-mapped I/O when allowed and safe, validates the mapping with `ahd_pci_test_register_access()`, and falls back to PIO BARs.
- `ahd_pci_map_int()` requests the shared IRQ with `ahd_linux_isr()`.
- `ahd_power_state_change()` maps the core power-state enum to `pci_set_power_state()`.

## Control Flow and State

On module initialization, `ahd_linux_pci_init()` registers the PCI driver. Probe starts by mapping the Linux `pci_dev` to a core identity with `ahd_find_pci_device()`. The softc name encodes bus/slot/function. The driver enables the device, sets bus mastering, chooses 64-bit, 39-bit, or 32-bit DMA based on `dma_get_required_mask()` and `dma_set_mask()`, then calls `ahd_pci_config()`. Multi-function devices on nonzero functions inherit `AHD_BIOS_ENABLED` from function 0. If configuration succeeds, the `pci_dev` driver data receives the softc and the SCSI host is registered.

Register mapping clears memory/port enable bits while probing resources. The memory path reserves BAR1, maps the containing page, sets both AHD register windows to memory space, enables memory access, and tests register access. On failure it unmaps/releases and falls back to PIO, reserving BAR0 and the secondary I/O BAR at index 3. Final command register bits are written after a path is chosen.

## State and Persistence Behavior

The file stores the softc in PCI driver data, records IRQ and memory BAR bus address in `struct ahd_platform_data`, and records DMA addressing capability in `ahd->flags`. It does not persist data across reboot. Suspend saves core and PCI state through functions in other files; resume restores and restarts the controller through the same split.

## Dependencies and Integration Points

This file depends on Linux PCI/device/IRQ/resource APIs, `aic79xx_osm.h` for platform state and locks, `aic79xx_inline.h` for core helpers, and `aic79xx_pci.h` for ID constants. It integrates with `aic79xx_pci.c` for identity and chip configuration and with `aic79xx_osm.c` for ISR and host registration.

## Risks

- In the allocation error path after `kstrdup()` succeeds but `ahd_alloc()` fails, the local name buffer is not explicitly freed unless `ahd_alloc()` assumes ownership only on success; this is worth checking against core allocation behavior.
- The 64-bit BAR comment notes Linux PCI BAR indexing ambiguity; resource assumptions can break on unusual bridges.
- Memory mapping is disabled for `AHD_PCIX_MMAPIO_BUG` and falls back to PIO, so regressions in bug flags can expose broken MMIO behavior.
- Remove assumes `pci_get_drvdata()` is valid and that `ahd_free()` handles all mapped resources and IRQs.

## Test Signals

- PCI ID matching should bind all known AHA-29320/AHA-39320 variants and generic AIC790x devices.
- Probe logs should show successful resource mapping, DMA mask selection, IRQ request, and SCSI host registration.
- Force `aic79xx_allow_memio=0` and MMIO-test failure scenarios to validate PIO fallback.
- Suspend/resume and hot-remove tests should confirm interrupts are disabled and resources are released without use-after-free.
