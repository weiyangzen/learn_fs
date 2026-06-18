# sources/distributed-fs/ceph-client/drivers/mtd/maps/scb2_flash.c

Purpose: PCI-attached BIOS flash map for Intel SCB2 boards using a ServerWorks CSB5 bridge. It enables southbridge decoding of a 1 MiB ROM window, probes CFI flash, and rewrites MTD geometry to model unusual x16 wiring exposed as byte-linear x8 access.

Important APIs/types/functions: `scb2_flash_probe()`, `scb2_flash_remove()`, `scb2_fixup_mtd()`, `scb2_map`, `scb2_mtd`, `scb2_flash_pci_ids`. It depends on PCI config register `CSB5_FCR`, `request_mem_region()`, `ioremap()`, `simple_map_init()`, `do_map_probe("cfi_probe")`, CFI private data, `mtd_device_register()`, and lock/unlock helpers.

Control flow: PCI probe enables decode, attempts to reserve the ROM region but continues if BIOS/e820 already reserved it, maps the window, probes CFI, validates x16 async interface, shrinks logical size to the map, halves erase sizes, trims erase regions to the visible high-address window, then registers the MTD. Remove locks the whole flash, unregisters, destroys, unmaps, and releases the region when it was reserved.

State and persistence: flash contents persist; driver state is one global map, MTD pointer, mapping pointer, and `region_fail` flag. The southbridge decode bit remains changed while loaded.

Risks and test signals: geometry surgery is fragile and assumes a specific wiring and CFI layout. The probe path calls `mtd_device_unregister()` before registration if fixup fails. Tests should cover CFI interface rejection, oversized chips, erase-region trimming, reserved-region continuation, and remove-time lock behavior.
