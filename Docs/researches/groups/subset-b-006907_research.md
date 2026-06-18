# subset-b-006907 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/librados/librados_cxx.cc -->
# sources/distributed-fs/ceph/src/librados/librados_cxx.cc

## Purpose
This file is the C++ librados facade over Ceph's internal `RadosClient`, `IoCtxImpl`, `ObjectOperationImpl`, completion, iterator, and objecter machinery. It implements most public `librados::Rados`, `librados::IoCtx`, `ObjectReadOperation`, `ObjectWriteOperation`, object-list cursor, watch/notify, locking, snapshot, pool, command, and asynchronous completion methods declared in `include/rados/librados.hpp`. The file is mostly an adapter layer: it converts C++ API types into internal Ceph types such as `object_t`, `SnapContext`, `bufferlist`, `hobject_t`, `ObjectOperation`, `pg_t`, and `object_locator_t`, delegates to `IoCtxImpl` or `RadosClient`, and preserves older API names and overloads for compatibility.

## Important APIs, Types, and Functions
`ObjectOperation::set_op_flags2`, `ObjectReadOperation::*`, and `ObjectWriteOperation::*` build internal OSD operations by appending stat, read, sparse read, checksum, xattr, omap, cache, tiering, manifest, compare, class-call, write, truncate, remove, rollback, and allocation-hint ops into `impl->o`. `get_op_flags()` and `translate_flags()` from `librados_util.cc` translate public flags to `CEPH_OSD_OP_FLAG_*` and `CEPH_OSD_FLAG_*`.

`ObjectOpCompletionCtx` adapts a `librados::ObjectOperationCompletion` to Ceph's `Context` callback interface and owns the completion object until `finish()`. `NObjectIteratorImpl` and `NObjectIterator` wrap the C object listing API (`rados_nobjects_list_*`) and expose `ListObject` values, seek by hash position or `ObjectCursor`, namespace, oid, and locator. `PoolAsyncCompletion` and `AioCompletion` wrap `PoolAsyncCompletionImpl` and `AioCompletionImpl`, including callback registration, waits, return values, versions, cancellation, and reference release.

`IoCtx` owns a refcounted `IoCtxImpl`, with copy/move constructors, `close()`, `dup()`, pool property helpers, synchronous object IO, omap helpers, compound `operate`, aio variants, snapshot APIs, cls-lock APIs, object listing, hit set, watch/notify, namespace and locator setters, application metadata, and full-try flags. `Rados` owns a refcounted `RadosClient` and implements cluster creation, config parsing, connect/shutdown, pool management, mon/osd/mgr/pg commands, pool stats conversion, inconsistent object/snapset queries, completion creation, and blocklist support. `PlacementGroup`, `ListObject`, and `ObjectCursor` are small value wrappers around `pg_t`, `ListObjectImpl`, and `hobject_t`.

## Control Flow
The common object IO path is: a public method constructs `object_t` from a string oid, checks that operation impl pointers are valid for compound ops, translates operation flags, and calls a matching `IoCtxImpl` method. Compound operations use `ObjectReadOperation` or `ObjectWriteOperation` to accumulate internal op entries before `IoCtx::operate()` or `aio_operate()` submits them. Multi-page omap reads loop while OSD-side `more` is true, using the last returned key as the next `start_after` and protecting against `more` with an empty result by returning `-EINVAL`.

Async control flow is mostly delegated to `IoCtxImpl`, but the file owns callback adapters. `AioCompletion` passes `pc` to internal aio calls; `aio_getxattr()` creates an internal completion whose callback converts the return code to the final buffer length on success and then invokes the user completion. `ObjectOperation::exec_impl(..., ObjectOperationCompletion*)` creates a context that receives the output buffer, calls user completion, and deletes it.

Object listing has two paths. `NObjectIterator` uses the legacy/list context API and advances through `rados_nobjects_list_next2()`, throwing `std::system_error` on unexpected negative returns. The newer cursor API uses `Objecter::enumerate_objects()` with an async waiter and converts returned `ListObjectImpl` records into `ObjectItem` values, returning the count or a negative error code.

Cluster-level control flow maps `Rados` calls directly to `RadosClient`: initialization goes through C API constructors, `connect()` enters the client, `shutdown()` drops the ref and deletes the client only on the final put, and pool/command/stat calls mostly normalize parameters before delegation.

## State and Persistence Behavior
This file does not persist data directly, but it is the public gateway for persistent RADOS object and pool mutations. Object data, xattrs, omap entries, object manifests, snapshots, locks, watch state, application metadata, and pool lifecycle changes are submitted through `IoCtxImpl`, class helpers, `Objecter`, or `RadosClient`. `IoCtx` state includes pool id, namespace, locator key, read snap sequence, write snap context, notify timeout, last object version, and extra OSD flags. The refcount rules on `IoCtxImpl`, `RadosClient`, and completion impls are central: constructors/getters increment refs, destructors/close/release drop refs, and misuse can leak callbacks or release live state too early.

