# subset-b-007000 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_restore.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_restore.cc

## Purpose
`rgw_restore.cc` implements the RGW cloud-tier restore coordinator. It persists restore work as sharded `RestoreEntry` records, runs a background `RestoreWorker` that scans those records under per-shard locks, invokes SAL object restore hooks for cloud-s3/cloud-s3-glacier tiers, updates restore-related object attributes, sends restore notifications, and exposes list/status helpers for administrative inspection.

## Important APIs, Types, and Functions
`RestoreEntry::{dump,decode_json,generate_test_instances}` provide JSON/debug and encoding support for queued restore work. `Restore::initialize()` creates `restore.N` shard object names from `rgw_restore_max_objs`, initializes a SAL `Restore` implementation, and creates a `RestoreWaiterRegistry`. `start_processor()`, `stop_processor()`, `wake_worker()`, and `RestoreWorker::entry()` own the background loop. `choose_oid()` hashes bucket/object/instance into a restore shard. `process(RestoreWorker*)` randomizes the shard start point and calls `process(index, max_secs)`. `process(index, max_secs)` takes a `RestoreSerializer` lock, lists entries, processes each entry, trims completed records, and re-adds entries still in `RestoreAlreadyInProgress`. `process_restore_entry()` loads the bucket and object, verifies status and tier, calls `Object::restore_obj_from_cloud()`, updates status, notifies waiters, and emits `ObjectRestoreCompleted`. `restore_obj_from_cloud()` is the request-time path that publishes `ObjectRestoreInitiated`, marks the object in progress, enqueues a `RestoreEntry`, and wakes the worker for cloud-s3 tiers.

## Control Flow
Incoming restore requests call `restore_obj_from_cloud()`: validate bucket/object, reserve notification, set `RGW_ATTR_RESTORE_STATUS` to `RestoreAlreadyInProgress`, append an entry to the chosen restore shard, optionally wake the worker, and commit the initiated notification. The worker periodically scans all shards from a random offset. For each shard it tries a bounded lock, paginates restore entries, and processes until entries end, time expires, or shutdown begins. Completed entries are removed by trimming to the final marker; still-in-progress entries are appended back after trim.

`process_restore_entry()` first filters temporary restores to their source zone. It then loads bucket/object state, checks that the persisted status is still in progress, derives target placement and storage class, resolves the placement tier, requires an S3-style cloud tier, and delegates the actual restore. The SAL object method returns `in_progress` and size by reference. If work remains asynchronous, the entry is requeued. If work finishes, the entry becomes `CloudRestored` and completion notification is sent.

## State and Persistence Behavior
Persistent state is split between sharded restore-entry objects managed by `sal_restore` and object attributes such as `RGW_ATTR_RESTORE_STATUS`, `RGW_ATTR_RESTORE_EXPIRY_DATE`, `RGW_ATTR_DELETE_AT`, `RGW_ATTR_INTERNAL_MTIME`, `RGW_ATTR_RESTORE_TYPE`, and `RGW_ATTR_RESTORE_VERSIONED_EPOCH`. Restore shard locks use `RestoreSerializer` with the `restore_process` lock name. `update_cloud_restore_exp_date()` atomically rewrites restore expiry/delete-at attrs for temporary restores. `finalize()` resets the SAL handle, clears shard names, and shuts down waiters.

## Dependencies and Integration Points
This file depends on SAL `Driver`, `Bucket`, `Object`, `PlacementTier`, `Restore`, `RestoreSerializer`, notification publishing, zone/zonegroup placement configuration, Ceph object encoding, `RGWFormatterFlusher`, and `RestoreWaiterRegistry`. It is tied to lifecycle/cloud-tier code through `Object::restore_obj_from_cloud()` and to GET/read-through behavior through waiter notification.

## Risks
The restore queue relies on trim-and-readd semantics. Errors after processing but before trim/readd can duplicate work or leave stale entries for a later pass. `process_restore_entry()` logs `bucket->get_name()` when bucket loading fails, but `bucket` may be null on that path. Notification publication failures are mostly logged without undoing restore state. Waiter notification only happens when `!in_progress`, so a failed attempt marked in-progress by the backend could leave GET waiters to timeout.

## Test Signals
Tests should cover request enqueueing, shard hash stability, worker lock contention, pagination/trim/requeue behavior, temporary restores constrained to source zone, missing bucket/object handling, non-S3 tier rejection, status attr decode, failed backend restore setting `RestoreFailed`, expiry-date updates, list/status formatting, initiated/completed notification paths, worker wake for cloud-s3, shutdown, and waiter completion on success/failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_restore.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_restore.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_restore.h

## Purpose
`rgw_restore.h` declares the RGW restore coordinator and the serializable restore queue entry used for cloud-tier object restoration. It is the public interface between request handling, background restore processing, the SAL restore backend, and GET waiters blocked on restore completion.

## Important APIs, Types, and Functions
`RestoreEntry` stores the durable unit of restore work: `rgw_bucket bucket`, `rgw_obj_key obj_key`, optional temporary-restore `days`, source `zone_id`, and `rgw::sal::RGWRestoreStatus status`. It provides Ceph encoding, JSON dump/decode, and test-instance generation.

