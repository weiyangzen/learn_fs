# sources/distributed-fs/ceph-client/net/tipc/netlink.h

## Purpose
`netlink.h` declares the shared TIPC generic netlink family, a small message-building context, nested attribute policy arrays, and lifecycle functions for modern and legacy netlink registration.

## Important APIs, Types, And Functions
The header exports `struct genl_family tipc_genl_family`, defines `struct tipc_nl_msg` with `skb`, `portid`, and `seq`, declares policy arrays for name table, socket, network, link, node, properties, bearer, media, UDP, and monitor attributes, and declares `tipc_netlink_start()`, `tipc_netlink_compat_start()`, `tipc_netlink_stop()`, and `tipc_netlink_compat_stop()`.

## Control Flow
The header has no executable flow. Subsystem dump helpers receive `struct tipc_nl_msg` to emit generic-netlink replies with the correct sender port and sequence. Module init/exit code calls the start/stop functions for both modern and compatibility families.

## State And Persistence
The header owns no storage beyond declarations. It describes global netlink registration state and immutable policy arrays defined in `netlink.c`, plus the transient `tipc_nl_msg` context used while constructing replies.

## Dependencies And Integration Points
It includes `<net/netlink.h>` and is included by netlink handlers across bearer, media, node, net, name table, socket, and compatibility code. Keeping policies declared here lets compatibility translation reuse the modern validation contract.

## Risks And Edge Cases
Any policy declaration mismatch with definitions in `netlink.c` causes compile or ABI errors. `tipc_nl_msg` assumes callers set all fields before nested `nla_put()`/`genlmsg_put()` operations. Start/stop ordering matters because compatibility code references the modern family id and policies.

## Test Signals
Build tests across optional TIPC configs, generic netlink family registration/unregistration tests, dump helper tests that verify `portid` and `seq` propagation, and malformed-attribute validation through declared policy arrays exercise this header.
