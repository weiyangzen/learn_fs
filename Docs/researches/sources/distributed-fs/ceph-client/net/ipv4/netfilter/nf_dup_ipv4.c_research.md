# sources/distributed-fs/ceph-client/net/ipv4/netfilter/nf_dup_ipv4.c

## Purpose
`nf_dup_ipv4.c` implements IPv4 packet duplication for netfilter users such as TEE/nft dup, cloning a packet and sending the clone to an alternate gateway/interface while the original continues.

## Important APIs, Types, And Functions
The exported API is `nf_dup_ipv4()`. Routing is handled by `nf_dup_ipv4_route()`.

## Control Flow
`nf_dup_ipv4()` disables bottom halves, refuses recursive duplication via `current->in_nf_duplicate`, copies the skb, clears conntrack on the copy, sets DF, decrements TTL for ingress/input hooks, routes the clone to the supplied gateway and optional output interface, and sends it with `ip_local_out()` under the recursion guard.

## State And Persistence
No persistent module state. It mutates only the cloned skb and temporarily sets `current->in_nf_duplicate`.

## Dependencies And Integration Points
It depends on IPv4 route output, skb cloning, conntrack reset/untracked marking, checksum/output path behavior, and netfilter duplicate callers.

## Risks
Risks include recursion loops, TTL underflow behavior, route lookup failure, conntrack accounting contamination if reset is missed, and clone MTU/DF side effects.

## Test Signals
Test duplication from PREROUTING, INPUT, FORWARD, OUTPUT, and POSTROUTING callers; route failure; specified output interface; conntrack state on clones; TTL decrement on ingress/input; and nested dup suppression.
