# sources/distributed-fs/ceph-client/drivers/ata/pata_ns87410.c

`pata_ns87410.c` supports the National Semiconductor NS87410 PATA controller. It is a PIO-only PCI SFF driver with per-channel rather than per-device timing, so it reloads timings on command issue when master/slave changes.

`ns87410_pre_reset()` checks enable bits in config bytes `0x43` and `0x47`. `ns87410_set_piomode()` computes PIO timing with `ata_timing_compute()` using a 30.303 ns clock, clamps setup/active/recovery values, maps active/recovery values through encoding tables, writes the timing byte, toggles IORDY, and caches the programmed device in `ap->private_data`. `ns87410_qc_issue()` reloads timing if the queued command targets a different device, then calls `ata_sff_qc_issue()`.

Probe uses `ata_pci_sff_init_one()` with PIO3, slave possible, and custom pre-reset/mode/issue hooks. There is no private allocation; state is PCI timing bytes plus the cached device pointer. Dependencies are PCI config access, libata SFF, and ATA timing helpers.

Risks include timing encoding mistakes, shared master/slave timing, and IORDY polarity. Tests should verify disabled-channel handling, PIO3 cap, timing reload on device switch, master/slave mixed modes, generic PM, and error handling for invalid timing computation.