## Dependencies and Integration Points
The file integrates with `librados` internal implementations, the C API in `include/rados/librados.h`, Ceph objecter, cls lock client, tracepoints/LTTng, config parsing, Ceph error conventions, mon/osd/mgr command paths, pool stats structures, and `common/async/waiter`. It also preserves deprecated API entry points such as category parameters, `rollback()`, old snap and aio overloads, and auid pool creation handling.

## Risks and Test Signals
Primary risks are adapter mismatches: incorrect flag translation, snap context conversion, object cursor ownership, refcount lifetime errors, async callback ordering, and compatibility regressions in deprecated overloads. Omap pagination must be tested for empty, exact-limit, and multi-batch cases. Watch/notify tests should cover ack/timeouts decoding, unwatch paths, and flush behavior. Object listing tests should cover namespace/locator/filter handling, cursor copy/assignment, end cursor comparison, and error propagation. Pool/admin tests should verify return-code passthrough, unsupported auid/category behavior, command parsing, and pool-stat field conversions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/librados/librados_cxx.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/librados/librados_tp.cc -->
# sources/distributed-fs/ceph/src/librados/librados_tp.cc

## Purpose
This file conditionally defines librados tracepoint probes for LTTng builds. When `WITH_LTTNG` is enabled it defines `TRACEPOINT_DEFINE` and `TRACEPOINT_PROBE_DYNAMIC_LINKAGE`, includes `tracing/librados.h`, then undefines those macros. When tracing is disabled, the file contributes no runtime behavior.

## Important APIs, Types, and Functions
There are no functions or classes. The important symbols are the tracepoint provider definitions emitted by `tracing/librados.h` under the two tracepoint macros. They back tracepoint calls in librados code, including `librados_cxx.cc`.

## Control Flow
There is no control flow beyond preprocessing. Build configuration decides whether tracepoint definitions are emitted into the `librados_tp` shared object or omitted.

## State and Persistence Behavior
No persistent state is managed. The file affects observability only by making tracepoint probes linkable.

## Dependencies and Integration Points
It depends on `acconfig.h` for `WITH_LTTNG` and on `tracing/librados.h` for provider declarations. It integrates with `TracepointProvider::Traits("librados_tp.so", "rados_tracing")` in `librados_cxx.cc`.

## Risks and Test Signals
Risks are build/link issues when tracepoint macros or provider names drift from the tracing header. Test signals are successful builds with `WITH_LTTNG` on and off, plus tracepoint-enabled runtime smoke tests showing librados probes load from `librados_tp.so`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/librados/librados_tp.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/librados/librados_util.cc -->
# sources/distributed-fs/ceph/src/librados/librados_util.cc

## Purpose
This file provides small translation helpers shared by librados public API wrappers. It maps public checksum, per-op, and operation submission flags to internal Ceph OSD flag constants.

## Important APIs, Types, and Functions
`get_checksum_op_type(rados_checksum_type_t)` maps `LIBRADOS_CHECKSUM_TYPE_XXHASH32`, `XXHASH64`, and `CRC32C` to `CEPH_OSD_CHECKSUM_OP_TYPE_*`, returning `-1` for unknown types despite the `uint8_t` return type. `get_op_flags(int)` maps `LIBRADOS_OP_FLAG_*` values such as exclusive create, failok, and fadvise hints to `CEPH_OSD_OP_FLAG_*`. `translate_flags(int)` maps C++ `librados::OPERATION_*` submission flags to `CEPH_OSD_FLAG_*`, including read balancing/localization, read-write ordering, cache/overlay/redirect controls, full handling, ordersnap, and return-vector behavior.

## Control Flow
Each function is a direct bitmask or switch translator. Unknown bit values are ignored by the two flag translators. Unknown checksum type produces the sentinel value used by callers such as `ObjectReadOperation::checksum()` and `IoCtx::checksum()`.

## State and Persistence Behavior
No state is stored. The behavior influences persistent operations indirectly because wrong mappings would change how OSDs execute writes, reads, cache hints, full-cluster policy, or checksum requests.

## Dependencies and Integration Points
The helpers depend on public librados constants, internal OSD constants, and `librados_util.h`. They are used by `librados_cxx.cc` operation builders and submit paths.

## Risks and Test Signals
The main risk is semantic drift when new public flags or checksum types are added without updating these mappings. The `uint8_t` return of `-1` should be tested because callers may pass an invalid checksum op to lower layers if they do not validate. Tests should cover each flag bit independently and combinations of flags passed through `IoCtx::operate()` and aio variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/librados/librados_util.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/librados/librados_util.h -->
# sources/distributed-fs/ceph/src/librados/librados_util.h

## Purpose
This header declares librados utility translators and defines `librados::ObjListCtx`, the state carrier used by object listing iterators.

