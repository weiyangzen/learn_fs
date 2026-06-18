# subset-b-006971 Research

Grouped research for the listed Ceph RGW RADOS files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_lc_tier.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_lc_tier.cc

## Purpose
Implements RGW lifecycle cloud-tier object transition and restore for the RADOS-backed gateway. It copies local RGW objects to an S3-compatible remote endpoint, handles target bucket creation, selects plain versus multipart transfer, records resumable multipart upload state, checks whether a remote copy already represents the current source version, and restores Glacier-style remote objects back through GET after issuing a restore request.

## Important APIs, Types, And Functions
The public entry points are `rgw_cloud_tier_transfer_object()`, `rgw_cloud_tier_get_object()`, `rgw_cloud_tier_restore_object()`, `cloud_tier_restore()`, and `is_restore_in_progress()`. Internal serialized state is `rgw_lc_multipart_upload_info`, which persists `upload_id`, source size, source mtime, and source etag. `rgw_lc_obj_properties` carries source mtime, etag, versioned epoch, ACL mappings, and target storage class into outbound headers.

`RGWLCStreamRead` wraps a SAL object read operation, validates the source mtime to avoid racing with object mutation, builds an `rgw_rest_obj` from local attributes/ACL, and streams either the whole object or a multipart byte range. `RGWLCCloudStreamPut` wraps `RGWRESTStreamS3PutObj`, maps source attributes and ACL grants into S3 headers, tracks returned ETag, and completes the remote request. Helper functions build target names, map RGW attrs to HTTP headers, issue multipart init/part/complete/abort calls, and issue remote RESTORE requests.

## Control Flow
`rgw_cloud_tier_transfer_object()` first checks a caller-provided cache of known target buckets. On miss it sends `HEAD` to the target bucket and creates it with optional location constraint if absent. It then sends a best-effort `HEAD` for the target object and treats a matching `x-amz-meta-rgwx-source-mtime` as already tiered. If the object is not already tiered, the source size is compared with `multipart_sync_threshold`, clamped to at least the S3 minimum multipart part size, to choose plain or multipart transfer.

Plain transfer constructs `RGWLCStreamRead` and `RGWLCCloudStreamPut`, initializes the source read, initializes/sends the destination PUT, streams object bytes from `read_op->iterate()` into the destination callback, and completes the request. Multipart transfer first checks a status object named `lc_multipart_<source_oid>` in the zone log pool. If the status exists but source mtime/size/etag changed, it aborts the remote upload and deletes the status. Otherwise it starts or resumes an upload, computes a part size that respects `MULTIPART_MAX_PARTS` and configured minimums, streams every part, collects returned ETags, completes the multipart upload, and best-effort deletes the status object.

Restore flow sends a remote `POST ?restore` XML request unless the caller already marks restore as in progress, polls `HEAD` up to two times looking for `ongoing-request="true"` in `x-amz-restore`, and only performs the actual GET when the remote reports completion.

## State And Persistence
Remote state is the target bucket/object plus S3 metadata headers: `x-amz-meta-rgwx-source`, `x-rgw-cloud`, `x-rgw-cloud-keep-attrs`, source mtime, source etag, source key/version, versioned epoch, storage class, and mapped ACL grants. Local resumability state for multipart transition is a system object in the zone log pool. The code does not persist per-part completion state, so a crash after uploaded parts but before completion will resume from the upload id but resend all parts. `cloud_targets` is only an in-memory bucket-existence cache passed by the lifecycle caller.

## Dependencies And Integration Points
The file integrates with RGW SAL object reads, `RGWRESTConn` and S3 streaming request classes, RGW attr names from `rgw_common.h`, XML formatting/decoding, zone parameters for the log pool, lifecycle bucket directory entries, and tier configuration types from `rgw_zone.h`. It assumes a RADOS-backed driver when reading/writing multipart status objects through `RGWSI_SysObj`; non-RADOS drivers are rejected for cloud transition state.

## Risks And Edge Cases
Race handling depends on matching source `mtime` during `ReadOp::prepare()`, but multipart only stores source mtime/size/etag at upload start and does not record individual parts. XML error parsing treats `RestoreAlreadyInProgress`, `BucketAlreadyOwnedByYou`, and `BucketAlreadyExists` as acceptable special cases but otherwise returns `-EIO`, so endpoint-specific XML differences are compatibility risks. Header name normalization is mixed between uppercase and lowercase forms; restore/already-tiered checks compensate for common variants but may miss unusual endpoint casing. Plain transfer uses shared pointers due to a noted stack-lifetime/performance issue, which is a signal that callback ownership is subtle. Best-effort abort/status deletion can leave remote uploads or status objects behind on failure.

## Test Signals
Useful tests include lifecycle transition of small objects, multipart threshold boundary cases, object mutation during transfer returning `-ECANCELED`, interrupted multipart uploads with status-object reuse, remote bucket already exists/absent paths, restore in-progress and restore-complete HEAD responses, ACL mapping output, ETag unquoting on get/restore, and endpoints returning transient `-EIO` during remote GET.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_lc_tier.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_lc_tier.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_lc_tier.h

## Purpose
Declares the lifecycle cloud-tier interface used by RGW lifecycle code to transfer objects to remote cloud storage and retrieve or restore them later. It also defines the context object that bundles local source object state, target endpoint configuration, tier policy, ACL mapping, multipart thresholds, and coroutine yield context.

## Important APIs And Types
`RGWLCCloudTierCtx` is the central API carrier. It includes source fields (`rgw_bucket_dir_entry& o`, `rgw::sal::Driver*`, `RGWBucketInfo&`, source `rgw::sal::Object*`, storage/restore classes, tier type), remote fields (`RGWRESTConn&`, location constraint, target bucket, target storage class), ACL mappings, multipart min/threshold sizes, flags for multipart, target bucket creation, per-bucket target naming, and `optional_yield`.

