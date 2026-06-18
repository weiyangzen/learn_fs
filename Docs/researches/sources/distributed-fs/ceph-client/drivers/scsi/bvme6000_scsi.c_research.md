<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bvme6000_scsi.c -->
## sources/distributed-fs/ceph-client/drivers/scsi/bvme6000_scsi.c

Purpose: this is a platform wrapper for BVME6000 NCR53C710 SCSI hardware. It wires board-specific physical addresses, IRQs, and NCR53C700 core parameters into the generic `53c700` SCSI driver.

Important APIs, types, and functions: `bvme6000_scsi_driver_template` supplies the SCSI host template name/proc name and target ID. `bvme6000_probe()` allocates `struct NCR_700_Host_Parameters`, populates BVME6000-specific fields, calls `NCR_700_detect()`, requests `BVME_IRQ_SCSI`, sets platform driver data, and scans the host. `bvme6000_device_remove()` reverses that setup. Module init/exit register and unregister both the platform driver and a simple platform device.

Control flow: module init registers `bvme6000_scsi_driver`, then creates a `"bvme6000-scsi"` platform device. Probe exits with `-ENODEV` unless `MACH_IS_BVME6000` is true. On the target machine it allocates host parameters, sets `base`, `clock`, `chip710`, `dmode_extra`, `dcntl_extra`, and `ctest7_extra`, detects the NCR core, sets host base/ID/IRQ, installs `NCR_700_intr`, and runs `scsi_scan_host()`. Remove calls `scsi_remove_host()`, `NCR_700_release()`, frees hostdata, and frees the IRQ.

State and persistence behavior: state is limited to the platform device pointer, the SCSI host, and host-private NCR parameters. There is no persistent storage. Resource ownership is linear: platform device owns the SCSI host and IRQ after successful probe.

Dependencies and integration points: it depends on m68k BVME6000 platform definitions, `53c700.h`, SCSI host/device/transport headers, and Linux platform driver APIs. It is integrated with the generic NCR53C700 core rather than implementing SCSI protocol logic itself.

Risks: the hard-coded `hostdata->clock = 40` comment notes CPU-clock dependence, so timing may be wrong on variants. Error paths must keep hostdata, host refs, and IRQ ownership balanced. Probe returns `-ENODEV` both for wrong machine and several setup failures, which limits diagnostics.

Test signals: validate on BVME6000 hardware or emulation that probe reaches `scsi_scan_host()`, IRQ delivery invokes `NCR_700_intr`, remove unloads cleanly, and wrong-machine builds fail probe without leaking the registered platform device or driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bvme6000_scsi.c -->
