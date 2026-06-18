# subset-b-006955 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osdc/Objecter.h -->
# sources/distributed-fs/ceph/src/osdc/Objecter.h

## Purpose

`Objecter.h` declares Ceph's client-side OSD operation engine. It is the main interface between higher layers such as librados, the CephFS client, RGW, and the OSD cluster. The header covers operation construction (`ObjectOperation`), target calculation state, per-OSD session tracking, asynchronous completions, linger/watch state, pool/statfs operations, command submission, scatter/gather helpers, throttling hooks, and map-version waiting.

## Important APIs, types, and functions

`ObjectOperation` is the mutable builder for OSD op vectors. It owns a small-vector of `OSDOp` plus parallel output slots: `out_bl`, `out_handler`, `out_rval`, and `out_ec`. It exposes helpers for object IO (`read`, `sparse_read`, `write`, `write_full`, `writesame`, `zero`, `truncate`, `remove`), metadata (`stat`, xattrs, omap keys/values/header, watch/list_snaps/list_watchers), class calls, cache/tier/manifest ops, copy operations, assertions, checksums, and internal version queries. Several callbacks decode wire replies into legacy `int*` outputs or modern `boost::system::error_code*` outputs.

`Objecter` derives from `md_config_obs_t` and `Dispatcher`. Public APIs include `op_submit()`, `mutate()`, `read()`, `pg_read()`, `linger_watch()`, `linger_notify()`, `osd_command()`, `pg_command()`, pool snap/pool create/delete helpers, pool/statfs stats, object listing/enumeration, scatter/gather reads and writes, OSD map waits, blocklist event consumption, and global read/write flag handling. `SplitOp`, `ECSplitOp`, and `ReplicaSplitOp` are friends so the split-read implementation can access `Op`, `osdmap`, `_calc_target()`, `_op_submit()`, reply handlers, and the special split-op session.

Key nested types are `op_target_t`, `Op`, `CommandOp`, `LingerOp`, `OSDSession`, `PoolOp`, `PoolStatOp`, `StatfsOp`, and `NListContext`. `op_target_t` holds the full mapping decision for a logical object or explicit PG: base/target oid and locator, PG ids, acting/up sets, pool flags, target OSD, pause/full state, and replica-use metadata. `Op` is the refcounted in-flight object request, carrying target, op vector, snap context, completion variant, trace, throttling budget, object version pointers, request id, retry bookkeeping, and optional `split_op_tids`.

## Control flow

Callers typically build an `ObjectOperation`, then pass it to `prepare_read_op()`, `prepare_mutate_op()`, `read()`, `mutate()`, or a specialized helper. These functions move the op vector and output handlers into a new `Objecter::Op`, set read/write flags, snap state, mtime, object version pointers, and submit via `op_submit()`. Submission maps the target against the current OSDMap, assigns an `OSDSession`, applies throttling, sends an `MOSDOp`, and later completes through dispatcher callbacks such as `handle_osd_op_reply()`.

Map churn is handled by `_calc_target()`, `_map_session()`, `_scan_requests()`, map-check queues, and wait-for-map callbacks. Linger operations use persistent `LingerOp` state with register, reconnect, ping, notify, and cancellation flows. Command and pool/statfs operations follow parallel submit/reply/cancel paths, but with distinct op types and completion signatures.

`process_op_reply_handlers()` is an important integration seam: it decodes individual OSD op outputs into the user-provided destinations and reports handler failures as `osdc_errc::handler_failed`. Split reads reuse the same reply-handler machinery after manually assembling synthetic `out_ops`.

## State and persistence behavior

This header declares in-memory client state, not durable persistence. Persistent cluster state is represented indirectly through the OSDMap, pool ids, snaps, object versions, and OSD replies. Internally, `Objecter` persists runtime state in maps of sessions, in-flight ops, linger ops, pool ops, statfs ops, map-check queues, `waiting_for_map`, cached PG mappings, blocklist events, and throttling counters. Locking is centered on `rwlock`, session locks, `pg_mapping_lock`, and per-session completion locks. Atomic counters track tids, inflight counts, client incarnation, global flags, and extra read flags.

## Dependencies and integration points

The header depends on Ceph primitives (`bufferlist`, `Context`, `SnapContext`, `OSDMap`, `OSDOp`, `MOSDOp`, `Messenger`, `MonClient`, throttles, tracing, admin socket formatting) and Boost.Asio completion tokens. It integrates with `SplitOp` for balanced/split read optimization, `Striper` through scatter/gather helpers, `osdc/error_code` for objecter-specific errors, and the Messenger dispatcher path for OSD op replies, maps, backoff, and watch notifications.

