# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nf_conntrack_sctp.h

## Purpose
Defines SCTP conntrack state enum exposed to userspace.

## Important APIs, Types, And Functions
Exports `sctp_conntrack` states from none/closed through cookie wait/echoed, established, shutdown states, heartbeat sent/acked, and max.

## Control Flow
SCTP conntrack transitions among these states as SCTP chunks are observed. Userspace tools decode the enum in conntrack state dumps.

## State, Persistence, And Dependencies
State persists in SCTP conntrack entries. Depends on `nf_conntrack_tuple_common.h`.

## Integration Points
Used by conntrack, nftables/iptables ct modules, and userspace conntrack tooling.

## Risks
`SCTP_CONNTRACK_HEARTBEAT_ACKED` is marked no longer used but remains ABI. Invalid transitions must be handled in implementation, not this header.

## Test Signals
Validate state reporting for SCTP association setup/shutdown, cookie paths, heartbeat cases, and compatibility for the unused heartbeat-acked value.