`Restore` derives from `DoutPrefixProvider` and owns `CephContext`, a SAL `Driver`, a SAL `Restore` backend, shard object names, shutdown state, a waiter registry, and one `RestoreWorker`. `initialize()` and `finalize()` manage backend setup/teardown. `start_processor()`, `stop_processor()`, and `wake_worker()` manage the background thread. `process()` variants implement the shard loop and per-entry processing. Public operation helpers include `set_cloud_restore_status()`, `get_expiration_date()`, `update_cloud_restore_exp_date()`, `restore_obj_from_cloud()`, `send_notification()`, `list()`, and `status()`.

`RestoreWorker` is a nested `Thread` with a mutex/condition variable. It calls back into the owning `Restore`, sleeps according to `rgw_restore_processor_period`, and can be woken by restore enqueue operations.

## Control Flow
The interface supports two paths. The foreground request path calls `restore_obj_from_cloud()` to set object state and enqueue work. The background path is started via `start_processor()`, then repeatedly calls `process(RestoreWorker*, optional_yield)`, which fans into shard-level and entry-level processors. The same class exposes admin-style `list()` and `status()` queries over restore state.

## State and Persistence Behavior
The header shows that queue persistence is abstracted behind `rgw::sal::Restore`, while object restore state is persisted through object attributes. `restore_oid_prefix` and `restore_index_lock_name` define the shard naming and locking conventions. `down_flag` is atomic and controls thread exit. `waiter_registry` is in-memory and intentionally not durable; it bridges active GET requests to background completion.

## Dependencies and Integration Points
The declarations include Ceph threading, conditions, librados types, RGW common types, notifications, SAL interfaces, and `rgw_restore_waiter.h`. Restore is instantiated and controlled by the RADOS-backed driver but uses SAL-level abstractions so the queue and object restore implementation can live in the selected backend.

## Risks
`Restore` has a destructor with side effects (`stop_processor()` and `finalize()`), so ownership/lifetime mistakes can block waiting for the worker. The class stores raw pointers to `CephContext` and `Driver`; callers must ensure those outlive restore processing. `max_objs` is bounded by `HASH_PRIME`, and a zero or invalid configuration would make shard choice unsafe unless initialization rejects it downstream.

## Test Signals
Interface tests should verify serialization compatibility for `RestoreEntry`, start/stop idempotence, worker wake behavior, waiter registry lifetime, status attr helpers, expiry-date calculation with normal and debug intervals, and that frontend restore requests can enqueue while background processing is already active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_restore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_restore_waiter.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_restore_waiter.cc

## Purpose
`rgw_restore_waiter.cc` implements an in-memory registry for GET requests waiting for a cloud restore to complete. It provides blocking and coroutine-friendly wait paths, pools waiter objects to reduce allocation churn, maps object identity to waiter vectors, and wakes or cancels all registered waiters when restore processing completes or shuts down.

## Important APIs, Types, and Functions
`RestoreWaiter::wait_for()` waits on `completed`. With `optional_yield`, it creates a Boost.Asio steady-clock timer and uses timer cancellation as the wake mechanism. Without yield, it uses `std::condition_variable::wait_for()`. `complete()` stores success/result flags, sets `completed`, notifies blocking waiters, and cancels any active async timer. `reset()` prepares a pooled waiter for reuse.

`RestoreWaiterPool::acquire()` evicts stale free waiters, returns a reset pooled waiter or allocates a new one, and wraps it in a `shared_ptr` with a deleter that returns it to the owning registry. `release()` returns waiters to a bounded free list or deletes when the pool is full. `evict_old_waiters()` drops waiters unused for five minutes.

`RestoreWaiterRegistry::register_waiter()` creates a key from bucket and object, acquires a pooled waiter, and appends it under a shared registry lock unless shutdown has begun. `unregister_waiter()` removes one waiter from its cached-key vector. `notify_completion()` moves all waiters for a key out of the map and completes them outside the lock. `shutdown()` rejects new registrations, drains all vectors, and completes waiters with `-ECANCELED`.

## Control Flow
A caller registers a waiter for a bucket/object, waits with a timeout, and uses `WaiterGuard` from the header to unregister on exit. Restore completion calls `notify_completion()`, which removes the key and signals all active waiters. Timeout callers unregister themselves; completed waiters are also removed by the registry move. When the last `shared_ptr` drops, the custom deleter returns the waiter to the pool.

## State and Persistence Behavior
All state is process-local. The registry map uses a `std::shared_mutex`, waiter status uses atomics, and timer lifetime is stored as a weak pointer behind `timer_mtx`. No restore waiter state survives restart; after restart, GET callers must re-check object attrs and register again if needed.

## Dependencies and Integration Points
The implementation depends on `optional_yield`, Boost.Asio timers, Ceph coarse time, `rgw_bucket`, `rgw_obj_key`, and restore worker calls to `notify_completion()`. It integrates with read-through restore behavior rather than persistent restore queue management.

