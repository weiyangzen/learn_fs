# sources/distributed-fs/ceph-client/drivers/ata/pata_it8213.c

`pata_it8213.c` supports the ITE IT8213 PATA controller, an ICH/PIIX-like PCI BMDMA controller with different cable detection and a single real port. It programs PIO, MWDMA, and UDMA timings in PCI config space and filters disabled ports during reset.

`it8213_pre_reset()` checks enable bit `0x41[7]`. `it8213_cable_detect()` reads config byte `0x42` and treats bit 1 as 40-wire. `it8213_set_piomode()` uses ICH-style ISP/RTC timing tables and sets PPE/IE/TIME/SITRE bits in config word `0x40` plus slave timing in `0x44`. `it8213_set_dmamode()` enables UDMA in `0x48`, writes UDMA timing in `0x4a`, selects 33/66/100 MHz clocks in `0x54`, or derives MWDMA timing from compatible PIO timing and clears UDMA enable.

Probe prints the version and delegates to `ata_pci_bmdma_init_one()` with one real port and one dummy port. The port info advertises PIO4, MWDMA1/2 only, UDMA6, and slave possible. PM uses generic libata PCI suspend/resume.

State is entirely in PCI config registers. Dependencies are PCI config access and libata BMDMA/SFF helpers. Risks include master/slave timing interactions, clock selection for high UDMA modes, cable-detect polarity, and MWDMA's DMA-only timing fallback. Tests should cover reset enable filtering, cable detection, PIO and DMA modes for master/slave, ATAPI PPE behavior, and one-real-port enumeration.
