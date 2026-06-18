# sources/distributed-fs/ceph-client/include/linux/ata_platform.h

## Purpose
Declares platform data and probe helper contracts for platform PATA/SATA drivers.

## Important APIs, Types, And Functions
`struct pata_platform_info` contains `ioport_shift` for nonstandard register spacing. `__pata_platform_probe()` accepts device, I/O/control/IRQ resources, ioport shift, PIO mask, SCSI host template, and 16-bit access flag. `struct mv_sata_platform_data` carries a Marvell SATA port count.

## Control Flow, State, And Persistence
The header does not implement control flow. Probe implementations use the declared helper to map resources, initialize libata host structures, and register ports. Platform data persists for device lifetime.

## Dependencies And Integration Points
Uses forward declarations for `struct device`, `struct resource`, and `struct scsi_host_template` from included contexts. Integrates platform bus resources, PATA platform driver, Marvell SATA platform data, libata, and SCSI host registration.

## Risks And Test Signals
Incorrect resource ordering or `ioport_shift` causes register misaddressing. Tests should cover platform probe with shifted I/O ports, IRQ absence/error paths, 16-bit access devices, PIO mask enforcement, and Marvell port-count handling.
