<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MDSMap.h -->
# sources/distributed-fs/ceph/src/mds/MDSMap.h

## Purpose
`MDSMap.h` defines the CephFS metadata-server map model used by MDS daemons, monitors, clients, and filesystem-map code to describe rank assignment, daemon identity, rank state, filesystem pools, feature compatibility, health, and quiesce-cluster membership. It is the main in-memory and encoded contract for deciding whether ranks are up, failed, damaged, stopped, active, replaying, or unavailable.

## Important APIs, Types, And Functions
The central type is `MDSMap`, with `DaemonState` mirroring Ceph wire states and `availability_t` summarizing client mountability. `mds_info_t` stores a daemon global id, name, rank, incarnation, state sequence, addresses, lag state, export targets, feature bits, flags, and compatibility set; it encodes in old and versioned forms depending on feature bits. Compatibility helpers expose all/default/base/v16.2.4 feature sets. The map provides getters and mutators for filesystem flags, sessions, max file and xattr sizes, data and metadata pools, required client features, standby replay, balancing, snap policies, rank masks, quiesce DB leader/members, and rank membership sets. State predicates such as `is_active`, `is_degraded`, `is_resolving`, `is_rejoining`, `is_resizeable`, `have_inst`, `get_gid`, `get_info`, and `state_transition_valid` are the primary consumers' API.

## Control Flow
Most methods are small queries over `up`, `in`, `failed`, `stopped`, `damaged`, and `mds_info`. Monitor-side code mutates the map, then daemons consume it to drive `MDSRank` transitions. Feature setters both update live flags and record `ever_allowed_features` or `explicitly_allowed_features`. Quiesce DB updates validate the chosen leader and every member against known MDS daemon gids before replacing membership. Encoding/decoding, `sanitize`, health reporting, and summary/dump methods make the map durable and observable.

## State And Persistence Behavior
The map persists epoch, enabled flag, filesystem name, feature flags, timestamps, failure epochs, tableserver/root rank, data and metadata pools, max MDS settings, rank mask, membership sets, gid-to-info records, required client feature bits, and compatibility metadata. Invariants documented in the file require `up + failed = in` and `in` disjoint from `stopped`. Health and availability are derived from this state; incorrect persistence can mislead rank assignment, client mount decisions, and recovery.

## Dependencies And Integration Points
The file depends on Ceph core types, `CompatSet`, health types, config, CephFS rank/gid definitions, feature bitsets, addresses, and buffer encoding. It is friended by `MDSMonitor`, `Filesystem`, and `FSMap`, and it is consumed heavily by `MDSRank`, balancer code, table code, quiesce code, clients, and monitors.

## Risks
The state predicates are safety-critical because stale or invalid answers can send traffic to wrong ranks, skip recovery, or allow resizing while recovery is active. Encoding is version and feature sensitive. `get_first_data_pool()` assumes `data_pools` is non-empty. Quiesce DB membership update asserts on unknown gids, so callers must update it only after daemon info is current. Rank masks and feature flags affect multi-MDS behavior cluster-wide.

## Test Signals
Useful tests cover encode/decode compatibility across feature sets, all legal and illegal state transitions, health and availability outputs for failed/damaged/stopped/replay combinations, pool add/remove and `pool_in_use`, rank-mask parsing including special values, standby replay counts, required client feature persistence, and quiesce DB leader/member validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MDSMap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MDSMetaRequest.h -->
# sources/distributed-fs/ceph/src/mds/MDSMetaRequest.h

## Purpose
`MDSMetaRequest.h` defines a tiny base object for MDS-created metadata requests. It records the operation code and Ceph transaction id for internal client-style operations, allowing `MDSRank` to keep typed request ownership in `internal_client_requests`.

## Important APIs, Types, And Functions
`MDSMetaRequest` has a constructor taking `int op` and `ceph_tid_t tid`, a virtual destructor for derived request classes, and simple `get_op()` and `get_tid()` accessors. The fields are private and immutable after construction except through object lifetime.

## Control Flow
There is no local control flow beyond construction and access. Callers allocate a request subclass or base instance with an operation and tid, store it, then later inspect the op/tid for dispatch, tracking, or cleanup.

## State And Persistence Behavior
The object is purely in-memory. It does not encode, journal, or write any state. Persistence, replay, and deduplication must be handled by callers using the stored transaction id and surrounding MDS request machinery.

## Dependencies And Integration Points
The only include is `include/types.h` for `ceph_tid_t`. The visible integration point in this subset is `MDSRank::internal_client_requests`, which owns `std::unique_ptr<MDSMetaRequest>` values for rank-originated requests such as stray or maintenance operations.

## Risks
The accessors are non-const, so const containers cannot read fields without adjustment. The class does not define copy or move policy, timeout behavior, or completion state. Misuse risk is mostly lifecycle-related: callers must ensure a tid remains unique in the owning rank and remove the object when the operation finishes.

