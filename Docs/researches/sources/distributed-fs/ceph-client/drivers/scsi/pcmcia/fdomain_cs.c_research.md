# sources/distributed-fs/ceph-client/drivers/scsi/pcmcia/fdomain_cs.c

Purpose: PCMCIA wrapper for Future Domain-compatible SCSI cards.

Important APIs/functions: `fdomain_config_check()` requests a 10-line auto-width I/O resource sized to `FDOMAIN_REGION_SIZE`. `fdomain_probe()` configures/enables the PCMCIA device, claims the I/O region, calls `fdomain_create(base, irq, 7, &link->dev)`, and stores the host. `fdomain_remove()` destroys the host, releases the region, and disables the card.

Control flow/state: direct probe-to-host creation with `link->priv` storing the `Scsi_Host`. Host ID is fixed at 7. No module parameters or persistent settings.

Dependencies/integration: PCMCIA APIs, SCSI host layer, and shared Future Domain core from `fdomain.h`.

Risks/test signals: resource acquisition must balance PCMCIA I/O and `request_region()`. Test product IDs, I/O conflict path, successful `fdomain_create()`, remove cleanup, and probe failure cleanup.
