# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_resource.h

## Purpose
`vnic_resource.h` defines the Cisco vNIC BAR resource table ABI, including magic/version values, resource type IDs, and resource table/header structures.

## Important APIs, types, and functions
- `VNIC_RES_MAGIC`, `VNIC_RES_VERSION`, `MGMTVNIC_MAGIC`, and `MGMTVNIC_VERSION` identify normal and management vNIC BAR maps.
- `enum vnic_res_type` enumerates WQ/RQ/CQ, interrupt, devcmd, devcmd2, SR-IOV, and admin channel resource types.
- `struct vnic_resource_header`, `struct mgmt_barmap_hdr`, and `struct vnic_resource` define BAR0 resource discovery records.

## Control flow and state
`vnic_dev_discover_res()` consumes these definitions to populate `vdev->res[]`. Queue-like resources use `count` and fixed stride; singleton resources expose the mapped address directly.

## Dependencies and integration points
This header is shared by `vnic_dev.c`, queue allocators, ENIC resource counting, and admin-channel detection.

## Risks and test signals
Resource ID or structure layout errors break device probe. Test signals include successful resource discovery logs, resource count sanity for all queue types, devcmd2 resource detection, and management-vNIC BAR compatibility.
