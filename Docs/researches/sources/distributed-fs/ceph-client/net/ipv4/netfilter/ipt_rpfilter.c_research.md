# sources/distributed-fs/ceph-client/net/ipv4/netfilter/ipt_rpfilter.c

## Purpose
`ipt_rpfilter.c` implements an IPv4 reverse-path filter match for legacy iptables, checking whether a reply route for the packet source would use the incoming interface.

## Important APIs, Types, And Functions
The match is `rpfilter_mt_reg`. Runtime helpers are `rpfilter_get_saddr()`, `rpfilter_lookup_reverse()`, `rpfilter_is_loopback()`, and `rpfilter_mt()`. Validation is `rpfilter_check()`.

## Control Flow
Loopback packets pass immediately. Zeronet sources to broadcast/local multicast are accepted. Otherwise the match builds a reverse `flowi4` from packet source/destination, optional mark, DSCP, L3 master, and uid, then performs `fib_lookup()` and verifies route type and nexthop device, optionally allowing loose mode or local addresses.

## State And Persistence
No persistent state beyond per-rule `struct xt_rpfilter_info`.

## Dependencies And Integration Points
It is limited to PREROUTING in the raw or mangle tables. It depends on IPv4 FIB lookup, nexthop-device checking, L3 master/VRF support, and xtables match validation.

## Risks
Risks include route-policy mismatches, VRF/L3 master mistakes, mishandling multicast/broadcast/zeronet cases, accepting unknown flags, and unexpected behavior with mark-sensitive routing.

## Test Signals
Test strict and loose modes, invert flag, accept-local flag, valid-mark flag, loopback packets, zeronet broadcast/multicast packets, VRF input, non-unicast reverse routes, and rejection outside raw/mangle tables.
