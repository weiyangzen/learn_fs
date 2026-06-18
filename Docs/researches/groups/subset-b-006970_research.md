# subset-b-006970 research

Grouped research for Ceph RGW RADOS deduplication, ETag verification, and garbage-collection files. Each source-file section is bounded for deterministic reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_dedup.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_dedup.h

## Purpose
`rgw_dedup.h` declares the main RGW deduplication background service. It ties together the dedup control plane, per-run shard coordination, bucket-index scanning, slab generation, duplicate estimation, and optional full dedup execution. The file is the facade for the RADOS driver dedup subsystem: it depends on the utility types, table, cluster coordinator, filter, and realm reloader interfaces.

## Important APIs, Types, And Functions
`rgw::dedup::control_t` is the run-control state carried locally and over watch/notify acknowledgements. It stores the requested dedup mode, start/execution state, local and remote pause or abort flags, restart requests, and two `Throttle` instances for bucket-index and metadata access. `local_urgent_req()`, `should_stop()`, and `should_pause()` are used by worker loops to react to shutdown, local pause, remote abort, and remote pause.

`rgw::dedup::Background` derives from `RGWRealmReloader::Pauser`. Its public API is `watch_reload()`, `unwatch_reload()`, `handle_notify()`, `start()`, `shutdown()`, `pause()`, and `resume()`. `DedupWatcher` is a nested `librados::WatchCtx2` wrapper that forwards RADOS notifications and errors to the background instance.

The private `dedup_step_t` enum names the main pipeline phases: bucket-index ingress, table build, attribute read, and duplicate removal. The declarations show two execution lanes: estimate support is always present, while strong hashing, manifest mutation, refcount changes, and actual dedup object rewrites are under `FULL_DEDUP_SUPPORT`.

## Control Flow
The service starts a runner thread with `start()` and coordinates an epoch through `setup()`. It reads bucket metadata, partitions bucket-index work across work shards, writes bucket entries as disk records grouped by MD5 shard, waits at shard barriers, builds a per-MD5 dedup table, optionally reads object attributes and BLAKE3 hashes, then optionally removes duplicates.

Shard processing is abstracted through `process_all_shards()` and member-function callbacks. Work-shard functions scan bucket-index shards and emit records. MD5-shard functions load slabs, build or update dedup table entries, and estimate or execute deduplication. Barrier methods wait for cluster shard-token completion between phases.

Urgent control runs alongside the pipeline. `handle_notify()` receives restart, abort, pause, resume, and throttle messages from the cluster control object. `handle_pause_req()` and the `control_t` predicates let long loops pause or stop without waiting for full phase completion.

## State And Persistence Behavior
The header itself stores only in-memory state, but its members point to persistent subsystems. `d_cluster` manages epoch and token objects in the RGW control pool. `d_dedup_cluster_ioctx` targets the dedup pool or control plane for slab access. The background object tracks global bucket counts, dedup thresholds, split-head settings, current control flags, filters, the RADOS watch handle, and the runner synchronization primitives.

The dedup pipeline persists intermediate `disk_record_t` records in slab objects via `rgw_dedup_store.*`. Full dedup mode persists object metadata changes, manifests, tail object refcount updates, and cleanup through functions declared behind `FULL_DEDUP_SUPPORT`.

## Dependencies And Integration Points
This file integrates with SAL (`rgw::sal::Driver`, `RadosStore`, `Bucket`), `RGWRados`, bucket-index APIs, object manifests, RADOS watch/notify, `RGWRealmReloader`, the cluster coordinator, the disk slab store, and the dedup hash table. The full dedup declarations depend on BLAKE3, RGW object manifest semantics, refcount operations, and object attribute reads and writes.

Admin-visible control flows are exposed indirectly by `rgw_dedup_cluster.cc` static control functions, which notify the watch object that this background service is watching.

## Risks And Edge Cases
The dedup service mutates live RGW object metadata in full mode, so pause, abort, rollback, refcount, and split-head paths are high risk. The header exposes rollback helpers for manifest refcounts and created tail objects, indicating partial failure is expected. Shard heartbeat and barrier correctness are also critical: a stuck worker, missed notify, or stale epoch can leave tokens incomplete and delay later phases.

`FULL_DEDUP_SUPPORT` changes the behavioral surface dramatically. Builds without it only allow estimate mode, while this source tree defines it in `rgw_dedup_utils.h`, enabling declarations for actual dedup work.

## Test Signals
Useful tests should exercise control flag encoding/decoding, remote pause/abort/restart notify handling, per-phase barriers, filtered bucket scans, dedup estimate counters, and full dedup rollback paths. Integration tests need multi-RGW participation because token acquisition, heartbeats, and epoch restarts are cluster-level behaviors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_dedup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_dedup_cluster.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_dedup_cluster.cc

## Purpose
`rgw_dedup_cluster.cc` implements the dedup cluster control plane. It owns epoch creation and compare-and-swap updates, work and MD5 shard token objects, shard progress xattrs, statistics aggregation, RADOS watch/notify control messages, and restart-scan orchestration.

## Important APIs, Types, And Functions
The file defines `DEDUP_EPOCH_TOKEN` and `DEDUP_WATCH_OBJ` control-pool objects. `get_control_ioctx()` opens the zone control pool. `get_epoch()`, `set_epoch()`, and `swap_epoch()` read and update the `RGW_DEDUP_ATTR_EPOCH` xattr on `DEDUP_EPOCH_TOKEN`.

`shard_progress_t` is the persisted progress xattr payload for each shard token. It records progress counters, completion state, creation, update and completion times, an owner cluster id, and encoded stats. It is encoded in `SHARD_PROGRESS_ATTR`.

`cluster::reset()` reads or initializes the epoch, waits for shard counts, cleans old token objects, creates current run tokens, and verifies that all expected token objects exist. `get_next_shard_token()` locks a shard token with `cls_lock`, writes initial progress, and returns the shard id. Completion and heartbeat updates are persisted through `mark_shard_token_completed()` and `update_shard_token_heartbeat()`.

