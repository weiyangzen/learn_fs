# sources/distributed-fs/ceph-client/drivers/scsi/mvme16x_scsi.c

Purpose: implements the NCR53C710 SCSI driver for Motorola MVME16x m68k boards using the generic `53c700` core behind a simple platform device/driver wrapper.

Important APIs/types/functions: `mvme16x_scsi_init()` registers the platform driver and synthetic platform device. `mvme16x_probe()` validates board presence/configuration, allocates `NCR_700_Host_Parameters`, fills chip register base and mode flags, calls `NCR_700_detect()`, requests `MVME16x_IRQ_SCSI`, enables PCCchip2 interrupt routing, and scans. `mvme16x_device_remove()` disables interrupts, removes and releases the host, frees hostdata, and releases the IRQ.

Control flow: init first registers the driver, then creates a `mvme16x-scsi` platform device so probe can run even without firmware enumeration. Probe returns `-ENODEV` for non-MVME16x systems or boards configured without a SCSI chip. On success, SCSI scanning begins after IRQ enable. Exit unregisters the device then the driver.

State and persistence: global state is limited to `mvme16x_scsi_device`; per-host state is allocated `NCR_700_Host_Parameters` and the Scsi_Host. No persistent settings are written, though PCCchip2 interrupt-enable bits are modified at probe/remove.

Dependencies and integration points: depends on m68k `asm/mvme16xhw.h`, platform bus, SCSI SPI transport headers, and the generic `53c700` core. The parent SCSI Makefile links `53c700.o` and `mvme16x_scsi.o` for `CONFIG_MVME16x_SCSI`.

Risks and test signals: fixed addresses and board-specific interrupt register writes make hardware testing essential. `NCR_700_release()`/hostdata ownership should be checked carefully because probe error paths and remove free different pieces. Test signals include m68k cross-builds, probing with `MVME16x_CONFIG_NO_SCSICHIP`, IRQ request failure, scan success, and remove/reload cleanup.
