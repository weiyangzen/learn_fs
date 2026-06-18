# sources/distributed-fs/ceph-client/net/sched/act_nat.c

## Purpose

`act_nat.c` implements a stateless IPv4 tc NAT action. It rewrites source or destination addresses matching an old-address/mask pair and updates IP, TCP, UDP, and selected ICMP error checksums.

## Important APIs, types, and functions

`tcf_nat_init()` parses `TCA_NAT_PARMS`, allocates or replaces a `struct tcf_nat_parms`, validates the tc control action, and installs params under RCU. `tcf_nat_act()` is the packet path. `tcf_nat_dump()` reports old/new address, mask, flags, and timing. `tcf_nat_cleanup()` frees RCU params.

## Control flow

Runtime reads params, rejects configured `TC_ACT_SHOT`, pulls the IPv4 header, chooses `iph->saddr` for egress mode or `iph->daddr` for ingress mode, and checks `(old_addr ^ addr) & mask`. On match it makes the IP header writable, rewrites only masked bits, and fixes the IPv4 checksum. For TCP and UDP first fragments it updates L4 checksums; for ICMP errors it rewrites the embedded inner address in the reverse direction and updates the ICMP checksum. Nonmatching non-ICMP packets and later fragments pass through unchanged.

## State and persistence

Action state is a single RCU parameter block containing old/new address, mask, flags, and control action. Statistics live in tc common action counters. No connection table is kept; the action is explicitly stateless and cannot remember flows or ports.

## Dependencies and integration points

The code depends on IPv4, TCP, UDP, ICMP, checksum, skb writability, and tc action IDR APIs. It integrates as a software tc action only; there is no `offload_act_setup` in this file.

## Risks and edge cases

It is IPv4-only and only handles L4 checksum updates for TCP/UDP plus ICMP error wrappers. Inner checksums inside ICMP errors are explicitly not fixed beyond the ICMP checksum. Fragment handling is limited, and `skb_try_make_writable()` failures drop. Because no conntrack state exists, reverse-path consistency must be supplied by symmetric tc rules.

## Test signals

Use IPv4 TCP, UDP with zero and nonzero checksums, ICMP errors, unmatched prefixes, fragments, ingress versus egress flags, and non-linear skbs. Verify address rewrite masks, checksums, drops on insufficient writable data, and tc dump output.
