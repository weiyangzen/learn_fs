<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/ichxrom.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/maps/ichxrom.c

Purpose: maps BIOS firmware hub flash on Intel ICH2/3/4/5-family southbridges as MTD devices.

Important APIs, types, and functions: `struct ichxrom_window`, `struct ichxrom_map_info`, `ichxrom_init_one()`, `ichxrom_cleanup()`, `init_ichxrom()`, and `cleanup_ichxrom()`. Register constants include `BIOS_CNTL`, `FWH_DEC_EN1`, `FWH_DEC_EN2`, `FWH_SEL1`, and `FWH_SEL2`.

Control flow: init scans a PCI ID table, derives the active ROM window from FWH decode registers, subtracts 4 MiB for lock-register reachability, refuses locked BIOS write enable, sets write enable, reserves/ioremaps the window, scans at 64 KiB increments with supported bank widths and `cfi_probe`/`jedec_probe`, adjusts CFI chip starts to the full window, and registers each found MTD.

State and persistence: runtime state is a singleton window and discovered map list. Hardware state includes BIOS write enable, which cleanup clears.

Dependencies and integration points: PCI config space, MTD CFI/JEDEC map probes, `simple_map_init()`, `iomem_resource`, and MTD registration.

Risks: BIOS access is destructive if misused. The code uses manual PCI scanning rather than enabled `pci_driver` registration. Probe avoidance of lower 4 MiB is required because probe cycles can alter FWH lock registers. Test signals are correct decode window computation, lock-bit refusal, MTD registration at expected top-of-memory addresses, and cleanup releasing resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/ichxrom.c -->
