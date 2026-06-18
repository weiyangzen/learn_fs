# sources/distributed-fs/ceph-client/include/uapi/scsi/scsi_netlink.h

## Purpose
`scsi_netlink.h` defines the generic SCSI transport netlink event ABI. It provides the common message type, broadcast group, message header, vendor-host message layout, vendor ID encoding, alignment helper, and initializer macro used by SCSI transport event producers and consumers.

## Important APIs, Types, and Constants
`SCSI_TRANSPORT_MSG` is the netlink message type. `SCSI_NL_GRP_FC_EVENTS` identifies the FC transport event broadcast group. `struct scsi_nl_hdr` is the aligned common header with version, transport, magic, message type, and message length. Version/magic/transport constants include `SCSI_NL_VERSION`, `SCSI_NL_MAGIC`, `SCSI_NL_TRANSPORT`, `SCSI_NL_TRANSPORT_FC`, and `SCSI_NL_MAX_TRANSPORTS`.

Generic vendor host messages use `SCSI_NL_SHOST_VENDOR` and `struct scsi_nl_host_vendor_msg`. `SCSI_NL_VID_TYPE_SHIFT`, `SCSI_NL_VID_TYPE_MASK`, `SCSI_NL_VID_TYPE_PCI`, and `SCSI_NL_VID_ID_MASK` define the 64-bit vendor ID namespace. `SCSI_NL_MSGALIGN()` rounds payloads to 8-byte boundaries, and `INIT_SCSI_NL_HDR()` populates the common header.

## Control Flow and State
Kernel producers allocate a netlink message of type `SCSI_TRANSPORT_MSG`, fill `scsi_nl_hdr`, append a transport or vendor-specific payload, align to 8 bytes, and multicast to interested listeners. Userspace validates version, magic, transport, msgtype, and `msglen` before parsing the trailing payload. Vendor messages can travel in both kernel-to-user and user-to-kernel directions.

## State and Persistence Behavior
The header defines transient event packets only. Persistent state is in transport drivers and userspace subscribers. `host_no`, vendor IDs, and payload length fields are snapshots carried in individual messages.

## Dependencies and Integration Points
It includes `<linux/netlink.h>` and `<linux/types.h>`. FC transport-specific netlink messages in `scsi_netlink_fc.h` embed `scsi_nl_hdr`. BSG FC vendor IDs reference the same formatting rules.

## Risks and Test Signals
Risks include misaligned payload parsing, trusting `msglen` without comparing netlink length, vendor ID type/ID bit mistakes, and accepting messages with wrong magic/version. Tests should validate header initialization, alignment, short-message rejection, and FC event subscription through a netlink listener.
