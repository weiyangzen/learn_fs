# sources/distributed-fs/ceph/src/mds/MDSMap.h

## Purpose
Defines the CephFS metadata-server map: daemon/rank states, gid-to-rank identity, feature compatibility, filesystem pools, health and availability decisions, standby replay, balancing flags, and quiesce DB membership.

## Important APIs, Types, And Functions
`MDSMap::DaemonState` mirrors wire MDS states. `mds_info_t` stores daemon global id, rank, incarnation, state, addresses, lag flag, export targets, feature bits, flags, and `CompatSet`, with versioned and legacy encoding. Map APIs expose flag setters, client feature requirements, pool membership, rank/gid lookups, state predicates, health checks, rank masks, quiesce DB leader/members, and `state_transition_valid`.

## Control Flow
Monitor-side code mutates map state; rank/client code consumes it. Most methods derive answers from `up`, `in`, `failed`, `stopped`, `damaged`, and `mds_info`. Feature setters update live flags and history bitmaps. Quiesce membership updates assert leader and members are known gids before replacing state.

## State And Persistence Behavior
Persistent map state includes epoch, filesystem name, flags, failure epochs, tableserver/root, data/metadata pools, max MDS values, membership sets, daemon info, required client features, compatibility, and quiesce cluster fields. The documented invariant is `up + failed = in`, with `in` disjoint from `stopped`.

## Dependencies And Integration Points
Depends on Ceph core types, CephFS rank/gid types, `CompatSet`, health, config, addresses, and buffer encoders. It is friended by monitor/filesystem map classes and is heavily used by `MDSRank`, balancer, quiesce, table, monitor, and client paths.

## Risks
Incorrect predicates can route traffic to wrong ranks or allow unsafe resize/recovery. Encoding is feature-sensitive. `get_first_data_pool()` assumes a non-empty vector. Quiesce updates assert on unknown gids. Rank mask parsing and feature flags affect cluster-wide behavior.

## Test Signals
Round-trip encoding across feature sets, legal/illegal state transitions, health/availability for failed/damaged/replay/stopped maps, pool add/remove, rank masks, standby replay counts, required client feature persistence, and quiesce member validation.
