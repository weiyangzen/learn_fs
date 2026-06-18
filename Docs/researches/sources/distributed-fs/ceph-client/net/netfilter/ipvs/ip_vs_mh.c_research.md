# sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_mh.c

## Purpose
Implements the IPVS Maglev hashing scheduler `mh`. It builds a per-service lookup table from destination permutations and uses a hash of source address, and optionally source/destination port, to select a stable destination with minimal remapping when the destination set changes.

## Important APIs, Types, and Functions
`struct ip_vs_mh_state` stores the lookup table, temporary destination setup array, two hsiphash keys, GCD of weights, and right-shift compression. `struct ip_vs_mh_lookup` stores RCU destination pointers. `ip_vs_mh_init_svc()`, `ip_vs_mh_dest_changed()`, and `ip_vs_mh_done_svc()` manage per-service state. `ip_vs_mh_permutate()` computes Maglev offset/skip values, `ip_vs_mh_populate()` fills the lookup table, `ip_vs_mh_get()` and `ip_vs_mh_get_fallback()` select destinations, and `ip_vs_mh_schedule()` is the scheduler callback.

## Control Flow
Initialization allocates the lookup table, initializes deterministic hash secrets, computes weight GCD and shift, and populates the Maglev table. Destination add, delete, or update recomputes the weight compression and fully reassigns the lookup table. Scheduling chooses the client-side hash address based on packet direction; with `IP_VS_SVC_F_SCHED_MH_PORT`, it reads TCP/UDP/SCTP ports from the packet. It hashes into the lookup table and returns the destination if weight and overload flags permit. With `IP_VS_SVC_F_SCHED_MH_FALLBACK`, an unavailable bucket triggers a deterministic search for another usable bucket.

## State and Persistence
State is per-service and lasts while the scheduler is bound. Lookup entries hold real-server references; `ip_vs_mh_reset()` releases existing references before reassignment or teardown. Hash keys are fixed constants, so mapping is deterministic across instances with the same service configuration. Weight distribution uses `last_weight`, GCD, and a shift to fit large weights into the finite table.

## Dependencies and Integration Points
Uses IPVS scheduler flags, destination lists, destination reference management, RCU pointer access, `hsiphash`, bitmaps, GCD and bit helpers, and transport header parsing from SKBs. It integrates with IPVS service flags supplied by user configuration, especially fallback and port-sensitive hashing.

## Risks
`svc->num_dests > IP_VS_MH_TAB_SIZE` fails reassignment, so configured table size bounds service scale. Reassignment is a full-table operation and can fail allocation of the temporary bitmap or setup array. Port extraction returns zero for unsupported protocols or truncated headers, reducing entropy. Fixed hash secrets are stable but not random. Fallback changes strict Maglev affinity when a chosen destination is unavailable.

## Test Signals
Test deterministic selection for repeated source addresses, changed mapping after destination add/delete/update, weighted distribution with varied `last_weight`, fallback behavior for overloaded or zero-weight destinations, `mh-port` hashing differences, IPv6 folded-address hashing, and failure handling when destination count exceeds table size.
