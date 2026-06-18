<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/ck804xrom.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/maps/ck804xrom.c

Purpose: maps BIOS ROM windows on NVIDIA CK804 and MCP55 southbridges as MTD flash devices.

Important APIs, types, and functions: `struct ck804xrom_window`, `struct ck804xrom_map_info`, `ck804xrom_init_one()`, `ck804xrom_cleanup()`, `init_ck804xrom()`, and `cleanup_ck804xrom()` implement discovery. Module parameter `win_size_bits` overrides BIOS window-size bits; device IDs distinguish `DEV_CK804` and `DEV_MCP55`.

Control flow: init scans PCI IDs, takes a device reference, programs CK804 register `0x88` or MCP55 registers `0x88/0x8c/0x90`, computes the ROM window, reserves/ioremaps it, enables writes through register `0x6d`, then scans every 64 KiB with bank widths down from 32 and `cfi_probe`/`jedec_probe`. Found MTDs are registered and tracked on a list.

State and persistence: runtime state is singleton window state plus per-map resources. Hardware state includes ROM decode windows and write-enable bit, disabled during cleanup.

Dependencies and integration points: PCI, IO resource reservation, MTD map probes, CFI private chip-start adjustment, and MTD device registration.

Risks: BIOS flashing danger, chipset-specific register assumptions, and disabled normal `pci_driver` path. Resource reservation failures are logged but may not stop probing. Test signals are matching CK804/MCP55 IDs, correct 4/5/16 MiB window handling, successful MTD registration, and cleanup unmapping and disabling writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/ck804xrom.c -->
