# sources/distributed-fs/ceph-client/drivers/scsi/lasi700.c

Purpose: PARISC LASI front-end for NCR 53c700/53c710 SCSI chips, configuring chip parameters and registering the generic `53c700` SCSI core as a PARISC driver.

Important APIs and functions: `lasi700_probe()` allocates `NCR_700_Host_Parameters`, maps LASI SCSI registers, selects clock/endian/chip710/burst parameters based on `sversion`, calls `NCR_700_detect()`, requests IRQ, stores driver data, and scans the host. `lasi700_driver_remove()` removes the host, releases the core, IRQ, mapping, and host parameters. `lasi700_init()`/`lasi700_exit()` register and unregister the PARISC driver.

Control flow: matching is by PARISC device IDs for LASI 700 and 710. Probe builds `base = hpa.start + LASI_SCSI_CORE_OFFSET`, sets 32-bit DMA mask, maps 0x100 bytes, and follows standard SCSI host registration. Failure unwinds through `scsi_host_put`, `iounmap`, and `kfree`.

State and persistence: state is in `hostdata`, MMIO mapping, SCSI host fields, and PARISC driver data. No durable state exists.

Dependencies and integration: depends on PARISC firmware/device model, generic 53c700 core, SCSI transport/SPI headers, shared IRQ handling via `NCR_700_intr`, and `scsi_scan_host()`.

Risks and test signals: version-specific parameters must match hardware; endian forcing for LASI700 and burst/DMODE for LASI710 are key. Tests should cover probe/remove on both device IDs, IRQ request failure cleanup, DMA mask behavior, host scanning, and no leaked ioremap/hostdata on detection failure.