## Important APIs, Types, and Functions
It declares `get_checksum_op_type()`, `get_op_flags()`, and `translate_flags()`. `ObjListCtx` contains a private duplicated `IoCtxImpl` (`dupctx`), a pointer `ctx` to that duplicate, an `Objecter::NListContext *nlc`, and a `legacy_list_api` flag. The constructor duplicates the caller's `IoCtxImpl` so namespace and locator changes by the caller do not affect an active listing. The destructor nulls `ctx` and deletes `nlc`.

## Control Flow
The important behavior is construction-time duplication and destructor cleanup. Object listing functions allocate an `ObjListCtx`, hand it to iterator wrappers, and list-next calls use the saved `IoCtxImpl` and `NListContext`.

## State and Persistence Behavior
`ObjListCtx` stores ephemeral listing state only. It intentionally snapshots IO context settings, which avoids persistent namespace-selection bugs during long listings. It owns `nlc` and is therefore responsible for releasing object-list resources.

## Dependencies and Integration Points
The header includes public C librados definitions, `IoCtxImpl`, tracepoint stubs, and Ceph configuration headers. `ObjListCtx` is consumed by `librados_cxx.cc` `NObjectIteratorImpl` and the C listing functions.

## Risks and Test Signals
Risks include ownership mistakes around `nlc`, accidental use after `ctx` is nulled, and failure to preserve namespace/list settings across iterator copies. Tests should duplicate iterators, mutate the original `IoCtx` namespace after opening a listing, and verify list results continue using the saved context.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/librados/librados_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/librados/snap_set_diff.cc -->
# sources/distributed-fs/ceph/src/librados/snap_set_diff.cc

## Purpose
This file implements `calc_snap_set_diff()`, which computes the object byte ranges that differ between two snapshots from a librados `snap_set_t`. It also reports the end snapshot object's size/existence, the clone snapshot id covering the end point, and whether the whole object must be treated as changed.

## Important APIs, Types, and Functions
The sole exported function is `calc_snap_set_diff(CephContext*, const librados::snap_set_t&, snap_t start, snap_t end, interval_set<uint64_t> *diff, uint64_t *end_size, bool *end_exists, snap_t *clone_end_snap_id, bool *whole_object)`. It walks `snap_set.clones`, interprets HEAD as the interval `[seq + 1, SNAP_HEAD]`, interprets non-HEAD clones from their `snaps` vector, and uses each clone's `size` and `overlap` vector to build the changed extents.

## Control Flow
The function initializes all outputs and scans clones in order. It skips clones whose effective snapshot interval ends before `start`. When it first reaches the start position, it records the start size or, if the object did not exist at `start`, inserts the whole current clone size into `diff`. If `end` falls inside the current clone interval, it sets `end_size`, `end_exists`, and `clone_end_snap_id`, then returns with the accumulated diff. If `end` is after the current clone, it compares the current clone to the next clone: it starts with a maximal interval up to the larger relevant size boundary, erases overlap extents, and unions the resulting intervals into `diff`. Truncation below the start size can erase ranges that should no longer count as changed.

If a non-HEAD clone has an empty `snaps` vector, the function cannot derive an interval, clears `diff`, sets `whole_object`, and returns. If the scan runs out before reaching `end`, it clears the diff and, if the object existed at `start`, marks `[0,start_size)` as changed because the object no longer exists at `end`.

## State and Persistence Behavior
The function is pure with respect to Ceph storage. It mutates only caller-provided output objects. Its result is derived from persisted object snapset metadata supplied by the caller and is used to answer diff-like API queries.

## Dependencies and Integration Points
It depends on `librados::snap_set_t`, `interval_set`, Ceph debug logging, and snapshot id conventions including `SNAP_HEAD`. It integrates with librados snap listing/diff consumers that need changed extents without reading all object data.

## Risks and Test Signals
Risks are off-by-one snapshot interval interpretation, trimmed snapshot behavior where `b < cloneid`, empty snap vectors, truncation across start/end, and incorrect overlap erasure. Tests should include HEAD-only objects, object creation after start, deletion before end, growth, shrink, overlapping clones, empty snaps causing `whole_object`, and end snapshots that land exactly on clone interval boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/librados/snap_set_diff.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/librados/snap_set_diff.h -->
# sources/distributed-fs/ceph/src/librados/snap_set_diff.h

## Purpose
This header declares the snapset diff helper used by librados snapshot diff code.

## Important APIs, Types, and Functions
It declares `calc_snap_set_diff()` with inputs for a Ceph context, `librados::snap_set_t`, start and end snap ids, and outputs for changed intervals, end size, end existence, end clone id, and whole-object fallback. The output interval type is `interval_set<uint64_t>`.

## Control Flow
The header has no runtime flow. It defines the linkage contract implemented in `snap_set_diff.cc`.

## State and Persistence Behavior
No state is declared. Callers pass all state explicitly and receive all derived diff state through output pointers.