## Test Signals
Tests are usually indirect: internal MDS request creation should assign unique tids, preserve operation codes, survive storage in `unique_ptr<MDSMetaRequest>`, and clean up after completion or error paths. A focused unit test could assert construction and virtual destruction through a base pointer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MDSMetaRequest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MDSPerfMetricTypes.h -->
# sources/distributed-fs/ceph/src/mds/MDSPerfMetricTypes.h

## Purpose
`MDSPerfMetricTypes.h` defines the wire and dump types for CephFS client-to-MDS and rank-to-manager performance metrics. It covers capability hit rates, read/write/metadata latency, dentry lease hits, opened files/inodes, pinned caps, IO size totals, per-subvolume metrics via `SubvolumeMetric`, and rank-level CPU/open-request counters.

## Important APIs, Types, And Functions
`UpdateType` distinguishes refresh from remove updates. `CapHitMetric`, latency metrics, lease/open/pinned/inode/IO-size metrics, `RankPerfMetrics`, and aggregate `Metrics` all implement `DENC` encoding, `dump(Formatter*)`, and stream output. `metrics_message_t` is the featureful encoded message payload carrying `seq`, source `rank`, `client_metrics_map`, `subvolume_metrics`, and `rank_metrics`.

## Control Flow
Metric producers fill leaf metric structs and set `updated` where the specific metric supports sparse reporting. `Metrics` encodes update type plus all supported metric groups with version gates for metrics added over time. `metrics_message_t::encode` writes the sequence, rank, client map, subvolume vector, and rank metrics; decode handles older versions by only reading fields present in the encoded struct version and defaulting `rank_metrics` when absent. Dump functions expose the same shape for admin and manager output.

## State And Persistence Behavior
These structs are transient message payloads rather than long-lived local persistence. Backward compatibility is explicit: several DENC blocks are versioned, with latency `mean`, `sq_sum`, and `count` added after the initial `lat`, and aggregate metrics adding dentry, opened/pinned/opened inode, and IO size groups in later versions. The numeric fields are mostly counters or duration aggregates; consumers are responsible for interpreting refresh versus remove.

## Dependencies And Integration Points
The file depends on `Formatter`, `denc`, `utime_t`, CephFS rank types, entity instances, and `mdstypes.h` for `SubvolumeMetric`. It integrates with `MetricsHandler`, `MetricAggregator`, `MMDSMetrics`, MDS messenger dispatch, and manager metric publication. `MDSRank` initializes rank metrics handling and only rank 0 creates the aggregator.

## Risks
Dump field names include apparent typos such as `avg_read_alatency`, `avg_write_alatency`, and `avg_metadata_alatency`; consumers may rely on these spellings. Some `updated` fields are encoded but not dumped. Uninitialized non-default fields in latency metrics should be set by producers before encoding. Versioned decode paths must remain stable because mixed-version clusters can exchange these messages.

## Test Signals
Tests should round-trip every metric struct through DENC and featureful message encode/decode, including older struct versions when fixtures exist. Manager-facing dump tests should cover expected field names. Integration signals include client refresh/remove updates, subvolume metric propagation, rank metrics defaults from older messages, and aggregator handling of multiple `entity_inst_t` clients.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MDSPerfMetricTypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MDSPinger.cc -->
# sources/distributed-fs/ceph/src/mds/MDSPinger.cc

## Purpose
`MDSPinger.cc` implements rank-to-rank ping tracking used to detect lagging MDS ranks through outstanding `MMDSPing` sequence acknowledgments. It maintains per-rank ping sequence state and compares the last acknowledged ping timestamp against `mds_ping_grace`.

## Important APIs, Types, And Functions
`MDSPinger::send_ping` initializes `PingState`, records the outgoing sequence timestamp, increments `last_seq`, and sends an `MMDSPing` through `MDSRank::send_message_mds`. `pong_received` validates that a rank and sequence were outstanding, updates `last_acked_time`, and erases older entries. `reset_ping` removes state for a rank. `is_rank_lagging` checks elapsed coarse monotonic time since the last acknowledged ping.

## Control Flow
Each public method takes the pinger mutex before touching `ping_state_by_rank`. `send_ping` sends while the scoped lock is still held despite a header comment warning not to hold the lock during `send_message_mds`, so this implementation relies on the send path not reentering the pinger lock. Pongs without prior state or without a known sequence are ignored and return false. Lag checks on missing state log an error and return false.

## State And Persistence Behavior
All state is memory-local: per rank, `last_seq`, `seq_time_map`, and `last_acked_time`. State is reset on rank changes or explicit reset and is not journaled. `pong_received` erases entries before the acknowledged sequence but leaves the acknowledged entry and later entries in the map because it erases `[begin, it2)`, not `it2` itself; this means acknowledged sequences can remain until a later pong arrives.

## Dependencies And Integration Points
The implementation depends on `MDSRank`, `MMDSPing`, Ceph config, coarse monotonic time, and MDS logging. It is part of MDS health/metric liveness infrastructure and sends to explicit address vectors supplied by map or caller code.

