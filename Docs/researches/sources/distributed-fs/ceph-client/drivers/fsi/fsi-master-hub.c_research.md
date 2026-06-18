<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fsi/fsi-master-hub.c -->
# sources/distributed-fs/ceph-client/drivers/fsi/fsi-master-hub.c

## Purpose
`fsi-master-hub.c` implements a cascaded FSI hub master discovered as an FSI engine. The hub exposes downstream links through an address window on an upstream FSI slave and registers a new `struct fsi_master` for those downstream links.

## Important APIs, types, and functions
`struct fsi_master_hub` embeds `struct fsi_master`, stores the upstream `fsi_device`, and records the slave-relative link-window address and size. Master callbacks are `hub_master_read()`, `hub_master_write()`, `hub_master_break()`, and `hub_master_link_enable()`. `hub_master_init()` programs hub master registers, and `hub_master_probe()`/`hub_master_remove()` bind through an FSI driver for engine type `0x1c`.

## Control flow
Probe reads `FSI_MVER` from the upstream device to determine link count, claims the downstream address range starting at `FSI_HUB_LINK_OFFSET`, allocates hub state, initializes common hub registers, registers a new FSI master, and takes an extra device reference. Downstream reads/writes reject nonzero slave IDs, translate link-local addresses to `hub->addr + link * FSI_HUB_LINK_SIZE + addr`, and call `fsi_slave_read/write()` on the upstream slave. Link enable writes `MSENP0` or `MCENP0`; break writes the magic break word through the translated write path.

## State and persistence behavior
The hub stores upstream device and address-window metadata plus the registered master object. Hardware state is in hub master registers and link enable masks. There is no persistence beyond runtime device state.

## Dependencies and integration points
It depends on the FSI core's client and master APIs, common master register constants from `fsi-master.h`, CRC/error behavior in the core, and FSI engine discovery. It bridges upstream FSI access into a nested master scan.

## Risks and edge cases
Only slave ID zero is supported on downstream links. `fsi_slave_claim_range()` does not enforce overlap today, weakening protection against conflicting clients. Initialization errors after allocation must release the claimed range. Link count from hardware controls the reserved address size, so malformed `MVER` can cause incorrect range assumptions.

## Test signals
Engine discovery for type `0x1c`, hub version/link count read, downstream master scan, translated read/write correctness per link, link enable/disable writes, break handling, and remove cleanup of range and master references are core signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fsi/fsi-master-hub.c -->