The header exports `rgw_cloud_tier_transfer_object()`, `rgw_cloud_tier_get_object()`, `rgw_cloud_tier_restore_object()`, `cloud_tier_restore()`, and `is_restore_in_progress()`. It also defines default and lower-bound multipart sizes: `DEFAULT_MULTIPART_SYNC_PART_SIZE` and `MULTIPART_MIN_POSSIBLE_PART_SIZE`.

## Control Flow And Integration
Callers populate `RGWLCCloudTierCtx` from lifecycle policy/tier configuration and call transfer or restore/get functions. The implementation uses `target_by_bucket` to choose between legacy `bucket/object` remote keys and per-bucket object-only keys, and mutates flags such as `is_multipart_upload` and `target_bucket_created` as transfer progresses.

## State And Persistence
The header itself persists no data but exposes fields that drive persisted state: remote object metadata, local multipart status objects, target bucket cache membership, and restore-in-progress handling. References in the context must remain valid for the duration of synchronous/coroutine work because most members are raw pointers or references.

## Dependencies And Risks
The interface is tightly coupled to RADOS RGW internals (`rgw_lc`, `rgw_rados`, `rgw_sal_rados`), REST connection code, zone tier configuration, and coroutine yield support. The raw pointer/reference style makes lifetime ownership external; misuse can lead to stale bucket/object/tier references. Tests should compile both callers and implementation under RADOS-enabled builds and exercise context values for legacy versus per-bucket target naming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_lc_tier.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_log_backing.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_log_backing.cc

## Purpose
Implements asynchronous support for RGW logs that can be backed by either legacy omap objects or newer neorados FIFO objects. It detects backing type across shards, removes complete log shard sets including FIFO parts, and maintains a generation metadata object so log consumers/producers can migrate backing type without losing cursors or violating tail/head ordering.

## Important APIs, Types, And Functions
`log_backing_type()` probes each shard with `fifo::FIFO::open()` and returns `log_type::fifo` or `log_type::omap`, creating shard zero if all shards are absent and the default is FIFO. `log_remove()` removes shards and FIFO parts, optionally preserving generation-zero shard zero as an empty lock rendezvous object.

`logback_generations` implements generation lifecycle. `setup()` reads or creates the metadata object, establishes a watch, and calls `handle_init()` with non-pruned generations. `update()` rereads metadata, validates monotonic tail/head changes, and invokes `handle_empty_to()` and `handle_new_gens()`. `new_backing()` appends a generation for a different `log_type`; `empty_to()` marks older generations pruned; `remove_empty()` deletes backing objects whose prune timestamp is at least one hour old and rewrites metadata. `handle_notify()` updates on remote notifications and reestablishes watches after watch errors.

## Control Flow
Shard probing first tries FIFO unless FIFO support has already been proven unsupported. FIFO `no_message_available` is interpreted as an empty OMAP-style object; `operation_not_permitted` disables FIFO probing and falls back to OMAP. Mixed shard types are considered corruption and raise `EIO`.

Generation setup reads metadata using a version check. If absent, it determines generation-zero backing type, creates the metadata object with a random version tag and version 1, and handles races by rereading if another writer created the object first. Writes are serialized through an Asio strand and use cls version checks plus version increments. Canceled writes trigger update-and-retry loops up to ten attempts. Successful generation changes notify watchers with a 10-second timeout.

## State And Persistence
Persistent state is a metadata object containing an encoded `flat_map<uint64_t, logback_generation>` and a cls version. Each generation records id, backing type, and optional prune time. Data state is stored in per-generation, per-shard objects generated by the caller-supplied `get_oid(gen, shard)` callback, plus FIFO part objects when FIFO is used. Runtime state includes local `entries`, `version`, `watchcookie`, `my_id`, and a strand protecting mutation.

## Dependencies And Integration Points
Uses neorados `RADOS`, `ReadOp`, `WriteOp`, object watches/notifies, cls version helpers, neorados cls FIFO/log helpers, Ceph async blocked/completion utilities, and derived-class callbacks. Higher-level RGW logs use this class to react when generations are added or pruned while maintaining cursor compatibility through the header helpers in `rgw_log_backing.h`.

## Risks And Edge Cases
The code deliberately terminates the process if watch reestablishment or notify-triggered update fails because continuing could miss generation changes. Corrupt or mixed shard types fail hard. `remove_empty()` deletes backing objects before successfully removing their generation entries from metadata; repeated cancellation can leave already-deleted objects referenced until a later retry. The one-hour prune grace is a correctness knob for late consumers. The `lowest_nomempty` helper name typo is harmless but search-unfriendly. Tests need real or mocked neorados/FIFO behavior because most bugs would be in async error handling and version races.

## Test Signals
Strong signals include backing detection for absent/omap/fifo/mixed shards, FIFO unsupported fallback, concurrent metadata creation, concurrent `new_backing()` and `empty_to()` version cancellation retries, notify from another instance updating callbacks, `remove_empty()` preserving generation-zero shard zero when requested, and cursor compatibility across generated and legacy markers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_log_backing.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_log_backing.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_log_backing.h

## Purpose
Declares the abstraction layer that lets RGW log users operate over omap-backed or FIFO-backed logs and transition between multiple log generations. It also provides cursor encoding helpers and a lazily initialized FIFO wrapper for producers/consumers.

## Important APIs And Types
`log_type` is a serializable enum with `omap` and `fifo`, plus `to_log_type()` and stream formatting. `logback_generation` encodes `gen_id`, `type`, and optional `pruned` timestamp. `logback_generations` is an abstract base class that owns neorados handles, metadata object id, generation-to-shard oid callback, shard count, watch cookie, version, strand, and current entries. Derived classes implement `handle_init()`, `handle_new_gens()`, and `handle_empty_to()`.