## Risks
Locking around send deserves attention because the header warns about deadlock. The retained acknowledged sequence may cause map growth if only the latest sequence is repeatedly acknowledged and no later acknowledgments prune it. Lag logic uses send time of the acknowledged ping, not receive time, so a rank can look laggy if no fresh pongs arrive even after one delayed pong is accepted. Configuration changes to `mds_ping_grace` immediately affect detection.

## Test Signals
Unit tests should cover first ping initialization, monotonically increasing sequences, unknown-rank and unknown-sequence pongs, reset behavior, lag threshold behavior with controlled time, and pruning semantics after acknowledging old and new sequences. Integration tests should confirm laggy rank health changes clear after valid pong traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MDSPinger.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MDSPinger.h -->
# sources/distributed-fs/ceph/src/mds/MDSPinger.h

## Purpose
`MDSPinger.h` declares the rank pinger helper used by an `MDSRank` to send ping messages to peer ranks, validate pong responses, reset per-peer tracking, and decide whether a peer is lagging.

## Important APIs, Types, And Functions
The public API is `send_ping(mds_rank_t, const entity_addrvec_t&)`, `pong_received(mds_rank_t, version_t)`, `reset_ping(mds_rank_t)`, and `is_rank_lagging(mds_rank_t)`. Internally it aliases Ceph coarse monotonic clock/time types, starts sequences at `MDS_PINGER_ISN`, and stores `PingState` with `last_seq`, a sequence-to-send-time map, and `last_acked_time`.

## Control Flow
The header describes the intended lifecycle: initialize ping state lazily on first send, mark a pong valid only if the sequence is outstanding, reset state when a rank changes, and compare ack age to detect lag. A mutex protects the rank-state map.

## State And Persistence Behavior
State is volatile and scoped to the pinger object. `last_acked_time` initializes to construction time for each `PingState`; no sequence state survives daemon restart, MDS failover, or explicit `reset_ping`.

## Dependencies And Integration Points
The class depends on MDS rank ids, Ceph mutex/time utilities, `version_t`, address vectors, and a forward-declared `MDSRank` used for message sending. It integrates with `MMDSPing` in the implementation and with MDS rank health or metric code that schedules pings.

## Risks
The header explicitly says to drop the pinger lock before `send_message_mds` to avoid deadlock, so implementations and future changes must preserve that intent. Because the API accepts raw address vectors, callers must ensure they are current for the peer rank. Sequence type and initial value must remain compatible with `MMDSPing` and pong handlers.

## Test Signals
Header-level contract tests should validate API behavior through the implementation: lazy state creation, sequence validity, reset, and lag decisions. Static or code-review checks should also look for lock ordering against `MDSRank::send_message_mds`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MDSPinger.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MDSRank.cc -->
# sources/distributed-fs/ceph/src/mds/MDSRank.cc

## Purpose
`MDSRank.cc` implements the running CephFS MDS rank service: subsystem construction, startup, dispatch, state-machine transitions, recovery, shutdown, admin socket commands, performance counters, client/session operations, OSD-map fencing, and integration with quiesce, metrics, scrub, cache, journal, table, balancer, and messenger components.

## Important APIs, Types, And Functions
Key lifecycle methods are `init`, `tick`, `shutdown`, `handle_mds_map`, `handle_osd_map`, `boot_create`, `boot_start`, `replay_start`, `resolve_start`, `reconnect_start`, `rejoin_start`, `clientreplay_start`, `active_start`, `stopping_start`, and their completion helpers. Dispatch flows through `ms_dispatch`, `_dispatch`, `is_valid_message`, `is_stale_message`, and `handle_message`. Rank services include `send_message_mds`, client send helpers, `forward_message_mds`, `evict_client`, `config_client`, `set_osd_epoch_barrier`, `apply_blocklist`, table accessors, and admin command handlers. Internal helper contexts implement flush-journal and cache-drop workflows.

## Control Flow
Startup constructs Objecter, MDCache, MDLog, MDBalancer, ScrubStack, InoTable, SnapServer/Client, Server, Locker, PurgeQueue, MetricsHandler, and QuiesceDbManager. `init` starts objecter, logging, progress thread, purge queue, and finisher. Incoming messages are filtered for stale peers, deferred while the beacon is laggy, then dispatched by port/type to cache, migrator, server, balancer, tables, locker, scrub, metrics/quiesce, or client logic. `handle_mds_map` is the main state driver: it validates transitions, updates messenger identity/incarnation, detects failed/restarted/recovered peers, starts recovery phases, reconciles snapserver table recovery, wakes waiters, updates cache/metrics/quiesce, and sets OSD barriers on active.

## State And Persistence Behavior
Rank state is a mix of monitor-driven `MDSMap` state, local volatile queues, and durable RADOS/journal structures. Durable pieces include MDLog, sessionmap, inotable, purge queue, snap table, subtree maps, and journaled replay/client operations. Boot paths create or load these structures, replay journals, validate session preallocated inode consistency, and write fresh hierarchy state for new ranks. Shutdown flushes/trims journal and drains cache/purge queue before asking the monitor for stopped state. Client eviction can blocklist addresses and sets an OSD epoch barrier so caps are not issued against stale OSD maps.