## Dependencies and Integration Points
It includes common forward declarations, RADOS type definitions, and `interval_set`. It is intended for code that has snapset metadata and needs a reusable extent-diff computation.

## Risks and Test Signals
The interface uses raw output pointers, so callers must provide non-null storage and should initialize no assumptions about prior values. Compile tests should ensure this header can be included wherever only `CephContext` is forward-declared, and unit tests should target the implementation through this declaration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/librados/snap_set_diff.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/Anchor.cc -->
# sources/distributed-fs/ceph/src/mds/Anchor.cc

## Purpose
This file implements serialization, formatting, test-instance generation, and stream printing for `Anchor`, the MDS structure that records primary inode linkage for path reconstruction through the anchor table.

## Important APIs, Types, and Functions
`Anchor::encode()` writes version 2 records containing `ino`, `dirino`, `d_name`, `d_type`, and `frags`. `Anchor::decode()` reads versioned records and only decodes `frags` when `struct_v >= 2`, preserving compatibility with older serialized anchors. `dump()` emits formatter fields except `frags`. `generate_test_instances()` creates an empty anchor and a sample directory anchor. `operator<<` prints a compact human-readable representation.

## Control Flow
Serialization is straightforward versioned encode/decode with `ENCODE_START` and `DECODE_START`. The decode path first loads core fields and conditionally loads the newer fragment set.

## State and Persistence Behavior
Anchors are persisted through Ceph buffer encoding, likely into the MDS anchor table. The versioning choice means existing v1 records remain readable and v2 records carry fragment membership. `omap_idx` is not encoded here, so it is runtime placement metadata rather than part of the durable anchor payload.

## Dependencies and Integration Points
It depends on `Anchor.h`, Ceph `Formatter`, denc/buffer helpers, and directory-entry type constants from `<dirent.h>`. It integrates with MDS anchor-table code that stores ancestor chains and with Ceph encoding tests via `generate_test_instances()`.

## Risks and Test Signals
The main risk is serialization compatibility: adding fields before existing v2 content would break decode. Tests should round-trip v1/v2 anchors, verify `frags` survives v2 encode/decode, and ensure dump/print output remains usable for debugging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/Anchor.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/Anchor.h -->
# sources/distributed-fs/ceph/src/mds/Anchor.h

## Purpose
This header defines `Anchor` and its recovered/opened variants. An anchor represents the primary parent linkage of an inode and lets the MDS recursively reconstruct paths by following anchored ancestors.

## Important APIs, Types, and Functions
`Anchor` stores `ino`, `dirino`, `d_name`, `d_type`, a set of `frag_t` values, and runtime `omap_idx`. It provides constructors, `encode()`, `decode()`, `dump()`, `generate_test_instances()`, equality, and `WRITE_CLASS_ENCODER`. `RecoveredAnchor` extends `Anchor` with an auth-rank hint. `OpenedAnchor` extends `Anchor` with a mutable child reference count `nref`.

## Control Flow
There is no complex flow in the header. The type is a value container with versioned serialization implemented in `Anchor.cc`.

## State and Persistence Behavior
The durable state is the inode number, parent inode number, dentry name/type, and fragments. `omap_idx`, recovered auth, and opened reference counts are runtime management state. The invariant described in the comment is that adding an inode to the anchor table also requires ancestor anchors, enabling recursive path lookup.

## Dependencies and Integration Points
It depends on Ceph inode, fragment, buffer, MDS rank, and filesystem types. It integrates with MDS anchor table persistence and recovery code, and uses standard Ceph class encoder conventions.

## Risks and Test Signals
Risks are incomplete ancestor maintenance outside this file, stale `frags`, and confusing durable vs runtime fields. Tests should validate equality, encoding, and recovery/opened behavior in anchor-table scenarios where paths cross fragmented directories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/Anchor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/BatchOp.cc -->
# sources/distributed-fs/ceph/src/mds/BatchOp.cc

## Purpose
This file implements logging wrappers for `BatchOp` forwarding and response handling. It centralizes debug output before dispatching to subclass-specific behavior.

## Important APIs, Types, and Functions
`BatchOp::forward(mds_rank_t target)` logs the target rank and prints the batch, then calls virtual `_forward(target)`. `BatchOp::respond(int r)` logs the result and prints the batch, then calls virtual `_respond(r)`.

## Control Flow
Both methods are template-method wrappers: public non-virtual method, debug print, private/protected virtual hook. The actual forwarding or responding behavior is defined by subclasses.

## State and Persistence Behavior
No state is stored or persisted here. The file affects the flow of metadata requests managed by concrete batch operations elsewhere.

## Dependencies and Integration Points
It depends on MDS debug logging, global Ceph context, `BatchOp.h`, `MDRequestImpl` references through the abstract interface, and MDS rank types. It integrates with code that batches MDS requests and needs a common forwarding/responding entry point.

