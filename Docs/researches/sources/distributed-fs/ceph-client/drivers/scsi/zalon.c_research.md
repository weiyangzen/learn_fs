# sources/distributed-fs/ceph-client/drivers/scsi/zalon.c

Purpose: PA-RISC GSC bus front-end for Bluefish/Zalon 720 NCR53c7xx SCSI hardware. It initializes Zalon-specific registers and hands the controller to the shared `ncr53c8xx` SCSI core.

Important APIs and functions: `zalon_probe` maps the HPA window, resets the module, enables interrupt/pre-fetch/packing bits, allocates a GSC IRQ, seeds a `struct ncr_device`, calls `ncr_attach`, requests the shared interrupt, adds and scans the SCSI host. `zalon_remove` removes the host, releases the NCR core, and frees IRQ. `zalon7xx_init/exit` pair `ncr53c8xx_init/exit` with PA-RISC driver registration.

Control flow: module init initializes the common NCR core then registers a PA-RISC driver for matching firmware IDs. Probe performs platform register setup before the common core takes over normal SCSI command processing and interrupt handling.

State and dependencies: state is mostly in the shared NCR core and SCSI host; local state is MMIO mapping, device IRQ, and static unit number. Dependencies include PA-RISC GSC/PDC hardware interfaces, raw MMIO, `ncr53c8xx`, and SCSI midlayer. Risks include missing `iounmap` on probe failure/removal in this legacy code path, interrupt setup ordering, old hardware revision quirks, and assumptions about differential mode and host ID. Test signals are boot-time Zalon version logs, IRQ allocation, `scsi_scan_host` discovering targets, interrupt-driven I/O, and clean module removal on PA-RISC hardware or emulation.