`cluster::collect_all_shard_stats()` is the admin-facing stats path. It reads worker and MD5 shard progress xattrs, decodes `worker_stats_t` and `md5_stats_t`, aggregates timing per owner, prints incomplete shards, and reports estimate and actual dedup ratios.

`watch_reload()`, `unwatch_reload()`, `ack_notify()`, `dedup_control_bl()`, `dedup_control()`, and `dedup_restart_scan()` implement the watch/notify command channel used by `radosgw-admin` and the background service.

## Control Flow
Startup calls `reset()`. It reads the current epoch; if shard counts are already set, the member accepts them. If counts are missing and the caller has counts, it attempts `swap_epoch()` until counts are visible. Old token objects whose mtimes predate the epoch are deleted. New work and MD5 token objects are created with prefixes `WRK.SHRD.TK.` and `MD5.SHRD.TK.`.

Workers call `get_next_work_shard_token()` and MD5 processors call `get_next_md5_shard_token()`. Each function scans forward from the current local cursor and attempts an exclusive lock on the token object. On success it writes a fresh `shard_progress_t`; on busy or missing tokens it skips to the next candidate.

Barrier checks call `all_shard_tokens_completed()`. They read every token's `SHARD_PROGRESS_ATTR`, decode progress, mark completed local cache slots, return `-EAGAIN` for active or not-started shards, and return `-ETIME` for shards whose heartbeat exceeds `EPOCH_MAX_LOCK_DURATION_SEC`.

Restart-scan flow first gets or creates an epoch, sends `URGENT_MSG_ABORT` to running watchers, compare-and-swaps a new epoch with zero shard counts, then notifies `URGENT_MSG_RESTART` with an optional encoded `dedup_filter_t`.

## State And Persistence Behavior
The control pool stores one epoch object, one watch object, and one object per work or MD5 shard token. The epoch is persisted as the `rgw.dedup.attr.epoch` xattr. Token progress is persisted as `shard_progress` xattr. Lock ownership uses RADOS cls lock with a generated cookie and the hard-coded lock name `dedup_shard_token`.

Shard token object names are compact hex suffixed strings, for example `WRK.SHRD.TK.000`. Cleanup only removes legal token names and skips objects newer than the epoch time, reducing risk of deleting tokens from a newer run.

## Dependencies And Integration Points
This file depends on zone control-pool configuration, SAL RADOS store access, `rgw_rados_operate()`, `rgw_rados_notify()`, cls lock, cls xattr compare operations, Ceph formatters, and stats types from `rgw_dedup_utils.h`. It is the bridge between `radosgw-admin` dedup commands and the background worker in `rgw_dedup.h`.

## Risks And Edge Cases
Epoch `set_epoch()` accepts existing epoch xattrs when the compare against an empty xattr fails, so stale epoch handling depends on later restart logic. `all_shard_tokens_completed()` treats missing, undecodable, or xattr-less tokens as corruption and returns `-ENODATA`; callers must distinguish transient incompleteness from real failure. Heartbeat timeout only records timeout state in memory and does not break locks in this implementation path.

`dedup_control_bl()` returns the first nonzero ack status; in multi-RGW deployments one bad ack can fail the command even if other members succeeded. Notify timeout returns `-EAGAIN`.

## Test Signals
Tests should cover epoch compare-and-swap races, cleanup skipping new token objects, token lock contention, xattr decode failures, heartbeat timeout reporting, stats aggregation with missing shards, restart with and without filters, throttle notify decoding, and no-watcher notify timeout behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_dedup_cluster.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_dedup_cluster.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_dedup_cluster.h

## Purpose
`rgw_dedup_cluster.h` declares the `rgw::dedup::cluster` coordinator used by RGW dedup workers to share a scan across multiple RGW processes. It provides token naming, epoch reset, token acquisition, token completion, heartbeat updates, statistics collection, and admin control notify helpers.

## Important APIs, Types, And Functions
`WORKER_SHARD_PREFIX` and `MD5_SHARD_PREFIX` identify the two token namespaces. `cluster::shard_token_oid` constructs legal token object names by appending a three-digit hex shard id to a prefix and validates token names during cleanup.

The constructor takes a `DoutPrefixProvider`, `CephContext`, and SAL driver and generates local lock and cluster identifiers. `reset()` prepares the coordinator for a run. `get_next_work_shard_token()` and `get_next_md5_shard_token()` return the next lockable shard or null sentinel values. `mark_work_shard_token_completed()` and `mark_md5_shard_token_completed()` encode shard stats, update local completion caches, and persist completion.

Static APIs support admin and watcher integration: `collect_all_shard_stats()`, `watch_reload()`, `unwatch_reload()`, `ack_notify()`, `dedup_control_bl()`, `dedup_control()`, and `dedup_restart_scan()`.

## Control Flow
The background service calls `reset()` at scan setup, then repeatedly asks for work shard tokens during bucket ingress. After work shards complete, MD5 shard processors use the same token pattern. Completion checks use `all_work_shard_tokens_completed()` and `all_md5_shard_tokens_completed()`, which delegate to a common private checker.

Admin commands use static functions and do not require a live `cluster` instance. They open the control pool, notify `DEDUP_WATCH_OBJ`, decode acknowledgements, or update the epoch before restart.

## State And Persistence Behavior
The class caches current worker and MD5 shard cursors, epoch time, token creation time, and per-shard completion arrays. Persistent state is stored outside the class in RADOS control-pool objects and xattrs. Completion states in `d_completed_workers` and `d_completed_md5` are local caches of persisted xattr states.

## Dependencies And Integration Points
The class depends on `rgw_dedup_utils.h` for shard and stats types, `rgw_dedup_store.h` for record/block identifiers, `rgw_dedup_filter.h` for restart filtering, RADOS watch contexts, SAL RadosStore, optional yields, and Ceph formatters.