Public coroutine methods are `init<T>()`, `update()`, `new_backing()`, `empty_to()`, `remove_empty()`, and `shutdown()`. Free functions `log_backing_type()` and `log_remove()` operate over all shards. `gencursor()` and `cursorgen()` encode/decode cursors as `G<20-digit-gen>@<cursor>`. `LazyFIFO` wraps `neorados::cls::fifo::FIFO` with synchronous-yield and coroutine methods for `push`, `list`, `trim`, and `last_entry_info`.

## Control Flow And State
`logback_generations::init()` constructs a derived instance and calls `setup()`, after which callbacks receive the active generation set. The class hides metadata reads/writes and watch handling behind protected/private methods. `LazyFIFO` protects the optional FIFO pointer with a mutex and allows races to create the FIFO because FIFO creation is designed to be multi-client safe; the first completed initializer wins.

## Dependencies And Integration
The header depends on Boost.Asio coroutines/strands, `boost::container::flat_map`, function2 unique functions, neorados RADOS/FIFO APIs, cls version types, Ceph encoding, and config parsing helpers. It is intended for RGW log subsystems such as metadata/data/bilog implementations that need to select backing stores and consume generation updates.

## Risks And Test Signals
The main API risk is derived classes failing to call `shutdown()` before destruction or overriding `shutdown()` without calling the base at the end. Cursor parsing intentionally falls back to generation zero when malformed, which preserves backward compatibility but can hide invalid cursor input. `LazyFIFO` initialization can duplicate creation work under concurrency, though only one pointer is retained. Unit tests should cover encoding compatibility, cursor edge cases, derived callback sequencing, and FIFO lazy initialization under parallel push/list calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_log_backing.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_mdlog.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_mdlog.h

## Purpose
Declares the metadata log service used by RGW multisite metadata replication and admin inspection. It stores metadata mutation entries into sharded cls timelog objects, lists and trims those logs, exposes shard information and locks, and tracks locally modified shards.

## Important APIs And Types
`META_LOG_OBJ_PREFIX` is the base object prefix. `RGWMetadataLogInfo` reports a shard marker and last update time. `RGWMetadataLogInfoCompletion` wraps asynchronous info retrieval with reference-counted lifetime and cancellation-protected callbacks. `RGWMetadataLog` exposes `add_entry()`, `store_entries_in_shard()`, `list_entries()`, `trim()`, synchronous/asynchronous `get_info()`, shard locking/unlocking, `update_shards()`, and modified-shard tracking through `read_clear_modified()`.

`LogListCtx` carries current shard, marker, time range, oid, and completion flag for iterative listing. `RGWMetadataLogData` encodes versioned mdlog status used in synchronization. `RGWMetadataLogHistory` records the oldest realm epoch and period id retained in metadata log history at object id `meta.history`.

## Control Flow And State
The constructor derives an object prefix from the period id, using `meta.log.` for current/default period and `meta.log.<period>.` for period-specific logs. `add_entry()` hashes a key to a shard, marks that shard modified, and adds a timelog entry. Listing initializes a handle for one shard and time interval, then repeated `list_entries()` calls advance the marker.

Persistent state lives in sharded timelog objects in the zone log pool plus the encoded mdlog data/history objects. Runtime state includes service pointers for zone and cls, the prefix, an RW lock, and a set of modified shard ids. The modified set is not durable; it is a local signal for update propagation.

## Dependencies And Integration Points
Depends on `RGWSI_Zone`, `RGWSI_Cls`, cls log types, cls version types, `RGWMDLogStatus`, and metadata manager interfaces. It integrates with metadata handlers that call mdlog completion after put/remove/mutate, and with multisite sync logic that lists, locks, and trims shards.

## Risks And Test Signals
Correctness depends on stable shard hashing and consistent `rgw_md_log_max_shards`. Async completion cancellation protects the callback but still requires caller reference discipline. Locking is per-shard and uses zone id/owner id strings supplied by the caller. Tests should validate shard oid generation by period, add/list/trim behavior, async info cancellation, lock/unlock failure propagation, and encoding compatibility for `RGWMetadataLogData` and `RGWMetadataLogHistory`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_mdlog.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_metadata.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_metadata.cc

## Purpose
Implements shard-name helpers and the concrete `RGWMetadataLog` operations declared in `rgw_mdlog.h`. It is the bridge between metadata mutation callers and cls timelog objects in the zone log pool.

## Important APIs And Functions
The three `rgw_shard_name()` overloads compute prefixed shard object names from a key, a section/key pair, or an explicit shard id. `RGWMetadataLog::add_entry()` writes a single timelog entry when metadata logging is enabled. `store_entries_in_shard()` writes a batch asynchronously. `init_list_entries()`, `list_entries()`, and `complete_list_entries()` implement iterative list handles. `get_info()` and `get_info_async()` return timelog header marker/time information. `trim()`, `lock_exclusive()`, `unlock()`, `mark_modified()`, and `read_clear_modified()` implement maintenance and local modification tracking.

## Control Flow
Hash-based shard selection uses `ceph_str_hash_linux()` modulo `rgw_md_log_max_shards`. Section/key sharding xors the section and key hashes. `add_entry()` returns immediately when `need_to_log_metadata()` is false; otherwise it builds the shard oid, marks the shard modified under the local RW lock, timestamps the entry with `real_clock::now()`, and calls `svc.cls->timelog.add()`. Listing reads from one oid/time range, treats `-ENOENT` as an empty shard, and advances the marker returned by cls.

## State And Persistence
Persistent metadata log entries are cls timelog records under objects named with `meta.log.*` prefixes. `RGWMetadataLogInfo` serializes to JSON marker and last update time for admin/reporting paths. `modified_shards` is process-local, protected by `RWLock`, and consumed by `read_clear_modified()` to report and clear modified shard ids.