## Dependencies And Integration Points
The file is the integration hub for MDS subsystems: `Beacon`, `MDSMap`, `MDCache`, `MDLog`, `Server`, `Locker`, `MDBalancer`, `Migrator`, `SnapServer`, `SnapClient`, `ScrubStack`, `PurgeQueue`, `SessionMap`, `MetricAggregator`, `MetricsHandler`, Objecter, Messenger, MonClient, MgrClient, and admin socket command parsing. It also coordinates with OSD maps, monitor commands, manager task status, perf counters, quiesce code in `MDSRankQuiesce.cc`, and table code through `MMDSTableRequest`.

## Risks
The state machine is highly order-sensitive: missed map epochs, invalid transitions, stale peer messages, or incorrect lock handling can lead to split-brain, replay loops, data loss, or hung recovery. Many callbacks require `mds_lock`; some operations deliberately drop it while waiting. Admin commands can be expensive or asynchronous and must not use `MDSRank` after shutdown-sensitive lock drops. Blocklist and OSD epoch barriers are critical for client fencing. `handle_mds_map` assumes map continuity only partially and compensates with restart detection.

## Test Signals
Strong signals include boot-create/start/replay integration tests, standby-replay takeover, multi-rank failover and rejoin, stale message rejection, laggy beacon deferral, table request routing, client reconnect/reclaim and replay completion, eviction with blocklist/barrier, cache drop and flush journal admin commands, quiesce command dispatch, scrub controls, OSD map blocklist handling, perf counter registration, and invalid transition respawn behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MDSRank.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MDSRank.h -->
# sources/distributed-fs/ceph/src/mds/MDSRank.h

## Purpose
`MDSRank.h` declares the public and dispatcher-facing interface for a CephFS MDS rank. It exposes the subsystem ownership graph, rank state predicates, message-sending APIs, wait queues, lifecycle hooks, admin command handlers, recovery state-machine functions, performance counter ids, memory counter ids, and configuration observer surface.

## Important APIs, Types, And Functions
`MDSRank` owns public services such as `server`, `mdcache`, `locker`, `mdlog`, `balancer`, `scrubstack`, `damage_table`, `inotable`, `snapserver`, `snapclient`, `sessionmap`, `purge_queue`, metrics, and quiesce manager/agent. Public methods include state predicates, `get_table_client/server`, session lookup, queue/waiter management, `send_message_mds`, client send helpers, `forward_message_mds`, OSD epoch barriers, status dump, export target tracking, client eviction/configuration, and path/inode helpers. Protected methods declare the boot/recovery/shutdown state machine. `MDSRankDispatcher` adds `init`, `tick`, `shutdown`, map handling, admin socket dispatch, config observation, session dump, and `ms_dispatch`.

## Control Flow
Consumers call dispatcher methods from the daemon layer; subsystems call public `MDSRank` methods for shared services. State changes flow from `handle_mds_map` into protected transition methods. Finished contexts and replay work flow through rank-owned queues and `ProgressThread`. Admin socket commands enter through `handle_asok_command` and fan out to command helpers, some synchronous under `mds_lock` and some asynchronous via finisher contexts.

## State And Persistence Behavior
The header defines in-memory ownership and durable subsystem entry points rather than encoding itself. Important state includes current and last MDS map state, incarnation, degraded flag, quiesce pointers, waiter vectors/maps, replay queue, OSD epoch barrier, peer map epochs, internal request map, export decay counters, heartbeat handle, stop flag, and active atomic. Persistent state is delegated to owned subsystems such as MDLog, SessionMap, InoTable, PurgeQueue, and Snap tables.

## Dependencies And Integration Points
It includes or forward-declares nearly every MDS subsystem plus Ceph admin socket, log client, tracked op, perf counters, timers, Objecter, Messenger, monitor/manager clients, and Boost.Asio. This header is intentionally broad because MDS subsystems use it as their access point to shared rank services.

## Risks
The header exposes many raw subsystem pointers and public members, so ownership and lifetime discipline are important. `mds_lock` is shared across many callers, and comments identify methods requiring callers to hold or not hold it. Public access to subsystem pointers can make future refactors risky. State predicates are simple comparisons and assume `state` is synchronized with the monitor-driven map.

## Test Signals
Compile coverage is important because many subsystems include this header. Runtime tests should exercise dispatcher lifecycle, message dispatch, waiter queues, state predicates across every MDS state, admin command routing, config-change propagation, active atomic visibility, and shutdown ordering under outstanding queued contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MDSRank.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MDSRankQuiesce.cc -->
# sources/distributed-fs/ceph/src/mds/MDSRankQuiesce.cc

## Purpose
`MDSRankQuiesce.cc` adds quiesce-database and quiesce-agent behavior to `MDSRank`. It handles admin commands for include/exclude/reset/release/cancel/query operations, maintains cluster membership callbacks for the quiesce DB manager, dispatches peer listing and ack messages, and bridges quiesce root requests into `MDCache`.