## Risks And Edge Cases
`shard_token_oid` has a fixed 16-byte buffer and prefixes are close to the limit; changes to prefixes must preserve the length invariant. The public completion helpers increment local completed counts before persisting the completed xattr, so caller behavior after a failed persist must be reviewed carefully.

## Test Signals
Unit-level tests should validate token object formatting and bounds, local completion-array transitions, null shard returns, and restart filter serialization. Integration tests should run multiple simulated workers contending for tokens.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_dedup_cluster.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_dedup_epoch.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_dedup_epoch.h

## Purpose
`rgw_dedup_epoch.h` defines the persisted epoch record for dedup scans. The epoch is the concurrency and restart boundary used by cluster coordination to distinguish old token objects from a current scan.

## Important APIs, Types, And Functions
`RGW_DEDUP_ATTR_EPOCH` is the xattr name used on the epoch token object. `dedup_epoch_t` contains a serial number, requested dedup type, timestamp, work shard count, and MD5 shard count.

Inline `encode()` and `decode()` serialize the epoch with Ceph encoding version 1. The dedup type is stored as an `int32_t`, then cast back to `dedup_req_type_t`. `operator<<` prints the epoch time, elapsed time, type, serial, and shard counts.

## Control Flow
The epoch is written by `set_epoch()` or `swap_epoch()` in `rgw_dedup_cluster.cc`. Background setup reads it during `cluster::reset()`, waits for nonzero shard counts when needed, and uses its time to clean old shard token objects.

## State And Persistence Behavior
The epoch is persisted as a single xattr payload in the RGW control pool. The timestamp is not just informational: cleanup compares token object mtime to epoch time and restart gating compares old and new epoch times.

## Dependencies And Integration Points
The type depends on Ceph `utime_t`, `ceph_clock_now()`, `rgw_dedup_utils.h` for `dedup_req_type_t`, and Ceph bufferlist encoding. It is consumed by the cluster coordinator and background setup.

## Risks And Edge Cases
Serial increments and timestamp comparisons are the main correctness signals. Clock skew or future epoch times can suppress restart in `can_start_new_scan()`. Adding fields requires a new encoding version and backward-compatible decode.

## Test Signals
Tests should verify encode/decode round trips for all dedup types and shard-count boundary values, stream output with elapsed time, and restart logic with equal, older, newer, and future epoch timestamps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_dedup_epoch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_dedup_filter.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_dedup_filter.cc

## Purpose
`rgw_dedup_filter.cc` implements bucket and storage-class filtering for dedup scans. It lets admin restart commands restrict scans by allowlist or denylist files and serializes the selected filter for watcher delivery.

## Important APIs, Types, And Functions
`dedup_filter_t::allow_bucket()` and `allow_storage_class()` apply `FILTER_NONE`, `FILTER_ALLOW`, or `FILTER_DENY` to bucket names and storage class names. `read_filter_file()` reads one name per line, strips `#` comments, trims whitespace, validates names, and populates a set.

The file-level validators currently return success unconditionally, intentionally allowing all strings rather than enforcing S3 bucket-name or storage-class validation. The constructor enforces mutual exclusion between allow and deny files per dimension, reads the configured files, sets modes, and records negative errno in `d_errcode` on failure.

`encode()` and `decode()` persist the two modes plus bucket set and storage-class vector in Ceph encoding version 1.

## Control Flow
The constructor validates arguments first. It then reads either the bucket allow file or bucket deny file, then either the storage-class allow file or storage-class deny file. Storage classes are read into a temporary set for deduplication and then moved to a vector for cheap iteration.

At scan time, bucket ingress calls filter methods to decide whether to scan a bucket and whether to skip an object based on its storage class. On restart, `rgw_dedup_cluster.cc` encodes an optional filter into the restart notify payload.

## State And Persistence Behavior
The runtime state is the bucket mode and set, storage-class mode and vector, and construction error code. The filter is not stored independently in RADOS; it is encoded into the restart notification payload and then held in the background service's `d_filter`.

## Dependencies And Integration Points
The file depends on Ceph bufferlist encoding, `DoutPrefixProvider` logging, errno values, and the S3 REST header context for potential validation. It integrates directly with dedup restart and object ingress.

## Risks And Edge Cases
Empty filter files return `-ENODATA`. Opening a missing file returns `-ENOENT`. Since validation accepts all strings, typos in names are not rejected and become silent allow or deny entries. Storage-class order is nondeterministic because it is copied from an unordered set; current logic only performs membership checks, so order is not semantic.

## Test Signals
Tests should cover comment stripping, whitespace trimming, empty files, duplicate names, mutually exclusive arguments, allow and deny behavior for buckets and storage classes, and encode/decode round trips with active and inactive filters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_dedup_filter.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_dedup_filter.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_dedup_filter.h

## Purpose
`rgw_dedup_filter.h` declares the filter contract used to include or exclude buckets and storage classes from dedup scans.

## Important APIs, Types, And Functions
`filter_mode_t` has `FILTER_NONE`, `FILTER_ALLOW`, and `FILTER_DENY`. `dedup_filter_t` exposes a default all-pass constructor, a file-path constructor, `errcode()`, `is_active()`, `allow_bucket()`, `allow_storage_class()`, and getters for the encoded filter contents.

Friend `encode()` and `decode()` functions serialize private fields for restart notifications.

## Control Flow
The background dedup service can be restarted with an encoded filter. During ingress, code checks `is_active()` or calls the allow methods as it iterates buckets and objects. A failed constructor leaves the object with `d_errcode` set and should prevent issuing a restart with invalid filter input.

## State And Persistence Behavior
The object holds bucket membership in an unordered set and storage-class membership in a vector. There is no direct persistent storage in this header; persistence is by bufferlist encoding in command payloads.

## Dependencies And Integration Points
It depends on Ceph encoding and logging types. It is included by the cluster coordinator and main dedup background service.

## Risks And Edge Cases
Callers must check `errcode()` after using the file-path constructor. The getters expose internal containers by const reference, so lifetime is tied to the filter object. Future encoding changes need versioned compatibility.

