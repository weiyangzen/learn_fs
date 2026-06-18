# sources/distributed-fs/ceph-client/net/ipv4/netfilter/ipt_REJECT.c

## Purpose
`ipt_REJECT.c` implements the IPv4 legacy `REJECT` target, converting filter-table rejections into ICMP unreachable responses or TCP resets before dropping the original packet.

## Important APIs, Types, And Functions
The registered target is `reject_tg_reg`. `reject_tg()` emits the selected response through `nf_send_unreach()` or `nf_send_reset()`. `reject_tg_check()` validates unsupported and TCP-specific modes.

## Control Flow
At packet traversal time the target switches on `struct ipt_reject_info.with`, emits an ICMP net/host/protocol/port/prohibited/admin unreachable or a TCP reset, and returns `NF_DROP`. Checkentry rejects obsolete `ECHOREPLY` and requires TCP protocol matching for `TCP_RESET`.

## State And Persistence
No persistent state beyond module registration and per-rule target data.

## Dependencies And Integration Points
It is restricted to the filter table and local-in/forward/local-out hooks. It depends on IPv4 reject helper functions and the iptables target check path.

## Risks
Risks include emitting resets for non-TCP traffic if validation regresses, wrong hook context passed to reject helpers, bridge-netfilter interactions, and accidentally supporting obsolete reject modes.

## Test Signals
Test each ICMP reject code, TCP reset only on valid TCP rules, invalid `ECHOREPLY`, hook restrictions, local-out and forward behavior, and interaction with packets already malformed enough for helper refusal.
