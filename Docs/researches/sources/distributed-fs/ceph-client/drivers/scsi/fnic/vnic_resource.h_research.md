# sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_resource.h

## Purpose

`vnic_resource.h` defines the BAR resource-table format used by Cisco vNIC hardware to advertise queue, interrupt, command, and other resource blocks to the driver.

## Important APIs, types, and data

- `VNIC_RES_MAGIC` and `VNIC_RES_VERSION` identify a valid resource table.
- `enum vnic_res_type` defines WQ, RQ, CQ, NIC config, interrupt control/table/PBA, devcmd, pass-through, subvnic, MQ queues, and devcmd2 resource types.
- `struct vnic_resource_header` is the table header.
- `struct vnic_resource` records type, BAR number, BAR offset, and count.

## Control flow

`vnic_dev_discover_res()` reads this table from BAR0, validates header magic/version, iterates entries until `RES_TYPE_EOL`, and stores recognized BAR0 resources in the vNIC device object.

## State and persistence behavior

The resource table is hardware/firmware-provided MMIO metadata. The header defines layout only.

## Dependencies and integration points

It is consumed by `vnic_dev.c` and all queue/interrupt allocation code that requests resources by type and index.

## Risks and edge cases

- Resource type numbering is firmware ABI and must remain stable.
- The discovery implementation only maps BAR0 resources for most queue types; non-BAR0 resources are ignored.
- Counts and offsets must be bounds-checked before being trusted.

## Test signals

Probe tests should validate correct resource discovery, malformed magic/version rejection, out-of-bounds resource rejection, and devcmd2 presence/absence handling.