## Test Signals
Header-level expectations include inactive default behavior, correct active detection for each dimension, and stable encode/decode API linkage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_dedup_filter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_dedup_remap.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_dedup_remap.h

## Purpose
`rgw_dedup_remap.h` provides a compact string-to-`uint8_t` remapping helper. Dedup uses it where variable strings, especially storage class names, must fit into byte-sized record or table keys.

## Important APIs, Types, And Functions
`remapper_t` is constructed with a maximum number of entries. `remap()` returns the existing index for a key, assigns the next index when capacity remains, or returns `NULL_IDX` and increments an overflow counter when full. `NULL_IDX` is `0xFF`.

## Control Flow
On every key lookup, `remap()` first checks the unordered map. New keys are assigned monotonically from zero to `d_max_entries - 1`. Overflow is reported through the caller-provided counter and debug log.

## State And Persistence Behavior
The remap table is in-memory only. Persisted records store the remapped byte, so the same remapper instance and mapping scope must be used consistently while building or processing a table.

## Dependencies And Integration Points
The class depends on `DoutPrefixProvider` for debug logging and is used by dedup table and full-dedup paths that need compact storage-class or similar identifiers.

## Risks And Edge Cases
Capacity above 255 is unsafe because the return type is `uint8_t` and `0xFF` is reserved as null. The constructor accepts `uint32_t`, so callers are responsible for passing a bound compatible with byte storage. Overflow must be handled by the caller or table keys may become invalid.

## Test Signals
Tests should cover repeated key stability, assignment order, exact-capacity behavior, overflow counting, and the reserved `NULL_IDX` value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_dedup_remap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_dedup_store.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_dedup_store.cc

## Purpose
`rgw_dedup_store.cc` implements the disk record and slab storage layer for RGW dedup. It serializes bucket-index-derived object records into fixed-size blocks, writes blocks as slab objects, reads records back by block and record id, and provides helpers for per-MD5-shard output streams.

## Important APIs, Types, And Functions
`disk_record_t` constructors build records either from a SAL bucket plus object metadata or from serialized bytes. `serialize()`, `length()`, and `validate()` define the on-disk record format. Records include MD5, BLAKE3 hash fields, object size, part count, bucket identity, tenant, instance, storage class, ref tag, and serialized manifest.

`disk_block_t::init()`, `add_record()`, and `close_block()` manage one 8 KiB block. `disk_block_header_t::deserialize()` and `verify()` validate loaded block headers, magic markers, record counts, and block id.

`disk_block_id_t::get_slab_name()` maps a block id and MD5 shard to a slab object name in the format `SLB.%03X.%02X.%04X`. `load_record()`, `load_slab()`, and `store_slab()` are the RADOS read/write primitives. `disk_block_seq_t` appends records to a sequence of blocks and flushes slabs. `disk_block_array_t` owns one sequence per MD5 shard for a work shard.

## Control Flow
Ingress creates `disk_record_t` instances from bucket-index entries. A `disk_block_array_t` chooses a `disk_block_seq_t` by `md5_low % num_md5_shards`. `add_record()` validates the record, tries the current block, closes and advances when full, flushes the slab when the block array is exhausted, and returns a block id plus record id for dedup table references.

At phase end, `flush_output_buffers()` writes a final block for every MD5 shard. Even empty sequences write a terminating block so the MD5 stage can distinguish no work from missing work.

The read path derives the slab object name and byte offset from `disk_block_id_t`, reads one block, deserializes the header, verifies expected block id and record count, constructs a `disk_record_t`, validates it, and compares the key fields against the target record before returning the source record.

## State And Persistence Behavior
Slab objects are RADOS objects named by MD5 shard, worker shard, and slab id. Each slab contains up to 256 fixed 8 KiB blocks. Each block contains a packed header and up to 32 variable-length records. Header offset is reused as a magic value when closed: `BLOCK_MAGIC` indicates more blocks follow, and `LAST_BLOCK_MAGIC` marks termination.

Records are serialized in little-endian Ceph order for numeric fields, while strings and manifest bufferlists are concatenated after the packed header. Fastlane records omit ref tag and manifest payload and assert those lengths are zero.

## Dependencies And Integration Points
The store layer uses librados `IoCtx`, RGW object manifests, SAL bucket identity, `parsed_etag_t`, BLAKE3 constants, dedup stats, and Ceph bufferlist helpers. It feeds `rgw_dedup_table.*` and the main background pipeline.

## Risks And Edge Cases
The serialized constructor uses lengths from the on-disk packed header while advancing with some raw packed lengths; malformed records could stress length validation. `load_record()` requires an exact `DISK_BLOCK_SIZE` read and treats short reads as errors. Header validation does not include CRC, and comments note a future CRC. `disk_block_array_t` aborts the process if raw memory is too small for the requested MD5 shard count.

## Test Signals
Tests should cover record serialize/deserialize round trips, endian conversion, fastlane omission, max record size, block full behavior, last-block marker handling, slab object name formatting, empty terminating slab writes, fragmented bufferlist reads, and corrupt header or wrong block id failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_dedup_store.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_dedup_store.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_dedup_store.h

## Purpose
`rgw_dedup_store.h` declares the on-disk data model for dedup intermediate records. It defines block and slab sizing, compact identifiers, record flags, the packed record layout, and APIs for loading and storing slabs.

## Important APIs, Types, And Functions
Constants define `DISK_BLOCK_SIZE` as 8 KiB, `DISK_BLOCK_COUNT` as 256, and `MAX_REC_IN_BLOCK` as 32. `disk_block_id_t` packs work shard id, slab id, and block offset into 32 bits. `record_flags_t` tracks valid hash, shared manifest, hash calculated, fastlane, split head, and tail ref-tag modes.

`disk_record_t::packed_rec_t` is the fixed prefix of a variable-length record. It includes a 256-bit hash array, shared-manifest fingerprint, MD5 high/low words, object size, part count, string lengths, ref tag and manifest lengths, record version, and flags.

