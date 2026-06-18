# sources/distributed-fs/ceph-client/net/ncsi/ncsi-netlink.h

## Purpose
This private header declares the netlink response helpers used outside `ncsi-netlink.c`, mainly by response and timeout paths.

## APIs, Types, and Functions
It declares `ncsi_send_netlink_rsp()`, `ncsi_send_netlink_timeout()`, and `ncsi_send_netlink_err()`. These functions send a successful raw-command response, a timeout notification, or an `NLMSG_ERROR` response to the saved generic netlink sender.

## Control Flow
There is no executable flow. `ncsi-rsp.c` calls the response helper for netlink-driven requests after command response processing, and `ncsi-manage.c` calls the timeout helper from `ncsi_request_timeout()`. Error reporting is used by bad response validation and immediate raw command send failures.

## State and Persistence
The functions operate on `struct ncsi_request` metadata (`snd_seq`, `snd_portid`, `nlhdr`, command/rsp skbs) and package/channel lookup results. The header itself holds no state.

## Dependencies and Integration
The header depends on `linux/netdevice.h` and `internal.h` for NCSI request, package, and channel types. It connects `ncsi-netlink.c` to `ncsi-rsp.c` and `ncsi-manage.c`.

## Risks
Prototype drift would break cross-file integration. Callers must pass valid request skb pointers because response helpers derive net namespace and ifindex from command or response skbs.

## Test Signals
Build coverage plus raw netlink command success, timeout, and validation-error tests exercise all three declarations.