References in `Objecter.cc` show `Objecter.h` declarations are backed by perf counters for split reads, config tracking for `osd_min_split_replica_read_size`, split op completion/cancellation, pool EIO/DNE handling, reply handler exception conversion, and enumeration precondition checks.

## Risks and edge cases

The major risks are lifetime and concurrency hazards: completions can be legacy `Context*`, function2 callables, or Asio handlers; callback code may throw; sessions hold raw pointers to refcounted operations; and lock ordering across objecter/session/watch locks matters. Output vectors must remain parallel to `ops`; `ObjectOperation::add_op()` asserts this, but manual `dup()`/pass-through logic can still be fragile. Read flag filtering in `get_read_flags()` strips balancing/localization for `RWORDERED`, which is correctness-sensitive. `omap_get_vals(std::optional...)` encodes `filter_prefix ? *start_after : std::string_view{}`; that apparent use of `start_after` under the `filter_prefix` condition deserves review because it can encode the wrong filter or dereference an absent `start_after`.

## Test signals

Useful tests are OSD client integration tests covering read/write/stat/xattr/omap/class calls, watch/notify reconnect, pool DNE/EIO and snapshot errors, map changes during in-flight ops, throttling, cancellation, and split-read fallback/retry. Existing source references show `Objecter.cc` routes `osdc_errc` into these paths and `SplitOp` relies on `process_op_reply_handlers()`. Scatter/gather behavior should be exercised with `Striper::StripedReadResult`, sparse reads, and caller-provided output buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osdc/Objecter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osdc/SplitOp.cc -->
# sources/distributed-fs/ceph/src/osdc/SplitOp.cc

## Purpose

`SplitOp.cc` implements client-side split/balanced read optimization for Ceph OSD reads. It can split eligible reads across erasure-coded data shards or replicated-pool replicas, submit parallel sub-operations through `Objecter`, detect torn reads with internal version checks, assemble synthetic replies, and fall back to the normal primary path when the optimization is unsafe or unhelpful.

## Important APIs, types, and functions

The implementation defines `osdcode()` for converting negative OSD returns into `boost::system::error_code`, `kReplicaMinShardReads`, EC and replica implementations of `init_reference_sub_read()`, `init_read()`, `assemble_buffer_read()`, `assemble_buffer_sparse_read()`, and `version_mismatch()`, plus shared `SplitOp::assemble_rc()`, `complete()`, `protect_torn_reads()`, `init()`, `prepare_single_op()`, and `create()`.

Anonymous helpers validate eligibility: `is_single_chunk()` detects EC reads that fit in one chunk, `validate_flags()` requires `CEPH_OSD_FLAG_BALANCE_READS`, rejects writes and Crimson pools, `validate_operations()` accepts reads/sparse reads plus selected primary-only metadata ops, rejects zero-length reads and unsupported opcodes, and `validate()` combines pool type and `osd_min_split_replica_read_size` checks.

## Control flow

`SplitOp::create()` is the entry point from `Objecter` submission. It rejects missing pools, snapshot operations, pools without `FLAG_CLIENT_SPLIT_READS`, invalid flags, invalid operations, and undersized replica reads. A single EC chunk can be rewritten by `prepare_single_op()` to use `EC_DIRECT_READ | FORCE_OSD` without constructing a split object. Otherwise it creates `ECSplitOp` or `ReplicaSplitOp`, calculates the target, initializes a reference sub-read, initializes per-op sub-reads, rejects if only one sub-read remains, adds the parent op to the split-op session, appends internal version requests, prepares child read ops, forces OSD targets, submits them, and records child tids in `op->split_op_tids`.

Sub-op finishers self-delete through the `Context` lifecycle and only record return codes. The `shared_ptr<SplitOp>` retained by each finisher keeps the split operation alive until all child contexts release it; derived destructors call `complete()`. `complete()` assembles return status, builds synthetic `out_ops`, reconstructs read/sparse-read data, preserves legacy preallocated `outbl` behavior, runs `Objecter::process_op_reply_handlers()`, and calls `op_post_split_op_complete()`. Negative returns or version mismatch lead to `-EAGAIN`, which is used to retry on the ordinary path.

## State and persistence behavior