`disk_block_header_t` contains the mutable block offset or closed-block magic, record count, block id, and record offsets. `disk_block_t`, `disk_block_seq_t`, and `disk_block_array_t` declare the write-side hierarchy.

## Control Flow
The header sets the structure for the ingress phase: worker shards append records to MD5-specific sequences, which batch blocks into slabs. The MD5 phase later loads slabs by worker shard and sequence number, iterates block records, and uses block id plus record id to reload source records when duplicates are found.

## State And Persistence Behavior
The file defines persistent binary ABI. `static_assert`s pin BLAKE3 hash size, packed record header size, and table element sizes. Changing fields or sizes affects all written dedup slabs. Slab object names are derived from `disk_block_id_t`; the header exposes `get_slab_name()` as the naming authority.

## Dependencies And Integration Points
It depends on Ceph RADOS and bufferlist types, RGW common types, dedup utility statistics, BLAKE3 constants, and SAL bucket metadata. It is included by the dedup table because table values point back to disk records.

## Risks And Edge Cases
The use of packed structs and manual endian conversion requires strict round-trip tests. `disk_block_id_t` asserts work shard and sequence bounds but stores only 8 bits of work shard and 24 bits of sequence. The record version is currently only version 0, so future migration needs compatibility logic.

## Test Signals
Tests should validate struct sizes, `disk_block_id_t` bit packing, max shard and slab sequence boundaries, flag setting and reading, record length calculation, and compatibility of slab names with reader expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_dedup_store.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_dedup_table.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_dedup_table.cc

## Purpose
`rgw_dedup_table.cc` implements the in-memory open-addressed hash table used by dedup MD5 shards. The table counts objects by dedup key, tracks a representative disk record for duplicate groups, estimates dedupable bytes, and prepares the table for a second pass by removing singletons.

## Important APIs, Types, And Functions
The constructor zeroes caller-provided slab memory and interprets it as an array of packed `table_entry_t`. `find_entry()` uses `key.hash() % entries_count` and linear probing until it finds a matching key or an empty slot.

`add_entry()` inserts or updates a key. On first insert it stores `block_id`, `rec_id`, and shared-manifest status. On duplicates it increments estimated duplicate counters, saturates the count at `uint16_t` max, and replaces the representative value with a shared-manifest record when one appears.

`remove_singletons_and_redistribute_keys()` clears singleton and nondedupable keys, then relocates surviving keys to their ideal hash positions where possible and resets counts for actual dedup counting. `update_entry()`, `set_src_mode()`, `inc_count()`, `get_val()`, and `count_duplicates()` support later passes.

## Control Flow
The first pass builds the table from disk records and counts duplicate candidates. After that, `remove_singletons_and_redistribute_keys()` compacts the table so only dedupable groups remain. Later processing looks up a record's key, finds the representative source block/record, loads source records from slabs, and increments counts as actual dedup proceeds.

## State And Persistence Behavior
The table is in-memory only and backed by raw memory supplied by the caller. Values store disk block ids and record ids that refer to persistent slab records. Dedup estimates use object size rounded to 4 KiB units and `calc_deduped_bytes()` from utilities.

## Dependencies And Integration Points
The table depends on `key_t` and disk record ids from `rgw_dedup_store.h`, dedup stats from utilities, and main pipeline settings for head object size, minimum object size, and split-head mode.

## Risks And Edge Cases
There is no dynamic resize. If the table fills, insert returns `-EOVERFLOW`. Linear probing assumes entries are not removed except during the controlled redistribution pass. Shared-manifest replacement mutates the representative source, so correctness depends on full-dedup rules for already-shared manifests.

## Test Signals
Tests should cover collision probing, table-full overflow, duplicate count saturation, singleton removal, nondedupable filtering, shared-manifest representative replacement, `get_val()` misses, and redistribution preserving lookup success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_dedup_table.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_dedup_table.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_dedup_table.h

## Purpose
`rgw_dedup_table.h` declares the compact dedup table key and value layout plus operations for duplicate detection and representative-record tracking.

## Important APIs, Types, And Functions
`key_t` is a 24-byte packed key made from object data MD5 high and low words, object size in 4 KiB units, multipart part count, and storage-class index. It uses raw `memcmp()` equality and `md5_low` as the hash.

`dedup_table_t::value_t` is an 8-byte packed value containing the representative `disk_block_id_t`, duplicate count, record id, and flags. Flags track valid strong hash, shared manifest, and occupied state. Public accessors expose duplicate count, source block id, source record id, shared-manifest state, and valid-hash state.

The table API includes `add_entry()`, `update_entry()`, `get_val()`, `inc_count()`, `set_shared_manifest_src_mode()` declaration, `set_src_mode()`, `count_duplicates()`, and `remove_singletons_and_redistribute_keys()`.

## Control Flow
Keys are generated from disk records during MD5-shard processing. The table first estimates duplicates, then after singleton removal and redistribution acts as an index from target records to source records for actual dedup or deeper verification.

## State And Persistence Behavior
The table layout is packed and size-asserted, but it is not persisted as a stable RADOS object by this header. It is a memory view over caller-owned raw memory. Values reference persistent slab records, not object data directly.

## Dependencies And Integration Points
It depends on disk-store identifiers and dedup stats. It is used by the background dedup pipeline and full-dedup paths that set source flags after strong hash or shared manifest checks.

## Risks And Edge Cases
`key_t` equality compares all bytes, so padding must be initialized; the constructor sets `pad8 = 0`, but default-constructed or manually filled keys require care. `md5_low` as the only hash is fast but can be collision-heavy for adversarial inputs. The declared `set_shared_manifest_src_mode()` is not defined in the visible implementation, so users should confirm link coverage or remove stale API.

## Test Signals
Tests should assert packed sizes, key equality with initialized padding, hash consistency, value flag transitions, duplicate group source selection, and public API link coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_dedup_table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_dedup_utils.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_dedup_utils.cc

