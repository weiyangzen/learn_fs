<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/esb2rom.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/maps/esb2rom.c

Purpose: maps firmware hub BIOS flash behind Intel ESB/ESB2-style southbridge decode windows as MTD devices.

Important APIs, types, and functions: `struct esb2rom_window`, `struct esb2rom_map_info`, `esb2rom_init_one()`, `esb2rom_cleanup()`, `init_esb2rom()`, and `cleanup_esb2rom()`. Register constants cover `BIOS_CNTL`, `FWH_DEC_EN1`, and decode masks from 0.5 MiB to 8 MiB.

Control flow: init scans PCI IDs, reads decode enable bits to find the continuous ROM window, expands the mapping 4 MiB lower to include firmware-hub lock/control areas, refuses to enable writes if BIOS lock is active, sets BIOS write enable, reserves/ioremaps the window, limits probing to the top 4 MiB where necessary, scans 64 KiB steps with bank widths and `cfi_probe`/`jedec_probe`, adjusts CFI chip offsets, and registers discovered MTDs.

State and persistence: runtime state is the singleton window and map list. Hardware state includes BIOS write enable; cleanup clears it and releases resources.

Dependencies and integration points: PCI config access, CFI/JEDEC probes, MTD registration, IO resource reservation, and top-of-memory firmware hub layout.

Risks: write enabling firmware is risky and blocked when firmware access control indicates lock. Probe logic assumes top-address firmware hub layout and no paging support. Test signals are decode-mask interpretation, locked BIOS refusal, successful window ioremap, discovered flash sizes, and cleanup disabling writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/esb2rom.c -->