## Important APIs, Types, And Functions
`command_quiesce_db` validates admin command options, builds a `QuiesceDbManager::RequestContext`, submits it, and formats JSON responses. `quiesce_cluster_update` derives leader/members from `MDSMap`, installs peer send callbacks, injects cancel-all during degraded leadership, adjusts inactive or standby-replay agent callbacks, and updates manager membership. `quiesce_dispatch` handles `MMDSQuiesceDbListing` and `MMDSQuiesceDbAck`. `quiesce_agent_setup` builds a `QuiesceAgent::ControlInterface` with submit, cancel, and ack callbacks.

## Control Flow
Admin command parsing enforces mutually exclusive operations and option constraints before touching the manager. Request contexts format set state, member state, timeouts, expiration, ages, and leader information. Membership updates install lambdas that either loop back to the local manager or send messages to the current leader/peer addresses under `mds_lock`. Active ranks bind the agent to manager updates; inactive ranks respond only in limited ways. Agent submit parses root URIs and either calls `MDCache::quiesce_path` for real roots or, when compiled with debug params, emulates quiesce/failure/pinning.

## State And Persistence Behavior
Quiesce state lives in `QuiesceDbManager` and `QuiesceAgent`; this file coordinates it but does not encode it directly. Membership is derived from MDSMap epoch, filesystem name, leader gid, members, and local gid. During degraded leadership it injects a cancel-all request so active sets do not remain quiescing across unsafe cluster states. Debug dummy requests are in-memory only and keyed by root.

## Dependencies And Integration Points
The file depends on `MDSRank`, `MDCache`, `MonClient`, `QuiesceDbManager`, `QuiesceAgent`, quiesce messages, Boost.URL, timers, formatters, and MDS map membership. It integrates with admin socket command handling in `MDSRank.cc`, map updates through `quiesce_cluster_update`, and peer message dispatch through the MDS messenger.

## Risks
The command validator must prevent ambiguous operations and invalid root/set combinations. Lambdas capture membership and rank state, so stale maps can cause `-ENOENT` sends. Degraded handling intentionally cancels all sets, which is safe but disruptive. Debug URI parameters are compile-gated and must not leak into production behavior. The file catches decode errors but relies on `ms_die_on_bad_msg` policy for fatal handling.

## Test Signals
Tests should cover admin validation errors, default include behavior, query/release/cancel/reset semantics, JSON response shape, leader loopback and remote ack/listing sends, decode-error handling, degraded cancel-all injection, inactive/standby-replay responder behavior, real `MDCache::quiesce_path` submission/cancel, and debug-param emulation where enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MDSRankQuiesce.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MDSTable.cc -->
# sources/distributed-fs/ceph/src/mds/MDSTable.cc

## Purpose
`MDSTable.cc` implements common persistence for MDS tables such as the inode table and snap table. It provides asynchronous full-object load and save against the metadata pool, version tracking, commit waiters, object naming, and error handling shared by table subclasses.

## Important APIs, Types, And Functions
`MDSTable::save` encodes the current `version` plus subclass state, writes the table object with Objecter, and records waiters by needed version. `save_2` completes a write, advances `committed_version`, and finishes waiters up to the saved version. `reset` delegates to subclass `reset_state` and marks the table active. `get_object_name` chooses `mds<rank>_<table>` for per-rank tables or `mds_<table>` for global tables. `load` issues `read_full`, and `load_2` decodes version and subclass state.

## Control Flow
Saves are only legal in active state. If a caller asks to wait for a version already being committed, the context is queued without issuing another write. Otherwise the table serializes and writes the full object. Loads require `STATE_UNDEF`, move through `STATE_OPENING`, then active on completion. Read errors damage or respawn the rank depending on error; decode errors also mark the rank damaged.

## State And Persistence Behavior
Persistent bytes are `version` followed by subclass-specific encoded state. Runtime versions track current, committing, committed, and projected values. `waitfor_save` queues contexts by version and is drained in ascending order after successful writes. Full-object writes mean each save replaces the whole persisted table object.

## Dependencies And Integration Points
The code depends on `MDSRank`, `MDSContext`, Objecter, Finisher, RADOS object names/locators, metadata pool id, `SnapContext`, and subclass implementations of `encode_state` and `decode_state`. Snap and inode table classes build on this base.

## Risks
Full-object persistence can be expensive for large tables and makes encode/decode correctness critical. Save error policy delegates to `MDSRank::handle_write_error`; depending on config it may ignore, force readonly, or respawn. Load errors call `damaged`, which is intentionally severe. Version waiters can leak if writes never complete. Per-MDS object names depend on `rank` being set before use.

## Test Signals
Tests should cover object naming for per-MDS and global tables, reset state, load success and decode failure, save coalescing by needed version, waiter completion ordering, write error handling including blocklist, and subclass encode/decode round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MDSTable.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MDSTable.h -->
# sources/distributed-fs/ceph/src/mds/MDSTable.h

