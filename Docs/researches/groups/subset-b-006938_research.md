# subset-b-006938

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/OSD.h -->
# sources/distributed-fs/ceph/src/osd/OSD.h

## Purpose
`OSD.h` declares the core classic Ceph OSD daemon surface: `OSD`, its `OSDService` helper, per-shard scheduling state, PG-slot ordering state, and the object-store benchmark helper. The header is the coordination contract between OSD message dispatch, OSDMap publication, PG lifecycle, recovery/backfill, scrub scheduling, heartbeat health, monitor reporting, admin-socket commands, and ObjectStore persistence.

## Important APIs, Types, and Functions
`OSDService` exposes service functions used by PGs and OSD internals: scheduler enqueueing, map publication and pre-publication, map sharing to peers, cluster and heartbeat connection lookup, op error replies, misdirected-op handling, scrub service access, PG locking, snap trim totals, tiering objecter finishers, watcher notification IDs, recovery and scrub queues, PG temp/create reporting, map cache access, OSD stats/fullness checks, boot/up/bind epoch accessors, heartbeat stamp lookup, readable lease renewal, stopping state, and PG timers.

The `OSDService` state model is broad: `superblock`, published and next OSDMaps, map reservation counts, agent queues for cache tiering/promotion/flush, promotion throttling counters, objecter and finisher shards, watch and recovery timers, backfill/snap/scrub reservers, PG merge readiness maps, `pg_temp` desired/pending maps, created-PG reports, recovery throttling lists, OSDMap LRU caches, stat/fullness state, epoch state, heartbeat stamps, lease timer, and stop state.

`OSDShardPGSlot` describes ordering and wait state for one PG slot inside a shard. It holds the PG ref, `to_process` queue, running count, client wait queue, epoch-keyed peering wait queues, requeue generation, split wait epochs, current slot epoch, intrusive epoch-order hook, and merge wait epoch.

`OSDShard` declares per-shard queueing and map consumption machinery: shard locks, `pg_slots`, intrusive `pg_slots_by_epoch`, min-PG-epoch waiters, the per-shard `OpScheduler`, `ContextQueue`, erasure-code extent-cache LRU, PG attach/detach, epoch update, map consumption, PG-slot waking, split/merge identification and priming, and op queue type lookup.

`OSDBenchTest` encapsulates local ObjectStore write benchmarks. It declares precheck, optional object prefill, write test execution, flush/commit wait, cleanup transaction, elapsed/prefill/bandwidth/iops accessors, and error-string reporting.

`OSD` itself derives from `Dispatcher` and `md_config_obs_t`. Major APIs include config observers, startup/shutdown (`pre_init`, `init`, `final_init`, `shutdown`, `fast_shutdown` via service, signal handling), static metadata and mkfs helpers, map object naming helpers, object-store metadata peek/write helpers, ObjectStore benchmark runner, NUMA/FUSE helpers, op queue and shard sizing helpers, message fast-dispatch gates, PG creation/removal and peering handlers, recovery dispatch, scrub rescheduling, command handling, status collection, session waiting-on-map handling, heartbeat dispatch/reset, admin-socket routing, and performance-query plumbing.

## Control Flow
The header documents a layered dispatch path. Messenger fast dispatch accepts client ops, peering, recovery, scrub, heartbeat, command, and lease messages. OSD dispatch turns messages into scheduler items keyed by PG/shard. `ShardedOpWQ` enqueues items into each shard scheduler, moves dequeued work into `OSDShardPGSlot::to_process`, waits when PGs or maps are unavailable, preserves per-client and per-peer ordering, and requeues waiters when a PG materializes, a split completes, or a map advances.

Map flow is split between globally visible and pre-published state. `OSDService::publish_map` and `get_osdmap` expose the active map under `publish_lock`; `pre_publish_map`, `get_nextmap_reserved`, `release_map`, and `await_reserved_maps` coordinate a next map that helpers may use only while respecting map reservations. `OSD::handle_osd_map`, `track_pools_and_pg_num_changes`, `consume_map`, `activate_map`, and `advance_pg` are declared as the path that persists maps, tracks PG split/merge history, updates shards, and advances PGs through peering state.