## Dependencies And Integration Points
The implementation depends on zone service configuration, cls timelog and lock service wrappers, librados async completions, `RGWMetadataLogInfoCompletion`, Ceph JSON helpers, and the zone log pool. It is used by metadata service and sync code that needs to replicate or trim metadata changes.

## Risks And Test Signals
The double-lock pattern in `mark_modified()` optimizes repeated inserts but requires the write lock to be the authoritative insertion path. `list_entries()` ignores `-ENOENT` and returns success, so callers must inspect `truncated` rather than expecting an error for empty shards. Async info holds a ref until completion; cancellation clears the callback but still releases the librados completion in the destructor. Test signals include deterministic shard ids, empty shard listing, modified set clear/swap behavior, and async completion callback/cancel races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_metadata.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_metadata.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_metadata.h

## Purpose
Defines RGW's metadata abstraction layer. Metadata handlers expose typed get/put/remove/mutate/list behavior for sections such as users, buckets, and OTP, while `RGWMetadataManager` dispatches string metadata keys to the right handler and provides common JSON/log/list operations.

## Important APIs And Types
`RGWMetadataObject` stores an object version, mtime, optional attr map pointer, and a virtual formatter hook. `RGWMetadataHandler` is the plugin interface: type name, JSON object construction, `get`, `put`, `remove`, transactional `mutate`, listing lifecycle, marker retrieval, shard selection, and manager attachment. `RGWMetadataManager` owns registered handlers plus a top handler and provides high-level `get()`, `put()`, `remove()`, `mutate()`, `list_keys_*()`, `dump_log_entry()`, `get_sections()`, `parse_metadata_key()`, and `get_shard_id()`.

The free `rgw_shard_name()` functions are declared here for shared shard naming. `RGWMDLogSyncType` and `RGWMDLogStatus` appear in handler methods to connect metadata writes with mdlog replication status.

## Control Flow And State
Callers pass keys shaped as metadata section plus entry. The manager parses the key, finds a handler, and delegates the operation. Handlers are responsible for persisting their own typed data, maintaining object version trackers, and completing mdlog entries when appropriate. Listing uses opaque handler-owned handles so each metadata section can list from its backing store.

## Dependencies And Integration Points
The header pulls in common RGW types, period history, mdlog types, cls version/log types, and SAL forward declarations. Concrete handlers in other files, including OTP in this subset, implement this interface and attach to the manager. Admin metadata APIs and multisite sync logic rely on the common manager dispatch semantics.

## Risks And Test Signals
The manager stores raw handler pointers, so ownership/lifetime is external except for its top handler. `RGWMetadataObject::pattrs` is a borrowed pointer. Handler `mutate()` callbacks must preserve version and mdlog semantics. Tests should exercise key parsing, unknown section errors, handler registration, list marker propagation, version conflict handling, and handler-specific mdlog completion behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_metadata.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_metadata_lister.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_metadata_lister.h

## Purpose
Provides a small reusable lister wrapper for metadata stored as system objects in an `RGWSI_SysObj::Pool`. It converts object listing results into metadata keys and gives handlers a common implementation for list operations.

## Important APIs And Types
`RGWMetadataLister` owns a `RGWSI_SysObj::Pool` and a `Pool::Op` listing operation. `init()` starts listing from a marker and prefix. `get_next()` fetches up to `max` object ids, handles missing pools/objects as an empty result, calls virtual `filter_transform()` to turn oids into keys, and returns truncation status. `get_marker()` is available in RADOS builds and delegates to the underlying listing operation.

## Control Flow And State
By default `filter_transform()` moves every oid into the output key list unchanged. Derived listers can override it to strip prefixes, filter internal objects, or transform object ids into metadata entry names. The only persistent state is the backing system object namespace; the lister itself keeps iteration state in `listing`.

## Dependencies And Integration Points
The class depends on `services/svc_sys_obj.h` and is used by metadata handlers such as the OTP handler to implement `list_keys_init/next/complete`. It abstracts enough of the pool listing API for metadata manager consumers to use opaque handles.

## Risks And Test Signals
Because `get_next()` clears `keys` before each listing call, callers must accumulate across calls if needed. Treating `-ENOENT` as success with `truncated=false` is useful for absent pools but can hide misconfiguration. Tests should verify marker progression, prefix filtering in subclasses, empty pool handling, and build behavior when `WITH_RADOSGW_RADOS` gates marker access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_metadata_lister.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_notify.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_notify.cc

## Purpose
Implements RGW bucket notification reservation, commit/abort, persistent queue management, and background delivery. It supports immediate push endpoints and persistent 2-phase-commit queues, including sharded topic queues, retry/TTL handling, stale reservation cleanup, and migration of entries created before creation-time metadata was present.

## Important APIs, Types, And Functions
Public functions in `rgw::notify` include `init()`, `shutdown()`, `add_persistent_topic()`, `remove_persistent_topic()`, `publish_reserve()`, `publish_commit()`, `publish_abort()`, and `get_persistent_queue_stats()`. `reservation_t` is the caller-facing reservation object; it records applicable topics and aborts uncommitted reservations in its destructor. `rgw_topic_stats` reports reservations, bytes, and entries.

The internal `Manager` owns an Asio `io_context`, worker thread, queue ownership locks, queue retry trackers, and a `SiteConfig`/RadosStore reference. It reads the global queue list object `queues_list_object`, takes exclusive cls locks on queue objects, processes queue entries through `RGWPubSubEndpoint`, removes successful/expired entries, and periodically expires stale 2PC reservations.