## Purpose
`MDSTable.h` declares the abstract base class for MDS tables persisted in the metadata pool. It centralizes table naming, active/opening state, version counters, load/save API, and subclass hooks for table-specific state.

## Important APIs, Types, And Functions
The public API includes `set_rank`, version getters, `force_replay_version`, state predicates, `reset`, `save`, `shutdown`, `get_object_name`, and `load`. Subclasses must implement `reset_state`, `decode_state`, and `encode_state`. Protected members include table name, per-MDS flag, rank, state, version counters, and save waiters.

## Control Flow
Subclasses are expected to set rank where needed, call `load` during boot or recovery, call `reset` when creating fresh state, and call `save` when durable table state must be written. `shutdown` saves active tables best-effort with no finish context.

## State And Persistence Behavior
The class tracks `STATE_UNDEF`, `STATE_OPENING`, and `STATE_ACTIVE`. Version fields distinguish current, committing, committed, and projected versions. It does not define the table payload; it only guarantees a version prefix plus subclass-managed payload in the implementation.

## Dependencies And Integration Points
It depends on Ceph buffer/object/types, rank ids, `MDSRank`, and MDS contexts. It is the base for server/client table implementations such as snap table and inode allocation structures.

## Risks
The abstraction assumes subclasses correctly update `version` and projected versions around mutations. `force_replay_version` can override version state and should be used only in replay recovery contexts. `shutdown` silently skips inactive tables and does not surface save errors to callers.

## Test Signals
Tests should instantiate a small fake table subclass to verify load/save/reset state transitions, version counters, object naming, and `shutdown` behavior. Subclass tests should assert that encoded payload follows the base version prefix.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MDSTable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MDSTableClient.cc -->
# sources/distributed-fs/ceph/src/mds/MDSTableClient.cc

## Purpose
`MDSTableClient.cc` implements the client half of distributed MDS table mutation. It sends prepare and commit messages to the table server, records pending state, handles agreement and acknowledgments, logs ACKs, and resends work after table-server recovery.

## Important APIs, Types, And Functions
`handle_request` processes negative table-server reply opcodes: query replies, notify-prep, agree, ack, and server-ready. `_prepare` allocates or defers request ids and sends `TABLESERVER_OP_PREPARE`. `commit` moves an agreed tid into pending commit state and sends `TABLESERVER_OP_COMMIT`. Recovery helpers are `got_journaled_agree`, `got_journaled_ack`, `resend_commits`, `resend_prepares`, and `handle_mds_failure`. `C_LoggedAck` logs `ETableClient` ACK completion.

## Control Flow
Before resolve, incoming table messages are deferred if the rank wants resolve. Prepares wait until the server has supplied a starting request id through `SERVER_READY`; otherwise they sit in `waiting_for_reqid`. An `AGREE` completes the original prepare context, stores tid-to-reqid mapping, and optionally returns a reply buffer. `commit` asserts the tid was prepared, marks the log segment pending, calls subclass `notify_commit`, and sends commit if server-ready. ACK removes the pending tid, updates the log segment, and journals a client ACK entry before waking waiters.

## State And Persistence Behavior
Runtime state includes last request id, server-ready flag, pending prepares by request id, prepared update tid mappings, waiting prepares, pending commits by tid, and ack waiters. Durable recovery state comes from MDLog `ETableClient` entries: journaled agrees and acks rebuild pending commit or remove it. The client itself does not write table data; it ensures committed table mutations are acknowledged and replayable.

## Dependencies And Integration Points
The file depends on `MDSRank`, `MDSMap` tableserver lookup, `MMDSTableRequest`, `MDLog`, `LogSegment`, `ETableClient`, retry contexts, and subclass callbacks. `SnapClient` is the visible table client in this subset.

## Risks
Protocol correctness depends on idempotent resend paths and strict tid/reqid mapping. Stray `AGREE` handling can send rollback only when the server is not ready, so recovery ordering matters. ACK handling requires the log segment pending set to contain the tid; otherwise ACKs are ignored. Several killpoint config asserts intentionally crash in tests. If `SERVER_READY` is missed, prepares remain deferred.

## Test Signals
Tests should cover prepare before and after server-ready, agree completion with reply buffer, duplicate agree, stray agree rollback, commit resend after server failure, ACK journaling and waiter wakeup, recovery from journaled agree/ack, and server failure clearing readiness only for the current tableserver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MDSTableClient.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MDSTableClient.h -->
# sources/distributed-fs/ceph/src/mds/MDSTableClient.h

## Purpose
`MDSTableClient.h` declares the abstract client-side protocol helper for MDS table mutations. It provides prepare/commit/recovery plumbing while leaving table-specific query, notify, and commit behavior to subclasses.