PG lifecycle flow runs through `_make_pg`, `register_pg`, `load_pgs`, `handle_pg_create_info`, fast PG create/notify/info/remove handlers, split/merge helpers, pending create throttles, and deletion queueing. The shard comments define how missing PGs, future epochs, split children, and merge waiters are held without violating client or peer ordering.

Recovery, scrub, and snap trim are queued through `OSDService` methods that create scheduler items or scrub event messages with costs and priorities. Recovery uses `awaiting_throttle`, active/reserved push counters, pause/defer state, and scheduler-specific sleep paths. Scrub uses explicit queues for primary and replica state transitions such as resched, pushes update, applied update, chunk free/busy, unblocking, digest update, replica maps, finish, and next chunk.

Heartbeat flow is isolated from the main op path. `HeartbeatDispatcher` fast-dispatches pings, and `T_Heartbeat` runs `heartbeat_entry`, which maintains peer connections, ping history, health classification, peer update needs, and monitor failure reporting.

## State and Persistence Behavior
Persistent ObjectStore state surfaced here includes the OSD superblock, meta collection handle, osdmap and incremental-osdmap objects (`osdmap.<epoch>` and `inc_osdmap.<epoch>`), snapmapper, purged snapshots, final pool info, PG num history, PG collections, and mkfs/write-meta artifacts. `write_superblock`, `read_superblock`, `trim_maps`, `trim_stale_maps`, `write_meta`, `peek_meta`, and `recursive_remove_collection` are the persistence-facing declarations.

Long-lived in-memory state includes atomic OSD daemon state, atomic/current OSDMap refs, PG count, pending creates, sessions waiting for newer maps, heartbeat peer state, failure queues, monitor report timestamps, full/nearfull/failsafe state, map caches, stat counters, op tracker, perf query limits, timers, worker queues, and Objecter/tiering state. Most shared state is guarded by explicit Ceph locks; the header also calls out lock ordering for PG map interactions: `PG::lock`, then `ShardData::lock`, then `OSD::pg_map_lock`.

## Dependencies and Integration Points
This header integrates with `PG.h`, `OpRequest.h`, `Session.h`, `ObjectStore`, `OSDMap`, `Messenger`, monitor and manager clients, `LogClient`, `OpScheduler`, `AsyncReserver`, scrubber services, timers, finishers, shared/simple LRUs, perf counters, admin socket hooks, and many OSD message types. `OSDService` is intentionally friend-accessible to `OSD`, `PG`, `PrimaryLogPG`, and scrub classes, making it the common service layer for placement-group code.

Monitor integration appears through OSDMap subscriptions, boot/preboot, metadata collection, alive/up-through beacons, failure reports, PG temp/create reports, full-status updates, and purged-snap replies. Client and peer integration appears through session wait queues, op error replies, backoff/reset cleanup, objecter tiering, heartbeat peers, and direct cluster/client messenger send helpers.

## Risks
The main risks are concurrency and ordering regressions. PG-slot queues must preserve client ordering and peer peering ordering while allowing map waits, PG creation, split waits, and merge waits. OSDMap pre-publication and reservation handling must avoid using stale maps to reopen connections to OSD instances that are about to go down. Recovery and scrub queues share scheduler resources and must keep cost/priority semantics consistent across weighted-priority and mclock paths.

State risks include stale OSDMap persistence leaks, incorrect PG num history for split/merge detection, full-status misclassification, missed heartbeat failures or false positives, leaked session/message/connection reference cycles, lingering PG temp/create reports, and ObjectStore cleanup errors in mkfs, benchmarks, or PG deletion.

Security and availability risks include fast-dispatch accepting a broad set of message types, peer identity gates in `require_mon_peer`, `require_mon_or_mgr_peer`, and `require_osd_peer`, admin-socket command routing to PGs, and `filter_xattrs` preserving only underscore-prefixed internal xattrs.