## Control Flow
`publish_reserve()` loads bucket notification configuration from v2 notification metadata when all zonegroups support it and v1 topics are absent, otherwise through `RGWPubSub`. For each event type it checks event name, key filter, metadata filter, and tag filter. Persistent topics reserve space on a selected queue shard computed from bucket/object hash; non-persistent topics only record intent in `reservation_t`.

`publish_commit()` builds an S3 event, populates identity, bucket/object fields, tags, metadata, sequence id, and opaque data. Persistent commits encode an `event_entry_t`, enlarge the queue reservation if the encoded size exceeds the initial 4 KiB reservation, then commit asynchronously to the queue shard. Non-persistent commits instantiate the endpoint and send immediately. `publish_abort()` aborts any uncommitted persistent reservation and clears its id.

The background manager refreshes the queue list every 30 seconds, locks queues with a 90-second failover duration, and spawns one processing coroutine per owned queue. Queue processing lists up to 1024 entries under the queue lock, fetches current topic info or falls back to cached entry fields, builds an endpoint, and spawns per-entry processing. Successful, expired, or migration-needed entries are removed up to an adjusted marker. Migration entries are re-reserved/recommitted after stamping current creation time and topic retry settings.

## State And Persistence
Persistent state is stored in the notification pool. `queues_list_object` stores queue names as omap keys. Each topic queue is a cls 2PC queue initialized with `MAX_QUEUE_SIZE` and optionally sharded as `<queue>.<shard_id>`. Queue objects carry cls lock state, committed entries, and reservations. Runtime state includes the global `s_manager`, per-entry retry counters and last retry time in `topics_persistency_tracker`, and per-topic perf counters.

## Dependencies And Integration Points
Depends on cls 2PC queue and cls lock clients, `RGWPubSub` topic/notification metadata, `RGWPubSubEndpoint` implementations from `rgw_pubsub_push.cc`, SAL RadosStore/Bucket/Object, zone feature detection, request state metadata/tags, notification event type matching, perf counters, and librados async completions. Lifecycle and other non-request callers use the alternate `reservation_t` constructor.

## Risks And Edge Cases
Persistent commit is asynchronous; failures after `aio_operate()` are only logged by the completion callback and are not returned to the original caller. The reservation destructor is a leak guard, but callers must keep `reservation_t` alive until commit/abort semantics are complete. Entry processing updates shared flags from spawned coroutines, so ordering depends on the single queue coroutine and token wait discipline. Topic fallback to cached endpoint fields preserves delivery if topic metadata is temporarily unavailable but may use stale policy. Queue migration has a TODO around tenant extraction and aborts if topic lookup by queue name fails. Queue ownership loss returns from processing and relies on failover locks for another RGW to take over.

## Test Signals
Tests should cover notification filter matching for events, key prefixes/suffixes, metadata and tags; v1/v2 config selection; persistent reservation and larger-than-reserved commit; destructor abort; queue sharding determinism; queue add/remove list-object consistency; retry TTL/max retry expiration; endpoint `-EBUSY` backoff behavior; stale reservation cleanup under lock; lock failover between two managers; and persistent queue stats across shards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_notify.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_notify.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_notify.h

## Purpose
Declares RGW notification manager APIs and the reservation contract used by object operations to publish S3-compatible bucket notifications. It covers lifecycle of persistent topic queues, per-operation reservation/commit/abort, and queue statistics.

## Important APIs And Types
`init()` and `shutdown()` manage the process-global notification delivery manager. `add_persistent_topic()` and `remove_persistent_topic()` create/delete cls 2PC queues and maintain the shared queue list. `reservation_t` stores matched topics and request/object context. Its nested `topic_t` records notification configuration id, topic config, 2PC reservation id, event type, and shard id. `publish_reserve()`, `publish_commit()`, and `publish_abort()` form the 2-phase API. `rgw_topic_stats` reports queue reservation count, byte size, and entry count.

## Control Flow And State
Callers construct `reservation_t` either from `req_state` or from explicit non-request context, call `publish_reserve()` before the object operation is finalized, and then call `publish_commit()` after successful object mutation or let the destructor/explicit `publish_abort()` clean up. Persistent topics create queue reservations during reserve and commit encoded events later; non-persistent topics defer sending until commit.

## Dependencies And Integration Points
The interface depends on SAL RadosStore/Object/Bucket, `SiteConfig`, request state, `RGWObjTags`, cls 2PC reservation ids, notification event types, and pubsub topic definitions. It is integrated with object PUT/COPY/DELETE/lifecycle paths that need event publication.

## Risks And Test Signals
`reservation_t` stores raw pointers to request, store, object, bucket, and optional object name; these must outlive reserve/commit/abort. The destructor calls `publish_abort()`, so partially moved or long-lived reservations need clear ownership. Tests should verify API ordering, non-request constructor behavior, metadata/tag caching, persistent and non-persistent publication, and idempotent abort after successful commit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_notify.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_obj_manifest.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_obj_manifest.cc

## Purpose
Implements object manifest manipulation, iteration, dumping, test instances, and conversion between logical RGW objects and raw RADOS object locations. Manifests describe how an RGW object is split between a head object and tail stripes or explicit part objects.

## Important APIs And Functions
`RGWObjManifest::append()` combines manifests, using rule merging when both are implicit and falling back to explicit conversion otherwise. `convert_to_explicit()` iterates implicit stripes and records concrete `RGWObjManifestPart` entries. `append_explicit()` appends explicit part maps at the current object size. `get_rule()` finds the active rule for an offset. `obj_find_part()` locates the start of a multipart part. `RGWObjManifest::generator::create_begin()` and `create_next()` build simple manifests as object data is written.

Dump and test-instance functions are implemented for manifest parts, rules, tiers, and manifests. `rgw_obj_select::get_raw_obj()` maps either an already raw object or a logical `rgw_obj` plus placement rule into a `rgw_raw_obj`.

