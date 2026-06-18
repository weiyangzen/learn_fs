# sources/distributed-fs/ceph-client/net/ipv4/xfrm4_output.c

## Purpose
This file is the IPv4 XFRM output wrapper. It routes packets through postrouting netfilter and then into the generic XFRM output engine, while handling rerouted packets and local PMTU errors.

## Important APIs, Types, and Functions
The exported functions are `xfrm4_output()` and `xfrm4_local_error()`. The internal `__xfrm4_output()` checks `skb_dst(skb)->xfrm` and calls either `dst_output()` for rerouted non-XFRM packets or `xfrm_output()` for transform processing.

## Control Flow
`xfrm4_output()` invokes `NF_HOOK_COND()` at `NF_INET_POST_ROUTING` unless `IPSKB_REROUTED` is already set. After the hook, `__xfrm4_output()` continues transform output when an XFRM state is attached; otherwise it marks the skb rerouted and sends it through normal dst output. Local EMSGSIZE reporting chooses the inner IP header for encapsulated packets and reports through `ip_local_error()`.

## State and Persistence Behavior
No persistent state is owned. The file mutates skb flags and reports socket errors. XFRM state and dst lifetime are managed by the core dst/XFRM subsystems.

## Dependencies and Integration Points
It integrates IPv4 netfilter postrouting, dst output, generic XFRM output, IPv4 local error reporting, UDP/TCP socket port context through `inet_sk()`, and encapsulated skb inner headers.

## Risks
Reroute flag handling prevents recursive postrouting. Incorrect inner/outer header selection for local errors can report the wrong destination or port to applications. Missing XFRM detection can bypass transforms.

## Test Signals
Test transformed and non-transformed dsts, netfilter postrouting reroute, encapsulated PMTU errors, non-encapsulated PMTU errors, and recursion avoidance with `IPSKB_REROUTED`.
