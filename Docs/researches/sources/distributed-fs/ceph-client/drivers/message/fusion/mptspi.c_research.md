# sources/distributed-fs/ceph-client/drivers/message/fusion/mptspi.c

Purpose: Fusion MPT SPI SCSI host driver for LSI/ATTO 53C1030/53C1035 PCI adapters. It binds the common Fusion MPT core to the Linux SCSI mid-layer and the SPI transport class, manages target negotiation, domain validation, RAID virtual/physical channels, reset recovery, and event-driven rescans.

Important APIs, types, and functions: `mptspi_driver_template` supplies the `Scsi_Host` callbacks; `mptspi_transport_functions` exposes SPI transport attributes; `mptspi_probe()` attaches the MPT IOC, allocates `Scsi_Host`, initializes lookup state, and starts `scsi_scan_host()`. Target/device state is carried in `VirtTarget`, `VirtDevice`, `MPT_SCSI_HOST`, and `MPT_ADAPTER`. Negotiation and config-page code centers on `mptspi_setTargetNegoParms()`, `mptspi_read_spi_device_pg0()`, `mptspi_write_spi_device_pg1()`, `mptspi_getRP()`, and setters such as `mptspi_write_period()`, `mptspi_write_width()`, `mptspi_write_qas()`.

Control flow: module init attaches the SPI transport, registers MPT completion/event/reset callbacks, then registers the PCI driver. Probe calls `mpt_attach()`, validates operational initiator-capable firmware, allocates the host, sets queue/SG limits, optionally enables the SPI transport, issues a bus reset if firmware requested it, and scans. SCSI target allocation establishes RAID-component mapping and initial SPI limits. Device configure initializes inquiry-based negotiation and runs DV unless an initial DV already occurred. I/O is delegated to `mptscsih_qcmd()` after local validity checks.

State and persistence: negotiation state lives in target SPI transport attributes and `VirtTarget` flags; firmware config pages persist requested/negotiated parameters. `ioc->spi_data` holds NVRAM, bus width, sync factors, IOC page data, SAF-TE policy, and global QAS disable. Workqueue wrappers asynchronously run RAID DV/rescan and reset renegotiation.

Dependencies and integration: depends on Fusion MPT core/scsih helpers, PCI, DMA coherent memory, SCSI mid-layer, SPI transport, RAID class, and firmware config/RAID action messages. It integrates with MPT event/reset dispatch and SCSI sysfs transport attributes.

Risks: config-page DMA sizes rely on firmware-provided page lengths; RAID quiesce timeout can hard-reset the IOC; target/channel remapping must stay consistent for RAID passthrough; global QAS disable for mixed targets affects all devices; asynchronous DV work races need valid host/target lifetime; `mptspi_read_parameters()` ignores read errors before decoding the stack struct.

Test signals: build with Fusion MPT SPI enabled, bind supported PCI IDs, verify host scan and `scsi_transport_spi` attributes, exercise tagged/wide/sync/DV negotiation, RAID volume and physical-disk channel behavior, integrated RAID domain-validation events, suspend/resume renegotiation, IOC reset recovery, and module unload cleanup.
