# sources/distributed-fs/ceph-client/drivers/scsi/zorro7xx.c

Purpose: Amiga Zorro bus front-end for NCR53C710-based SCSI controllers such as WarpEngine, A4091, PowerUP, and GForce boards. It configures board offsets and delegates command handling to the `53c700` core.

Important APIs and functions: the Zorro ID table maps products to `zorro_driver_data`. `zorro7xx_init_one` reserves the Zorro device, allocates `NCR_700_Host_Parameters`, maps the controller address using either `ioremap` or `ZTWO_VADDR`, configures clock/chip flags and CTEST settings, calls `NCR_700_detect`, requests the Amiga ports IRQ, stores drvdata, and scans the host. `zorro7xx_remove_one` reverses these allocations and releases the common core.

Control flow: Zorro probe selects absolute or board-relative IO address, initializes host parameters, then SCSI processing moves to `NCR_700_intr` and the 53c700 host template. Removal stops the SCSI host before freeing shared IRQ and board reservation.

State and dependencies: state lives in `Scsi_Host`, NCR hostdata, and Zorro drvdata. Dependencies include Amiga Zorro resources, Amiga interrupt constants, SCSI SPI transport, and `53c700`. Risks are product-specific offsets, mixed Zorro II/absolute address handling, shared IRQ behavior, and cleanup ordering. Test signals are board detection by Zorro ID, successful region reservation, target scan, interrupt-driven transfers, and unload without stale IRQ or mapping references.