## Risks
`register_waiter()` can return `nullptr` during shutdown after acquiring a pooled waiter; the local `shared_ptr` then releases through the pool deleter, which is okay but should be covered. Async waits do not hold `mtx`, so correctness depends on atomic ordering and timer cancellation. Key construction includes bucket key, object name, and optional instance; mismatches with restore queue object identity would strand waiters.

## Test Signals
Tests should cover blocking wait success, blocking timeout, async-yield wake by timer cancellation, shutdown cancellation, unregister after timeout, multiple waiters on one object, multiple object keys, pool reuse, pool max-size deletion, stale waiter eviction, and registration races with shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_restore_waiter.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_restore_waiter.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_restore_waiter.h

## Purpose
`rgw_restore_waiter.h` declares the in-memory waiter subsystem used by restore/read-through paths. It abstracts a single waiting GET request, a bounded object pool, a bucket/object registry, and an RAII guard for automatic unregistration.

## Important APIs, Types, and Functions
`RestoreWaiter` contains the synchronization state for one waiter: a condition variable for blocking callers, a Boost.Asio steady-clock timer for coroutine callers, atomic `completed`, `failed`, and `result`, a cached registry key, and a last-used timestamp. `wait_for()`, `complete()`, and `reset()` are the core operations.

`RestoreWaiterPool` owns a mutex-protected `free_list` of `unique_ptr<RestoreWaiter>`, bounded by `MAX_POOL_SIZE` and aged by `EVICTION_TIME`. `acquire()` returns a `shared_ptr` using a custom deleter; `release()` and `evict_old_waiters()` are private registry-owned helpers.

`RestoreWaiterRegistry` derives from `enable_shared_from_this` so pooled waiters can safely return to their owner. It maps string keys to vectors of waiters and exposes `register_waiter()`, `unregister_waiter()`, `notify_completion()`, and `shutdown()`. `WaiterGuard` unregisters a waiter in its destructor and is non-copyable.

## Control Flow
Callers acquire a registry from `Restore`, register a waiter for the object, construct a `WaiterGuard`, and then call `wait_for()` with either a blocking or coroutine yield context. Restore completion uses the same bucket/object key to notify all matching waiters. Shutdown flips an atomic flag before draining the map so late callers are rejected.

## State and Persistence Behavior
The subsystem intentionally persists nothing. Registry keys are derived from RGW bucket and object identity. Pooled waiters are reset before reuse; `last_used` only drives memory reclamation. Result codes are stored as `int16_t`, which assumes restore-related error values fit in that range.

## Dependencies and Integration Points
The header depends on C++ synchronization primitives, Boost.Asio timers, Ceph time, `optional_yield`, `rgw_common.h`, and SAL object identity types. It is used by `rgw_restore.{h,cc}` and by request paths that need to block until restore completion.

## Risks
The `int16_t` result field can truncate uncommon large negative errors. `WaiterGuard` relies on callers keeping both registry and waiter pointers valid and on `unregister_waiter()` being safe after completion moved the waiter vector out of the registry. The timer and condition-variable paths must stay semantically aligned.

## Test Signals
Header-level tests should instantiate the RAII guard, verify non-copyability, validate that shutdown prevents registration, and exercise result/failed/completed state after `complete()` and `reset()`. Integration tests should cover a GET waiting on a restore entry completed by the background worker.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_restore_waiter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_role.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_role.cc

## Purpose
`rgw_role.cc` implements common IAM role metadata behavior shared by SAL backends. It formats and parses `RGWRoleInfo`, validates role input, constructs role ids/ARNs/creation timestamps, and mutates inline policies, trust policy, tags, and session duration before backend-specific persistence.

## Important APIs, Types, and Functions
`RGWRoleInfo::dump()` emits IAM-facing JSON fields, including tenant-qualified role name, trust policy, inline policies, managed policy ARNs, tags, description, account id, and max session duration. `decode_json()` reconstructs the same fields, splitting tenant from names that contain `$`.

`RGWRole::RGWRole(...)` initializes a role from request input, defaulting path to `/`, parsing tenant from the name, defaulting max session duration to 3600 seconds, and storing tags/trust policy/description. The id constructor initializes lookup-by-id objects. `validate_input()` enforces name/path lengths and regexes plus max-session duration bounds. `create()` validates input, generates a UUID id if absent, constructs `arn:aws:iam::<account-or-tenant>:role<path><name>`, fills an ISO-like creation timestamp, and calls virtual `store_info(exclusive=true)`.

Policy/tag helpers mutate `RGWRoleInfo`: `set_perm_policy()`, `get_role_policy_names()`, `get_role_policy()`, `delete_policy()`, `update_trust_policy()`, `set_tags()`, `get_tags()`, `erase_tags()`, and `update_max_session_duration()`.

## Control Flow
Request handlers generally obtain a backend role object through `Driver::get_role()`, call common mutators/validation, then call a virtual persistence method. Creation is the main full flow in this file: validate, choose/generate id, compute ARN and creation date, then store through the backend. Loads, deletes, and low-level stores are abstract virtual methods from the header.