## Important APIs, Types, And Functions
Public methods include `handle_request`, `_prepare`, `commit`, resend helpers, journal recovery hooks, `has_committed`, `wait_for_ack`, `get_journaled_tids`, `handle_mds_failure`, and `is_server_ready`. Subclasses implement `resend_queries`, `handle_query_result`, `handle_notify_prep`, and `notify_commit`. `_pending_prepare` stores an onfinish context, tid output pointer, optional reply buffer pointer, and encoded mutation.

## Control Flow
Callers prepare a mutation to receive a table tid, journal or otherwise use that tid, then call `commit` with the owning log segment. During failover, journal replay feeds `got_journaled_agree` or `got_journaled_ack`, and server-ready triggers resend of queries, prepares, and commits.

## State And Persistence Behavior
The header defines volatile protocol state maps for pending prepare, prepared update, waiting-for-reqid, pending commit, and ack waiters. It exposes journaled tids by reading pending commits. Durable state is externalized in MDS log entries, not in this class directly.

## Dependencies And Integration Points
It depends on bufferlists, rank ids, Ceph refs, `LogSegmentRef`, `MMDSTableRequest`, and `MDSRank`. It is consumed by table-specific clients such as the snap client.

## Risks
`_prepare` writes through raw `version_t*` and `bufferlist*` supplied by the caller; those must outlive asynchronous completion. `wait_for_ack` stores raw contexts and relies on ACK journaling to wake them. Subclasses must resend queries and process notify-prep correctly or recovery can stall.

## Test Signals
Compile-time fake subclasses can validate abstract callback invocation. Integration tests should prove prepare/commit lifecycle, ack waiters, journal replay reconstruction, and failover resend behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MDSTableClient.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MDSTableServer.cc -->
# sources/distributed-fs/ceph/src/mds/MDSTableServer.cc

## Purpose
`MDSTableServer.cc` implements the server half of MDS table mutation. It serializes prepare, commit, rollback, server-update, notification, and recovery behavior on top of `MDSTable` persistence and MDLog `ETableServer` entries.

## Important APIs, Types, And Functions
`handle_request` routes query, prepare, commit, rollback, and notify-ack requests. `_note_prepare`, `_note_commit`, `_note_rollback`, and `_note_server_update` update version and pending state during live operation or replay. `handle_prepare` journals a prepare; `_prepare_logged` applies subclass preparation and sends or delays `AGREE`. `handle_commit` journals commit; `_commit_logged` applies subclass commit and sends `ACK`. Rollback and server update mirror that pattern. Recovery uses `finish_recovery`, `_do_server_recovery`, `handle_mds_recovery`, and `handle_mds_failure_or_stop`.

## Control Flow
Prepare increments projected version and logs the mutation before applying table-specific `_prepare`. If `_notify_prep` is required, the reply is held in `pending_notifies` until active clients send notify ACKs; otherwise the requester gets `AGREE` immediately. Commit for a pending tid is journaled once, guarded by `committing_tids`, then applied and acknowledged. Already committed tids receive immediate ACK. Recovery resends agrees for pending tids, computes next request ids per active client, and sends `SERVER_READY`.

## State And Persistence Behavior
Persistent server state consists of subclass server state plus `pending_for_mds`, encoded by `encode_state`. Runtime-only state includes `active_clients`, `recovered`, `committing_tids`, and `pending_notifies`. Every table mutation advances `version`; replay paths also synchronize `projected_version`. Pending prepares survive table load so the server can reconstruct agrees after failover.

## Dependencies And Integration Points
The implementation depends on `MDSRank`, MDLog, `ETableServer`, `MMDSTableRequest`, and subclass hooks for table-specific prepare/reply/commit/rollback/server-update behavior. SnapServer is the key table-server consumer in this area.

## Risks
The protocol relies on journal-before-reply ordering. A missing notify ACK can delay agree replies until failure handling removes the peer from the gather. `handle_rollback` asserts the tid is pending and not committing; unexpected rollback can crash. `tid > version` commit is asserted as impossible. Recovery must compute next request ids correctly or clients may reuse ids unsafely.

## Test Signals
Tests should cover prepare-agree, notify-prep gather, commit-ack, duplicate commit while committing, already committed commit ACK, rollback, server updates, encode/decode of pending prepares, recovery resend of agrees/server-ready, new client recovery after server recovered, and failure/stop removing notify waiters or rolling back unsent replies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MDSTableServer.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MDSTableServer.h -->
# sources/distributed-fs/ceph/src/mds/MDSTableServer.h

## Purpose
`MDSTableServer.h` declares the abstract server-side table protocol class. It extends `MDSTable` with distributed prepare/commit/rollback/query handling, table-server recovery hooks, active-client tracking, and encoded pending prepare state.

## Important APIs, Types, And Functions
Subclasses implement `handle_query`, `_prepare`, `_get_reply_buffer`, `_commit`, `_rollback`, `encode_server_state`, and `decode_server_state`; they may override `_server_update` and `_notify_prep`. Public helpers record replayed operations with `_note_*`, handle incoming requests, perform server updates, reset/encode/decode state, finish recovery, and handle peer recovery/failure. Private protocol methods implement logged prepare/commit/rollback/update and notify ACK handling.