## Risks and Test Signals
The notable risk is that `_respond` is declared in the header as taking `mds_rank_t` even though `respond()` passes an int result. If intentional via typedef compatibility it should be documented; otherwise it is a type/semantic mismatch to watch. Tests should instantiate concrete subclasses and verify `forward()` and `respond()` call the expected hooks once with the expected argument and logging does not mutate batch state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/BatchOp.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/BatchOp.h -->
# sources/distributed-fs/ceph/src/mds/BatchOp.h

## Purpose
This header defines the abstract base class for MDS batch operations. It gives callers a common interface for collecting requests, finding a new head request, printing batch state, forwarding the batch to another rank, and responding to all batched requests.

## Important APIs, Types, and Functions
Subclasses must implement `add_request(const ceph::ref_t<MDRequestImpl>&)`, `find_new_head()`, `print(std::ostream&)`, `_forward(mds_rank_t)`, and `_respond(mds_rank_t)`. Public `forward()` and `respond()` are implemented in `BatchOp.cc`.

## Control Flow
The base class enforces a two-layer pattern: public methods handle common logging, then protected virtual methods perform subclass-specific transport or response work.

## State and Persistence Behavior
The class itself has no fields and does not persist state. Concrete subclasses own request sets and any state needed to coordinate MDS metadata operations.

## Dependencies and Integration Points
It depends on Ceph intrusive/ref counted request references and `mds_rank_t`. It integrates with MDS request handling code where multiple `MDRequestImpl` instances are grouped for forwarding or completion.

## Risks and Test Signals
The `_respond(mds_rank_t)` signature looks inconsistent with `respond(int r)` semantics. If `mds_rank_t` is not meant to carry return codes, subclasses can misinterpret results. Compile-time concrete subclass coverage and response-path tests are important signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/BatchOp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/Beacon.cc -->
# sources/distributed-fs/ceph/src/mds/Beacon.cc

## Purpose
This file implements the MDS beacon subsystem. A `Beacon` runs a separate sender thread so monitor heartbeats and health reports continue even when the main MDS is busy holding its own lock. It sends `MMDSBeacon` messages to monitors, tracks acknowledgements and lagginess, and snapshots health metrics from `MDSRank`.

## Important APIs, Types, and Functions
`Beacon::init()` copies the initial MDSMap epoch and starts the `mds-beacon` thread. `shutdown()` stops and joins that thread. `ms_dispatch2()` receives monitor beacon replies and sends them to `handle_mds_beacon()`. `send()` and `send_and_wait()` submit immediate beacons, with the latter waiting for ack or timeout. `_send()` constructs `MMDSBeacon` with fsid, gid, daemon name, epoch, desired state, sequence, features, health, compat set, target filesystem, and boot-time sys info. `notify_mdsmap()` and `set_want_state()` update copied epoch/state under the beacon lock. `is_laggy()` compares time since last ack to `mds_beacon_grace`.

`notify_health()` is the broad health collector. It copies health metrics for dummy injection, damage table entries, slow journal trimming, late cap release, client cache recall pressure, oldest client tid/flush lag, slow MDS requests, slow metadata IOs, read-only mode, broken root squash clients, oversized cache, laggy clients deferred due to laggy OSDs, and replay progress estimates.

## Control Flow
The sender thread loops until `finished`. On each iteration it computes time since last send; near the beacon interval it calls `_send()`, otherwise it waits for the remaining interval. If `_send()` failed because the internal heartbeat map is unhealthy, the next wait interval is shortened to 500 ms. If the condition-variable wait times out after a send, it records a missed ack. Replies are matched by sequence number in `seq_stamp`; matching replies update `last_acked_stamp`, compute RTT, clear laggy state when RTT is below grace, erase old sequence stamps, and wake waiters.

`_send()` refuses to send when Ceph's internal heartbeat map is unhealthy, intentionally allowing monitors to see lagginess instead of masking a wedged MDS. Otherwise it increments `last_seq`, records the timestamp, builds a beacon message, optionally adds boot sys-info, sends through `MonClient`, and updates `last_send`.

## State and Persistence Behavior
Beacon state is in-memory and protected by `mutex`: sender thread state, condition variable, last send/ack times, sequence stamps, desired MDS state, MDSMap epoch, compat set, laggy markers, and copied health metrics. It does not persist data directly, but monitor-visible daemon liveness and health state are derived from this state.

## Dependencies and Integration Points
It integrates with `MonClient`, messenger dispatch, `MMDSBeacon`, MDSMap, `MDSRank`, `MDLog`, `MDCache`, `Locker`, `SessionMap`, `Objecter`, `HeartbeatMap`, config options, and cluster log health codes. It assumes `notify_health()` is called with the MDS lock held and asserts that condition.

## Risks and Test Signals
Risks include sender-thread shutdown races, stale copied MDSMap state, missed ack false positives, holding beacon mutex while traversing health data, and summary threshold mistakes that hide specific client metrics. Tests should cover ack matching/out-of-order replies, `send_and_wait()` timeout, heartbeat unhealthy skip, laggy enter/exit, state transitions via `set_want_state()`, shutdown during wait, and health metric generation for each major warning family.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/Beacon.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/Beacon.h -->
# sources/distributed-fs/ceph/src/mds/Beacon.h

