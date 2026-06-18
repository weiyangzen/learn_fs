<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/pci.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/maps/pci.c

Purpose: generic PCI MTD map driver for flash on add-in devices, specifically Intel IQ80310 ATU and Intel/DEC DC21285 blank-ROM programming mode.

Important APIs, types, and functions: `struct mtd_pci_info` supplies per-device init/exit/translate/map probe data. `struct map_pci_info` embeds `map_info`, PCI base mapping, and callbacks. Generic map hooks are `mtd_pci_read8/read32`, `mtd_pci_write8/write32`, and copy helpers. PCI lifecycle is `mtd_pci_probe()` and `mtd_pci_remove()`.

Control flow: PCI probe enables the device, requests regions, allocates map state, calls the matched device init, probes the requested map type (`cfi_probe` or `jedec_probe`), registers the MTD, and stores it as PCI driver data. IQ80310 init remaps BAR0, temporarily changes window base config, and translates offsets with page programming. DC21285 init maps ROM resource or BAR2 fallback and handles ROM enable/disable.

State and persistence: runtime state is PCI device enablement, mapped BAR/ROM aperture, saved IQ80310 window config, and MTD registration. Persistent state is flash contents.

Dependencies and integration points: PCI core, MTD map probes, CFI/JEDEC, and device-specific PCI resources/config registers.

Risks: probe error path calls `map->exit` even if per-device init failed before setting resources, so callback robustness matters. DC21285 BAR/ROM comments indicate incomplete resource migration. Test signals are PCI bind/unbind, saved config restoration, map translate correctness, and MTD registration on both supported IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/pci.c -->