## State and Persistence Behavior
`rgw_role.cc` only mutates the in-memory `RGWRoleInfo`; persistence is delegated to `store_info()`, `load_by_name()`, `load_by_id()`, and `delete_obj()` implemented by a SAL backend. Encoding in the header persists versioned role fields. `objv_tracker` and `mtime` are part of role state but not manipulated much here beyond setting `mtime` to a default construction value.

## Dependencies and Integration Points
The file depends on Ceph formatter/JSON/time utilities, UUID generation, RGW string helpers, zone services, managed policy structures, and SAL backend role implementations. It is used by IAM APIs such as CreateRole, PutRolePolicy, AttachRolePolicy-related metadata, tagging, and role listing.

## Risks
`std::stoull()` in constructors and `update_max_session_duration()` can throw on malformed input unless callers prevalidate. `get_role_policy_names()` applies `std::move()` to keys from a const map iteration, which is ineffective but surprising. `set_tags()` appends tags before checking the 50-tag limit; on failure the object remains mutated. Regexes must match AWS semantics closely, especially path formatting.

## Test Signals
Tests should cover valid/invalid role names and paths, session duration min/max and malformed strings, tenant extraction, ARN construction with account id versus tenant, UUID generation, creation timestamp format, inline policy CRUD, duplicate/many tags, JSON dump/decode round trip including managed policies, and backend store failure propagation from `create()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_role.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_role.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_role.h

## Purpose
`rgw_role.h` defines the IAM role metadata record and the abstract SAL role interface. It separates common IAM role validation/mutation logic from backend persistence, while preserving Ceph encoding compatibility for stored role objects.

## Important APIs, Types, and Functions
`RGWRoleInfo` contains id, name, path, ARN, creation date, trust policy, inline permission policies, managed policies, tenant, description, max session duration, tags, object version tracker, mtime, and account id. Its encoder is at struct version 4: older versions lack tenant, max session duration, account id, description, and managed policies. JSON helpers are declared for admin/API formatting.

`rgw::sal::RGWRole` owns a protected `RGWRoleInfo info` and declares backend virtuals: `load_by_name()`, `load_by_id()`, `store_info()`, and `delete_obj()`. Common methods validate max session duration and input, extract tenant from names, create roles, update trust policy, mutate inline policies/tags, and update max session duration. Constants define ARN prefix, max name/path lengths, and session duration bounds.

## Control Flow
Code constructs an `RGWRole` via driver factories either from request fields, an id, or existing `RGWRoleInfo`. Common methods mutate/validate the cached `info`, then backend virtuals persist or load it. Getters expose fields to IAM handlers and response formatters.

## State and Persistence Behavior
Persistent state is represented by `RGWRoleInfo` encoding. Versioned decode protects rolling upgrades by only reading newer fields when present. `RGWObjVersionTracker` supports optimistic concurrency in backend stores but is not encoded in `RGWRoleInfo`; it is runtime metadata alongside `mtime`.

## Dependencies and Integration Points
The header depends on Ceph encoding, JSON, time, async yield, RGW common identities, and `rgw_iam_managed_policy.h`. `Driver::get_role()` in `rgw_sal.h` returns concrete implementations of this interface.

## Risks
The interface exposes mutable `RGWRoleInfo& get_info()`, so callers can bypass validation. Decode compatibility means defaults for missing fields must remain safe. `set_tags()` and other common mutators do not persist automatically; callers must remember to call `store_info()`.

## Test Signals
Tests should exercise encode/decode across struct versions, JSON decode with tenant-qualified names, validation boundary constants, virtual backend contract for exclusive store, and mutation methods followed by backend persistence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_role.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_s3_filter.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_s3_filter.cc

## Purpose
`rgw_s3_filter.cc` implements S3 notification filter parsing, formatting, and matching. Filters can match object key prefix/suffix/regex, user metadata key-value pairs, and object tag key-value pairs.

## Important APIs, Types, and Functions
`rgw_s3_key_filter::{dump,decode_xml,dump_xml,has_content}` handles the `S3Key` filter. XML decode allows one prefix, one suffix, and one regex rule and throws on invalid or duplicate rule names. `rgw_s3_key_value_filter` handles metadata/tag `FilterRule` lists as a flat key-value map. `rgw_s3_filter` composes key, metadata, and tag filters and emits JSON/XML only when content exists.

`match(const rgw_s3_key_filter&, const std::string&)` checks prefix, suffix, and full regex match. `match(const rgw_s3_key_value_filter&, const KeyValueMap&)` uses sorted `std::includes()` for flat metadata. The multimap overload checks that each filter pair appears among equal-range values. `match(const rgw_s3_filter&, const rgw::sal::Object*)` returns true if any one of key, metadata, or tag filter matches.

## Control Flow
Notification configuration XML is decoded into filter structs. During event evaluation, the object pointer is checked, then key filter is evaluated first. If metadata rules exist, RGW object attrs with `RGW_ATTR_META_PREFIX` are converted into a flat map and compared. If tag rules exist, `RGW_ATTR_TAGS` is decoded into `RGWObjTags` and compared. A match in any category returns true.

## State and Persistence Behavior
The structs are serializable into bucket notification configuration. `rgw_s3_filter` encoder version 2 added `tag_filter`; decoding old version 1 configs leaves tags empty. Matching reads cached object attrs but does not persist or mutate state.

## Dependencies and Integration Points
The file depends on RGW XML helpers, formatter encode helpers, notification/pubsub structures, SAL `Object`, RGW object tags, Boost string prefix checks, and C++ regex. It is used by bucket notification topic filtering.

## Risks
Top-level matching is OR across key, metadata, and tags; if intended semantics require all configured filter categories to match, this is broad. Regexes are compiled on every match and invalid regex strings can throw. Metadata key stripping uses `sizeof(RGW_ATTR_PREFIX)-1` after checking `RGW_ATTR_META_PREFIX`, so prefix constants must stay compatible. Metadata comparison depends on sorted `flat_map` ordering.

## Test Signals
Tests should cover XML duplicates, JSON/XML dump elision, prefix/suffix/regex combinations, invalid regex handling, metadata extraction from attrs, tag decode failure returning false, multivalue tag matching, old encoded filters without tags, and OR-versus-AND behavior expected by notification APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_s3_filter.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_s3_filter.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_s3_filter.h

## Purpose
`rgw_s3_filter.h` declares serializable filter structures for S3 bucket notifications. It is the contract used to store, decode, dump, and evaluate key, metadata, and tag filters.

## Important APIs, Types, and Functions
`rgw_s3_key_filter` stores `prefix_rule`, `suffix_rule`, and `regex_rule`, with content checks, XML/JSON formatting, XML decode, and Ceph encoding. `rgw_s3_key_value_filter` stores a `boost::container::flat_map<std::string,std::string>` for metadata or tag filter rules. `rgw_s3_filter` composes key, metadata, and tag filters. Free `match()` overloads evaluate key filters, flat metadata maps, multimap tags, and complete object filters.

## Control Flow
Configuration decode fills the structs from XML. Persistence uses the inline encode/decode methods. Runtime notification code calls the appropriate `match()` overload, usually the object-level matcher, against a SAL object with cached attrs.

## State and Persistence Behavior
The key and key-value filters are version 1 encodings. The composite `rgw_s3_filter` is version 2 with backwards-compatible decoding that only reads `tag_filter` for version 2 or newer payloads. No runtime state is stored beyond filter fields.

## Dependencies and Integration Points
The header depends on Ceph `bufferlist` encoding, `Formatter`, `XMLObj`, `boost::container::flat_map`, and SAL object types. It is included by notification and pubsub configuration code.

## Risks
Filter structures expose public fields, so validation is concentrated in XML decode and can be bypassed by internal callers. Runtime regex validity is not represented in the type. The complete-object matcher returns a boolean without explaining which category matched, limiting diagnostics.

## Test Signals
Tests should verify encoder compatibility, XML round trips, `has_content()` for each filter type, public-field direct construction behavior, and object-level matching with empty filters and null object pointers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_s3_filter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_s3select.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_s3select.cc

## Purpose
`rgw_s3select.cc` implements the S3 Select operation for RGW. It creates the select RGW op, parses AWS SelectObjectContent XML, streams object data through the s3select engine for CSV/JSON and optionally Parquet, formats AWS event-stream responses with CRCs, tracks usage counters, and handles scan ranges and Trino-specific row-boundary shaping.

## Important APIs, Types, and Functions
`rgw::s3select::create_s3select_op()` returns `RGWSelectObj_ObjStore_S3`. `aws_response_handler` builds AWS event-stream messages: headers for Records, Cont, Progress, Stats, End, and errors; `create_message()` fills total length/header length/prelude CRC/message CRC; send methods write binary data via RGW formatter and set chunked transfer encoding.

`RGWSelectObj_ObjStore_S3::get_params()` reads the request body, detects Trino user-agent, and calls `handle_aws_cli_parameters()`. That parser extracts SQL expression, input/output serialization fields, compression type, progress flag, and scan range using tag-string extraction. `execute()` blocks disabled S3 Select, validates Parquet magic, invokes Parquet processing, or starts a GET/range request for CSV/JSON. `send_response_data()` dispatches to `csv_processing()`, `json_processing()`, or `parquet_processing()`.

`run_s3select_on_csv()`, `run_s3select_on_json()`, and `run_s3select_on_parquet()` configure the external s3select engine, execute it, send records/progress/errors, and update returned byte counters. `range_request()` reuses `RGWGetObj` range execution for Parquet and scan ranges. `shape_chunk_per_trino_requests()` trims scan-range chunks to row delimiters for Trino.

## Control Flow
The operation first reads XML parameters, then defers normal object reads to `RGWGetObj_ObjStore_S3`. Each returned data chunk arrives in `send_response_data()`. CSV/JSON chunks are fed to the select engine; emitted rows are wrapped in AWS event-stream Records frames. When processed bytes reach the target size or SQL LIMIT is reached, Stats and End frames are sent. Parquet reverses control: the Arrow-backed reader calls RGW range callbacks through `m_rgw_api`, and `parquet_processing()` accumulates buffers for those reads.

## State and Persistence Behavior
There is no object metadata persistence. Per-request state includes parsed XML fields, serialization delimiters, scan range, object size for processing, response buffers, byte counters stored into `s->s3select_usage`, chunk count, Parquet/JSON mode flags, and range-request scratch buffers. Responses are streamed over HTTP using chunked transfer encoding.

## Dependencies and Integration Points
The file depends on `RGWGetObj_ObjStore_S3`, request state/formatters, RGW range parsing, Ceph logging, Boost CRC, Boost string replacement, the external `s3select` engine, optional Arrow/Parquet support, and S3 REST error formatting. It integrates directly with GET object read callbacks and usage accounting.

## Risks
XML parsing is ad hoc string extraction and may mis-handle namespaces, missing sections, or repeated tags. Compression other than `NONE` is rejected. Regex/SQL/parser errors are mapped inconsistently between AWS event-stream errors and normal RGW XML errors. Some CSV paths update processed bytes with buffer length instead of shaped `len`, which can affect stats and termination. `parquet_processing()` appends `len` bytes from each buffer segment using the same offset/length, which is sensitive to multi-segment bufferlists. SQL LIMIT uses `-ENOENT` to stop fetching, which callers must treat as nonfatal.

## Test Signals
Tests should cover CSV, JSON DOCUMENT, unsupported JSON type, Parquet magic validation with and without Arrow, disabled config, empty objects, malformed XML, unsupported compression, progress frames, stats/end frames, event-stream CRC compatibility, scan ranges, Trino row-boundary shaping, SQL LIMIT early termination, range callbacks, usage counters, and chunked response setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_s3select.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_s3select.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_s3select.h

## Purpose
`rgw_s3select.h` is the minimal public factory header for RGW S3 Select. It hides the concrete implementation class in `rgw_s3select_private.h` and exposes a single operation factory.

## Important APIs, Types, and Functions
The only declaration is `rgw::s3select::create_s3select_op()`, returning an `RGWOp*`. The implementation allocates `RGWSelectObj_ObjStore_S3`, which derives from the S3 GET object operation.

## Control Flow
REST routing code can include this header and call the factory when dispatching SelectObjectContent, without depending on the private class definition or the external s3select engine headers.

## State and Persistence Behavior
The header declares no state and no persistence. Ownership of the returned raw pointer follows existing RGW operation allocation conventions.

## Dependencies and Integration Points
The declaration depends on `RGWOp` being visible before inclusion. It integrates with S3 REST operation registration and keeps heavy select dependencies out of broader compile units.

## Risks
Because the function returns a raw pointer and the header does not include the `RGWOp` definition, callers must include it in the correct context and manage operation lifetime according to RGW conventions.

## Test Signals
Build tests should verify the factory is visible to REST dispatch code. Runtime tests should confirm the returned op executes SelectObjectContent rather than normal GET behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_s3select.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_s3select_private.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_s3select_private.h

## Purpose
`rgw_s3select_private.h` declares the concrete S3 Select implementation and AWS event-stream response helper. It centralizes heavy dependencies on RGW S3 REST internals, the external s3select engine, liboath/auth headers, and optional Arrow/Parquet types so they stay out of the small public factory header.

## Important APIs, Types, and Functions
`aws_response_handler` owns event-stream payload buffers, CRC state, request/op pointers, usage counters, header constants, and chunked-transfer callback wiring. It declares methods to initialize records/progress/stats/end/error frames, create headers, send success/progress/stats/error responses, update bytes processed/returned, and choose main versus continuation buffers.

`RGWSelectObj_ObjStore_S3` derives from `RGWGetObj_ObjStore_S3`. It stores the parsed Select request XML, CSV/JSON/Parquet engine objects, delimiter/quote/escape/header options, scan range fields, progress flag, Trino flags, response handler, range-request scratch buffers, and callback functions for result formatting, continuation, debug logging, chunked encoding, range reads, and object size. It overrides `send_response_data()`, `get_params()`, and `execute()`.

## Control Flow
The concrete op behaves like a GET with a transform callback. `get_params()` parses the select request and then calls the base GET parameter setup. `execute()` initializes response handling and starts normal GET/range processing or Parquet reader-driven range processing. `send_response_data()` receives object bytes and dispatches to CSV, JSON, or Parquet processors.

## State and Persistence Behavior
All state is per-request and transient. The class tracks scan offsets, object size, whether a chunk should be skipped for Trino range alignment, continuation response buffers, and byte counters. It does not modify object attributes or bucket metadata.

## Dependencies and Integration Points
The header includes `rgw_rest_s3.h`, `rgw_s3select.h`, `s3select/include/s3select.h`, Boost CRC/tokenizer/string helpers, Ceph crypto/JSON/UTF-8 helpers, and optional Arrow-related Parquet declarations guarded by `_ARROW_EXIST`. It is only suitable for implementation files that can absorb those dependencies.

## Risks
The private class has many mutable request fields and callback functions, making reentrancy and partial-error behavior delicate. Header-level inclusion of several broad dependencies can increase compile sensitivity. The event-stream helper assumes the request state formatter and RGW op pointers are set before sending; `is_set()` guards that at runtime but does not enforce it statically.

## Test Signals
Tests should instantiate the concrete op through the public factory, validate callback initialization, exercise response-handler frame construction with CRCs, and cover mode flags for CSV, JSON, Parquet, scan ranges, progress, and Trino shaping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_s3select_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_sal.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_sal.cc

## Purpose
`rgw_sal.cc` implements SAL driver-manager construction and a few shared SAL helpers. It selects and initializes the configured storage backend, applies optional filter drivers, creates raw/admin providers, closes drivers, chooses config-store implementations, normalizes object byte ranges, and stringifies restore enums.

## Important APIs, Types, and Functions
`make_neorados()` builds a neorados handle for the D3N cache path. `DriverManager::init_storage_provider()` creates full daemon drivers for `rados`, `d3n`, `dbstore`, `posix`, `motr`, or `daos` depending on compile flags and config. The RADOS/D3N paths configure `RGWRados` background threads such as GC, lifecycle, restore, quota, sync, reshard, notification, and bucket logging, then run `init_begin()`, `driver->initialize()`, and `init_complete()`. `init_raw_storage_provider()` creates stripped-down providers for admin/raw use. `close_storage()` finalizes and deletes a driver. `get_config()` maps config options to store/filter names and conditionally enables D3N. `create_config_store()` returns RADOS, dbstore, posix/dbstore, or JSON config-store implementations.

Shared SAL helpers include `Object::range_to_ofs()`, which interprets negative offsets and clamps end offsets against object size, and `rgw_restore_status_dump()` / `rgw_restore_type_dump()`, which map restore enums to stable strings.

## Control Flow
Startup asks `DriverManager::get_config()` for configured store/filter, creates a config store, then calls `get_storage()` or `get_raw_storage()`. Full RADOS startup performs backend construction, option chaining on `RGWRados`, service initialization, SAL driver initialization, and final RADOS completion. After backend creation, optional filters wrap the driver and initialize themselves. Shutdown calls `close_storage()`.

## State and Persistence Behavior
The file itself persists no user data, but it determines which backend owns all subsequent persistence. It passes `SiteConfig`, config store, thread booleans, and cache/GC flags into the selected backend. `get_config()` may switch from `rados` to `d3n` only when D3N config constraints are satisfied.

## Dependencies and Integration Points
The file depends on compile-time backend factories, RADOS/D3N internals, dbstore/posix/motr/daos drivers, JSON/RADOS config stores, Ceph global config, Boost.Asio, and SAL interfaces from `rgw_sal.h`. It is the central integration point between daemon startup and backend-specific code.

## Risks
Many branches are compile-flag-dependent; unsupported config values can silently leave `driver == nullptr`. Filter wrapping assumes a valid underlying driver. Error cleanup deletes drivers but must also avoid leaking backend-owned RADOS objects on partially initialized paths. D3N enablement depends on chunk size equaling stripe size and async Beast being enabled. The log message says "neroados" typo but behavior is unaffected.

## Test Signals
Tests should cover driver selection for each compiled backend, unsupported backend behavior, D3N enable/disable conditions, full RADOS init failure cleanup at each stage, filter initialization failure cleanup, raw provider creation, config-store type selection and exception handling, `range_to_ofs()` boundary cases, and restore enum string outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_sal.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_sal.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_sal.h

## Purpose
`rgw_sal.h` defines the RGW Store Abstraction Layer. It is the main contract separating protocol/front-end RGW code from storage backends and filters. It declares abstractions for drivers, users, buckets, objects, multipart upload, lifecycle, restore, notifications, writers, zones, placement tiers, Lua, and driver management.

## Important APIs, Types, and Functions
Core streaming abstractions are `DataProcessor`, `ObjectProcessor`, `DataProcessorFactory`, and `Writer`. `Driver` is the singleton backend/filter interface and includes account/user/group/role lookup and persistence, bucket/object creation and listing, zone and sync access, lifecycle/restore managers, notifications, pubsub topics, usage logs, quotas, rate limits, metadata listing, Lua managers, OIDC providers, IAM roles, and atomic/append writer factories.

`User` abstracts identity metadata, attrs, usage, MFA, persistence, and group listings. `Bucket` abstracts listing, attrs, ACLs, creation/removal, stats, quota, owner changes, index repair, multipart upload access, bucket notifications, and bucket logging. `Object` abstracts read/delete operations, copy, ACLs, cached state/attrs, atomic/prefetch/compression flags, transitions to and from cloud tiers, multipart part listing, OMAP helpers, versioning helpers, torrent info, chown, tracing, and object identity.

`MultipartUpload` and `MultipartPart` cover multipart state, part listing, abort, complete, writer creation, object-lock metadata, checksum type/flags, and orphan cleanup. `Serializer`, `MPSerializer`, `LCSerializer`, and `RestoreSerializer` define backend locks. `Lifecycle` and SAL `Restore` define persistent lifecycle/restore queues. `Notification` publishes reserve/commit events. `PlacementTier`, `ZoneGroup`, and `Zone` expose placement and multisite topology. `LuaManager` abstracts script/package storage. `DriverManager` declares factory helpers implemented in `rgw_sal.cc`.

## Control Flow
Protocol handlers interact with SAL objects rather than backend internals. A request resolves a `Driver`, loads a `User`/`Bucket`/`Object`, prepares read/write/delete/copy operations, streams data through processors or callbacks, and commits via virtual backend methods. Background services obtain `Lifecycle` or `Restore` handles from the driver and manipulate queue entries through serializers. Admin APIs use `DriverManager` and config stores to choose the correct backend.

## State and Persistence Behavior
This header defines persistence contracts but usually not storage details. Most methods operate on cached metadata plus explicit read/store calls. Optimistic concurrency is represented by `RGWObjVersionTracker` and writer/serializer handles. Object write visibility is defined by `ObjectProcessor::complete()`. Flags such as `FLAG_LOG_OP`, `FLAG_PREVENT_VERSIONING`, `FLAG_FORCE_OP`, and `FLAG_SKIP_UPDATE_OLH` influence backend persistence semantics. Restore status/type enums are encoded as small integer values.

## Dependencies and Integration Points
The header includes RGW common types, checksums, Lua, notifications, request context, tracing, RADOS-specific temporary headers, and many forward declarations. It is included by most RGW subsystems and every SAL backend. The RADOS-specific includes are marked as temporary subclass dependencies.

## Risks
The interface is very broad, so backend implementations can drift semantically. Several methods are marked temporary or "may be removed", indicating unstable boundaries. Many APIs use raw pointers, mutable references, and caller-owned output parameters, so lifetime and partial-mutation behavior require discipline. Adding virtual methods affects every backend/filter. Some methods expose backend-specific concepts such as bucket index repair and RADOS-style OMAP through generic SAL.

## Test Signals
Conformance tests should exercise each backend through common user/bucket/object CRUD, object range reads, copy/write/delete with versioning and conditions, multipart lifecycle, restore and lifecycle queues, notifications, topic mappings, quota/stats, role/OIDC/group/account APIs, cloud transition/restore, Lua manager, and driver filters. Compile tests should build all enabled backends after any interface change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_sal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_sal_config.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_sal_config.h

## Purpose
`rgw_sal_config.h` declares the SAL configuration-store interface for realm, period, zonegroup, zone, and period-config metadata. It abstracts how multisite topology configuration is persisted so RADOS, dbstore, JSON, or other implementations can share higher-level zone/realm logic.

## Important APIs, Types, and Functions
`ListResult<T>` returns a subspan of caller-provided entries plus a next marker. `ConfigStore` groups virtual operations by metadata domain. Realm methods manage default realm id, create/read realm by id/name/default, read a realm id by name, notify new periods, create realm watchers, and list realm names. Period methods create/read/delete/list periods and update latest epoch. Zonegroup methods manage default zonegroup ids, create/read zonegroups, and list names. Zone methods manage default zone ids, create/read zones by id/name/default, and list names. Period-config methods read and write `RGWPeriodConfig`.

`RealmWriter`, `ZoneGroupWriter`, and `ZoneWriter` are optimistic update handles returned by read/create calls. They can write, rename, or remove the object and are documented to fail with `-ECANCELED` if another writer updates the same object after the read.

## Control Flow
Higher-level realm/period/zone management code calls a `ConfigStore` chosen by `DriverManager::create_config_store()`. Reads optionally return a writer handle tied to the object version. Subsequent updates go through that writer to enforce atomicity. Listing APIs use caller-provided spans and markers for pagination.

## State and Persistence Behavior
The interface owns durable multisite configuration metadata: defaults, named records, period epochs, latest epoch pointers, and period configuration. Exclusive flags control create/write conflict behavior. Writer handles represent read-modify-write state and are the main concurrency boundary.

## Dependencies and Integration Points
The header forward-declares RGW realm/period/zone types and depends on `optional_yield`, `DoutPrefixProvider`, spans, string views, and `rgw_sal_fwd.h`. Implementations are selected in `rgw_sal.cc` from RADOS, dbstore/posix, or JSON config stores.

## Risks
Because the interface uses spans supplied by callers, implementations must not outlive the input buffer and must set `ListResult::entries` correctly. Rename operations must enforce id immutability while updating name indexes. Default id operations are scoped by realm where appropriate; mistakes can break multisite bootstrap or period updates. Watcher support may return null, so callers need fallback behavior.

## Test Signals
Tests should cover create/read/list/delete for realm, period, zonegroup, and zone; default id read/write/delete; exclusive create conflicts; writer stale-update returning `-ECANCELED`; rename preserving ids; latest period epoch updates; pagination markers; null watcher behavior; and JSON/RADOS/dbstore implementation parity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_sal_config.h -->
