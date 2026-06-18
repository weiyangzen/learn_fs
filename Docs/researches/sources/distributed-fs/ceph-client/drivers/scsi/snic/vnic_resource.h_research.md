## sources/distributed-fs/ceph-client/drivers/scsi/snic/vnic_resource.h

### Purpose
Defines the vNIC PCI resource table ABI used by SNIC and related Cisco virtual NIC drivers to discover hardware regions inside PCI BARs. It provides the magic/version header and resource-type enumeration consumed by `vnic_dev` discovery code.

### Important APIs, Types, and Constants
- `VNIC_RES_MAGIC` is the ASCII `vnic` signature and `VNIC_RES_VERSION` is the resource table version.
- `enum vnic_res_type` names BAR-backed resources such as work queues, receive queues, completion queues, NIC config, interrupt control/table/PBA regions, device command regions, pass-through pages, subvnic resources, multiqueue resources, and `RES_TYPE_DEVCMD2`.
- `struct vnic_resource_header` stores resource table `magic` and `version`.
- `struct vnic_resource` stores `type`, `bar`, `bar_offset`, and `count`, which lets callers map an indexed resource of a given type.

### Control Flow and State
This header has no executable control flow. Runtime state is in the device resource table exposed by firmware. Consumers scan entries until `RES_TYPE_EOL`, validate the header, and use `bar` plus `bar_offset` to derive MMIO addresses.

### Dependencies and Integration Points
The definitions are used by `vnic_dev` helpers such as resource lookup and by SNIC queue/interrupt allocation paths. `vnic_wq.c` asks `svnic_dev_get_res()` for `RES_TYPE_WQ` or `RES_TYPE_DEVCMD2`, and interrupt code asks for `RES_TYPE_INTR_CTRL`.

### Risks and Test Signals
Because this is a hardware contract, enum renumbering or structure packing changes would break probing. Tests should cover device probe on real or emulated SNIC hardware, resource count validation, and failure paths when required WQ, CQ, INTR, or DEVCMD2 resources are absent.