## Control Flow
Append checks whether either manifest is explicit. If both are implicit and the destination has no rules, it copies the source manifest. Otherwise it compares adjacent rule part size, stripe size, and effective prefixes to decide whether rules can be merged or must be appended with adjusted offsets and optional override prefix. Explicit conversion walks object iterators from begin to end, computes raw locations through zone placement, and records part size as the distance to the next stripe offset.

The generator initializes tail placement by inheriting from the head placement when needed, assigns a random prefix when absent, fetches rule zero, sets initial stripe size from head size or stripe max, and updates object size/head size/current stripe on each `create_next()` call.

## State And Persistence
The manifest itself is serialized by methods in the header; this file mutates in-memory fields that later persist as object attributes. Important fields include `explicit_objs`, `objs`, `obj_size`, `obj`, `head_size`, `max_head_size`, `prefix`, `tail_placement`, `rules`, `tail_instance`, tier type, and tier config. Raw object mapping depends on zonegroup and zone params at interpretation time.

## Dependencies And Integration Points
Depends on zone service placement, `RGWRados::get_obj_data_pool()` under RADOS builds, bucket helpers, random prefix generation, and `RGWSI_Tier_RADOS::raw_obj_to_obj()` for explicit conversion. The manifest is consumed by object read/write, multipart, copy, tiering, and data layout code across RGW.

## Risks And Edge Cases
Append mutates source manifest rules by filling zero `part_size`, so callers should not assume the appended source is unchanged. `obj_find_part()` is linear over stripes. Explicit test instance construction stores parts keyed by accumulated total size, which is useful for encoding coverage but does not mirror every production layout. Raw object mapping falls back to default placement if head placement has no data pool; placement drift can affect interpretation of older manifests. Tests should cover old explicit manifests, implicit append with same/different prefix, multipart part seeking, generated random prefixes, and pool selection for normal and extra data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_obj_manifest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_obj_manifest.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_obj_manifest.h

## Purpose
Defines the serialized object-manifest data model for RGW. A manifest maps logical object byte ranges to head/tail RADOS objects, supports old explicit part maps and newer rule-based implicit layouts, and stores cloud-tier metadata for transitioned objects.

## Important APIs And Types
`rgw_obj_select` stores either a logical `rgw_obj` or a raw `rgw_raw_obj` plus placement rule and can resolve raw locations. `RGWObjManifestPart` records an explicit part location, offset, and size. `RGWObjManifestRule` records implicit layout rule start part, start offset, part size, stripe max size, and optional override prefix. `RGWObjTier` stores tier name, placement, and multipart-upload flag.

`RGWObjManifest` exposes setters/getters for head object, size, prefix, tail placement, tail instance, rules, explicit objects, tier type/config, append operations, rule lookup, object iterators, and a nested `generator`. The nested `obj_iterator` walks stripes/parts and exposes current location, offsets, part id, stripe id, stripe size, and location offset. Encoding version 8 includes placement rules and tier fields while retaining compatibility logic for older structures.

## Control Flow And State
Implicit manifests use ordered `rules` keyed by start offset. Iterators choose the current rule, compute part/stripe ids, and use prefix/override prefix plus tail placement to synthesize locations. Explicit manifests use the `objs` map directly. Decoding handles legacy structures by marking old maps explicit, reconstructing head information, patching issue-16435 old copied head entries, and conditionally decoding tail bucket/instance to avoid redundant serialization.

Cloud-tier methods gate tier config on supported `RGWTierType::CLOUD_S3` and `CLOUD_S3_GLACIER`. `has_tail()` distinguishes single-head objects from objects with tail parts or size beyond head. `set_trivial_rule()` and `set_multipart_part_rule()` are helpers for common layout creation.

## Dependencies And Integration Points
Because this header defines fundamental serialized types, it deliberately avoids includes that require only RGW/OSD contexts beyond placement, bucket, object, and zone type headers. It integrates with object IO, multipart upload, copy/append, lifecycle tiering, admin formatting, and encoding test machinery through `WRITE_CLASS_ENCODER()` and `generate_test_instances()`.

## Risks And Test Signals
Backward-compatible decode paths are sensitive: old manifests without tail instance or placement fields must still map correctly. The mix of explicit and implicit layouts means append/iteration logic must be tested across both representations. Tier setters silently ignore unsupported tier types, which callers must account for. Tests should cover encode/decode versions, iterator seek and increment around rule boundaries, head-only objects, multipart layouts, copied old explicit manifests, tier config round trips, and raw/logical object selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_obj_manifest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_object_expirer_core.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_object_expirer_core.cc

## Purpose
Implements the RGW object expirer worker and its time-indexed hint store. It processes deletion hints created for objects that should expire at a future time, calls object-specific expiry handling, and trims processed hints from RADOS timeindex shards.

## Important APIs And Functions
Static helpers derive shard object names (`obj_delete_at_hint.%010u`), shard ids from object index keys, and key extensions containing tenant, bucket name/id, object name, and instance. `RGWObjExpStore::objexp_hint_add()` writes encoded `objexp_hint_entry` values with `cls_timeindex_add()`. `objexp_hint_list()` reads hints for a time range. `objexp_hint_trim()` trims processed timeindex entries, using `cls_timeindex_trim_repeat()` until `-ENODATA`.

`RGWObjectExpirer::garbage_single_object()` loads the bucket and calls `RadosObject::handle_obj_expiry()`. `garbage_chunk()` decodes listed hints and attempts deletion. `process_single_shard()` locks a shard, repeatedly lists chunks up to the configured chunk size, processes and trims them, and stops early when the configured interval budget is reached. `OEWorker::entry()` runs periodic rounds.