## Purpose
This header declares `Beacon`, the MDS monitor heartbeat and health-report dispatcher.

## Important APIs, Types, and Functions
`Beacon` derives from `Dispatcher` and exposes lifecycle (`init`, `shutdown`), messenger dispatch (`ms_dispatch2` and reset/refused stubs), MDSMap and health notifications, beacon sending, desired-state setters/getters, lagginess queries, and `send_and_wait()`. It uses `ceph::coarse_mono_clock` aliases for timing.

Important fields include `mutex`, `sender`, `cvar`, `last_send`, `beacon_interval`, `finished`, `MonClient *monc`, copied daemon identity and epoch, `CompatSet`, `want_state`, sequence tracking (`last_seq`, `seq_stamp`, `last_acked_stamp`), laggy tracking, and `MDSHealth health`. Two public booleans record missed ack/internal heartbeat dump signals.

## Control Flow
The header documents why a separate beacon class exists: it decouples monitor liveness messages from the main MDS lock. Public notification methods copy data into Beacon-owned state; private `_send()` and `_notify_mdsmap()` perform locked internal updates.

## State and Persistence Behavior
All state is volatile process state. The key invariant is that data needed for beacon messages is duplicated under Beacon's own mutex so the sender thread does not need to take the main MDS lock.

## Dependencies and Integration Points
It depends on Ceph dispatcher/messenger types, MDSMap daemon states, `MMDSBeacon` health structures, `MonClient`, and `MDSRank`. It is part of MDS daemon liveness and health integration with monitors.

## Risks and Test Signals
Header-level risks are locking discipline and stale copied fields. Tests and static analysis should verify every shared field is accessed under `mutex`, sender thread lifetime is bounded by `shutdown()`, and `get_want_state()` is safe concurrently with state updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/Beacon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/CDentry.cc -->
# sources/distributed-fs/ceph/src/mds/CDentry.cc

## Purpose
This file implements `CDentry`, the MDS cache object for a directory entry. A dentry links a name and snap interval in a `CDir` to either a primary inode, a remote inode reference, or a null/negative entry. It manages projected linkage during metadata mutations, dirty tracking, authority pins, client leases, export/import state, lock-state encoding, remote-link encoding, path formatting, dump output, and corruption checks.

## Important APIs, Types, and Functions
Constructors create null or remote dentries with hash, snap range, alternate name, locks, and dirty-list items. `operator<<`, `print()`, and `dump()` expose debug and admin state. `authority()` delegates to the containing `CDir`. `pre_dirty()`, `_mark_dirty()`, `mark_dirty()`, `mark_clean()`, and `mark_new()` synchronize dentry versions and dirty membership with the parent dir and log segment.

Linkage APIs include `link_remote()`, `unlink_remote()`, `push_projected_linkage()`, `push_projected_linkage(CInode*)`, and `pop_projected_linkage()`. Projected primary linkage preserves dirty rstat state while pushing/popping projected inode parent state. `add_client_lease()`, `remove_client_lease()`, and `remove_client_leases()` manage intrusive client lease records and SimpleLock lease counters. `encode_remote()` and `decode_remote()` serialize remote dentries, including v2 alternate names. `scrub()` and `check_corruption()` detect invalid snap ranges and optionally mark damage or abort to avoid committing newly corrupt metadata.

## Control Flow
Dirtying a dentry starts by asking the parent dir for a projected version, then `mark_dirty()` records the committed dentry version, marks the dentry dirty, inserts it into both the dir dirty list and log segment dirty list, and marks the dir dirty. Cleaning removes the dirty state, list items, and dirty pin. Projected linkage follows a two-phase mutation flow: push a future linkage before the mutation is committed, use projected readers when locks allow it, then pop to apply the change by calling `CDir::link_remote_inode()` or `CDir::link_primary_inode()`.

Authority pins are delegated upward. `auth_pin()` pins the dentry and increments nested auth pins on the containing `CDir`; `auth_unpin()` reverses that and may unblock freezes. Waiters for unfreeze or single-auth are redirected to the dir, while other waiters stay on the dentry.

Client lease removal erases the lease from both per-session and global lists, updates the dentry lock's client lease count, drops the lease pin when the last lease goes away, and asks `Locker` to re-evaluate gathers if the lock became gatherable.

## State and Persistence Behavior
Durable dentry state includes name, snap range, first/version fields, linkage type, remote inode/type, primary inode store through the parent dir commit path, and alternate name. Runtime state includes lock objects, version lock, projected linkage list, dirty-list membership, LRU position, auth pins, client leases, batch ops, reintegration id, and corruption-loaded marker. Export/import encoding captures snap first, state, versions, locks, and replicas; import restores auth, dirty pins, replica pins, and nonce behavior.

