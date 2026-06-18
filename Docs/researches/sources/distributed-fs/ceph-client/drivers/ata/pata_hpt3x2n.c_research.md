# sources/distributed-fs/ceph-client/drivers/ata/pata_hpt3x2n.c

`pata_hpt3x2n.c` supports HighPoint HPT371N, HPT372N, and HPT302N controllers. These N-series chips differ from the older HPT37x path because they use a fixed 66 MHz DPLL timing table and dynamically switch clock sources around queued commands. The driver exposes the hardware as a libata PCI BMDMA controller.

The key timing table is `hpt3x2n_clocks[]`; `hpt3x2n_find_mode()` and `hpt3x2n_set_mode()` resolve transfer modes and update PCI timing registers. `hpt372n_filter()` removes UDMA1-3 and all MWDMA for SATA identify data behind Marvell bridges. `hpt3x2n_set_clock()` tristates the bus, switches between DPLL and PCI clock sources, resets state machines, and reconnects channels. `hpt3x2n_qc_defer()` prevents a clock switch while the sibling port has active commands, and `hpt3x2n_qc_issue()` performs the switch before generic BMDMA issue.

`hpt3x2n_init_one()` enables PCI, rejects non-N revisions, maps IDs/revisions to generic N-series or HPT372N port ops, configures PCI registers, disables the phantom HPT371 primary channel, computes PCI clock, programs/calibrates a 66 MHz DPLL, records `USE_DPLL`/`PCI66` flags in `host->private_data`, and calls `ata_pci_bmdma_init_one()`.

Persistent state is compact: clock flags in `host->private_data`, timing registers in PCI config space, and global timing tables. Dependencies are PCI, libata BMDMA/SFF, and low-level I/O. Risks center on two-port concurrency during clock transitions, DPLL calibration failure, single-channel HPT371 masking, and SATA bridge mode filtering. Tests should stress paired-port reads/writes with alternating DPLL needs, 66 MHz PCI detection, DPLL failure, cable detection, reset filtering, and DMA stop cleanup.
