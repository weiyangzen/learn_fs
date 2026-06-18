# sources/distributed-fs/ceph-client/arch/mips/sgi-ip32/crime.c

Purpose: initializes CRIME and MACE register mappings for SGI O2 and handles CRIME memory/CPU error interrupts.

Important APIs and control flow: `crime_init()` maps the MACE PCI low I/O window, CRIME registers, and MACE registers, reads CRIME ID/revision, and logs it. `crime_memerr_intr()` decodes memory error status/address, ECC syndrome/check bits, fatal multiple/hard errors, access source fields, clears status, and panics on fatal errors. `crime_cpuerr_intr()` logs and clears CPU error status/address.

State, persistence, and integration: state includes global `crime` and exported `mace` MMIO pointers. Dependencies include fixed CRIME/MACE physical addresses, IP32 memory init calling `crime_init()`, and IRQ code requesting error IRQs. Risks include assuming `ioremap()` succeeds, panic on fatal memory errors, and direct MMIO clearing. Test signals are CRIME ID log, MACE-backed device operation, and error IRQ diagnostics.