## Dependencies and Integration Points
`CDentry` is tightly integrated with `CDir`, `CInode`, `MDCache`, `Locker`, `LogSegment`, `SnapClient`, `SnapRealm`, MDS locks, client sessions, memory pools, and MDS damage reporting. It is manipulated by dir fetch/commit, rename/link/unlink, scatterlock, cache trimming, exports/imports, and scrub.

## Risks and Test Signals
High-risk areas are projected linkage ordering, dirty version invariants, auth pin balance, remote parent registration, client lease cleanup, snap range corruption, and export/import state masks. Tests should cover primary/remote/null transitions, projected pop after rename/link/unlink, dirty and clean list membership, lease add/remove with lock gather, corrupt `first > last` handling, remote encode/decode v1/v2, and scrub detection of invalid snap intervals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/CDentry.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/CDentry.h -->
# sources/distributed-fs/ceph/src/mds/CDentry.h

## Purpose
This header defines the `CDentry` cache object and `ClientLease` records used by CephFS MDS directory cache. It describes dentry state flags, pin types, linkage representation, versioning, authority operations, exporting/importing, locking, leases, and serialization helpers.

## Important APIs, Types, and Functions
`ClientLease` is an intrusive set/list node keyed by client id and linked into both session and global lease lists. `CDentry::linkage_t` distinguishes primary, remote, and null entries and stores a primary `CInode *` or remote inode/type. `CDentry` inherits from `MDSCacheObject`, `LRUObject`, and `Counter<CDentry>`.

State flags include new, fragmenting, purging, bad remote ino, stray evaluation, purge pinned, bottom LRU, and stray notify-ref. Pin constants include inode pin, fragmenting, purging, and scrub parent. Public APIs cover waiter routing, key construction, corruption checks, name/alternate name accessors, projected linkage, refcount LRU hooks, auth pins, remote links, path construction, version dirtying/cleaning, export/import, lock-state encode/decode, client leases, dump/print, and remote dentry serialization.

## Control Flow
The header exposes the dentry mutation model: direct linkage is durable/current, `projected` holds pending mutation state, and `use_projected()` selects the projected view for clients allowed by the lock or mutation. Export/import methods inline the state-mask and pin transitions used during migration. `first_get()` and `last_put()` bind object references to LRU pinning.

## State and Persistence Behavior
Persistent fields are the name, alternate name, hash, snap interval, linkage, and versions as committed through `CDir`. Lock state and replica state can be encoded for MDS replication/migration. Runtime-only fields include `dir`, projected list, LRU state, lease maps, dirty items, batch ops, auth pins inherited from `MDSCacheObject`, and reintegration request id.

## Dependencies and Integration Points
It depends on MDS cache base classes, lock classes, log segment refs, Ceph buffer types, intrusive containers, CDir/CInode forward declarations, and session/locker types. It is one of the central types shared by MDS cache, request handling, locker, migrator, stray manager, and scrub code.

## Risks and Test Signals
The API is easy to misuse if callers read `linkage` directly instead of projected linkage during locked mutations. State and pin constants must stay aligned with import/export masks and debug dump code. Tests should validate projected/current view selection, LRU pin hooks, encode/decode of export and lock state, and lease map uniqueness by client.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/CDentry.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/CDir.cc -->
# sources/distributed-fs/ceph/src/mds/CDir.cc

## Purpose
This file implements `CDir`, the MDS cache object for a CephFS directory fragment. `CDir` owns dentries for one inode fragment, tracks fragment and recursive stats, manages dirty fnode versions, fetches and commits dirfrag omap objects, handles split/merge, import/export, subtree authority, auth pins, freezing, scrub metadata, LRU/popularity signals, and damage handling.

## Important APIs, Types, and Functions
Construction binds a directory inode, `frag_t`, `MDCache`, auth state, dirty lists, lock-cache lists, freezing lists, popularity counters, and default authority. Lookup APIs (`lookup`, `lookup_exact_snap`) search `items` by `dentry_key_t`. Dentry mutators (`add_null_dentry`, `add_primary_dentry`, `add_remote_dentry`, `remove_dentry`, `link_*`, `unlink_inode`, `steal_dentry`) maintain item maps, item counters, LRU selection, inode parent links, open-file table membership, auth pin nesting, snaprealm parentage, frozen inode lists, and quiesce state.

Fragmentation APIs (`prepare_old_fragment`, `prepare_new_fragment`, `finish_old_fragment`, `split`, `merge`) repartition dentries, waiters, stats, replica maps, pins, and authority. Dirty APIs (`project_fnode`, `pop_and_dirty_projected_fnode`, `pre_dirty`, `mark_dirty`, `_mark_dirty`, `mark_clean`, `log_mark_dirty`) manage projected fnode state and log-segment membership. Fetch/commit APIs (`fetch`, `fetch_keys`, `_omap_fetch`, `_omap_fetch_more`, `_load_dentry`, `_omap_fetched`, `commit`, `_omap_commit`, `_omap_commit_ops`, `_parse_dentry`, `_committed`) implement durable omap IO.

