<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/gtp.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/gtp.h

## Purpose
`gtp.h` defines the generic-netlink ABI for the kernel GPRS Tunneling Protocol implementation. It lets userspace create, delete, query, and monitor PDP contexts for GTP-U tunnels.

## Important APIs, types, and functions
The multicast group name is `GTP_GENL_MCGRP_NAME`. `enum gtp_genl_cmds` defines `GTP_CMD_NEWPDP`, `GTP_CMD_DELPDP`, `GTP_CMD_GETPDP`, and `GTP_CMD_ECHOREQ`. `enum gtp_version` distinguishes `GTP_V0` and `GTP_V1`. `enum gtp_attrs` defines attributes for link index, version, v0 TID, peer address, MS address, flow, network namespace fd, v1 input/output TEIDs, padding, IPv6 peer/MS addresses, and address family.

## Control flow
User space discovers the generic-netlink family, sends `NEWPDP` with link, version, tunnel identifiers, peer/MS addresses, and optional netns fd, then deletes or dumps contexts through `DELPDP`/`GETPDP`. Echo requests use the command channel to probe peers.

## State and persistence behavior
PDP context state lives in the kernel GTP device and is keyed by GTP version and tunnel IDs. It persists until deleted, the netdevice is removed, or the network namespace exits.

## Dependencies and integration points
It relies on generic netlink definitions and integrates with GTP netdevices, network namespaces, mobile-core control planes, and route/address management.

## Risks and test signals
Risks include mixing v0 TID and v1 TEID attributes, IPv4/IPv6 family mismatches, stale namespace fds, duplicate tunnel keys, and userspace assuming multicast group availability. Test signals include netlink policy tests, PDP add/delete/dump round trips, packet encapsulation/decapsulation tests, namespace teardown, echo request handling, and IPv6 attribute coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/gtp.h -->
