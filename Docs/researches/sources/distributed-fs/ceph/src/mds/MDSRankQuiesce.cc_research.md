# sources/distributed-fs/ceph/src/mds/MDSRankQuiesce.cc

## Purpose
Adds quiesce DB and quiesce agent support to `MDSRank`: admin commands, cluster membership updates, peer listing/ack dispatch, and root quiesce/cancel bridging to `MDCache`.

## Important APIs, Types, And Functions
`command_quiesce_db` validates include/exclude/reset/release/cancel/query options and submits a `QuiesceDbManager::RequestContext`. `quiesce_cluster_update` derives leader/members from `MDSMap`, installs send callbacks, handles degraded cancel-all, and updates membership. `quiesce_dispatch` processes `MMDSQuiesceDbListing` and `MMDSQuiesceDbAck`. `quiesce_agent_setup` builds the agent control interface.

## Control Flow
Commands enforce mutually exclusive operations and option constraints, then format JSON responses with set/member state and ages. Membership callbacks loop back locally when leader is self or send messages to current peer addresses under `mds_lock`. Active ranks bind agent callbacks to the manager; inactive and standby-replay ranks provide limited responder behavior.

## State And Persistence Behavior
Quiesce state is held in `QuiesceDbManager` and `QuiesceAgent`. Membership comes from MDSMap epoch, fs name, leader gid, members, and local gid. During degraded leadership the code injects cancel-all to avoid unsafe active quiesce sets. Debug dummy requests are volatile.

## Dependencies And Integration Points
Depends on MDSRank, MDCache, MonClient, QuiesceDbManager, QuiesceAgent, quiesce messages, Boost.URL, timers, formatters, and MDSMap membership. Admin socket routing is in `MDSRank.cc`.

## Risks
Validator mistakes can allow ambiguous commands. Captured membership can go stale between map updates and sends. Degraded cancel-all is disruptive but safety-oriented. Debug URI behavior is compile-gated. Bad-message handling follows `ms_die_on_bad_msg`.

## Test Signals
Validation errors/default include, query/release/cancel/reset, JSON response shape, leader loopback and remote sends, decode errors, degraded cancel-all, inactive/standby-replay responses, real quiesce/cancel through MDCache, and debug emulation when enabled.
