# sources/distributed-fs/ceph-client/drivers/ata/pata_isapnp.c

`pata_isapnp.c` is a small ISA Plug-and-Play PATA driver for generic `PNP0600` IDE controllers. It maps the PnP command port and optional control/altstatus port, then registers a single PIO0 libata SFF host.

The driver defines normal `isapnp_port_ops` and `isapnp_noalt_port_ops`. The no-alt variant disables `.lost_interrupt` because libata's lost-interrupt polling cannot safely run without an alternate-status register. `isapnp_init_one()` validates PnP port 0, optionally takes IRQ 0 and `ata_sff_interrupt`, allocates a one-port host, maps the command region, maps optional control port 1, fills SFF addresses, reports port addresses, and activates the host. `isapnp_remove_one()` detaches the host.

There is no private state beyond devm-managed I/O mappings and the libata host. Dependencies are ISA PnP, libata SFF/PIO, and SCSI host glue through `ATA_PIO_SHT()`. The driver assumes `ATA_PIO0`, 40-wire cable, and possible slave devices.

Risks are mostly resource-shape issues: no IRQ, no altstatus, malformed PnP ports, or hardware that can run faster than PIO0 but is intentionally limited. Tests should cover devices with and without control ports, with and without IRQ, map failures, no-alt lost-interrupt behavior, identify/read in PIO0, and module unload detach.
