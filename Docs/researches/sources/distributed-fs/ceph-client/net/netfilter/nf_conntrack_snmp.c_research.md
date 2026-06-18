<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_snmp.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_snmp.c

## Purpose
Implements a small IPv4 SNMP broadcast helper. It uses the generic broadcast helper to expect replies to SNMP requests and optionally delegates SNMP NAT handling.

## Important APIs, Types, and Functions
The helper entry point is `snmp_conntrack_help()`. Module lifecycle is `nf_conntrack_snmp_init()` and `nf_conntrack_snmp_fini()`. The exported RCU hook pointer is `nf_nat_snmp_hook`. The helper registers for IPv4 UDP source port 161 with one expected reply.

## Control Flow
Every helper invocation calls `nf_conntrack_broadcast_help()` with the configured timeout. If NAT is active and a NAT SNMP hook is installed, the hook processes the skb; otherwise the packet is accepted.

## State and Persistence
No per-connection private state is defined here. The expectation policy timeout is initialized from the module parameter `timeout`, defaulting to 30 seconds. NAT hook state is external and RCU-protected.

## Dependencies and Integration Points
Depends on conntrack helper/expectation APIs, broadcast helper support, and optional NAT SNMP code. It is IPv4-only by tuple registration.

## Risks
The helper is intentionally broad for broadcast semantics and does not parse SNMP payloads itself. NAT hook dereference must remain under RCU protection supplied by netfilter hook context.

## Test Signals
Test broadcast SNMP requests, expected replies from agents, timeout parameter behavior, NAT enabled/disabled, missing NAT hook, and helper registration/unregistration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_snmp.c -->