## Control Flow
The server accepts client table requests, journals them through MDLog contexts, then calls subclass hooks only after the journal event is durable. Recovery code rebuilds state from encoded table state and pending operations, then notifies active clients.

## State And Persistence Behavior
The class stores table id, recovered flag, active client set, pending prepares by tid, currently committing tids, and pending notification gathers. Only subclass state plus `pending_for_mds` are encoded in table object state; other members are runtime coordination state rebuilt during recovery.

## Dependencies And Integration Points
It depends on `MDSTable`, `mds_table_pending_t`, table name helpers, Ceph refs, and `MMDSTableRequest`. It is used by table-specific servers, especially snap table server, and is driven by `MDSRank` table request routing.

## Risks
Subclasses must encode enough server state to make pending tids meaningful after replay. `_notify_prep` changes reply ordering and must be paired with notify ACK handling. Copy constructor and assignment exist for dencoder support, so pointer/runtime members must remain safely copyable or ignored in tests.

## Test Signals
Fake subclass tests should verify abstract protocol hooks, encode/decode wrapping, reset, replay note helpers, and recovery APIs. Integration tests should validate table-specific server behavior under MDS failover.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MDSTableServer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/Mantle.cc -->
# sources/distributed-fs/ceph/src/mds/Mantle.cc

## Purpose
`Mantle.cc` implements the Lua-backed balancer policy runner for MDS load balancing. It loads a policy script, exposes current rank id and per-rank metric tables, executes the script, and converts the returned Lua table into target-rank weights.

## Important APIs, Types, And Functions
`Mantle::balance` takes a script string, local rank, vector of metric maps, and output map of rank targets. `Mantle::Mantle` creates a Lua state, loads a restricted set of standard libraries, and registers `BAL_LOG`. `dout_wrapper` lets Lua scripts emit Ceph debug log messages at a requested level.

## Control Flow
Each balance call clears the Lua stack, compiles the supplied script, sets global `whoami`, builds global `mds` as an indexed table of metric dictionaries, executes the script expecting one return value, validates that the return value is a table, and iterates integer keys/numeric values into `my_targets`. Compilation, execution, or response-shape failures return `-EINVAL`.

## State And Persistence Behavior
The Lua VM is held for the life of the Mantle object, but each `balance` call resets the stack and overwrites globals. No policy or result is persisted by this class. The caller owns the script source, metrics, and output target map.

## Dependencies And Integration Points
The implementation depends on Lua C APIs, Ceph debug logging, MDS rank types, and balancer callers that provide metrics and consume target weights. `MDBalancer` is the natural integration point, with the MDS map `balancer` string identifying a policy object elsewhere.

## Risks
Scripts run inside the MDS process, so even with a limited library set they can consume CPU or memory. The metric table uses zero-based C++ vector indices via `lua_seti`, which policy authors must understand. Output validation only checks integer keys and numeric values, not rank range or negative/NaN weights. `my_targets` is not cleared by `balance`, so callers should pass an empty map or handle stale entries.

## Test Signals
Tests should cover valid script output, compile errors, runtime errors, malformed non-table returns, malformed key/value entries, BAL_LOG behavior, zero and multiple rank metrics, repeated calls on one Mantle instance, and caller-side validation of target ranks/weights.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/Mantle.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/Mantle.h -->
# sources/distributed-fs/ceph/src/mds/Mantle.h

## Purpose
`Mantle.h` declares the Lua-based MDS balancer policy wrapper. It gives C++ balancer code a compact interface for running a policy script against per-rank metric maps and receiving target weights.

## Important APIs, Types, And Functions
The class owns a `lua_State *L`, constructs it in `Mantle()`, closes it in the destructor, and exposes `balance(const std::string&, mds_rank_t, const std::vector<std::map<std::string,double>>&, std::map<mds_rank_t,double>&)`. The output map associates destination MDS ranks with numeric weights or scores.

## Control Flow
Callers instantiate `Mantle`, then call `balance` whenever a policy decision is needed. The implementation handles script loading, metric table publication, execution, and output parsing.

## State And Persistence Behavior
Only the Lua VM pointer is stored. There is no encoded or RADOS-persisted state. The destructor is responsible for releasing the VM if construction succeeded.

## Dependencies And Integration Points
The header depends on Lua headers, STL containers, and CephFS rank types. It integrates with the MDS balancer and indirectly with metrics collected from active ranks.

## Risks
The header exposes raw `lua_State*` as a protected member; subclassing or future changes must preserve ownership rules. Copying is not disabled explicitly, so accidental copies would duplicate a raw VM pointer and risk double close; current usage should keep Mantle non-copied. Script safety and runtime limits are not represented in the API.

## Test Signals
Compile and lifecycle tests should construct/destroy Mantle repeatedly, prevent or avoid copying, and exercise `balance` with controlled metric maps. Integration tests should verify balancer behavior when policy scripts fail or return invalid targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/Mantle.h -->
