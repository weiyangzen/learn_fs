# sources/distributed-fs/ceph-client/include/net/seg6_local.h

## Purpose
This header declares SRv6 local-action helpers, especially BPF-facing SRH validity state and nexthop lookup support.

## Important APIs, Types, And Functions
It declares `seg6_lookup_nexthop()` and `seg6_bpf_has_valid_srh()`. `struct seg6_bpf_srh_state` stores a per-cpu local lock, current SRH pointer, header length, and validity flag. `DECLARE_PER_CPU(seg6_bpf_srh_states)` exposes per-cpu BPF SRH state.

## Control Flow
SRv6 local processing and BPF helpers use per-cpu state to expose a currently validated SRH while avoiding cross-CPU sharing. Nexthop lookup is shared with core SRv6 route handling.

## State And Persistence
State is per CPU and transient for packet/BPF processing. `local_lock_t` protects bottom-half local access to the current SRH pointer and validity metadata.

## Dependencies And Integration Points
It integrates with IPv6 sk_buffs, SRv6 local actions, BPF helpers, and the SRv6 core nexthop lookup API.

## Risks And Test Signals
Risks include stale per-cpu SRH pointers, missing local lock coverage, BPF helpers accepting invalid SRH state, and nexthop lookup inconsistencies. Test signals include SRv6 BPF local action tests, concurrent softirq traffic, invalid SRH rejection, and route lookup behavior.