## Purpose
`rgw_dedup_utils.cc` implements serialization, parsing, formatting, and stats aggregation helpers for the RGW dedup subsystem. It provides encoded forms for throttles, stats, and throttle messages; parses S3 ETags into dedup keys; and dumps worker and MD5 shard stats for admin output.

## Important APIs, Types, And Functions
`operator<<` for `dedup_req_type_t` prints estimate or execution mode. `validate_max_calls_offset()` enforces that `Throttle::max_calls` is first for aligned non-atomic updates. `encode()` and `decode()` for `Throttle` persist only its configured rate limit, not runtime counters.

`throttle_action_t` and `throttle_msg_t` have stream and encode/decode helpers. `dedup_stats_t`, `worker_stats_t`, and `md5_stats_t` implement `operator+=`, stream formatting via `JSONFormatter`, `dump()` methods, and Ceph encode/decode.

`hex2int()`, private `dec2int()`, `get_num_parts()`, `parse_etag_string()`, and `etag_to_bufferlist()` convert S3 ETag strings to and from MD5 high/low words and multipart part counts. `get_next_data_ptr()` extracts contiguous data from possibly fragmented bufferlists by zero-copy when possible or copying into a caller buffer.

## Control Flow
Stats flow from worker and MD5 shard phases into token completion xattrs. Cluster stats aggregation decodes them and calls their `dump()` methods. ETag parsing runs during bucket-index ingress and filters out corrupted or unsupported ETags before a disk record is created.

Throttle messages arrive over watch/notify, decode into action vectors, and change the live control throttles in the background service.

## State And Persistence Behavior
All encode/decode functions use Ceph encoding version 1 and form part of the persisted xattr/notify ABI. Worker and MD5 stats are stored in shard progress xattrs. Throttle config is carried in notify payloads and control acknowledgements.

## Dependencies And Integration Points
The file depends on Ceph crypto MD5 support, bufferlist, formatter, JSON formatter, and the utility declarations. It is heavily consumed by `rgw_dedup_cluster.cc`, the main background dedup implementation, and `rgw_dedup_table.cc`.

## Risks And Edge Cases
`parse_etag_string()` assumes a 32-hex-character MD5 prefix and optional `-parts` suffix. Quoted or otherwise decorated ETags must be normalized before this function or they will fail. `get_num_parts()` caps multipart parts at 10,000 and rejects too-long suffixes. `get_next_data_ptr()` relies on the caller-provided buffer being at least `len` bytes.

Stats encoding is append-only sensitive: changing field order breaks decode compatibility. Some dump methods always emit zero counters while others emit conditionally, so admin output stability should be considered.

## Test Signals
Tests should cover single-part and multipart ETag parsing, invalid hex, invalid part suffixes, max part count, ETag formatting, fragmented bufferlist copy paths, encode/decode round trips for stats and throttle messages, and aggregation of every stats counter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_dedup_utils.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_dedup_utils.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_dedup_utils.h

## Purpose
`rgw_dedup_utils.h` declares shared constants, request types, throttling, stats structures, ETag parsing helpers, byte-size helpers, and urgent control message types for RGW dedup.

## Important APIs, Types, And Functions
The header defines `FULL_DEDUP_SUPPORT`, shard integer types and limits, null shard sentinels, and `MAX_COPIES_PER_OBJ`. `dedup_req_type_t` distinguishes no-op, estimate, and execution modes.

`Throttle` is a simple rate limiter with `set_max_calls_per_sec()`, `disable()`, `is_disabled()`, `acquire()`, and counters for sleep events and time. `dedup_stats_t`, `worker_stats_t`, and `md5_stats_t` collect phase-specific counters and provide aggregation, formatter dumping, and encoding APIs.

`parsed_etag_t` stores MD5 high/low and multipart part count. Size helpers convert bytes to 4 KiB disk blocks and calculate on-disk allocation. `urgent_msg_t`, `op_type_t`, `throttle_action_t`, and `throttle_msg_t` define the watch/notify control payload surface. `dedupable_object()` and `calc_deduped_bytes()` encode the estimate rules.

## Control Flow
The main dedup pipeline uses these types in every phase: work shard ingress fills `worker_stats_t`, MD5 shard processing fills `md5_stats_t`, control messages use `urgent_msg_t`, and throttling is applied around bucket-index and metadata operations. Dedup table estimation calls `calc_deduped_bytes()`.

## State And Persistence Behavior
Stats, throttles, and control messages can be encoded into RADOS xattrs or notification payloads. The `Throttle` runtime token state is intentionally not encoded, only the configured max calls per second. Many counters become admin-observable through shard stats.

## Dependencies And Integration Points
The header depends on Ceph bufferlist, encoding, formatters, `utime_t`, and logging. It is a central include for cluster coordination, store, table, filter, and background dedup code.

## Risks And Edge Cases
`FULL_DEDUP_SUPPORT` is defined directly in this header, so any include enables full-dedup declarations and compile paths unless guarded elsewhere. `Throttle::acquire()` is documented as single-threaded and uses non-atomic counters. `MAX_WORK_SHARD` is 255 while work shard id is stored in 8 bits, so sentinel and hard-limit assumptions must remain aligned.

## Test Signals
Tests should exercise shard limit constants, throttle disabled and limited behavior, all encode/decode helpers, dedupable-object threshold logic, split-head byte estimates, and admin formatting of nonzero failure counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_dedup_utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_etag_verifier.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_etag_verifier.cc

## Purpose
`rgw_etag_verifier.cc` implements a put-object data processor that recomputes ETags while object data is streamed. It verifies multisite-copied objects by reproducing either atomic-object MD5 ETags or multipart-upload ETags from object manifests.

## Important APIs, Types, And Functions
`create_etag_verifier()` decodes an `RGWObjManifest`, chooses `ETagVerifier_Atomic` for atomic objects, or constructs `ETagVerifier_MPU` with part offsets for MPU objects. For compressed sources it maps compressed manifest offsets back to original offsets using `RGWCompressionInfo::blocks`.

