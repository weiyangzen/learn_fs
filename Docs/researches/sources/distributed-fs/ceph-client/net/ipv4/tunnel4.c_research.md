# sources/distributed-fs/ceph-client/net/ipv4/tunnel4.c

## Purpose

`tunnel4.c` is the generic IPv4 XFRM tunnel dispatcher for IP-in-IP, IPv6-in-IPv4, and MPLS-in-IPv4 protocols. It lets tunnel implementations register prioritized `struct xfrm_tunnel` handlers and wires those handlers into the IPv4 protocol receive and ICMP error paths.

## Important APIs, Types, and Functions

Exported APIs are `xfrm4_tunnel_register()` and `xfrm4_tunnel_deregister()`. Internal state consists of three RCU handler lists: `tunnel4_handlers`, `tunnel64_handlers`, and `tunnelmpls4_handlers`, protected for updates by `tunnel4_mutex`. Helpers and callbacks include `fam_handlers()`, `tunnel4_rcv()`, optional `tunnel4_rcv_cb()`, `tunnel64_rcv()`, `tunnelmpls4_rcv()`, `tunnel4_err()`, `tunnel64_err()`, `tunnelmpls4_err()`, protocol descriptors, and module init/exit.

## Control Flow

Registration selects a handler list by family, locks the mutex, walks the RCU list in priority order, rejects duplicate priority, and inserts the handler before the first lower-priority entry. Deregistration removes the matching handler from the selected list, unlocks, and waits for `synchronize_net()` before returning.

Receive handlers first ensure enough header bytes are present with `pskb_may_pull()`. They iterate the relevant handler list under RCU and call each handler's `handler(skb)`. A return value of zero means the handler consumed the skb and receive processing succeeds. If no handler accepts the packet, the code sends ICMP destination/port unreachable and frees the skb. Error handlers similarly iterate and stop when a handler's `err_handler()` returns zero, otherwise returning `-ENOENT`.

Module init registers `net_protocol` handlers for `IPPROTO_IPIP`, optionally `IPPROTO_IPV6` and `IPPROTO_MPLS`, and optionally registers XFRM input AF info for tunnel callbacks. Failures unwind previously registered protocols. Module exit unregisters in reverse order and logs failures.

## State and Persistence Behavior

Handler lists are global module state and persist until handlers deregister or the module exits. RCU protects readers while mutex-protected updates mutate list links. No per-namespace or durable state is stored in this file.

## Dependencies and Integration Points

The file integrates with the IPv4 protocol table via `inet_add_protocol()`/`inet_del_protocol()`, XFRM tunnel handlers, optional IPv6/MPLS builds, optional `xfrm_input_afinfo`, ICMP error generation, skbuff header pulling/freeing, and RCU network synchronization. Registered tunnel modules supply the actual encapsulation-specific receive and error behavior.

## Risks and Edge Cases

Duplicate priorities are rejected, so independent tunnel modules must coordinate priority values. A handler that returns zero owns the skb; later handlers will not run. If no handler accepts traffic, ICMP unreachable is emitted, which can affect diagnostics and peer behavior. Optional build combinations require correct init unwind. Deregistration must wait for readers to avoid use-after-free.

## Test Signals

Tests should verify priority-ordered insertion, duplicate priority rejection, deregistration and `-ENOENT`, receive dispatch for IPIP/IPv6/MPLS, fallback ICMP unreachable and skb free, error dispatch, optional XFRM callback behavior, module init failure unwind, and RCU safety under concurrent receive and unregister.
