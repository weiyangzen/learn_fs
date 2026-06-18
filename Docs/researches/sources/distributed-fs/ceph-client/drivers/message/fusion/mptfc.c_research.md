# sources/distributed-fs/ceph-client/drivers/message/fusion/mptfc.c

## Purpose
`mptfc.c` is the Fibre Channel SCSI host driver for LSI Fusion MPT FC adapters. It binds supported FC PCI IDs, attaches the common MPT base, registers a SCSI host and FC transport, discovers remote FC ports through firmware config pages, maps them to SCSI targets/LUNs, and routes I/O and error recovery through the common `mptscsih` layer.

## Important APIs, Types, and Functions
The main kernel contracts are `mptfc_driver_template`, `mptfc_pci_table`, `mptfc_transport_functions`, and `mptfc_driver`. Module parameters are `mptfc_dev_loss_tmo` and `max_lun`. Key functions include `mptfc_probe()`, `mptfc_remove()`, `mptfc_init()`, `mptfc_exit()`, `mptfc_qcmd()`, `mptfc_target_alloc()`, `mptfc_target_destroy()`, `mptfc_sdev_init()`, `mptfc_abort()`, `mptfc_dev_reset()`, `mptfc_bus_reset()`, `mptfc_event_process()`, `mptfc_ioc_reset()`, `mptfc_GetFcPortPage0()`, `mptfc_GetFcDevPage0()`, `mptfc_register_dev()`, `mptfc_rescan_devices()`, and `mptfc_setup_reset()`.

## Control Flow
Module init attaches FC transport, registers three base callbacks for I/O completion, task management, and internal scan/DV commands, installs event and reset handlers, and registers the PCI driver. Probe calls `mpt_attach()`, verifies the IOC is operational and initiator-capable, allocates a `Scsi_Host`, sets queue and SGE limits, creates `ScsiLookup`, adds the host, builds a workqueue, fetches FC port pages, applies Page1 defaults, and performs an initial rport rescan. SCSI commands validate rport readiness and then delegate to `mptscsih_qcmd()`. Firmware rescan events queue work that refreshes port attributes, walks FC Device Page0 entries, registers or updates remote ports, and deletes ports still marked missing.

## State and Persistence
Persistent state is per IOC: `ioc->sh`, `ScsiLookup`, `fc_rports`, `fc_port_page0`, cached/dma-backed FC Port Page1 data, link-speed cache, FC work structs, and the ordered rescan workqueue. Per SCSI target state is `VirtTarget`; per LUN state is `VirtDevice`. Remote-port information is mirrored in `struct mptfc_rport_info`. State is rebuilt from firmware config pages after probe and reset, and is not stored outside memory.

## Dependencies and Integration Points
The driver integrates with PCI, SCSI mid-layer, FC transport class, workqueues, sorting, DMA config-page reads, and the common `mptscsih` SCSI implementation. It consumes MPI FC Port and FC Device config pages through `mpt_config()`, uses base reset/event callbacks, and exposes host/rport attributes through `scsi_transport_fc`.

## Risks and Edge Cases
Discovery relies on repeated config-page polling and can wait up to roughly 40 seconds for firmware discovery to settle. The code assumes only port 0 populates the single allocated SCSI host attributes. Reset and rescan work manipulate rport registration state asynchronously, so stale `starget`/`vtarget` mappings must be guarded. Error handlers first block on FC rport readiness; if the IOC remains inactive, recovery fails. Queue-depth and SGE calculations must match IOC chain-depth facts or DMA request construction can overrun hardware limits.

## Test Signals
Useful validation includes FC PCI probe/remove, SCSI host registration, initial rport discovery from synthetic FC Device Page0 data, rport deletion/re-addition on rescan events, link status change handling, IOC reset setup/post paths, queuecommand rejection for missing rports, and SCSI error-handler flows for abort, device reset, and bus reset.