`ETagVerifier_Atomic::process()` updates a single MD5 hash for every bufferlist and passes data down the pipe. `calculate_etag()` finalizes that hash and hex-encodes it.

`ETagVerifier_MPU::process_end_of_MPU_part()` finalizes a part hash, feeds the raw MD5 digest into the MPU hash, restarts the part hash, and advances indexes. `process()` splits input that spans part boundaries and updates the appropriate hashes. `calculate_etag()` finalizes the last part, finalizes the MPU hash, and appends `-<parts>`.

## Control Flow
The verifier is inserted into the put pipeline before object data is written or passed to the next processor. Data chunks arrive with logical offsets. Atomic mode is linear. MPU mode tracks `cur_part_index` and `next_part_index`, detects boundary crossings, and updates per-part and aggregate hashes to match RGWCompleteMultipart behavior.

## State And Persistence Behavior
The verifier has no persistent state. It computes `calculated_etag` in memory and exposes it through the base class. It depends on the persisted source manifest and optional compression metadata to derive part boundaries.

## Dependencies And Integration Points
The file depends on `rgw_obj_manifest.h`, `rgw_putobj` data processors, Ceph MD5 crypto, compression metadata, and logging. It is related to dedup because both depend on accurate ETag and manifest interpretation, but it lives under `rgw::putobj`.

## Risks And Edge Cases
If manifest decode or rule lookup fails, verifier construction returns `-EIO`. If compressed offsets cannot be mapped exactly to compression blocks, verification is disabled by returning `-EIO`. MPU boundary logic is sensitive to off-by-one errors; the condition `logical_offset + in.length() + 1 == part_ofs[next_part_index]` deserves targeted tests because offsets are usually half-open ranges.

`process()` uses `in.c_str()` and assumes the bufferlist content is contiguous enough for the requested update. If fragmented bufferlists are possible in this pipe, callers or MD5 update semantics must make that safe.

## Test Signals
Tests should cover atomic ETag, multipart ETag with chunks aligned and crossing part boundaries, compressed offset remapping, malformed manifests, missing manifest rule, empty data, repeated `calculate_etag()` idempotence, and FIPS-allowed MD5 behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_etag_verifier.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_etag_verifier.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_etag_verifier.h

## Purpose
`rgw_etag_verifier.h` declares the ETag verifier data processors used during RGW put-object flows, especially multisite sync verification.

## Important APIs, Types, And Functions
`ETagVerifier` derives from `rgw::putobj::Pipe`, owns `CephContext`, an MD5 hash, and the calculated ETag string, and requires `calculate_etag()`. `ETagVerifier_Atomic` implements single-hash ETags. `ETagVerifier_MPU` stores part offsets, current and next part indexes, and a second MD5 for the aggregate MPU ETag.

`etag_verifier_ptr` is a `ceph::static_ptr` sized to the larger verifier type, avoiding heap polymorphic allocation. `create_etag_verifier()` constructs the correct concrete verifier into that static storage.

## Control Flow
Consumers call `create_etag_verifier()` with a manifest, optional compression info, and the next data processor. They stream data through the resulting `Pipe`, then call `calculate_etag()` and compare `get_calculated_etag()` to expected metadata.

## State And Persistence Behavior
The classes are transient stream processors. Their state is the in-progress hash context, part indexes, part offset vector, and final string. No persistent state is written.

## Dependencies And Integration Points
The header depends on RGW put-object pipe abstractions, RGW operation types, Ceph `static_ptr`, MD5, manifests, and compression metadata through the factory signature.

## Risks And Edge Cases
Because `etag_verifier_ptr` uses static storage, `max_etag_verifier_size` must be updated if a verifier class grows in a way the `std::max` expression does not cover. `ETagVerifier_MPU` initializes `next_part_index` to 1 and expects `part_ofs` to contain at least one offset with MPU semantics.

## Test Signals
Tests should instantiate both verifier types through the factory, verify static pointer lifetime and destruction behavior, and assert correct ETag strings for known atomic and MPU payloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_etag_verifier.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_gc.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_gc.cc

## Purpose
`rgw_gc.cc` implements RGW garbage collection for deferred object deletion. It shards GC logs across RADOS objects, supports transition from legacy omap entries to the `cls_rgw_gc` queue, processes expired entries under per-shard locks, schedules asynchronous refcount puts, and runs a background worker loop.

## Important APIs, Types, And Functions
`RGWGC::initialize()` sizes the GC shard set, initializes object names `gc.<index>`, prepares `transitioned_objects_cache`, and initializes each GC object with versioned queue state. `tag_index()` hashes tags with XXH64 and a fixed seed to choose a shard.

`send_split_chain()` splits large object chains according to `rgw_max_chunk_size`. `send_chain()` enqueues a chain into the v2 queue and falls back to legacy `cls_rgw_gc_set_entry()` on `-ECANCELED` or `-EPERM`.

`async_defer_chain()` defers a chain asynchronously, using queue operations when a shard has transitioned and legacy omap operations otherwise. `on_defer_canceled()` handles version-check cancellation as a transition signal and rewrites the defer into the queue.

`list()` merges legacy omap and queue entries while tracking markers and whether queue processing is in progress. `process()` handles one shard with a `gc_process` cls lock, lists expired entries, schedules tail object deletion through `RGWGCIOManager`, and removes retired GC entries. The overload `process(bool)` iterates shards from a random start. `GCWorker::entry()` runs periodic expired-only processing.

`RGWGCIOManager` batches asynchronous tail-object operations, tracks tag removal only after all shadow objects for a tag are done, limits concurrent AIO, and removes queue entries or legacy tags.

