# sources/distributed-fs/ceph-client/drivers/scsi/scsi_netlink.c

## Purpose

`scsi_netlink.c` implements the SCSI transport netlink endpoint for `NETLINK_SCSITRANSPORT`. It creates a kernel netlink socket, validates inbound SCSI transport messages, dispatches supported message classes, and exports `scsi_nl_sock` so transport implementations such as Fibre Channel can multicast events through the same socket.

## Important APIs, types, and functions

`struct sock *scsi_nl_sock` is the exported socket handle. `scsi_netlink_init()` registers the netlink endpoint with `netlink_kernel_create(&init_net, NETLINK_SCSITRANSPORT, ...)`, using `scsi_nl_rcv_msg()` as the receive callback and `SCSI_NL_GRP_CNT` multicast groups. `scsi_netlink_exit()` releases the socket with `netlink_kernel_release()`. The receive path parses `struct nlmsghdr` and `struct scsi_nl_hdr`, checks `SCSI_TRANSPORT_MSG`, `SCSI_NL_VERSION`, `SCSI_NL_MAGIC`, `CAP_SYS_ADMIN`, message length, transport id, and message type.

## Control flow

`scsi_nl_rcv_msg()` loops over every aligned netlink message in the incoming skb. It rejects malformed headers, unsupported message types, invalid protocol version/magic, unprivileged senders, and partial payloads. For `SCSI_NL_TRANSPORT` it currently recognizes `SCSI_NL_SHOST_VENDOR` but only returns `-ESRCH` because no driver dispatch is implemented here; unknown SCSI transport message types get `-EBADR`, and unknown transports get `-ENOENT`. If an error occurred or the sender requested `NLM_F_ACK`, the callback sends `netlink_ack()` before advancing to the next aligned message.

## State and persistence behavior

The persistent state is the global kernel socket pointer. The receive path does not keep per-client sessions or durable message state. Multicast group membership is owned by the netlink core. Message handling is synchronous with skb parsing, and every error is transient except for socket registration failure during init.

## Dependencies and integration points

The file depends on Linux netlink APIs, capability checks, `scsi/scsi_netlink.h`, and `scsi_priv.h` declarations. It integrates with the SCSI subsystem initialization/exit path through `scsi_netlink_init()` and `scsi_netlink_exit()`. Other transport files use `scsi_nl_sock` for event delivery; `scsi_transport_fc.c` checks it and calls `nlmsg_multicast()` to publish FC events.

## Risks and edge cases

The vendor message path is effectively a stub, so user-space requests of that kind receive an error even though the message type is recognized. The parser must be strict about `nlmsg_len`, `hdr->msglen`, and `skb_pull()` alignment to avoid walking malformed skbs. Because `scsi_netlink_exit()` releases the socket but does not clear `scsi_nl_sock`, callers must rely on subsystem teardown ordering to avoid use after release. All inbound messages require `CAP_SYS_ADMIN`, so any future message type added here must consciously preserve or adjust that privilege boundary.

## Test signals

Build with `CONFIG_SCSI_NETLINK` enabled and disabled to validate the real and inline-stub declarations in `scsi_priv.h`. Runtime tests can send invalid netlink type, bad magic/version, partial payloads, and unprivileged messages and assert the expected `netlink_ack()` errors. Transport event tests should enable a producer such as FC transport and confirm multicast events use `scsi_nl_sock` only after successful initialization.
