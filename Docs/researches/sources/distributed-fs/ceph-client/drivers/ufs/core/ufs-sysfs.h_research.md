# sources/distributed-fs/ceph-client/drivers/ufs/core/ufs-sysfs.h

## Purpose

This header declares host-level and LUN-level UFS sysfs group integration.

## Important APIs, Types, and Functions

It declares `ufs_sysfs_add_nodes()`, `ufs_sysfs_remove_nodes()`, and extern attribute groups `ufs_sysfs_unit_descriptor_group` and `ufs_sysfs_lun_attributes_group`.

## Control Flow

No runtime control flow exists in the header. Host code calls add/remove for controller groups, and SCSI device setup can attach exported LUN groups.

## State and Persistence Behavior

The header owns no state. It exposes sysfs ABI registration points.

## Dependencies and Integration Points

It depends on `linux/sysfs.h` and a forward declaration of `struct device`.

## Risks and Test Signals

Risks are declaration/definition drift and missing extern groups in configurations that build UFS core. Test signals are host sysfs and SCSI LUN sysfs group compilation and runtime registration.