## Control Flow
Producers enqueue GC chains by tag. Processing begins by locking a GC shard object for a bounded duration. The processor lists up to 100 entries, respecting legacy or queue mode. For each chain, it opens the target pool when needed, sets object locator, allows deletion when pool is full, issues `cls_refcount_put(tag, true)` against each raw object, and later removes the GC tag or queue entries after successful scheduling and completion.

The background worker sleeps for `rgw_gc_processor_period` minus work duration and stops when `down_flag` is set.

## State And Persistence Behavior
GC state persists in RADOS GC pool objects named `gc.<index>`. Legacy entries live in cls_rgw omap-like structures at object version 0; queue entries live in `cls_rgw_gc` queue at version 1. `transitioned_objects_cache` memoizes which shard objects can use the queue path. Locks use cls lock name `gc_process`.

Tail deletion uses refcount class operations rather than direct removes. Successful tag removal retires entries from the GC log.

## Dependencies And Integration Points
The file depends on `RGWRados` GC pool contexts, cls_rgw, cls_rgw_gc, cls_refcount, cls_version, cls_lock, RGW perf counters, random utilities, and XXH64 hashing. It is used by RGW object delete, overwrite, lifecycle, and transition paths that defer raw object cleanup.

## Risks And Edge Cases
The async defer state has an explicit TODO about holding a reference to `RGWGC` to avoid use-after-free if the GC object destructs before callback completion. Transition handling mixes legacy and queue paths and must avoid deleting queue entries before all tail object puts succeed. `RGWGCIOManager::schedule_io()` drains only while `ios.size() > max_aio`, allowing one more than the configured max.

Failure behavior differs by mode: queue mode returns deletion errors to avoid removing queue entries; legacy mode often logs and continues to prevent unbounded tag buildup. Lock duration depends on `max_secs`, and zero or negative time returns `-EAGAIN`.

## Test Signals
Tests should cover enqueue fallback, chain splitting at encoded size boundaries, legacy-to-queue transition via `-ECANCELED`, list pagination across legacy and queue entries, per-shard locking, AIO concurrency and drain behavior, tag removal after multiple shadow objects, queue entry removal only after successful deletes, and worker shutdown wakeup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_gc.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_gc.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_gc.h

## Purpose
`rgw_gc.h` declares the RGW garbage collection service interface. It manages deferred cleanup of raw objects and chains through sharded GC logs and a background worker.

## Important APIs, Types, And Functions
`RGWGC` derives from `DoutPrefixProvider`. Public APIs include `initialize()`, `finalize()`, `send_split_chain()`, `async_defer_chain()`, `on_defer_canceled()`, `remove()`, `list()`, `process()`, `start_processor()`, and `stop_processor()`.

Private helpers include `tag_index()` for shard selection and `send_chain()` for enqueueing. Nested `GCWorker` derives from `Thread` and owns a mutex and condition variable for periodic processing and shutdown notification.

## Control Flow
Clients initialize the service with `CephContext` and `RGWRados`, enqueue or defer chains, optionally list GC entries for admin operations, and run processing either manually or through the worker. `stop_processor()` sets `down_flag`, wakes the worker, joins it, and deletes it.

## State And Persistence Behavior
The object stores GC shard count, shard object names, a transition cache, and a `down_flag`. Persistent queue contents live in RADOS and are manipulated in `rgw_gc.cc`. The destructor stops processing and finalizes the object-name array.

## Dependencies And Integration Points
It depends on librados, Ceph mutex and threading primitives, RGW common and SAL types, `RGWRados`, and cls RGW GC types. It exposes the cleanup service used by the RADOS backend.

## Risks And Edge Cases
Lifetime and async callbacks are important because the implementation schedules AIO operations that may outlive immediate calls. The destructor calls `stop_processor()` and `finalize()`, but external references or callbacks must not race destruction.

## Test Signals
Tests should cover initialization/finalization, worker start and stop idempotence, `going_down()` visibility, shard count sizing against configuration, and public list/process behavior with mocked GC pool responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_gc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_gc_log.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_gc_log.cc

## Purpose
`rgw_gc_log.cc` provides small helper functions that compose version-checked RADOS object operations for RGW GC log initialization, enqueue, and defer paths. It centralizes the transition boundary between legacy version-0 entries and version-1 `cls_rgw_gc` queue entries.

## Important APIs, Types, And Functions
`gc_log_init2()` checks object version 0, initializes the queue with configured max size and max deferred count, then sets version 1. `gc_log_enqueue1()` writes a legacy cls_rgw GC entry under version 0. `gc_log_enqueue2()` checks version 1 and enqueues into the queue.

`gc_log_defer1()` checks version 0 and defers an existing legacy entry by tag. `gc_log_defer2()` checks version 1, defers into the queue, and removes the legacy tag as cleanup.

## Control Flow
`RGWGC::initialize()` uses `gc_log_init2()`. Producer paths prefer `gc_log_enqueue2()` and fall back to legacy operations when version checks fail. Asynchronous defer paths use `gc_log_defer1()` until a version-check cancellation indicates transition, then retry through queue operations.

## State And Persistence Behavior
These helpers do not execute operations; they append cls operations to a caller-owned `librados::ObjectWriteOperation`. Version state is stored through `cls_version_check()` and `cls_version_set()`. Queue state is managed by `cls_rgw_gc_queue_*` operations; legacy state by `cls_rgw_gc_set_entry()`, `cls_rgw_gc_defer_entry()`, and `cls_rgw_gc_remove()`.

## Dependencies And Integration Points
The file depends on cls RGW, cls RGW GC, and cls version client APIs. It is included by `rgw_gc.cc` enqueue, defer, and initialization paths.

## Risks And Edge Cases
Correct operation ordering matters: version checks must precede mutations to prevent writing legacy entries after transition or queue entries before initialization. `gc_log_defer2()` removes the legacy tag after queue defer; comments note this should ideally be conditional on omap emptiness knowledge.

## Test Signals
Tests should verify composed operation order, expected version checks for each helper, fallback-triggering return codes in callers, and migration behavior with mixed legacy and queue entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_gc_log.cc -->