## Control Flow
Hints are added to a shard selected by bucket index hashing over object name plus instance, and stored in the zone log pool. The worker keeps `last_run`; each round records `start` and processes all shards for hints in `[last_run, start]`. If all shards complete, `last_run` advances to `start`; otherwise the next round retries the same interval. Each shard uses a cls lock named `gc_process` with duration equal to `rgw_objexp_gc_interval`, so concurrent RGWs skip shards already locked by another processor.

Within a shard, listing uses marker pagination and chunk size `rgw_objexp_chunk_size`. Any decoded entry attempts object expiry. `-ERR_PRECONDITION_FAILED` means the hint is stale or no longer applicable and is not treated as a hard failure. If any entries were inspected, the code trims from the previous marker to the returned marker across the time range.

## State And Persistence
Persistent state is the set of cls timeindex objects in the zone log pool, each keyed by expiry time and key extension with encoded hint data. Locks are stored on the shard objects through cls lock. Runtime state includes `last_run`, per-round `start`, markers, and the worker thread/down flag.

## Dependencies And Integration Points
Depends on `RGWObjExpStore`, SAL RadosStore/Driver, bucket loading, bucket index hashing, `cls/timeindex`, `cls/lock`, zone log pool, and `RadosObject::handle_obj_expiry()`. Configuration knobs include number of hint shards, chunk size, and GC interval.

## Risks And Edge Cases
`objexp_hint_parse()` logs decode errors but returns 0, so a corrupt hint can flow with default fields and should be watched. `process_single_shard()` uses `continue` on list errors inside the loop; without marker progress, repeated errors can spin until the time budget expires. Unlock is not guarded by RAII, so unexpected early returns after lock acquisition would risk waiting for lock expiry. Hints are trimmed even if object deletion failed with errors other than precondition failure, which can drop retry opportunities. Tests should validate stale hints, bucket missing, decode failures, lock contention, time-budget early exit, trim repeat behavior, and retry interval advancement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_object_expirer_core.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_object_expirer_core.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_object_expirer_core.h

## Purpose
Declares the object expiration hint store and background expirer. It gives callers a way to enqueue future delete hints and provides a worker that scans those hints, garbage-collects expired objects, and trims processed timeindex entries.

## Important APIs And Types
`RGWObjExpStore` exposes `objexp_hint_add()`, `objexp_hint_list()`, and `objexp_hint_trim()` over RADOS timeindex shards. `RGWObjectExpirer` wraps a SAL driver and store, exposes `hint_add()`, object garbage collection methods, shard processing methods, and worker lifecycle methods. Nested `OEWorker` is a Ceph `Thread` and `DoutPrefixProvider` used for periodic background processing.

## Control Flow And State
`start_processor()` allocates and starts the worker thread; `stop_processor()` sets `down_flag`, wakes the condition variable, joins, and deletes the worker. The worker calls `inspect_all_shards()` and sleeps based on `rgw_objexp_gc_interval`. `going_down()` exposes the atomic shutdown flag. `hint_add()` is a thin delegation into the store.

## Dependencies And Integration Points
The header depends on RADOS SAL types, Ceph thread/mutex/condition primitives, formatting/config utilities, crypto/global includes inherited from older RGW components, and `objexp_hint_entry` from RGW object expiry types. It integrates with bucket/object code that schedules delayed deletion and with RGW daemon startup/shutdown.

## Risks And Test Signals
The class stores the driver as a base pointer but downcasts to RadosStore in the store constructor and implementation, so it is RADOS-specific despite accepting `rgw::sal::Driver*`. Worker lifetime is manual and must not double-start. Tests should exercise start/stop idempotence, down-flag wakeup, hint add/list/trim delegation, and shard-processing behavior with mocked or test RADOS stores.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_object_expirer_core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_otp.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_otp.cc

## Purpose
Implements the metadata handler for RGW user one-time-password/MFA device metadata. It adapts cls MFA storage to the generic metadata manager interface so OTP devices can be fetched, set, removed, listed, formatted, and completed in the metadata log.

## Important APIs, Types, And Functions
`MetadataObject` derives from `RGWMetadataObject` and stores a list of `rados::cls::otp::otp_info_t` devices, dumping them as JSON. `MetadataHandler` derives from `RGWMetadataHandler` and reports type `"otp"`. It implements JSON decoding, `get()` through `mfa.list_mfa()`, `put()` through `mfa.set_mfa()`, `remove()` through `rgw_delete_system_obj()`, `mutate()` by running a callback then completing mdlog, and listing with `RGWMetadataLister`.

The namespace exports `rgwrados::otp::get_meta_key()` and `create_metadata_handler()`.

## Control Flow
Metadata JSON input must contain a decodable `"devices"` list or `get_meta_obj()` returns null. `put()` stores the device list with version tracking and the metadata object mtime, then calls `mdlog.complete_entry("otp", entry, &objv)`. `remove()` deletes the system object from the OTP pool and also completes mdlog. `mutate()` assumes the provided callback performed the actual mutation and only completes mdlog on success.

## State And Persistence
OTP device lists are persisted in the zone OTP pool via cls MFA/system object APIs. Object version and mtime are carried through `RGWMetadataObject`. The metadata key format is `otp:user:<user_string>`.

## Dependencies And Integration Points
Depends on `RGWSI_SysObj`, `RGWSI_Cls::MFA`, `RGWSI_MDLog`, zone params, `RGWMetadataLister`, cls OTP types, and metadata manager interfaces. It integrates with metadata sync/admin paths through the handler factory and with mdlog completion for replication.

## Risks And Test Signals
`put()` always passes `true` to `set_mfa()`, so overwrite/version semantics must match cls MFA expectations. `mutate()` does not use `mtime` or `op_type` directly, relying on the callback and mdlog completion. Listing uses no prefix, so the OTP pool should contain only OTP entries or callers must tolerate every oid as a key. Tests should cover JSON decode failure, get/put/remove mdlog completion, version conflict behavior, list marker handling, and key formatting for tenants/users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_otp.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_otp.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_otp.h

