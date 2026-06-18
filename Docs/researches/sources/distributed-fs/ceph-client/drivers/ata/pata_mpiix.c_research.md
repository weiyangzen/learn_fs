# sources/distributed-fs/ceph-client/drivers/ata/pata_mpiix.c

`pata_mpiix.c` supports Intel 82371MX MPIIX, a bridge-style controller whose ATA timings are PCI-configured while command/control ports are legacy ISA addresses. It avoids normal PCI IDE BAR plumbing and keeps MPIIX-specific legacy behavior out of generic libata.

The central config register is `IDETIM` at `0x6c`. `mpiix_pre_reset()` checks the enabled bit before SFF reset. `mpiix_set_piomode()` computes ICH-like PIO timing bits, sets PPE for ATA disks, IORDY when needed, and FTIM for faster PIO modes, then writes `IDETIM`. Because hardware effectively times one device at a time, it caches the currently programmed device in `ap->private_data`. `mpiix_qc_issue()` reloads timings before issuing a command to a different device.

Probe allocates a one-port host, reads `IDETIM`, rejects disabled IDE, chooses primary `0x1f0/0x3f6/14` or secondary `0x170/0x376/15`, maps those I/O ports, fills SFF addresses, and activates with a shared IRQ. It intentionally avoids normal PCI disable assumptions because MPIIX has other bridge functions.

State is `IDETIM` plus `ap->private_data`. Dependencies are PCI config access, legacy I/O mapping, and libata SFF. Risks include master/slave timing switching, primary/secondary address choice, PM on multifunction hardware, and ThinkPad/PCMCIA decoded secondary cases. Tests should cover enabled/disabled `IDETIM`, both mappings, master/slave PIO changes, IORDY/PPE bits, shared IRQ, and resume.
