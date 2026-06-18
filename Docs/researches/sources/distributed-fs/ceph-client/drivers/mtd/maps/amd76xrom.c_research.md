<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/amd76xrom.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/maps/amd76xrom.c

Purpose: exposes BIOS flash behind AMD76x/AMD8111 southbridge ROM windows as MTD devices, allowing firmware image access through CFI/JEDEC probes.

Important APIs, types, and functions: `struct amd76xrom_window` tracks the global ROM window, PCI device, resource, ioremap, and discovered maps. `struct amd76xrom_map_info` wraps each found MTD. `amd76xrom_init_one()`, `amd76xrom_cleanup()`, `init_amd76xrom()`, and `cleanup_amd76xrom()` are the main paths. Module parameter `win_size_bits` can widen the BIOS-configured window.

Control flow: init scans a static PCI ID table, adjusts PCI config register `0x43` window-size bits, derives top-of-address-space window start, reserves and ioremaps it, enables writes via register `0x40`, and probes every 64 KiB from at most the last 4 MiB with supported bank widths and `cfi_probe`/`jedec_probe`. Found chips have CFI chip starts offset to the full window and are registered as MTDs.

State and persistence: runtime state is the singleton window and per-chip list. Hardware state includes PCI ROM window size and write-enable bit, which cleanup disables.

Dependencies and integration points: uses PCI config access, `iomem_resource`, `simple_map_init()`, CFI/JEDEC map probes, and MTD registration.

Risks: write-enabling BIOS flash is inherently dangerous. The driver bypasses normal `pci_driver` registration and uses the first matching device. Probing can touch firmware-hub lock registers, so it avoids lower regions. Test signals are correct window sizing, probe discovery, resource reservation behavior when BIOS reserved ranges exist, cleanup disabling writes, and no probing below the guarded address.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/amd76xrom.c -->