## Test Signals
Useful tests include OSDMap publication/reservation races, map trimming and stale-map cleanup, PG creation under max-PG throttles, split and merge wait/requeue behavior, ordered client ops across map waits, peering message ordering by peer, session reset cleanup, recovery pause/defer/sleep throttling, scrub event queue transitions, heartbeat peer add/remove and stale/unhealthy detection, full/backfillfull/nearfull/failsafe thresholds including injected full states, mkfs/read-superblock/peek-meta paths, benchmark cleanup after failures, and messenger fast-dispatch authentication/refusal/reset handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/OSD.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/OSDCap.cc -->
# sources/distributed-fs/ceph/src/osd/OSDCap.cc

## Purpose
`OSDCap.cc` implements parsing, rendering, matching, profile expansion, network restriction, capability merging, and authorization checks for Ceph OSD capability strings. It turns monitor/auth cap text such as `allow rwx pool foo`, `allow class rbd metadata_list`, `allow *`, `profile rbd`, or app-tag grants into `OSDCap` objects that can be checked against pool, namespace, object, class-operation, application metadata, and client address.

## Important APIs, Types, and Functions
Stream operators render `osd_rwxa_t`, `OSDCapSpec`, `OSDCapPoolNamespace`, `OSDCapPoolTag`, `OSDCapMatch`, `OSDCapProfile`, and `OSDCapGrant`. Match helpers include `OSDCapPoolNamespace::is_match`, `OSDCapPoolNamespace::is_match_all`, `OSDCapPoolTag::is_match`, `OSDCapPoolTag::is_match_all`, `OSDCapMatch::is_match`, and `OSDCapMatch::is_match_all`.

Grant-level logic is in `OSDCapGrant::set_network`, `allow_all`, `is_capable`, `expand_profile`, and `to_string`. Cap-level logic is in `OSDCap::allow_all`, `set_allow_all`, `is_capable`, `parse`, `merge`, and `to_string`.

`OSDCapParser` is a Boost.Spirit Qi grammar. It defines quoted and unquoted strings, optional pool and namespace clauses, object prefixes, application tags, wildcard/all spelling, rwx/class-read/class-write specs, explicit class/method specs, profile specs, optional `network` clauses, grant separators, and the top-level cap.

## Control Flow
Authorization starts at `OSDCap::is_capable`, which creates a `class_allowed` vector sized to the operation's class calls, then scans grants in order. A single grant that accepts the whole operation returns success.

`OSDCapGrant::is_capable` first rejects invalid or nonmatching network restrictions with `parse_network`/`network_contains`. Profile grants recurse through cached `profile_grants`. Non-profile grants then require the pool/namespace/tag/object match to pass. Read and write intent are checked against `OSD_CAP_R` and `OSD_CAP_W`. If the op invokes classes, `allow *` immediately succeeds; otherwise each class call can be allowed by an explicit `allow class <class> [method]` spec or by class read/write bits (`x`, `class-read`, `class-write`) only when `OpInfo::ClassInfo::allowed` says the class is eligible. Every class call must become allowed for the grant to pass.

Parser control flow accepts either `allow <capspec> <match>`, `allow <match> <capspec>`, or `profile <name> ...`, each with optional `network`. Grants are separated by semicolons or commas. `OSDCap::parse` requires the entire input to be consumed and clears all grants on failure so partially parsed privileges are not retained.

Profile expansion is deterministic. `read-only` expands to read on the profile pool/namespace. `read-write` expands to read/write. `rbd` adds special `rbd_info`, `rbd_children`, `rbd_mirroring`, `rbd metadata_list`, and full rwx grants for the profile pool/namespace. `rbd-read-only` adds `rbd metadata_list`, read plus class-read, and `rbd child_attach`/`child_detach` for `rbd_header.` objects.

`OSDCap::merge` is specialized for a one-grant incoming cap, primarily app-tag capability updates. It updates an existing grant with the same app/key/value when the allow mask differs, keeps idempotent matches unchanged, or appends a new tag grant otherwise.