## Purpose
Declares the RADOS OTP metadata integration API. It provides a stable way to derive OTP metadata keys and to construct the metadata handler used by the RGW metadata manager.

## Important APIs
`rgwrados::otp::get_meta_key(const rgw_user&)` returns the metadata key for a user's OTP data. `create_metadata_handler()` accepts system object, cls, mdlog, and zone parameter services and returns a `std::unique_ptr<RGWMetadataHandler>`.

## State, Dependencies, And Integration
The header stores no state. It depends only on forward declarations for RGW services and user/zone types, making it a small factory interface. Concrete persistence and listing behavior live in `rgw_otp.cc`. Tests should verify the key contract and that the factory registers a handler whose type is `"otp"`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_otp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_pubsub_push.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_pubsub_push.cc

## Purpose
Implements concrete bucket-notification push endpoints for HTTP/S webhooks and optional AMQP/Kafka backends. It serializes S3 event payloads to JSON, manages global endpoint libraries/managers, validates endpoint arguments, and sends events with synchronous or coroutine-compatible waiting.

## Important APIs, Types, And Functions
`json_format_pubsub_event()` formats a single event inside the expected plural JSON wrapper. `get_bool()` parses boolean endpoint arguments. `RGWPubSubHTTPEndpoint` sends JSON by `RGWHTTPManager` and supports `verify-ssl`, `cloudevents`, and `http-ack-level` parsing. Optional `RGWPubSubAMQPEndpoint` supports AMQP 0-9-1 with exchange, ack level, SSL verification, and publisher confirms. Optional `RGWPubSubKafkaEndpoint` supports Kafka SSL/auth options and broker/no-ack modes.

`RGWPubSubEndpoint::create()` dispatches based on endpoint schema (`http`, `https`, `amqp`, `amqps`, `kafka`). `init_all()` initializes optional AMQP/Kafka libraries and the HTTP manager. `shutdown_all()` shuts them down. `init_http_manager()` and `shutdown_http_manager()` guard the global HTTP manager with a shared mutex and in-flight counter.

## Control Flow
HTTP send checks that the global manager exists, enforces `rgw_http_notif_max_inflight`, builds a POST request with configured connect/message timeouts, serializes the event, optionally adds CloudEvents binary-mode headers, increments pending perf counters, queues the request, waits, and decrements counters. AMQP/Kafka sends either fire-and-return for no-ack or publish with confirm, using `yield_waiter` when a coroutine yield is available and blocking waiter otherwise.

Endpoint creation first normalizes the schema. Unsupported schemas throw `configuration_error`. AMQP version defaults to `0-9-1`; AMQP 1.0 explicitly throws unsupported. The global initialization order is AMQP, Kafka, then HTTP; failure of any enabled backend aborts overall initialization.

## State And Persistence
This file persists no RGW data. Runtime singleton state includes `s_http_manager`, `s_http_manager_mutex`, and `s_http_manager_inflight`. AMQP/Kafka endpoint instances hold connection ids from their backend libraries. Perf counters record pending/failed/ok signals but are not durable.

## Dependencies And Integration Points
Depends on curl-backed RGW HTTP request classes, `RGWHTTPManager`, Ceph async waiters, JSON formatting, CloudEvents/RGW event types, endpoint argument parsing, optional `rgw_amqp.h` and `rgw_kafka.h`, RGW data sync/pubsub types, config values, and notification perf counters. It is used by `rgw_notify.cc` for immediate and persistent delivery.

## Risks And Edge Cases
HTTP `ack_level` is parsed but not yet used to interpret response status/body, so HTTP success is currently tied to request execution rather than configurable status semantics. `shutdown_http_manager()` takes an exclusive lock and stops the manager while sends use shared locks, which avoids reset during send but can block shutdown behind long requests. In-flight max returns `-EBUSY`, feeding retry behavior in persistent queues. Optional AMQP/Kafka code paths compile only when enabled, so coverage can vary by build. Tests should cover schema dispatch, invalid args, HTTP manager absent/busy, CloudEvents headers, endpoint initialization/shutdown, and AMQP/Kafka confirm/no-ack paths in enabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_pubsub_push.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_pubsub_push.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_pubsub_push.h

## Purpose
Declares the polymorphic endpoint interface for RGW pubsub notification delivery. Implementations send `rgw_pubsub_s3_event` payloads to configured webhook, AMQP, Kafka, or future endpoint types.

## Important APIs And Types
`RGWPubSubEndpoint` is non-copyable and uses `std::unique_ptr` alias `Ptr`. `create()` is the factory taking endpoint URI, topic, parsed HTTP-style args, and optional Ceph context. `send()` is the virtual delivery method and accepts a `DoutPrefixProvider`, event, and optional coroutine yield. `to_str()` returns a human-readable endpoint description. `configuration_error` is a `logic_error` subclass used for invalid endpoint configuration. `init_all()` and `shutdown_all()` manage global backend resources.

## Control Flow And State
The header defines the contract only. Endpoint construction may throw configuration errors; callers should catch them and decide whether to retry or fail the notification. Runtime state is owned by concrete derived classes and global backend managers in the implementation file.

## Dependencies And Integration Points
Depends on common forward declarations, `optional_yield`, `RGWHTTPArgs`, and `rgw_pubsub_s3_event`. It integrates with `rgw_notify.cc`, which creates endpoints during persistent queue processing or immediate commit and calls `send()`.

## Risks And Test Signals
Because `send()` returns negative errno-style values and construction throws exceptions, callers must handle both failure styles. Endpoint lifetime is per factory result unless callers add caching. Tests should verify factory failure handling, polymorphic deletion through the virtual destructor, and coroutine/non-coroutine send behavior for each compiled backend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_pubsub_push.h -->
