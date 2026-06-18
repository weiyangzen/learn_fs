# sources/distributed-fs/ceph-client/include/linux/netfilter/nf_conntrack_amanda.h

## Purpose
This header defines the NAT extension hook used by the AMANDA conntrack helper when it discovers related data connections.

## Important APIs, Types, and Functions
It defines `nf_nat_amanda_hook_fn`, a function type taking an skb, conntrack direction info, protocol offset, match offset/length, and an expectation. It declares the RCU-published hook pointer `nf_nat_amanda_hook`.

## Control Flow
The AMANDA helper parses control traffic, creates or updates an `nf_conntrack_expect`, and calls the NAT hook if present so NAT can rewrite payload and expectation details. Hook lookup must be protected by RCU in implementation code.

## State and Persistence
Only a global RCU function pointer is declared. Expectations and conntrack state live elsewhere and are in-memory only.

## Dependencies and Integration Points
It depends on netfilter, skb, and conntrack expectation APIs. Integration is between the AMANDA helper and NAT helper module.

## Risks
Payload offsets and lengths must match parsed control data, or NAT rewriting can corrupt packets. Hook lifetime requires RCU discipline. Expectation ownership and NAT updates must remain synchronized.

## Test Signals
AMANDA control-session tests with NAT enabled/disabled, malformed control payloads, module load/unload under traffic, expectation creation, and payload rewrite checksum validation.