## State and Persistence Behavior
This file does not persist data directly. It mutates in-memory `OSDCap::grants`, `OSDCapGrant::profile_grants`, parsed network fields, and grant allow masks. Persistence is indirect: monitor/auth code stores cap strings and uses this parser and `to_string`/`merge` behavior when validating or updating OSD caps.

Important state invariants are that failed parses leave `grants` empty; profile grants are expanded and cached inside the grant at construction; `network_valid` records whether the textual network parsed; and cap checks accumulate class-call permissions across grants through one shared `class_allowed` vector during an `OSDCap::is_capable` call.

## Dependencies and Integration Points
The implementation depends on Boost.Spirit Qi/Phoenix/Fusion for parsing, Boost string predicates for namespace wildcard matching, Ceph debug/config headers, `include/ipaddr.h` for network parsing and containment, `OSDCap.h` for data structures, and `osd_op_util.h` through `OpInfo::ClassInfo`.

Monitor integration is visible in `AuthMonitor.cc`, which parses OSD caps and merges cap updates, and `OSDMonitor.cc`, which parses OSD caps to reason about writable OSD permissions. At runtime the OSD operation path can use `OSDCap::is_capable` to decide whether a client operation over a pool/namespace/object/class set is authorized.

## Risks
Authorization risks center on parser ambiguity and match semantics. The grammar accepts both capspec-before-match and match-before-capspec forms, optional fields, wildcards, quoted empty namespaces, namespace suffix `*`, and tag wildcards; regressions here can silently broaden or narrow permissions. Namespace wildcard matching treats a namespace ending in `*` as a prefix match. Object prefix uses `object.find(prefix) == 0`, so empty or poorly quoted prefixes matter.

Class authorization is subtle because explicit class/method grants and class read/write bits interact with `classes[i].allowed`; bugs can over-permit class execution or deny valid RBD workflows. `OSDCap::is_capable` keeps `class_allowed` across grants, so multiple grants may collectively satisfy class calls, while read/write checks are still per matching grant. `OSDCap::merge` only compares tag fields and ignores other match dimensions, with an in-code TODO for cases such as `allow rw tag cephfs *`.

Network restrictions fail closed when parsing fails, but incorrect network parsing, address family handling, or missing client address propagation would affect access. `to_string` is lossy for profiles, networks, object prefixes, pool/namespace matches, class-name specs, and some class-write formatting choices, so it should not be treated as a canonical serializer for every parsed cap form.

## Test Signals
Tests should cover successful and failed parse strings; full-consumption parse failures; `allow *` and `allow all`; all rwx/class-read/class-write combinations; capspec-before-match and match-before-capspec forms; quoted pool/object/tag values; empty namespace quotes; namespace prefix wildcard; object prefix matching; pool tag wildcard key/value cases; profile expansion for read-only, read-write, rbd, and rbd-read-only; network allow/deny and invalid networks; explicit class/method grants; multi-class operations satisfied by one or more grants; `merge` idempotent/update/append behavior; and failure clearing existing grants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/OSDCap.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/OSDCap.h -->
# sources/distributed-fs/ceph/src/osd/OSDCap.h

## Purpose
`OSDCap.h` declares the OSD capability data model and authorization API. It represents authenticated-user OSD caps as grants with allow masks, class/method permissions, pool/namespace/tag/object match constraints, optional network restrictions, and named profiles. The comments define the supported user-facing cap model and warn that `*` caps imply full administrative message permissions and should be reserved for monitors and OSDs.

## Important APIs, Types, and Functions
Capability bits are `OSD_CAP_R`, `OSD_CAP_W`, `OSD_CAP_CLS_R`, `OSD_CAP_CLS_W`, `OSD_CAP_X` as combined class read/write, and `OSD_CAP_ANY` for `*`. `osd_rwxa_t` wraps an 8-bit mask with assignment and conversion helpers.

`OSDCapSpec` stores either an allow mask or an explicit `class_name`/`method_name` permission. `allow_all()` identifies `OSD_CAP_ANY`.

