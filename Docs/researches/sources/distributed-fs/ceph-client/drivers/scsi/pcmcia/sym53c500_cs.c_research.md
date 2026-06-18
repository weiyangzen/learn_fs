# sources/distributed-fs/ceph-client/drivers/scsi/pcmcia/sym53c500_cs.c

Purpose: standalone PCMCIA driver for Symbios Logic 53C500 SCSI cards. It performs chip init/reset, PIO data transfer, interrupt-driven phase handling, SCSI queueing, BIOS geometry, sysfs `fast_pio`, and PCMCIA lifecycle.

Important APIs/functions: `chip_init()` and `SYM53C500_int_host_reset()` program/reset the chip. `SYM53C500_pio_read()`/`pio_write()` move SG data through the FIFO. `SYM53C500_intr()` handles errors, disconnect, and SCSI data/status/message phases. `SYM53C500_queue()`, `SYM53C500_host_reset()`, `SYM53C500_biosparm()`, `SYM53C500_info()`, and `fast_pio` show/store methods back the SCSI template. PCMCIA flow is in probe/config/release/detach/resume.

Control flow/state: probe configures I/O/IRQ, applies quirks, initializes chip, allocates host, requests IRQ, adds/scans. Queue writes destination and CDB then selects. ISR completes on disconnect/error after capturing status/message. `sym53c500_data` stores `current_SC` and `fast_pio`; per-command private state stores status, message, and phase.

Dependencies/integration: PCMCIA, SCSI midlayer, I/O port primitives, shared IRQ, and shost sysfs attribute groups.

Risks/test signals: no explicit queue busy guard, ISR dereferences `current_SC` before NULL check, limited disconnect/save-pointer handling, and fragile failed-config release paths. Test probe/scan, fast/slow PIO, sysfs validation, host reset, BIOS geometry, error paths, command completion, and removal.