All state is transient: `orig_op`, `sub_reads`, per-sub-read `ObjectOperation`, return codes, response buffers, optional sparse extent maps, optional internal-version buffers, reference index, abort flag, and generated child tids. No persistent data is written. Correctness depends on OSD-side object versions and OSDMap acting sets captured during target calculation.

## Dependencies and integration points

The file depends on `Objecter.h`, `SplitOp.h`, OSD pool/shard metadata, `ceph_assert`, buffer encoding/decoding, and OSD flags. It integrates tightly with `Objecter::_calc_target()`, `prepare_read_op()`, `_op_submit()`, `add_op_to_splitop_session()`, `process_op_reply_handlers()`, and `op_post_split_op_complete()`. OSD-side support is signaled by `CEPH_OSD_FLAG_EC_DIRECT_READ`, `CEPH_OSD_FLAG_FAIL_ON_EAGAIN`, and pool `FLAG_CLIENT_SPLIT_READS`.

## Risks and edge cases

The EC path assumes shard index conversion through `pg_pool_t::get_shard()` and `target.acting` remain aligned; missing or down OSDs abort to fallback. Replica `init_reference_sub_read()` counts valid OSDs but chooses `rand() % valid_osd_count` and then treats it as an acting index, which is risky if invalid OSDs are interspersed in `target.acting`. `ECSplitOp::init_read()` comments discuss zero-length reads being rejected earlier, but it still relies on assertion. Sparse assembly assumes per-shard extent maps and buffers advance consistently. The destructor-driven completion pattern is subtle: setting `abort` before fallback is necessary to avoid completing abandoned split objects.

## Test signals