`OSDCapPoolNamespace` stores an optional pool name and optional namespace. It declares `is_match` and `is_match_all`.

`OSDCapPoolTag` stores an application metadata predicate (`application`, `key`, `value`) and declares tag matching against nested application metadata maps. It is adapted with `BOOST_FUSION_ADAPT_STRUCT` so the Qi parser in `OSDCap.cc` can populate it directly.

`OSDCapMatch` combines pool/namespace constraints, pool tag constraints, and object prefix constraints. Its constructors support tag-only, pool/namespace-only, pool-prefix, pool-namespace-prefix, app tag, and namespace-tag forms. It declares `is_match` and `is_match_all`.

`OSDCapProfile` stores a profile name and optional pool/namespace scope. `is_valid()` is a simple non-empty-name check.

`OSDCapGrant` combines a match, spec, profile, optional textual and parsed network, network prefix, network validity, and cached `profile_grants`. It declares `set_network`, `allow_all`, `is_capable`, `expand_profile`, and `to_string`.

`OSDCap` is the top-level vector of grants. It declares `allow_all`, `set_allow_all`, `parse`, `merge`, `to_string`, and the operation-level `is_capable` check. The inline stream operator renders it as `osdcap` plus the grants vector.

## Control Flow
The declared authorization flow is hierarchical. An `OSDCap` contains grants; each `OSDCapGrant` either evaluates its direct match/spec/network or delegates to expanded profile grants. A direct grant matches request context using `OSDCapMatch`, checks read/write intent against `OSDCapSpec::allow`, and evaluates class operation permissions against `OpInfo::ClassInfo`. The top-level `OSDCap::is_capable` returns true when the grant set collectively authorizes the operation.

Parsing is declared on `OSDCap` but implemented in `OSDCap.cc`; it fills the grant vector from the textual grammar. `merge` is declared for applying another parsed one-grant cap into an existing cap set. `set_allow_all` is the imperative shortcut for replacing current grants with unrestricted access.

## State and Persistence Behavior
The header defines only in-memory structures. No encoding/decoding or ObjectStore persistence is declared here. Persistent cap storage elsewhere is expected to be textual and parsed into these structures. The important state-bearing fields are the ordered `grants` vector, cached profile expansions in each grant, textual plus parsed network representation, `network_valid`, and optional namespace values that distinguish absent namespace constraints from an explicit empty namespace.

## Dependencies and Integration Points
`OSDCap.h` depends on Ceph base types (`include/types.h`), OSD operation class metadata (`osd/osd_op_util.h`), `entity_addr_t` for client/network checks, Boost.Optional for optional namespaces, Boost.Fusion for parser struct adaptation, and standard containers/streams.

It is included by `OSDCap.cc` for implementation, monitor/auth code for validating and updating cap strings, OSD monitor code for checking whether caps imply writable OSD access, and OSD operation authorization code that needs `OSDCap::is_capable`.

## Risks
Because this header is the authorization contract, small semantic changes have security impact. Distinguishing absent namespace from explicit empty namespace is important. `OSD_CAP_X` is not an independent bit; it is the union of class read and class write. `OSD_CAP_ANY` is `0xff`, so callers must use `allow_all()` or bit checks consistently. Profile validity is name-only, so unknown profile names can exist structurally but expand to no grants. Network restrictions carry both original string and parsed state; callers must preserve both when rendering, auditing, or evaluating.

Constructor overloads for `OSDCapMatch` are convenient but easy to misuse because several accept strings with different meanings. The top-level `merge` contract is not a general cap union; implementation assumes a one-grant incoming cap and has specialized tag behavior.

## Test Signals
Header-level test signals include compile coverage for all constructor forms, stream rendering of all declared types, parser population of `OSDCapPoolTag` through Boost.Fusion adaptation, `allow_all` behavior for unrestricted direct and profile grants, namespace absent versus empty versus wildcard behavior, network-set construction, `set_allow_all` replacement semantics, and `merge` precondition enforcement with one-grant inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/OSDCap.h -->
