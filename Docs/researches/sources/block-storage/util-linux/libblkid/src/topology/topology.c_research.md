# File Research: sources/block-storage/util-linux/libblkid/src/topology/topology.c

## Scope

Implements the libblkid topology probing chain, binary topology object, public topology APIs, and result setters/getters.

## Behavior

- Registers Linux topology probers in order: sysfs, ioctl, md, dm, lvm, evms.
- `topology_probe()` only works on block devices, resets binary/tag state, runs drivers until minimum I/O size is available, then adds logical sector size.
- Supports both NAME=value output and binary `blkid_topology` data.
- Setter helpers suppress zero values and write either probe values or struct fields.
- Public getters expose alignment offset, minimum/optimal I/O size, logical/physical sector size, DAX, and disk sequence.

## Dependencies And Risks

- Completeness is defined by `MINIMUM_IO_SIZE`; drivers that cannot provide it are skipped.
- Kernel `-1` alignment offset is hidden as zero.
- Binary topology data is overwritten on the next topology retrieval for the same probe.