Authority and migration APIs include `encode_export`, `finish_export`, `decode_import`, `abort_import`, `authority`, `set_dir_auth`, `auth_pin`, `auth_unpin`, and `adjust_nested_auth_pins`. Freezing APIs include `freeze_tree`, `_freeze_tree`, `unfreeze_tree`, `adjust_freeze_after_rename`, `freeze_dir`, `_freeze_dir`, `unfreeze_dir`, and `maybe_finish_freeze`. Scrub APIs track last local/recursive scrub versions and repair local stat mismatches.

## Control Flow
Fetch starts only on auth, incomplete dirfrags. A full fetch pins auth, sets `STATE_FETCHING`, reads the omap header and a batch of omap keys, and optionally verifies backtrace. If more keys remain, `_omap_fetch_more()` chains additional reads. `_omap_fetched()` decodes the fnode header, initializes a fresh fnode when needed, handles stale snap purging, decodes each dentry in reverse omap order, creates null dentries for missing requested keys, marks the dir complete on full fetch, opens rejoin-undefined inodes, dirties the dir if stale snap state must be removed, unpins auth, and queues waiters. Corrupt headers or dentries go through `go_bad()` or `go_bad_dentry()` and damage-table reporting.

Commit queues waiters by desired version and auth-pins for the commit sequence. `_commit()` avoids duplicate overlapping commits, marks `STATE_COMMITTING`, and calls `_omap_commit()`. `_omap_commit()` converts dirty dentries or all new-fragment entries into remove/set vectors, trimming stale snap dentries as needed and parsing primary inode stores into commit items. `_omap_commit_ops()` runs off the MDS lock, chunks omap set/remove operations under `max_dir_commit_size`, writes the omap header only in the final op to preserve crash ordering, and gathers completions. `_committed()` advances `committed_version`, clears committing/dirty state when versions match, cleans dentries and inodes whose versions are covered, drops clean null strays, wakes satisfied waiters, possibly starts a later commit, and releases the commit auth pin.

Split creates subfrags, scales popularity counters, moves dentries according to hashed names, redistributes dentry waiters, preserves stats differentials, and finishes the old fragment. Merge prepares a new parent fragment, steals all subfrag dentries, combines replica maps/state/version, closes old dirfrags, merges waiters, and rebuilds accounted stats.

Freezing uses auth pins as the barrier. Tree freeze creates shared `freeze_tree_state`, walks nested dirfrags, counts auth pins, invalidates lock caches, and either freezes immediately or waits. `_freeze_tree()` adjusts subtree authority so the frozen tree has stable ambiguous authority. Unfreeze clears state across the tree, resets authority, and queues waiters. Directory-only freeze is similar but does not walk descendants.

## State and Persistence Behavior
Durable dirfrag state is stored as an omap object in the metadata pool: fnode in the omap header and each dentry as an omap key/value. Primary dentries encode inode store, symlink, dirfragtree, xattrs, snaprealm, old inode versions, oldest snap, and damage flags; remote dentries encode remote ino/type and alternate name; null dentries are removed. In-memory state includes `items`, dirty dentry lists, projected fnode queue, fnode versions (`projected`, `committing`, `committed`), dirty old rstat, stale item set, auth and nested auth pins, freeze state, waiters, bloom filter, popularity counters, replica maps, scrub info, and damage state.

The commit ordering invariant is critical: dentry omap updates are sent before the fnode header update in the final operation so a crash cannot expose a header version that claims uncommitted entries are durable.

## Dependencies and Integration Points
`CDir` integrates with `CInode`, `CDentry`, `MDCache`, `MDSRank`, `MDLog`, `LogSegment`, `Locker`, `MDBalancer`, `SnapClient`, `SnapRealm`, `EMetaBlob`, `Objecter`, `DamageTable`, `OpenFileTable`, backtrace verification, MDS health/logging counters, and Ceph memory pools. It is a core join point for request mutation, journal replay, metadata IO, cache trimming, directory fragmentation, migration, scrub, and subtree authority balancing.

## Risks and Test Signals
High-risk areas include version ordering, omap commit chunking, header-last crash safety, auth pin balance, freeze/unfreeze races, stale snap trimming, duplicate inode loading, dirty rstat assimilation, split/merge stat preservation, and damage handling that marks a dir complete despite missing dentries. Tests should cover full and key fetch, multi-batch fetch, corrupt fnode/dentry decode, missing object behavior, commit after dirty primary/remote/null dentries, commit retries and waiter ordering, crash/replay with underwater dirty items, snap purge, split/merge with waiters and auth pins, export/import state restoration, freeze tree after rename, scrub repair, and split/merge threshold decisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/CDir.cc -->
