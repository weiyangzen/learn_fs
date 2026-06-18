# sources/distributed-fs/ceph-client/drivers/ata/pata_opti.c

## Purpose
Supports early OPTi 621/621X PCI PATA controllers using indexed controller registers and PIO-only libata operation.

## Important APIs, Types, And Functions
`opti_pre_reset()` checks controller enable bits before generic SFF reset. `opti_write_reg()` performs the OPTi indexed-register access sequence. `opti_set_piomode()` computes PIO timing from `ata_timing_compute()` and writes read/write/control timing fields. `opti_init_one()` registers a single PIO port via `ata_pci_sff_init_one()` style libata infrastructure.

## Control Flow
On probe, the PCI ID table selects OPTi 82C621-class hardware. Reset first checks port enablement. Mode setup derives address/setup/recovery/active timing from the ATA timing table and writes the controller's read, write, strap, control, and miscellaneous timing registers through the indexed configuration window.

## State And Persistence
State persists in PCI/controller timing registers only. The driver does not allocate private state and has no runtime cache beyond libata's device mode fields.

## Dependencies And Integration Points
Depends on PCI config access, libata SFF PIO operations, `ata_timing_compute()`, and generic PCI driver registration.

## Risks And Edge Cases
The hardware programming sequence is register-index sensitive and old-chip documentation is sparse. Unsupported variants may have incompatible strap/control behavior. Since the driver is PIO-only, DMA-capable later OPTi chips belong in `pata_optidma.c`.

## Test Signals
Probe/reset on both ports, PIO0-4 mode programming, IORDY-needed devices, disabled-port detection, and comparison with legacy IDE timing behavior on real OPTi hardware or emulation.