Tests should cover EC single-chunk direct read, multi-shard dense and sparse reads, replica split threshold behavior, missing/down OSD fallback, unsupported operations, snapshot rejection, reads with primary-only ops, object version mismatch retry, `outbl` preallocated-buffer compatibility, and cancellation of child tids. Existing references in `Objecter.cc` show split reads are counted, cancelled through `split_op_tids`, and retried or completed through `op_post_split_op_complete()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osdc/SplitOp.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osdc/SplitOp.h -->
# sources/distributed-fs/ceph/src/osdc/SplitOp.h

## Purpose

`SplitOp.h` declares the split-read abstraction used by `Objecter` to parallelize eligible client reads across multiple OSDs. It defines shared bookkeeping for sub-reads, EC stripe iteration, result assembly contracts, torn-read protection, and the concrete EC and replicated-pool specializations.

## Important APIs, types, and functions

`SplitOp` defines `extent`, `extents_map`, and `extent_set` aliases for read ranges. `ECChunkInfo`, `ECStripeIterator`, and `ECStripeView` model logical-to-shard traversal for erasure-coded stripes. The iterator reports logical object offset, shard offset, chunk length, and raw shard id for each chunk and is asserted to satisfy `std::input_iterator`.

`Details` stores one sub-operation's response buffer, return value, error code, and optional sparse extent map. `InternalVersion` stores the reply from `CEPH_OSD_OP_GET_INTERNAL_VERSIONS`. `SubRead` owns the child `ObjectOperation`, response details by original op index, a sub-op return code, and optional version data. `Finisher` is the child completion context that records the return code while retaining the parent split op.

`SplitOp` declares virtual assembly and initialization hooks: `assemble_buffer_sparse_read()`, `assemble_buffer_read()`, `init_read()`, `version_mismatch()`, and `init_reference_sub_read()`. Public APIs are `complete()`, `prepare_single_op()`, `protect_torn_reads()`, and static `create()`.

`ECSplitOp` implements shard-aware EC assembly and version comparison. `ReplicaSplitOp` implements replica chunking and assembly, with a constructor that sizes sub-read storage from pool size.

## Control flow

The header establishes a staged lifecycle. `create()` validates an `Objecter::Op`, constructs the right subclass, initializes the reference sub-read, calls `init()` for each original OSD op, protects torn reads by appending version checks, and submits child reads. `init()` dispatches reads and sparse reads to `init_read()` while primary-only supported ops pass through to the reference sub-read. When the last child completion releases its `shared_ptr`, the derived destructor invokes `complete()`, which assembles replies and informs `Objecter`.

## State and persistence behavior

`SplitOp` state is entirely in-memory and bound to one parent operation. It holds the original op pointer, `Objecter` reference, sub-read map, abort flag, flags, reference sub-read index, and an unused-looking `op_offset_map`. The state is not durable; consistency is maintained by comparing OSD internal versions and falling back to a retry if torn reads are detected.

## Dependencies and integration points

The header includes `Objecter.h`, Ceph buffer and interval-set types, pool/EC types, `mini_flat_map`, locks, and Boost error codes. It is intentionally close to `Objecter`: the split classes are friends of `Objecter`, and the implementation calls private objecter methods. It also depends on EC pool geometry from `pg_pool_t` and OSD op codes such as read, sparse read, and get-internal-versions.

## Risks and edge cases

`ECStripeIterator::operator!=()` only compares current length because it is used as a sentinel-driven range; this is valid for the local loop style but not a general-purpose iterator equality model. The pre-increment expression updates `shard_offset` by `current_info.length - chunk_size`, which relies on unsigned arithmetic and later wrap logic; EC boundary tests are important. `Finisher` uses a legacy self-destructing `Context` pattern, so ownership assumptions must match Ceph's completion semantics. Derived destructors calling `complete()` make the `abort` flag a correctness guard against fallback paths accidentally completing.

## Test signals

Header-level behavior should be tested through `SplitOp.cc` integration: EC stripe iteration across chunk boundaries, sparse and dense assembly, mixed read/metadata ops, torn-read version checks, fallback when sub-read count is one, and parent/child lifetime under cancellation or error.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osdc/SplitOp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osdc/Striper.cc -->
# sources/distributed-fs/ceph/src/osdc/Striper.cc

## Purpose

`Striper.cc` implements the mapping between logical file offsets and RADOS object extents for CephFS-style striped layouts, and provides helpers to assemble read results from multiple object reads back into file-order buffers or sparse extent maps.

## Important APIs, types, and functions

`format_oid()` creates object names from a printf-style object format and object number. `OrderByObject` supports binary insertion/search by object number in lightweight extent vectors. The internal templated `add_partial_sparse_result()` merges sparse read replies into the `StripedReadResult::partial` map while accounting for holes.

Public `Striper` functions implemented here include three `file_to_extents()` overloads, `extent_to_file()`, `object_truncate_size()`, `get_num_objects()`, `get_file_offset()`, and `StripedReadResult` methods for adding dense/sparse partial results and assembling final results into a `bufferlist`, raw buffer, or sparse extent map plus buffer.

## Control flow

`file_to_extents()` first maps a logical `(offset, len)` through `file_layout_t` fields: `object_size`, `stripe_unit`, and `stripe_count`. It computes block number, stripe number, stripe position, object set, object number, in-object offset, and slice length. Adjacent extents for the same object are merged when contiguous; each object extent records `buffer_extents` so later IO completion can place data back into logical output order. Lightweight extents can be returned directly or converted to heavyweight `ObjectExtent` values with formatted oid and `OSDMap::file_to_object_locator()`.

`extent_to_file()` performs the reverse mapping from object number and in-object extent to file extents. `object_truncate_size()` maps a file truncate size to the truncate size visible for one backing object. `get_num_objects()` computes object count for a file size using layout period and remainder. `get_file_offset()` maps one object offset back to file offset.

`StripedReadResult` accumulates partial object results keyed by logical buffer offset. Dense adds splice or move buffers according to `buffer_extents`. Sparse adds use the sparse map to skip holes and record intended lengths. Assembly emits data in sorted offset order, zero-filling holes when requested or when copying to a raw buffer; sparse assembly emits only present extents and returns total intended length.

## State and persistence behavior

No persistent state is stored. `StripedReadResult` holds transient `partial` buffers and `total_intended_len`, then clears `partial` on assembly. Mapping behavior is pure with respect to the file layout and truncate parameters.

## Dependencies and integration points

The file depends on Ceph buffer utilities, `file_layout_t`, `ObjectExtent`, `OSDMap::file_to_object_locator()`, debug logging, and `StriperTypes.h`. It is used by `Filer`, `ObjectCacher`, CephFS client code, MDS purge/accounting paths, and `Objecter` scatter/gather assembly. The lightweight path reduces allocation overhead for common small stripe counts before converting to heavyweight structures for older APIs.

## Risks and edge cases

`file_to_extents()` asserts `len > 0` and `object_size >= stripe_unit`; callers must avoid zero-length mapping requests. The VLA-style `char buf[strlen(object_format) + 32]` in `format_oid()` depends on compiler support and bounded format strings. Sparse assembly mutates input `bufferlist` by splicing, so callers must not expect the source buffer to remain intact. `total_intended_len` is incremented on every added partial and is not reset after assembly, so `StripedReadResult` instances should be one-shot or carefully reused. Truncate math around stripe/objectset boundaries is correctness-sensitive.

## Test signals

Tests should cover stripe_count 1, multi-object stripes, non-power-of-two stripe units, adjacent extent merging, buffer offset remapping, truncate sizes before/inside/after a target object, reverse mapping, sparse holes, raw-buffer zero fill, and integration through `Filer`/`ObjectCacher` scatter-gather reads and writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osdc/Striper.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osdc/Striper.h -->
# sources/distributed-fs/ceph/src/osdc/Striper.h

## Purpose

`Striper.h` declares the static striping utility used to translate file byte ranges into object byte ranges and to reassemble striped object read results. It is a central shared helper for CephFS client IO, the filer/object cacher stack, and objecter scatter/gather helpers.

## Important APIs, types, and functions

`Striper::file_to_extents()` has overloads returning lightweight extents, a map from `object_t` to `ObjectExtent` vectors, and a flat vector of `ObjectExtent`. Another overload accepts an inode number and builds the conventional `%llx.%08llx` object name format. `extent_to_file()` maps object extents back to file extents. `object_truncate_size()`, `get_num_objects()`, and `get_file_offset()` expose layout math helpers.

`StripedReadResult` stores partial results by output offset and supports dense results from vector buffer extents or lightweight buffer extents, sparse results from either map or vector sparse extents, and final assembly into a `bufferlist`, caller buffer, or sparse extent map plus buffer.

## Control flow

The declared mapping flow is stateless: callers provide a `file_layout_t`, logical offset/length, truncate size, and optional buffer offset. The implementation computes one or more object extents, each with its in-object offset/length/truncate size and mapping back to output buffer extents. Read paths add each object's result to `StripedReadResult`, then call an assembly overload to produce the final logical read result.

## State and persistence behavior

`Striper` itself has no instances and no persistent state. `StripedReadResult` has transient aggregation state that is cleared by assembly methods. The persistent interpretation comes from the caller's file layout and object naming convention, not from this class.

## Dependencies and integration points

The header depends on Ceph file and OSD types plus `StriperTypes.h`. It forward-declares `file_layout_t`. Integration points include `Filer.cc`, `ObjectCacher`, CephFS client layout handling, MDS code that reasons about object counts/offsets, and `Objecter` scatter/gather read completion.

## Risks and edge cases

All APIs assume valid layout values, especially `object_size`, `stripe_unit`, and `stripe_count`. The vector/map overloads differ in grouping behavior; callers that need object grouping should use the map overload. The raw-buffer assembly requires the destination length to match `total_intended_len`, so mismatched extents will assert. Sparse assembly has several overloads with different sparse-map types; tests should protect against semantic drift between them.

## Test signals

Useful signals are unit tests for file-to-object and object-to-file mapping across stripe boundaries, object count calculations, truncate propagation, and read assembly through dense and sparse paths. Integration tests should validate `Filer` and `ObjectCacher` behavior for multi-object reads/writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osdc/Striper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osdc/StriperTypes.h -->
# sources/distributed-fs/ceph/src/osdc/StriperTypes.h

## Purpose

`StriperTypes.h` defines lightweight extent containers used by `Striper` to represent object extents and their output-buffer mappings without the heavier `ObjectExtent` type. These types support fast common-case file layout mapping.

## Important APIs, types, and functions

Inside namespace `striper`, `BufferExtent` is an `(offset, length)` pair for an extent in the logical striped output buffer. `LightweightBufferExtents` is a `boost::container::small_vector<BufferExtent, 4>`, optimized for the common case of a few buffer spans.

`LightweightObjectExtent` is a non-default-constructible struct with `object_no`, in-object `offset`, in-object `length`, `truncate_size`, and `buffer_extents`. `LightweightObjectExtents` is a small vector of up to four lightweight object extents before heap allocation. An `operator<<` prints the extent fields and buffer mappings.

## Control flow

The types are passive data carriers. `Striper::file_to_extents()` constructs and possibly merges `LightweightObjectExtent` entries, then either returns them directly or converts them into heavyweight `ObjectExtent` values with object names and locators.

## State and persistence behavior

There is no persistent state. The containers hold transient mapping results for a single layout operation or read assembly operation.

## Dependencies and integration points

The header depends on `include/types.h`, Boost small vectors, and stream output. It is included by `Striper.h` and used by `Striper.cc`, `ObjectCacher`, and any path that wants lower-allocation mapping output.

## Risks and edge cases

The types do not validate ranges or ordering; callers must preserve sorted object order and meaningful buffer extents. `operator<<` relies on stream support for the small-vector of buffer extents. The deleted default constructor prevents accidental uninitialized object extents, but it also means container operations must construct with full extent values.

## Test signals

Test coverage is indirect through `Striper::file_to_extents()` and read assembly. Useful checks include small-vector behavior for one to four extents, conversion to heavyweight `ObjectExtent`, output formatting for debug logs, and preservation of `truncate_size` and `buffer_extents`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osdc/StriperTypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osdc/WritebackHandler.h -->
# sources/distributed-fs/ceph/src/osdc/WritebackHandler.h

## Purpose

`WritebackHandler.h` declares the abstract writeback interface consumed by `ObjectCacher`. It separates cache management from the concrete backend that reads, writes, performs copy-on-write checks, and optionally supports scattered writes.

## Important APIs, types, and functions

`WritebackHandler` is an abstract base class with virtual `read()`, `may_copy_on_write()`, and object write methods. `read()` takes object id, object number, locator, offset/length, snap id, output buffer, truncate metadata, op flags, trace, and completion context. The primary `write()` takes object id, locator, extent, `SnapContext`, buffer, mtime, truncate metadata, journal tid, trace, and commit context. `overwrite_extent()` is an optional hook for remapping a journal tid after overwrite. `can_scattered_write()` defaults false, and the vector write overload defaults to returning 0 without doing work.

## Control flow

`ObjectCacher` calls this interface when dirty or missing cached object ranges need backend IO. Implementations such as `client/ObjecterWriteback.h` bridge these calls to `Objecter` operations. The scattered-write overload is available only when an implementation advertises support through `can_scattered_write()`.

## State and persistence behavior

The interface stores no state. Backend implementations determine durability by submitting writes to RADOS/Objecter and completing the supplied contexts. `journal_tid` and `overwrite_extent()` tie cache writeback to higher-level journaling/order tracking.

## Dependencies and integration points

The header depends on `Context`, Ceph core types, Zipkin tracing, and OSD object types. It is included by `ObjectCacher.cc` and implemented by client-side objecter writeback code. It connects cache, CephFS client, tracing, snap context, and RADOS object IO.

## Risks and edge cases

Because completions are raw `Context*`, implementations must define ownership and always complete or safely cancel callbacks. The default scattered write overload returns success-looking `0` without committing anything; callers must honor `can_scattered_write()` before using it. `may_copy_on_write()` correctness matters for snapshot isolation and cache coherency.

## Test signals

Tests should exercise `ObjectCacher` with a concrete `WritebackHandler`: read miss fill, dirty writeback, truncation metadata, snapshot copy-on-write decisions, journal tid overwrite tracking, and both unsupported and supported scattered-write paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osdc/WritebackHandler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osdc/error_code.cc -->
# sources/distributed-fs/ceph/src/osdc/error_code.cc

## Purpose

`error_code.cc` implements the Boost.System error category for Objecter/OSDC-specific errors. It gives `osdc_errc` values names, human messages, default generic/Ceph conditions, equivalence rules, and conversion back to negative errno-style codes.

## Important APIs, types, and functions

`osdc_error_category` derives from `ceph::converting_category`. It implements `name()`, the char-buffer and string `message()` overloads, `default_error_condition()`, `equivalent()`, and `from_code()`. `osdc_category()` returns a function-local static category instance.

The handled errors are pool does-not-exist, pool exists, precondition violation, operation not supported, snapshot exists, snapshot does-not-exist, timeout, pool EIO, and handler failure.

## Control flow

Objecter code can return `make_error_code(osdc_errc::...)`. Boost.System dispatches category methods when code is formatted, compared to conditions, or converted by Ceph helpers. `default_error_condition()` maps objecter domain errors to `ceph::errc` or `boost::system::errc`, while `equivalent()` adds compatibility with standard conditions such as `no_such_file_or_directory` and `file_exists`. `from_code()` maps each category value to a negative errno used by legacy Ceph APIs.

## State and persistence behavior

The only state is the immutable singleton error category. No persistent state is involved.

## Dependencies and integration points

The file includes `common/error_code.h` and `osdc/error_code.h`. `Objecter.cc` uses these errors for pool DNE/EIO, pool/snapshot create/delete failures, operation precondition failures, timeouts, and reply handler failures. Callers using Boost.System can compare against both objecter-specific codes and generic conditions.

## Risks and edge cases

Every new `osdc_errc` must be added consistently to `message()`, `default_error_condition()`, `equivalent()` if needed, and `from_code()`. Unknown values return "Unknown error", a self condition, and `-EDOM`. The diagnostic pragmas suppress non-virtual destructor warnings around the category class; changing the base type may require revisiting them.

## Test signals

Tests should verify category name, messages, implicit `make_error_code()`, comparisons with generic conditions, `ceph::errc::not_in_map` equivalence for missing pools/snaps, errno conversion, and Objecter paths that surface `handler_failed` after callback exceptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osdc/error_code.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osdc/error_code.h -->
# sources/distributed-fs/ceph/src/osdc/error_code.h

## Purpose

`error_code.h` declares the Objecter/OSDC error domain for Boost.System. It allows `osdc_errc` enum values to be used directly as error codes and conditions by Objecter callers and asynchronous completions.

## Important APIs, types, and functions

The header declares `osdc_category()`, enum class `osdc_errc`, Boost.System traits `is_error_code_enum` and `is_error_condition_enum`, and inline `make_error_code()` / `make_error_condition()` conversions. Enum values cover pool existence, precondition, unsupported operation, snapshot existence, timeout, pool EIO, and handler failure cases.

## Control flow

When code returns or passes an `osdc_errc`, Boost.System finds the specialized trait and constructs a `boost::system::error_code` using `osdc_category()`. Objecter APIs with Asio completion signatures can therefore report objecter-specific failures without exposing negative errno as the primary typed interface.

## State and persistence behavior

No state is declared here. Runtime category state is provided by `error_code.cc`.

## Dependencies and integration points

The header depends only on Boost.System. It is included by Objecter code and any consumers that compare or construct OSDC-specific errors. `Objecter.h` includes it indirectly through error handling and completion interfaces.

## Risks and edge cases

The enum starts at 1 so zero remains success in the category implementation. Adding enum values requires updating `error_code.cc`; otherwise messages and conversions fall through to unknown handling. The header marks `is_error_condition_enum` false but still provides an explicit `make_error_condition()`, so generic comparison behavior relies on category methods rather than implicit condition conversion.

## Test signals

Compile-time tests should verify implicit conversion to `boost::system::error_code`. Runtime tests should check success remains zero, category identity is stable, and every enum value has the expected message/default condition/errno mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osdc/error_code.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/CMakeLists.txt -->
# sources/distributed-fs/ceph/src/rgw/CMakeLists.txt

## Purpose

`src/rgw/CMakeLists.txt` defines the RADOS Gateway build graph. It configures feature-dependent source lists, generated gperf sources, static libraries, executables, shared librgw output, include paths, compile definitions, dependencies, link libraries, tests, and install rules for RGW components.

## Important APIs, types, and functions

The CMake file requires `gperf`, defines `gperf_generate(input output)`, finds ICU, and conditionally configures Arrow/Parquet/Flight, ISA-L, AMQP, Kafka, DBStore, Motr, DAOS, POSIX, D4N, Jaeger, Lua package, LTTng, curl/OpenSSL, and tests. Main targets are `rgw_common` static library, `rgw_a` static library, `rgw_schedulers`, `radosgw`, `radosgw-admin`, `radosgw-es`, `radosgw-token`, `radosgw-object-expirer`, `rgw-policy-check`, and shared library `rgw`.

`librgw_common_srcs`, `rgw_a_srcs`, scheduler sources, and executable source lists define which `.cc` files participate in each target. `target_link_libraries()`, `target_include_directories()`, `target_compile_definitions()`, `target_compile_options()`, and `add_dependencies()` express integration contracts.

## Control flow

Configuration begins by detecting tools/features and appending source files based on feature flags. `rgw_common` is created first and linked to common Ceph, cls clients, ICU, Lua, RapidJSON, Boost, fmt, OpenSSL, and optional backend/transport libraries. `rgw_a` layers frontend/application sources on top of `rgw_common`. Scheduler, daemon, admin, utility, and shared-library targets then link against these libraries. Generated IAM policy keyword code is produced by `gperf_generate()` and attached to `rgw_iam_policy.cc` through `OBJECT_DEPENDS`.

## State and persistence behavior

The file affects build-system state, not runtime persistence. It writes generated build artifacts such as `rgw_iam_policy_keywords.frag.cc` into the build tree and installs selected binaries/libraries/scripts into configured destinations.

## Dependencies and integration points

It integrates RGW with Ceph common/global libraries, cls clients, librados/libneorados, dmclock, Boost context/url, Lua, RapidJSON, OpenSSL, BLAKE3, ICU, curl, expat, optional Arrow/Flight, OATH, LMDB, RDKafka, RabbitMQ, OpenLDAP, Motr, DAOS, Jaeger, LTTng tracepoint targets, and tests. The conditional source lists mirror RGW's pluggable storage/transport architecture.

## Risks and edge cases

Conditional target creation is complex. `radosgw-admin` is only created under `WITH_RADOSGW_RADOS` or POSIX-without-RADOS, but later Arrow link logic refers to `radosgw-admin` unconditionally under `WITH_RADOSGW_ARROW_FLIGHT`; unusual option combinations could break configuration if the target does not exist. Global `add_definitions()` affects directory scope and may leak feature macros more broadly than target-scoped definitions. Source list drift can silently omit new RGW files from the intended library. Optional dependency order matters for Arrow Flight and linkers.

## Test signals

Validation should include CMake configure/build matrices for default RGW, without RADOS, POSIX, DBStore, D4N, Arrow/Parquet/Flight, Kafka, AMQP, DAOS/Motr, Jaeger/LTTng, and `WITH_TESTS`. Build tests should verify generated gperf output, install target presence, no missing target references, and successful link of all executables/shared libraries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/async_utils.h -->
# sources/distributed-fs/ceph/src/rgw/async_utils.h

## Purpose

`async_utils.h` provides RGW helpers for invoking Boost.Asio C++ coroutines from synchronous or stackful-coroutine code. The helpers co_spawn awaitables, optionally block the caller, capture exceptions, convert exceptions to negative Ceph return codes, and log failures with RGW debug-prefix context.

## Important APIs, types, and functions

All APIs are overloads of `rgw::run_coro()`. There are executor-based and execution-context-based overloads for awaitables returning `void`, a single value `T`, or `std::tuple<Ts...>`. The first family is intended for interactive/blocking frontends and writes exception text to `std::string* what`. The second family accepts `std::string_view name`, `optional_yield y`, and a log level; it runs through an existing stackful yield context when available or blocks otherwise.

The implementation uses Boost.Asio concepts, `asio::awaitable`, `asio::co_spawn`, Ceph async completion adapters `use_blocked` and `redirect_error`, `maybe_warn_about_blocking()`, `ceph::from_exception()`, and `ldpp_dout_fmt()`.

## Control flow

For blocking calls, `run_coro()` initializes `std::exception_ptr e`, warns about blocking, spawns the awaitable on the supplied executor with `async::use_blocked[e]`, optionally assigns the returned value(s), then returns `ceph::from_exception(e, what)`. For yield-aware calls, if `optional_yield` is present the coroutine is spawned on the yield executor with `async::redirect_error(yield, e)` so it cooperates with the stackful coroutine. If no yield is present, it falls back to the blocking path. After completion, it converts any exception and logs `name: failed: what` when an exception was captured.

Execution-context overloads forward to executor overloads through `get_executor()`. Template constraints require the supplied executor to be convertible to the awaitable executor, which catches mismatched coroutine/executor use at compile time.

## State and persistence behavior

The helpers keep only stack-local exception/value state. They do not persist data. They may block an RGW thread when called with null yield or from synchronous tools such as `radosgw-admin`.

## Dependencies and integration points

The header depends on Boost.Asio coroutine support, Ceph async concepts/adapters, Ceph error conversion, dout logging, and `rgw_asio_thread.h` for blocking warnings/yield types. Source references show `radosgw-admin.cc` and RGW REST log code use `rgw::run_coro()` to bridge coroutine implementations into command handlers and admin flows.

## Risks and edge cases

The helpers are marked `noexcept` only for the void blocking overloads; value and tuple overloads assume assignment from `co_spawn()` result does not throw. Blocking fallback can deadlock or harm latency if used on an executor that requires the current thread to make progress; `maybe_warn_about_blocking()` is the guard signal. Tuple overloads assign to `std::tuple<Ts&...>`; caller lifetimes and exact arity/types must match. The comments contain typos but not behavioral issues.

## Test signals

Tests should cover successful void/value/tuple coroutines, exception conversion and `what` population, yield-present versus null-yield execution, logging on failure, executor-convertibility compile checks, and integration in `radosgw-admin` commands that currently call `run_coro()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/async_utils.h -->
