# Research: subset-b-007865

Grouped research for OrangeFS server request scheduling and SeaweedFS filer metadata, backend stores, chunk manifests, and empty-folder cleanup. Each section preserves its source path for reconciliation into the final per-file documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/server/pvfs2-server.h -->
# sources/distributed-fs/orangefs/src/server/pvfs2-server.h

## Purpose
This header is the central server-side contract for OrangeFS/PVFS2 request handling. It defines initialization flags, reserved Trove metadata keys, permission and scheduler metadata hooks, request-specific scratch structures, and the large `PINT_server_op` state object passed through server state machines.

## Important APIs, Types, and Functions
- `PINT_server_req_permissions` classifies request permission checks: invalid, write, read, none, attribute ownership, and create-directory-entry write/execute checks.
- `Trove_Common_Keys` and `Trove_Special_Keys` are external key tables indexed by the reserved and optional metadata-key enums.
- `PINT_server_status_flag` tracks server subsystem initialization and cleanup responsibility for gossip, config, BMI, Trove, Flow, Job, request scheduler, state machines, precreate pools, security caches, and similar subsystems.
- Request operation scratch structs include creation, lookup, directory reads and mutations, remove, mkdir, getattr/listattr/eattr, I/O, mirroring, immutable-copy creation, tree operations, and performance updates.
- `PINT_server_op` is the main per-request state record. It carries queue links, cancellation/unexpected-message fields, operation type, event timing, scheduler id, generic keyval buffers, target attributes, client address/tag, decoded and encoded request/response objects, message-array state, prelude/scheduler metadata, and the request-specific union.
- `PINT_server_req_params` binds each request type to a string name, permission callback, access-type callback, scheduler policy, object-reference extractor, credential extractor, and the state machine that implements it.
- `PINT_CREATE_SUBORDINATE_SERVER_FRAME` allocates and initializes subordinate server operation frames, choosing local execution or remote msgarray setup based on handle placement and host id.
- Public helpers include request-table lookup functions, access-debug wrappers, keyval buffer ownership helpers, unexpected receive posting, state-machine lifecycle functions, and no-request state-machine entry points.

## Control Flow and State
Incoming server requests are decoded into `PINT_server_op`, then table-driven metadata from `PINT_server_req_table` selects permission checking, access classification, scheduling policy, object reference, credential, and state machine. The `prelude_mask` records prelude work such as permission checks before the operation-specific state machine consumes the relevant union member. Subordinate server frames allow nested/pjump state machines to reuse the same structure while resetting operation-specific state.

## State and Persistence Behavior
This header does not persist data directly, but it defines the handles, filesystem ids, Trove keyvals, object attributes, distribution metadata, mirror state, and encoded responses used by persistent server state machines. The reserved key enums are part of the persistent metadata namespace, so changes to indexes or meanings can affect on-disk Trove compatibility.

## Dependencies and Integration Points
It depends on core OrangeFS subsystems: BMI messaging, Trove storage, job/flow systems, request protocol encoding, state machines, cached configuration, performance counters, events, and mirror/distribution support. The request scheduler integrates through `scheduled_id`, `access_type`, `sched_policy`, and the request parameter table. State machine modules integrate through the declared external `PINT_state_machine_s` symbols.

## Risks and Edge Cases
- `PINT_server_op` is a broad shared mutable structure; state machines must clean only the fields they own and use the correct union member for `op`.
- The subordinate-frame macro has several side effects, allocates memory, and can return from the caller on allocation failure.
- Reserved Trove key enum order is ABI-like for metadata lookup and must stay synchronized with table definitions.
- Scheduler and permission callbacks rely on every request table entry being populated consistently.
- Ownership for capability, keyval buffers, encoded/decoded data, and nested frames is manual.

## Test Signals
No tests are in this header. Coverage is indirect through server state-machine tests and integration tests that exercise request decoding, permission prelude, scheduling, Trove metadata, mirroring, and nested server-to-server operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/server/pvfs2-server.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/server/request-scheduler/module.mk.in -->
# sources/distributed-fs/orangefs/src/server/request-scheduler/module.mk.in

## Purpose
This makefile fragment wires the OrangeFS request scheduler into the build. It defines the request-scheduler source directory and adds `request-scheduler.c` to the library and, when server builds are enabled, to the server source list.

## Important APIs, Types, and Functions
There are no runtime APIs. Build variables are `BUILD_SERVER`, `DIR`, `LIBSRC`, and `SERVERSRC`.

## Control Flow and State
The file is processed by the build system. `request-scheduler.c` is always included in `LIBSRC`; `ifdef BUILD_SERVER` also appends it to `SERVERSRC`.

## State and Persistence Behavior
No runtime state or persistence.

## Dependencies and Integration Points
The fragment assumes autoconf substitutes `@BUILD_SERVER@` and that the parent build includes module fragments that aggregate `LIBSRC` and `SERVERSRC`.

## Risks and Edge Cases
Duplication between library and server source lists can matter if build rules compile the same translation unit into multiple targets. Incorrect `BUILD_SERVER` substitution can omit scheduler symbols from server binaries.

## Test Signals
Coverage is build-level: successful server/library compilation and link resolution for request scheduler functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/server/request-scheduler/module.mk.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/server/request-scheduler/request-scheduler.c -->
# sources/distributed-fs/orangefs/src/server/request-scheduler/request-scheduler.c

## Purpose
This file implements the OrangeFS server request scheduler. It serializes or admits requests by object handle to preserve consistency while allowing concurrency for safe classes such as simultaneous I/O, readonly operations, and selected directory-entry operations. It also provides timer completions and server mode changes between normal and admin mode.

## Important APIs, Types, and Functions
- Internal states: `REQ_QUEUED`, `REQ_SCHEDULED`, `REQ_READY_TO_SCHEDULE`, and `REQ_TIMING`.
- `req_sched_list` is one hash bucket entry per handle and owns a per-handle request list.
- `req_sched_element` represents one request, timer, or mode change with list links, caller pointer, generated id, state, handle, access type, mode-change fields, and timer deadline.
- Globals: `req_sched_table`, `ready_queue`, `timer_queue`, `mode_queue`, `sched_count`, and `current_mode`.
- Lifecycle: `PINT_req_sched_initialize`, `PINT_req_sched_finalize`, and `PINT_timer_queue_finalize`.
- Mode APIs: `PINT_req_sched_change_mode`, `PINT_req_sched_get_mode`, `PINT_req_sched_in_admin_mode`, `PINT_req_sched_schedule_mode_change`, and `PINT_req_sched_do_change_mode`.
- Scheduling APIs: `PINT_req_sched_post`, `PINT_req_sched_unpost`, `PINT_req_sched_release`, `PINT_req_sched_post_timer`, `PINT_req_sched_test`, `PINT_req_sched_testsome`, and `PINT_req_sched_testworld`.
- Hash helpers: `hash_handle` and `hash_handle_compare`.

## Control Flow and State
Initialization creates a quickhash table keyed by `PVFS_handle`. Posting a bypass request may return immediately unless it is a modifying non-management request during or near admin mode. Scheduled requests allocate an element, register a generated id, find or create the handle queue, and either schedule immediately or enqueue behind existing work. If the queue contains only already scheduled I/O operations, another I/O may run concurrently. If it contains only already scheduled readonly work, another readonly request may run concurrently. Create/remove dirent requests also bypass each other by being marked readonly for scheduler purposes.

Release removes the completed element from its handle queue, destroys an empty queue, or advances the next request(s) into `ready_queue`. It advances consecutive I/O or readonly requests together. Test APIs move ready elements into scheduled state and return the caller's user pointer. Timer posts insert by deadline and tests complete expired timers. Mode changes are queued separately; normal mode can proceed immediately, while admin mode waits until `sched_count` is zero.

## State and Persistence Behavior
All scheduler state is in memory. It persists no data, but it gates access to persistent filesystem objects by handle. The generated scheduler id maps back to allocated elements through the id generator and must be released, unposted, or timer-completed to avoid leaks and stale ids.

## Dependencies and Integration Points
The implementation depends on quickhash, qlist, the id generator, server op tables/macros from `pvfs2-server.h`, and protocol definitions for `PVFS_server_op`, `PVFS_server_mode`, `PVFS_fs_id`, and `PVFS_handle`. Server state machines post before executing and release when complete. Debugging integrates with `GOSSIP_REQ_SCHED_DEBUG`.

## Risks and Edge Cases
- The scheduler is global and has no explicit locking in this file; callers must serialize access or run it in an event-loop context.
- `fs_id` and `in_user_ptr` release arguments are mostly unused, so future multi-filesystem semantics are not represented in the hash key.
- Concurrent dirent optimization treats create/remove dirent as readonly after scheduling, which is a consistency assumption specific to directory-entry handling.
- Timer test frees timer elements without unregistering ids in this file; correctness depends on id-generator behavior or external expectations.
- `PINT_req_sched_unpost` assumes `id_gen_fast_lookup` succeeds and that the element is not already scheduled.
- `PINT_timer_queue_finalize` frees `user_ptr`, while normal scheduler finalize does not; caller ownership expectations differ by path.

## Test Signals
No local tests are present. Useful coverage should include per-handle serialization, concurrent I/O and readonly admission, mixed modify/read queues, admin-mode blocking of modifying requests, timer ordering, unpost behavior, and release-time promotion of multiple ready elements.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/server/request-scheduler/request-scheduler.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/server/request-scheduler/request-scheduler.h -->
# sources/distributed-fs/orangefs/src/server/request-scheduler/request-scheduler.h

## Purpose
This header declares the OrangeFS server request scheduler interface and its access/scheduling policy enums. It is the public API used by server request processing to post, test, unpost, and release scheduled work.

## Important APIs, Types, and Functions
- `req_sched_id` aliases `PVFS_id_gen_t`; `req_sched_error_code` aliases `int`.
- `PINT_server_req_access_type` distinguishes readonly versus modifying requests.
- `PINT_server_sched_policy` distinguishes bypassed requests from scheduled requests.
- Lifecycle: `PINT_req_sched_initialize`, `PINT_req_sched_finalize`, `PINT_timer_queue_finalize`.
- Submission and control: `PINT_req_sched_post`, `PINT_req_sched_post_timer`, `PINT_req_sched_change_mode`, `PINT_req_sched_get_mode`, `PINT_req_sched_unpost`, and `PINT_req_sched_release`.
- Completion polling: `PINT_req_sched_test`, `PINT_req_sched_testsome`, and `PINT_req_sched_testworld`.

## Control Flow and State
Callers initialize the scheduler, post requests with operation, filesystem id, handle, access type, and policy, then either proceed immediately or poll for readiness using the returned id. Completed requests are released to unblock later work. Timers use the same polling model. Mode changes also return scheduler ids and become ready once conditions allow.

## State and Persistence Behavior
The header exposes only in-memory scheduling state. It affects ordering of persistent object mutations but does not define durable storage.

## Dependencies and Integration Points
It includes `pvfs2-req-proto.h` for protocol types and is included by server state-machine code that needs scheduler admission. `pvfs2-server.h` uses the access type and scheduler policy enums in request-table metadata.

## Risks and Edge Cases
The interface requires callers to pair scheduled ids with releases or unposts. `out_id` is zero for bypassed operations, and callers must handle that specially. The API does not expose locking or ownership semantics for `user_ptr`; those are implementation- and caller-dependent.

## Test Signals
Tests should compile both header and implementation users and exercise post/test/release, timer completion, bypass id handling, and mode changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/server/request-scheduler/request-scheduler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/abstract_sql/abstract_sql_store.go -->
# sources/distributed-fs/seaweedfs/weed/filer/abstract_sql/abstract_sql_store.go

## Purpose
This file implements the common SQL-backed SeaweedFS filer metadata store. Backend-specific SQL generators provide statements, while this store handles filer entry serialization, CRUD, directory listing, transactions, retry hooks, and optional S3 bucket-per-table behavior.

## Important APIs, Types, and Functions
- `SqlGenerator` defines statement factories for insert, update, find, delete, delete-folder-children, list-exclusive/list-inclusive, create-table, and drop-table.
- `AbstractSqlStore` embeds the generator and stores `*sql.DB`, bucket-table support, a protected bucket table cache, and an optional retryable-error callback.
- `BucketAware` methods: `CanDropWholeBucket`, `OnBucketCreation`, and `OnBucketDeletion`.
- Transaction methods: `BeginTransaction`, `CommitTransaction`, `RollbackTransaction`, and internal `getTxOrDB`.
- Filer store methods: `InsertEntry`, `UpdateEntry`, `FindEntry`, `DeleteEntry`, `DeleteFolderChildren`, `ListDirectoryPrefixedEntries`, `ListDirectoryEntries`, and `Shutdown`.
- Table helpers: `isValidBucket`, `CreateTable`, and `deleteTable`.

## Control Flow and State
Operations call `getTxOrDB` to select either a transaction from context key `"tx"` or the base DB. If bucket tables are enabled and the path is under `/buckets/<bucket>`, the method maps the filer path to a bucket table and a short path, lazily creating and caching the table after S3 bucket-name validation. Inserts encode the entry as protobuf bytes, optionally gzip metadata for large chunk lists, then insert by directory hash, name, directory, and metadata. Duplicate insert errors fall back to update. Updates and deletes execute their generated statements and check `RowsAffected`. Finds scan the metadata blob and decode it into `filer.Entry`. Listings query by hashed directory, start name, directory, prefix pattern, and `limit+1`, invoking `eachEntryFunc` until it stops or errors.

## State and Persistence Behavior
The persisted row stores directory hash, name, full directory string, and encoded metadata. The full directory protects against hash collisions in statement predicates. Bucket-table mode persists each bucket's object metadata in a separate SQL table and deletes an entire table when deleting bucket-root children. Transactions are carried through context, and retry wrappers are skipped inside transactions.

## Dependencies and Integration Points
It integrates with the SeaweedFS `filer.FilerStore` interface, `filer.BucketAware`, `util.FullPath`, `filer.Entry` protobuf encoding, `filer_pb.ErrNotFound`, S3 bucket name validation, and backend SQL dialect implementations. `util.RetryUntil` handles retryable database errors when configured.

## Risks and Edge Cases
- The context key `"tx"` is a plain string, which can collide with other context users.
- Duplicate detection depends on error text containing "duplicate entry"; non-English or dialect-specific messages may bypass fallback.
- `RowsAffected` is checked only for API support, not for actual row count.
- Bucket table names come from bucket strings through backend SQL generator code; injection safety depends on generators quoting/validating identifiers.
- Listing returns `limit+1` rows but does not stop by `limit` itself; callers may rely on the extra row to page.
- `DeleteFolderChildren` drops a bucket table when bucket root maps to `/`, which is efficient but broad.

## Test Signals
Coverage should use shared filer store tests for insert/update/find/delete/list, transaction commit/rollback, bucket-table creation/deletion, duplicate insert fallback, compressed metadata decoding, and prefix listings. This file has no local tests in the listed set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/abstract_sql/abstract_sql_store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/abstract_sql/abstract_sql_store_kv.go -->
# sources/distributed-fs/seaweedfs/weed/filer/abstract_sql/abstract_sql_store_kv.go

## Purpose
This file adapts `AbstractSqlStore` to SeaweedFS's simple key-value store interface by encoding arbitrary byte keys into the same SQL table shape used for filer metadata.

## Important APIs, Types, and Functions
- `KvPut` inserts a key/value pair and falls back to update on duplicate insert.
- `KvGet` retrieves the stored bytes and maps `sql.ErrNoRows` to `filer.ErrKvNotFound`.
- `KvDelete` deletes a key.
- `GenDirAndName` pads keys to at least 8 bytes, derives an int64 directory hash from the first eight bytes, and base64 encodes the directory and name components.

## Control Flow and State
All KV operations call `getTxOrDB` without bucket mapping and use `DEFAULT_TABLE`. `KvPut` computes `(dirStr, dirHash, name)`, attempts insert, logs duplicate fallback, then updates. `KvGet` runs the generated find statement and scans the metadata column directly into the value byte slice. `KvDelete` uses the generated delete statement.

## State and Persistence Behavior
The first eight key bytes form the directory partition and hash, while remaining bytes become the encoded name. Values are stored as raw bytes in the metadata column, not as encoded `Entry` protobufs. Short keys are padded with zero bytes, so callers must treat the key encoding as store-internal and not expect a reversible textual key.

## Dependencies and Integration Points
It shares SQL statement generation, transaction selection, and DB connection handling with `AbstractSqlStore`. It integrates with the filer KV interface and `util.BytesToUint64`.

## Risks and Edge Cases
- Short keys are padded in a local slice copy, making keys with trailing zero differences potentially non-obvious.
- Duplicate detection logs regardless of exact duplicate cause; comments intentionally avoid returning non-duplicate insert errors before fallback.
- The same `filemeta` table may contain both metadata rows and KV rows, so key partitioning must avoid collision with real filer directory/name pairs.
- `RowsAffected` behavior is driver-specific.

## Test Signals
Useful tests should cover put/get/delete, overwrite fallback, short keys, binary keys, transaction context use, and compatibility with SQL generator predicates. No local tests are listed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/abstract_sql/abstract_sql_store_kv.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/arangodb/arangodb_store.go -->
# sources/distributed-fs/seaweedfs/weed/filer/arangodb/arangodb_store.go

## Purpose
This file implements the SeaweedFS filer store for ArangoDB. It registers the backend, connects to or creates the configured database, stores entries as Arango documents, supports bucket-specific collections, and implements filer CRUD/list transactions.

## Important APIs, Types, and Functions
- `ArangodbStore` holds the connection, client, database, KV collection, bucket collection cache, lock, and database name.
- `Model` maps stored documents with `_key`, directory, name, ttl, and metadata encoded as `[]uint64`.
- `Initialize` reads config and calls `connection`.
- `connection` creates the HTTP connection, authenticates, opens or creates the database, and ensures the KV collection.
- Transaction methods begin exclusive transactions over cached bucket collections plus KV collection, then commit or abort using a context-stored transaction id.
- Filer methods: `InsertEntry`, `UpdateEntry`, `FindEntry`, `DeleteEntry`, `DeleteFolderChildren`, `ListDirectoryPrefixedEntries`, `ListDirectoryEntries`, and `Shutdown`.

## Control Flow and State
Insert/update derive directory and name, encode entry metadata, optionally gzip large chunk metadata, build a `Model`, set TTL timestamp text, find the target collection from the full path, and create or update a document keyed by MD5 hash of the full path. Insert conflicts call `UpdateEntry`. Finds read the hashed document and decode metadata. Deletes remove by hashed full path. Folder deletion runs an AQL query to remove documents whose directory equals or appears under the target. Listing builds an AQL query for name range, optional prefix, exact directory, sorting, and limit, then decodes each document and calls the listing callback.

## State and Persistence Behavior
Each entry persists as one document. ArangoDB cannot store arbitrary binary directly in this model, so metadata bytes are converted to a length-prefixed `[]uint64`. TTL is stored in a field indexed by helpers. Bucket paths map to per-bucket collections, while non-bucket paths use a default collection. The bucket collection cache is in-memory and lazily filled.

## Dependencies and Integration Points
It integrates with `github.com/arangodb/go-driver`, SeaweedFS `filer.Stores`, `filer.Entry` encoding, `filer_pb.ErrNotFound`, S3 bucket path conventions, and helper functions in `helpers.go` for keying, byte conversion, collection selection, and index creation.

## Risks and Edge Cases
- Listing and delete queries concatenate `startFileName`, `prefix`, and transformed full path into AQL, creating injection or quoting risks if names contain special characters.
- `DeleteFolderChildren` transforms `/` to `,` for `starts_with`, which looks suspicious and should be validated against intended directory encoding.
- `BeginTransaction` only includes collections currently in the cache; a transaction may miss a lazily created bucket collection.
- `UpdateEntry` stores TTL `"none"` while insert stores empty string when no TTL; TTL index semantics depend on Arango behavior for these values.
- Hashing full paths with MD5 gives compact keys but collision handling is absent.

## Test Signals
No local tests are listed. Store-level tests should cover create/update conflict fallback, find/delete not found behavior, TTL, bucket collection mapping, directory listing order and prefix filtering, and transaction coverage across buckets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/arangodb/arangodb_store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/arangodb/arangodb_store_bucket.go -->
# sources/distributed-fs/seaweedfs/weed/filer/arangodb/arangodb_store_bucket.go

## Purpose
This file implements `filer.BucketAware` behavior for the ArangoDB filer store, allowing bucket creation and deletion to create or drop the corresponding ArangoDB collection.

## Important APIs, Types, and Functions
- Compile-time interface assertion `var _ filer.BucketAware = (*ArangodbStore)(nil)`.
- `OnBucketCreation` ensures a bucket collection with a 10-second context timeout.
- `OnBucketDeletion` ensures/opens the collection, removes it, and deletes it from the in-memory cache.
- `CanDropWholeBucket` returns true.

## Control Flow and State
Bucket creation delegates to `ensureBucket`, which creates the collection and indexes if absent. Bucket deletion obtains the collection, removes it unless already missing, and updates `store.buckets` under lock.

## State and Persistence Behavior
Persistent state is the ArangoDB collection per bucket. Dropping a bucket deletes the entire collection and therefore all metadata for that bucket.

## Dependencies and Integration Points
It uses ArangoDB driver errors, `context.WithTimeout`, SeaweedFS `BucketAware`, and helper cache/index management from `helpers.go`.

## Risks and Edge Cases
- `OnBucketDeletion` calls `ensureBucket`, which can create a missing collection immediately before deleting it.
- Errors are logged but not returned, so callers cannot react to bucket collection failures.
- Bucket name to collection name transformation must stay consistent between creation, deletion, and path extraction.

## Test Signals
Tests should verify collection creation, deletion, cache invalidation, idempotent deletion, and behavior when ArangoDB returns not found. No local tests are listed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/arangodb/arangodb_store_bucket.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/arangodb/arangodb_store_kv.go -->
# sources/distributed-fs/seaweedfs/weed/filer/arangodb/arangodb_store_kv.go

## Purpose
This file implements SeaweedFS KV operations for the ArangoDB store using a dedicated KV collection.

## Important APIs, Types, and Functions
- `KvPut` creates or updates a document keyed by `hashString(".kvstore."+string(key))`.
- `KvGet` reads the document and returns decoded metadata bytes or `filer.ErrKvNotFound`.
- `KvDelete` removes the document and maps errors to not found after logging.

## Control Flow and State
`KvPut` builds a `Model` with the hashed key, a synthetic directory field, and `Meta` converted by `bytesToArray`. It first checks `DocumentExists`, then updates or creates. `KvGet` reads into `Model` and converts `Meta` back to bytes. `KvDelete` removes by the same hash.

## State and Persistence Behavior
KV data persists in `KVMETA_COLLECTION` and uses the same uint64-array binary representation as entry metadata. The key is not stored reversibly except in the synthetic directory field, and document identity is an MD5 hex string.

## Dependencies and Integration Points
Depends on the ArangoDB driver, helper hash/conversion functions, and SeaweedFS KV error contract.

## Risks and Edge Cases
- Using `string(key)` for binary keys can embed unusual bytes in `Directory`, although the document key is hashed.
- `DocumentExists` plus create/update is a read-before-write race under concurrent writers.
- `KvDelete` treats all errors as not found after logging, which can hide connectivity or permission failures from callers.

## Test Signals
Tests should cover binary keys, overwrite, missing key, delete idempotence, and concurrent put races. No local tests are listed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/arangodb/arangodb_store_kv.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/arangodb/helpers.go -->
# sources/distributed-fs/seaweedfs/weed/filer/arangodb/helpers.go

## Purpose
This helper file provides hashing, byte conversion, bucket extraction, collection-name normalization, bucket cache lookup, collection creation, and index creation for the ArangoDB filer store.

## Important APIs, Types, and Functions
- `hashString` returns MD5 hex for full paths and KV keys.
- `bytesToArray` stores arbitrary bytes as a length-prefixed big-endian `[]uint64`.
- `arrayToBytes` reconstructs the original bytes using the first element as byte length.
- `extractBucketCollection` and `extractBucket` map `/buckets/<bucket>/...` paths to bucket collections and short paths.
- `ensureBucket` performs double-checked cache lookup and collection creation under `store.mu`.
- `bucketToCollectionName` replaces dots and prefixes names that start with disallowed characters.
- `ensureCollection` opens or creates a collection and ensures directory/name unique, directory, TTL, and name indexes.

## Control Flow and State
Path lookup extracts a bucket name if the full path is under the bucket prefix; otherwise it uses the default collection. `ensureBucket` first tries an RLock cache lookup, then creates/opens and indexes the collection under a write lock. Collection names are normalized before all ArangoDB calls.

## State and Persistence Behavior
Persistent schema state consists of collections and indexes. The unique `(directory,name)` index prevents duplicate entries within a collection. TTL index uses the `ttl` field. In-memory state is `store.buckets`.

## Dependencies and Integration Points
It depends on the ArangoDB driver and `util.FullPath`. Store CRUD and bucket-aware methods depend on these helpers for consistent collection selection and metadata encoding.

## Risks and Edge Cases
- `arrayToBytes` allocates `len(xs)*8` and slices to `first` without validating `first <= capacity`, so corrupt stored data can panic.
- MD5 keys have no collision resolution.
- `bucketToCollectionName` only replaces dots and prefixes certain starts; other collection-name constraints should be verified.
- `extractBucket` does not validate S3 bucket names.
- Concurrent first access serializes collection creation but all callers pay index-ensure work on cache miss.

## Test Signals
Tests should cover byte round trips, corrupt `Meta`, bucket extraction, collection-name normalization, cache behavior, and index creation idempotence. No local tests are listed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/arangodb/helpers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/cassandra/cassandra_store.go -->
# sources/distributed-fs/seaweedfs/weed/filer/cassandra/cassandra_store.go

## Purpose
This file implements the original Cassandra-backed SeaweedFS filer store. It stores metadata in a `filemeta` table keyed by directory and name, supports optional super-large-directory key rewriting, and implements standard filer CRUD/list methods.

## Important APIs, Types, and Functions
- `CassandraStore` holds cluster config, session, and `superLargeDirectoryHash`.
- `Initialize` reads keyspace, hosts, credentials, large-directory config, local DC, and timeout.
- `initialize` configures gocql auth, keyspace, timeout, token-aware host policy, local quorum, session, and super-large-directory hashes.
- Transaction methods are no-ops.
- Store methods: `InsertEntry`, `UpdateEntry`, `FindEntry`, `DeleteEntry`, `DeleteFolderChildren`, `ListDirectoryPrefixedEntries`, `ListDirectoryEntries`, and `Shutdown`.

## Control Flow and State
Insert/update derive directory and name from full path, rewrite large-directory entries to `dirHash+name` with empty name, encode metadata, optionally gzip large chunk metadata, and execute an insert with TTL. Find and delete apply the same key rewrite. Directory deletion deletes by `directory`. Listing scans `filemeta` for one directory and name greater than or greater/equal to the start name, ordered ascending and limited by `limit+1`.

## State and Persistence Behavior
Rows are stored as `(directory, name, meta)` with TTL from `entry.TtlSec`. Super-large-directory mode avoids huge Cassandra partitions by moving file names into the directory key, but listing/deleting such directories returns without doing work. Consistency is local quorum.

## Dependencies and Integration Points
It uses `github.com/apache/cassandra-gocql-driver/v2`, `filer.Entry` encoding, `filer_pb.ErrNotFound`, glog, and SeaweedFS store registration. The expected Cassandra schema must support the queried primary key and ordering.

## Risks and Edge Cases
- Super-large directories cannot be listed or folder-deleted through normal paths.
- Four-character MD5 prefixes for large-directory hashes can collide; initialization fatal-checks configured directories only.
- No transaction support despite implementing transaction methods.
- Prefix listing is unsupported.
- `KvGet` in the companion file has suspicious error mapping; store-level semantics should be tested.

## Test Signals
No local tests are listed. Shared filer tests should cover CRUD, TTL, listing order, unsupported prefixed listing, large-directory behavior, and session shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/cassandra/cassandra_store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/cassandra/cassandra_store_kv.go -->
# sources/distributed-fs/seaweedfs/weed/filer/cassandra/cassandra_store_kv.go

## Purpose
This file implements SeaweedFS KV operations on top of the original Cassandra `filemeta` table.

## Important APIs, Types, and Functions
- `KvPut` inserts value bytes into `filemeta` with TTL 0.
- `KvGet` selects `meta` and maps missing or empty data to `filer.ErrKvNotFound`.
- `KvDelete` deletes the row.
- `genDirAndName` pads keys to eight bytes and base64 encodes the first eight bytes as directory and the remaining bytes as name.

## Control Flow and State
Every operation converts a byte key to `(directory,name)`. Put is a Cassandra insert/upsert. Get scans metadata into a byte slice. Delete removes by directory/name.

## State and Persistence Behavior
KV values share the `filemeta` table with metadata rows. The first eight key bytes determine the partition, while remaining bytes determine the clustering/name component. Values are raw bytes.

## Dependencies and Integration Points
It uses gocql, filer KV errors, and the Cassandra session owned by `CassandraStore`.

## Risks and Edge Cases
- The `KvGet` error branch returns `ErrKvNotFound` only when the error is not `gocql.ErrNotFound`, then falls through for `ErrNotFound` and relies on empty data; this is easy to misread and should be tested.
- Short keys are zero-padded.
- KV rows can collide with metadata rows if encoded directory/name overlap real paths.

## Test Signals
Tests should cover missing keys, empty values, overwrites, binary/short keys, and delete behavior. No local tests are listed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/cassandra/cassandra_store_kv.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/cassandra2/cassandra_store.go -->
# sources/distributed-fs/seaweedfs/weed/filer/cassandra2/cassandra_store.go

## Purpose
This file implements the newer Cassandra2 SeaweedFS filer store. It extends the Cassandra backend with TLS/mTLS configuration and a schema that adds `dirhash` to reduce partitioning and query costs.

## Important APIs, Types, and Functions
- `Cassandra2Store` mirrors the original store with cluster config, session, and super-large-directory hash map.
- `Initialize` reads credentials, TLS paths, host verification, large directories, local DC, and timeout.
- `initialize` validates TLS file combinations and existence, configures gocql `SslOptions`, optionally uses AWS Keyspaces port 9142, then creates a local-quorum session.
- CRUD/list methods mirror Cassandra but query `filemeta` using `dirhash`, `directory`, and `name`.
- Transaction methods are no-ops.

## Control Flow and State
TLS options are set before session creation when CA/cert/key paths are provided. Insert/update apply super-large-directory rewriting, encode and optionally gzip metadata, then insert `(dirhash,directory,name,meta)` with TTL. Find, delete, folder delete, and listing compute `util.HashStringToLong(dir)` and include it in predicates. Listing orders by `name` within a hashed directory and returns `limit+1` rows.

## State and Persistence Behavior
Rows persist `dirhash` beside directory and name. This schema is distinct from the original Cassandra backend and must match table definitions. TTL comes from entry attributes. Super-large-directory behavior still disables normal listing/deletion for those directories.

## Dependencies and Integration Points
It integrates with gocql v2, TLS file paths from configuration, SeaweedFS `filer.Stores`, `filer.Entry` encoding, `filer_pb.ErrNotFound`, and `util.HashStringToLong`.

## Risks and Edge Cases
- TLS path validation requires cert and key together but permits CA-only TLS.
- Hosts without explicit ports switch to 9142 when TLS is enabled, which is suitable for AWS Keyspaces but may surprise standard Cassandra users.
- No transaction support.
- Prefix listing is unsupported.
- Hash collisions are guarded by also storing/querying directory, but schema design must preserve this.

## Test Signals
Tests should cover TLS config validation, port selection, CRUD/listing against the Cassandra2 schema, large-directory behavior, and unsupported prefix listing. No local tests are listed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/cassandra2/cassandra_store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/cassandra2/cassandra_store_kv.go -->
# sources/distributed-fs/seaweedfs/weed/filer/cassandra2/cassandra_store_kv.go

## Purpose
This file implements KV operations for the Cassandra2 filer store using the `dirhash,directory,name,meta` schema.

## Important APIs, Types, and Functions
- `KvPut` inserts raw value bytes into `filemeta` with TTL 0.
- `KvGet` selects bytes by hash, directory, and name and maps missing or empty values to `filer.ErrKvNotFound`.
- `KvDelete` deletes the KV row.
- `genDirAndName` pads and base64 encodes byte keys into directory/name strings.

## Control Flow and State
The key encoding matches the original Cassandra KV store, but all CQL includes `util.HashStringToLong(dir)`. Put is an upsert-style insert. Get and delete use the same derived key triplet.

## State and Persistence Behavior
KV rows share the Cassandra2 `filemeta` table. The stored value is raw bytes. Directory hash is derived from the base64 first-eight-byte directory string.

## Dependencies and Integration Points
It depends on the Cassandra2 session, gocql errors, filer KV errors, and SeaweedFS hash utilities.

## Risks and Edge Cases
- Like the original Cassandra KV file, missing-key handling is non-obvious and should be covered explicitly.
- Empty values are treated as not found.
- Key padding can make some short binary keys surprising.

## Test Signals
Tests should cover short keys, binary keys, overwrites, missing keys, empty values, and delete. No local tests are listed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/cassandra2/cassandra_store_kv.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/configuration.go -->
# sources/distributed-fs/seaweedfs/weed/filer/configuration.go

## Purpose
This file loads SeaweedFS filer store configuration, selects the enabled default store, and configures optional path-specific stores.

## Important APIs, Types, and Functions
- Global `Stores []FilerStore` receives store implementations via backend `init` functions.
- `(*Filer).LoadConfiguration` validates default store selection, instantiates a fresh store of the registered type, initializes it, installs it on the filer, then scans for path-specific store configs.
- `validateOneEnabledStore` enforces at most one default store.

## Control Flow and State
Configuration first checks that only one top-level `<store>.enabled` is true. The first enabled registered store is cloned using reflection, initialized with prefix `<store>.`, and passed to `f.SetStore`. Then all config keys ending in `.enabled` with a dotted `<store>.<id>` prefix are examined. Enabled path-specific configs are cloned, initialized, require a `.location`, and are added through `f.Store.AddPathSpecificStore(location, storeId, store)`.

## State and Persistence Behavior
The file does not persist metadata itself. It determines which persistent backend receives future filer operations and whether path-specific routing is active.

## Dependencies and Integration Points
It uses `util.ViperProxy`, registered `FilerStore` implementations, reflection to create new concrete store instances, and logging/fatal exits for invalid configuration.

## Risks and Edge Cases
- Reflection assumes registered stores are pointers to concrete types and can be `Elem()` cloned.
- Store selection depends on registration order.
- Validation only enforces top-level default stores; path-specific store conflicts are not checked here.
- On missing default or invalid path-specific config, the process exits instead of returning an error.

## Test Signals
Tests should cover single default selection, duplicate default fatal behavior, missing default behavior, path-specific store loading, missing location, and registered store cloning. No local tests are listed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/configuration.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/copy_params.go -->
# sources/distributed-fs/seaweedfs/weed/filer/copy_params.go

## Purpose
This file centralizes query parameter and response header names for SeaweedFS copy operations.

## Important APIs, Types, and Functions
It defines constants for copy source, overwrite, data-only mode, request id, source/destination inode, mtime and size, plus response headers for committed state and request id.

## Control Flow and State
No control flow. Callers import these constants to avoid spelling drift across HTTP handlers and clients.

## State and Persistence Behavior
No direct persistence. Some parameters carry inode, mtime, size, and request id metadata that may affect copy idempotency or verification elsewhere.

## Dependencies and Integration Points
It belongs to package `filer`, so filer HTTP/API code can reuse the constants without an extra package.

## Risks and Edge Cases
Changing any constant is an API compatibility change for clients and proxies.

## Test Signals
Tests are not needed for behavior, but integration tests for copy APIs should assert these parameter/header names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/copy_params.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/elastic/v7/doc.go -->
# sources/distributed-fs/seaweedfs/weed/filer/elastic/v7/doc.go

## Purpose
This package documentation file explains that the Elasticsearch filer store is build-tagged and compiled only in full installs because the `olivere/elastic/v7` dependency is large.

## Important APIs, Types, and Functions
No APIs are defined. It declares package `elastic` and documents the build/install context.

## Control Flow and State
No runtime control flow.

## State and Persistence Behavior
No persistence.

## Dependencies and Integration Points
It documents the package implemented by `elastic_store.go` and `elastic_store_kv.go`, both of which use the `elastic` build tag.

## Risks and Edge Cases
The comment notes build-size concerns; users may not have this backend unless building with the correct tag/full install path.

## Test Signals
Package availability should be covered by build-tag CI or full-install builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/elastic/v7/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/elastic/v7/elastic_store.go -->
# sources/distributed-fs/seaweedfs/weed/filer/elastic/v7/elastic_store.go

## Purpose
This build-tagged file implements SeaweedFS filer stores for Elasticsearch 7 and 8. It stores each entry as JSON in Elasticsearch, partitions metadata by top-level path-derived index, supports listing via parent id searches, and keeps a separate KV index.

## Important APIs, Types, and Functions
- Build tag: `//go:build elastic`.
- Globals define index type, prefix, KV index, and KV mapping.
- `ESEntry` stores `ParentId`, optional `Id` for ES8 sorting, and the `filer.Entry`.
- `ElasticStore` holds the client, max page size, and ES8 mode flag.
- `Elastic8Store` embeds `ElasticStore` and toggles ES8 mode.
- Initialization configures URL, basic auth, sniff/healthcheck, max result window, creates the KV index if needed, and registers both store types.
- Filer methods: `InsertEntry`, `UpdateEntry`, `FindEntry`, `DeleteEntry`, `DeleteFolderChildren`, `ListDirectoryEntries`, and unsupported `ListDirectoryPrefixedEntries`.
- Search helpers: `listSorter`, `search`, `searchAfter`, `deleteIndex`, `deleteEntry`, and `getIndex`.

## Control Flow and State
Insert computes the target index from the path, sets parent id to MD5 of the directory, sets document id to MD5 of full path, marshals `ESEntry`, and indexes it. ES8 additionally stores the id in an indexed field because `_id` fielddata is disallowed. Find does a direct get by id. Delete removes the entry and, when deleting a top-level directory, attempts to delete the corresponding bucket index. Folder deletion lists child entries and deletes them one by one. Listing refreshes the index, creates it if absent, searches by parent id, sorts descending by `_id` or `Id.keyword`, and pages with `search_after`.

## State and Persistence Behavior
Entry metadata persists as JSON documents that include the full `filer.Entry`. Index selection is based on the first path segment. The root/top-level index is `.seaweedfs_`; deeper paths use `.seaweedfs_<top-level>`. KV data lives in `.seaweedfs_kv_entries`.

## Dependencies and Integration Points
It uses `github.com/olivere/elastic/v7`, `jsoniter`, SeaweedFS filer store registration, `filer.Entry`, `filer_pb.ErrNotFound`, and `weed_util.FullPath`/hash helpers.

## Risks and Edge Cases
- Prefix directory listing is unsupported.
- Sorting by MD5 document id does not obviously match filename lexical order, so pagination/list order should be scrutinized.
- `SearchAfter(after)` passes a string hash and must match sort-field values, especially for ES8 `Id.keyword`.
- `DeleteFolderChildren` is iterative and can be costly for large folders.
- `getIndex` lowercases top-level names, which can merge differently cased names.
- The build tag means this code may receive less routine CI coverage.

## Test Signals
Tests should run under the `elastic` build tag against ES7/ES8, covering index creation, insert/find/delete, top-level directory deletion, listing pagination/order, missing index behavior, and KV operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/elastic/v7/elastic_store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/elastic/v7/elastic_store_kv.go -->
# sources/distributed-fs/seaweedfs/weed/filer/elastic/v7/elastic_store_kv.go

## Purpose
This build-tagged file implements KV operations for the Elasticsearch filer store using a dedicated KV index.

## Important APIs, Types, and Functions
- `KvPut` marshals `ESKVEntry{Value}` and indexes it by raw key string.
- `KvGet` gets a document by raw key string and unmarshals the value.
- `KvDelete` deletes by raw key string and treats `"deleted"` and `"not_found"` as success.

## Control Flow and State
KV put writes to `indexKV` using `indexType` and document id `string(key)`. KV get maps Elasticsearch not found to `filer.ErrKvNotFound`; other failures are logged and also returned as not found. Delete checks the delete result and returns an error for unexpected outcomes.

## State and Persistence Behavior
Values persist as JSON documents with a binary field under `.seaweedfs_kv_entries`, whose mapping disables normal indexing and marks `Value` as binary.

## Dependencies and Integration Points
It depends on the `elastic` build tag, olivere Elasticsearch client, jsoniter, glog, and SeaweedFS KV error semantics.

## Risks and Edge Cases
- Raw binary keys are converted to string document ids and may not be safe or portable for all byte sequences.
- Non-not-found get errors are collapsed to `ErrKvNotFound`, which hides backend failures.
- `Type(indexType)` remains in use for ES8 compatibility via the v7 client and may be sensitive to server version.

## Test Signals
Build-tagged integration tests should cover binary keys, missing keys, overwrite, delete not found, and backend error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/elastic/v7/elastic_store_kv.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/empty_folder_cleanup/cleanup_queue.go -->
# sources/distributed-fs/seaweedfs/weed/filer/empty_folder_cleanup/cleanup_queue.go

## Purpose
This file implements a thread-safe, deduplicated, time-ordered queue for folders that may need empty-folder cleanup.

## Important APIs, Types, and Functions
- `CleanupQueue` owns a mutex, a doubly linked list of `queueItem`, a map from folder path to list element, and max size/age thresholds.
- `queueItem` stores folder, triggering child name, and queue time.
- Public methods: `NewCleanupQueue`, `Add`, `Remove`, `ShouldProcess`, `Pop`, `PopOlderThan`, `Peek`, `Len`, `Contains`, `Clear`, and `OldestAge`.
- Internal helpers: `insertSorted` and `shouldProcessLocked`.

## Control Flow and State
`Add` deduplicates by folder. New folders are inserted in event-time order. Existing folders are updated only if the new event time is later, in which case the list element is removed and reinserted. Processing can be triggered by size or age, but the cleaner primarily uses `PopOlderThan` to avoid deleting folders before a delay has elapsed. All operations hold the queue mutex.

## State and Persistence Behavior
The queue is in-memory only. It tracks pending cleanup candidates and does not survive process restart.

## Dependencies and Integration Points
It is used by `EmptyFolderCleaner` to queue delete-event parent folders, cancel cleanup on create events, process aged items, and skip evicting cache entries still queued.

## Risks and Edge Cases
- Ordering is by event time, not enqueue wall-clock time; incorrect event timestamps can delay or accelerate cleanup.
- Duplicate older events are ignored, preserving newer trigger information.
- `ShouldProcess` uses `time.Since`, so tests and behavior depend on wall clock.
- The queue exposes `maxAge` as a field used directly by the cleaner, coupling internals across files in the same package.

## Test Signals
`cleanup_queue_test.go` covers add/update, out-of-order insert, duplicate older/newer events, remove, pop, peek, contains, size/age processing triggers, clear, oldest age, ordering, and concurrent access smoke testing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/empty_folder_cleanup/cleanup_queue.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/empty_folder_cleanup/cleanup_queue_test.go -->
# sources/distributed-fs/seaweedfs/weed/filer/empty_folder_cleanup/cleanup_queue_test.go

## Purpose
This file tests the `CleanupQueue` data structure used by empty-folder cleanup.

## Important APIs, Types, and Functions
Test functions cover `Add`, out-of-order add, duplicate older/newer events, `Remove`, `Pop`, `Peek`, `Contains`, `ShouldProcess`, `Clear`, `OldestAge`, ordering, and concurrent operations.

## Control Flow and State
The tests construct queues with controlled max sizes and ages, add synthetic folder paths with explicit times, and verify list order by popping. The concurrency test runs goroutines for add, remove, pop, and read methods to catch panics or map/list inconsistencies.

## State and Persistence Behavior
No persistence. The tests validate in-memory queue invariants: deduplication map and linked-list order stay synchronized.

## Dependencies and Integration Points
It depends only on Go's `testing` and `time` packages and the cleanup queue implementation.

## Risks and Edge Cases
- The concurrent test is a smoke test and does not assert a final deterministic state.
- Time-based tests use `time.Now`/`time.Since`, so very slow or skewed test environments could affect boundary assertions.

## Test Signals
These tests give strong signal for queue ordering and deduplication behavior. They do not directly test integration with `EmptyFolderCleaner`, which is covered separately.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/empty_folder_cleanup/cleanup_queue_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/empty_folder_cleanup/empty_folder_cleaner.go -->
# sources/distributed-fs/seaweedfs/weed/filer/empty_folder_cleanup/empty_folder_cleaner.go

## Purpose
This file implements asynchronous deletion of implicit empty folders in bucket paths. It listens to create/delete events, queues possibly empty parent folders, delays cleanup, verifies ownership and bucket policy, checks actual emptiness, preserves explicit directory markers, deletes empty metadata, and eagerly cascades cleanup to parent folders.

## Important APIs, Types, and Functions
- Constants define default count check limit, cache expiry, queue size/age, and processor sleep.
- `FilerOperations` abstracts the filer methods needed by the cleaner.
- `folderState` caches rough counts and last add/delete/check times.
- `bucketCleanupPolicyState` caches bucket policy lookup results.
- `EmptyFolderCleaner` holds filer ops, lock ring, host identity, caches, cleanup queue, configuration, enabled flag, and stop channel.
- Constructor and controls: `NewEmptyFolderCleaner`, `SetEnabled`, `IsEnabled`, `Stop`, `GetPendingCleanupCount`, and `GetCachedFolderCount`.
- Event and processing methods: `OnDeleteEvent`, `OnCreateEvent`, `cleanupProcessor`, `processCleanupQueue`, and `executeCleanup`.
- Helpers: `ownsFolder`, `countItems`, `deleteFolder`, `getBucketCleanupPolicy`, `autoRemoveEmptyFoldersEnabled`, `isUnderPath`, `isUnderBucketPath`, `cacheEvictionLoop`, and `evictStaleCacheEntries`.

## Control Flow and State
Construction starts background loops for cache eviction and queue processing. Delete events outside the bucket path or owned by another filer are ignored. Owned delete events decrement a rough count and enqueue the directory only if the rough count suggests it may be empty. Create events increment tracked counts and remove the directory from the queue. The processor periodically pops only items older than the queue delay, then `executeCleanup` rechecks enabled state, cached count, event ordering, ownership, bucket policy, actual item count, and explicit directory marker status before deleting. After deleting a folder, it removes cached state and recursively attempts the parent to avoid per-level delay.

## State and Persistence Behavior
Cleaner state is in-memory: rough count cache, bucket policy cache, and queue. Persistent effects are calls to `DeleteEntryMetaAndData` for empty implicit folder metadata. Bucket policy is read from bucket attributes using `s3_constants.ExtAllowEmptyFolders`; missing/empty/non-true values enable automatic cleanup, while `"true"` preserves empty folders.

## Dependencies and Integration Points
It integrates with SeaweedFS lock ring ownership, filer metadata APIs, bucket path extraction, S3 extended attributes, `filer_pb.ErrNotFound`, and glog. It is intended for multi-filer deployments where consistent hashing prevents duplicate cleaners from acting on the same folder.

## Risks and Edge Cases
- `Stop` closes `stopCh` unconditionally; calling it twice would panic.
- Recursive `executeCleanup` can walk many parent levels synchronously.
- Cached rough counts are approximate and rely on final `CountDirectoryEntries` for correctness.
- Policy cache can delay recognition of bucket attribute changes until expiry.
- `autoRemoveEmptyFoldersEnabled` has inverted semantics relative to `ExtAllowEmptyFolders`: `"true"` disables cleanup.
- The cleaner uses background goroutines immediately; tests often construct structs manually to avoid goroutines.
- Lock-ring ownership can change between queue and execution, so recheck is necessary and present.

## Test Signals
`empty_folder_cleaner_test.go` covers path filtering, bucket-depth filtering, policy interpretation, ownership across rings, create cancellation, delete deduplication, disabled cleaner behavior, directory deletion events, cached count updates, stop cleanup, cache eviction, queued-item eviction protection, queue order, aged-only processing, policy-disabled skip, and explicit directory marker preservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/empty_folder_cleanup/empty_folder_cleaner.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/empty_folder_cleanup/empty_folder_cleaner_test.go -->
# sources/distributed-fs/seaweedfs/weed/filer/empty_folder_cleanup/empty_folder_cleaner_test.go

## Purpose
This file tests `EmptyFolderCleaner` helper logic, event handling, ownership, cache behavior, policy handling, queue processing, and deletion decisions.

## Important APIs, Types, and Functions
- `mockFilerOps` implements `FilerOperations` with configurable function fields.
- Tests cover `isUnderPath`, `isUnderBucketPath`, `autoRemoveEmptyFoldersEnabled`, `ownsFolder`, create/delete event handling, disabled behavior, cached counts, stop, cache eviction, FIFO/time ordering, aged processing, bucket-policy skip, and directory-marker preservation.

## Control Flow and State
Tests often construct `EmptyFolderCleaner` structs directly with a lock ring, host, maps, cleanup queue, and stop channel. This avoids background goroutines unless testing constructor-level behavior is needed. Mock filer functions record deletions or provide counts/attrs/marker status so tests can drive `executeCleanup` branches.

## State and Persistence Behavior
No external persistence. Tests verify that in-memory caches and queues are updated and that persistent deletion would be requested only for eligible implicit empty folders.

## Dependencies and Integration Points
Tests depend on `lock_manager.LockRing`, `pb.ServerAddress`, S3 constants, and `util.FullPath`. They validate integration assumptions around consistent-hash ownership and bucket cleanup policy attributes.

## Risks and Edge Cases
- Some tests call `Stop` on manually constructed cleaners; they are valid because `stopCh` is initialized, but double stop remains untested.
- Ownership tests may skip one branch if a non-owned folder cannot be found in the sample.
- There is limited coverage for errors from `CountDirectoryEntries`, `DeleteEntryMetaAndData`, `GetEntryAttributes`, and `IsDirectoryKeyObject`.

## Test Signals
The tests provide good signal for race-prevention behavior: create cancels cleanup, only aged items are processed, cache eviction skips queued folders, explicit directory markers are preserved, and policy `"true"` disables auto-removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/empty_folder_cleanup/empty_folder_cleaner_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/entry.go -->
# sources/distributed-fs/seaweedfs/weed/filer/entry.go

## Purpose
This file defines SeaweedFS filer metadata objects: file attributes and entries. It provides conversion to and from protobuf entries and helper methods for size, timestamps, cloning, S3 expiration/version markers, and full-entry wrappers.

## Important APIs, Types, and Functions
- `Attr` stores times, mode, ownership, MIME, TTL, user/group names, symlink target, MD5, file size, device, and inode.
- `Entry` embeds `util.FullPath` and `Attr`, plus extended metadata, chunks, hard-link fields, inline content, remote entry, quota, and WORM timestamp.
- Methods include `Attr.IsDirectory`, `Entry.Size`, `Entry.Timestamp`, `Entry.ShallowClone`, `ToProtoEntry`, `ToExistingProtoEntry`, `ToProtoFullEntry`, `GetChunks`, `IsExpireS3Enabled`, `IsS3Versioning`, and `GetS3ExpireTime`.
- Conversion functions: `FromPbEntryToExistingEntry`, `FromPbEntry`, and `maxUint64`.

## Control Flow and State
`ToExistingProtoEntry` populates a protobuf entry, reusing existing attribute storage if present. `FromPbEntryToExistingEntry` decodes protobuf attributes and assigns chunks, extended metadata, hard links, content, remote entry, quota, computed file size, and WORM timestamp. `Size` returns the maximum of chunk total size, recorded file size, and inline content length.

## State and Persistence Behavior
`Entry` is the in-memory representation that filer stores serialize and persist. Chunks reference volume-server data; extended fields carry S3 and SeaweedFS metadata; TTL and WORM fields influence lifecycle semantics.

## Dependencies and Integration Points
It integrates with `filer_pb.Entry`, `filer_pb.FullEntry`, S3 constants, `util.FullPath`, and helper functions such as `EntryAttributeToPb`, `PbToEntryAttribute`, `FileSize`, and `TotalSize` defined elsewhere.

## Risks and Edge Cases
- `ShallowClone` shares slices, maps, and pointers, so callers must not mutate shared fields unexpectedly.
- `Timestamp` returns creation time for directories and modification time for files.
- `Size` can report inline content length or file-size metadata even when chunks differ.
- S3 expiration falls back from mtime to crtime and uses TTL seconds directly.

## Test Signals
Tests in this set indirectly cover entry serialization through `entry_codec_atime_test.go`, backend stores, and chunk tests. Additional tests should cover shallow clone sharing, size precedence, proto reuse, and S3 marker helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/entry.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/entry_codec.go -->
# sources/distributed-fs/seaweedfs/weed/filer/entry_codec.go

## Purpose
This file implements efficient serialization/deserialization of filer entries to protobuf bytes and conversion between `Entry.Attr` and protobuf `FuseAttributes`.

## Important APIs, Types, and Functions
- `pbEntryPool` reuses `filer_pb.Entry` objects with preallocated attributes.
- `resetPbEntry` and `resetFuseAttributes` clear pooled protobuf objects before reuse.
- `EncodeAttributesAndChunks` marshals an entry to bytes.
- `DecodeAttributesAndChunks` unmarshals bytes into an existing entry.
- Attribute conversions: `EntryAttributeToPb`, `EntryAttributeToExistingPb`, `PbToEntryAttribute`, `atimeSecondsForPb`, and `atimeNanosForPb`.
- Equality helpers: `EqualEntry` and `eq`.

## Control Flow and State
Encoding gets a pooled protobuf entry, fills it through `ToExistingProtoEntry`, marshals it, copies the returned bytes to avoid retaining mutable pooled memory, resets the message, and returns it to the pool. Decoding gets a pooled message, unmarshals into it, copies fields into the target entry, resets, and returns it. Attribute conversion preserves nanoseconds for mtime, ctime, and atime; missing ctime falls back to mtime and missing atime falls back to mtime.

## State and Persistence Behavior
The protobuf bytes produced here are the metadata blobs persisted by filer stores. The fallback behavior for ctime/atime preserves compatibility with older blobs that lack those fields.

## Dependencies and Integration Points
It uses `google.golang.org/protobuf/proto`, `filer_pb.Entry`, `filer_pb.FuseAttributes`, and conversion helpers in `entry.go`. All filer stores call these methods before storing and after loading metadata.

## Risks and Edge Cases
- Pool reuse requires complete reset; missed fields could leak between entries.
- The marshaled data copy is intentional and should not be removed without proving protobuf marshal ownership.
- `EqualEntry` compares protobuf-converted attributes and selected entry fields, but not every field from `Entry` such as full path.
- Atime zero semantics distinguish all-zero missing atime from sub-second epoch atime using `AtimeNs`.

## Test Signals
`entry_codec_atime_test.go` verifies atime round trip, fallback to mtime, and sub-second epoch preservation. More tests should cover pool reset isolation and equality behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/entry_codec.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/entry_codec_atime_test.go -->
# sources/distributed-fs/seaweedfs/weed/filer/entry_codec_atime_test.go

## Purpose
This file tests access-time handling in filer entry attribute protobuf conversion.

## Important APIs, Types, and Functions
- `TestEntryCodec_AtimeRoundTrip` verifies seconds and nanoseconds are encoded and decoded.
- `TestEntryCodec_AtimeZeroFallsBackToMtime` verifies older/missing atime fields default to mtime.
- `TestEntryCodec_AtimeSubSecondEpochPreserved` verifies `Atime=0` with nonzero `AtimeNs` is treated as a valid timestamp.

## Control Flow and State
Tests construct `Entry` or `FuseAttributes`, convert through `EntryAttributeToPb` and `PbToEntryAttribute`, and compare exact timestamps.

## State and Persistence Behavior
The tests protect compatibility of persisted metadata blobs, especially distinguishing missing atime from an actual timestamp in the first second of the Unix epoch.

## Dependencies and Integration Points
They use `filer_pb.FuseAttributes`, `util.FullPath`, and the conversion functions in `entry_codec.go`.

## Risks and Edge Cases
The sub-second epoch case is subtle because protobuf `Atime` seconds can be zero for both missing values and real timestamps; preserving `AtimeNs` prevents incorrect fallback.

## Test Signals
These are focused regression tests for atime serialization and backward compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/entry_codec_atime_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/etcd/etcd_store.go -->
# sources/distributed-fs/seaweedfs/weed/filer/etcd/etcd_store.go

## Purpose
This file implements the SeaweedFS filer store using etcd v3 as the metadata backend. It maps each directory/name pair to a lexicographically ordered key and stores encoded entry metadata as the value.

## Important APIs, Types, and Functions
- `EtcdStore` holds the etcd client, key prefix, and timeout.
- `Initialize` reads endpoints, credentials, key prefix, timeout, and TLS files.
- `initialize` creates the client, verifies connectivity with `Status`, and stores the client.
- Store methods: `InsertEntry`, `UpdateEntry`, `FindEntry`, `DeleteEntry`, `DeleteFolderChildren`, `ListDirectoryPrefixedEntries`, `ListDirectoryEntries`, and `Shutdown`.
- Key helpers: `genKey`, `genDirectoryKeyPrefix`, and `getNameFromKey`.

## Control Flow and State
Initialization parses timeout and optional TLS CA/client cert/key into an etcd TLS config, then connects and checks status. Insert/update encode metadata, optionally gzip large chunk metadata, and `Put` under `etcdKeyPrefix + dir + NUL + name`. Find gets that key and decodes the first KV. Delete removes the key. Folder deletion deletes all keys with the directory prefix. Listing computes a prefix and optional start key, uses an etcd range ending at `GetPrefixRangeEnd`, applies `limit+1`, decodes values, skips start when exclusive, and invokes `eachEntryFunc`.

## State and Persistence Behavior
Metadata persists as etcd keys. The NUL separator makes keys sort by directory then name. `etcdKeyPrefix` namespaces all keys. There is no explicit transaction implementation and no TTL handling in this file.

## Dependencies and Integration Points
It depends on `go.etcd.io/etcd/client/v3`, etcd TLS transport helpers, SeaweedFS `filer.Entry` encoding, `filer_pb.ErrNotFound`, and `weed_util.FullPath`.

## Risks and Edge Cases
- Values are stored via `string(meta)`, which preserves bytes in Go but relies on etcd API accepting arbitrary string bytes.
- `getNameFromKey` is called with full etcd keys including prefix; because it scans from the last NUL, prefix contents are safe unless names contain NUL.
- No transaction support.
- Range listing assumes etcd key ordering matches filename ordering after the directory prefix.
- Connection status only checks the first endpoint.

## Test Signals
`etcd_store_test.go` documents a disabled integration test path requiring docker and `make test_etcd`. Useful tests should cover CRUD, listing, prefix listing, delete folder children, TLS config, and key-prefix namespacing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/etcd/etcd_store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/etcd/etcd_store_kv.go -->
# sources/distributed-fs/seaweedfs/weed/filer/etcd/etcd_store_kv.go

## Purpose
This file implements SeaweedFS KV operations for the etcd backend.

## Important APIs, Types, and Functions
- `KvPut` stores a raw key/value pair under the configured etcd key prefix.
- `KvGet` retrieves the value or returns `filer.ErrKvNotFound`.
- `KvDelete` deletes the key.

## Control Flow and State
Operations concatenate `store.etcdKeyPrefix` with `string(key)` and call etcd `Put`, `Get`, or `Delete`. Get returns the first KV value if present.

## State and Persistence Behavior
KV state persists directly as etcd keys separate from filer metadata only by caller-provided key namespace and the shared prefix. Values are raw bytes.

## Dependencies and Integration Points
It uses the etcd client in `EtcdStore` and the SeaweedFS KV error contract.

## Risks and Edge Cases
- Raw key bytes are converted to string and concatenated with the same prefix used for metadata, so namespace collisions depend on callers.
- Delete of a missing key is treated as success.
- No transaction or compare-and-swap semantics are exposed.

## Test Signals
Tests should cover put/get/delete, missing key, binary keys, prefix isolation, and backend errors. No enabled local KV tests are listed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/etcd/etcd_store_kv.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/etcd/etcd_store_test.go -->
# sources/distributed-fs/seaweedfs/weed/filer/etcd/etcd_store_test.go

## Purpose
This file documents an etcd filer store integration test hook.

## Important APIs, Types, and Functions
- `TestStore` contains a disabled `if false` block that would initialize `EtcdStore` against `localhost:2379` and run `store_test.TestFilerStore`.

## Control Flow and State
As written, the test always passes without executing the store test. The comment instructs developers to run `make test_etcd` under the docker folder to set up a local environment.

## State and Persistence Behavior
No state is touched unless a developer edits/enables the block.

## Dependencies and Integration Points
The intended test uses `filer/store_test` shared store conformance tests and an external etcd service.

## Risks and Edge Cases
Because the integration test is disabled, regressions in etcd CRUD/list behavior may not be caught by default `go test`.

## Test Signals
The file is a weak signal in normal CI and a pointer to manual/docker-backed integration testing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/etcd/etcd_store_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filechunk_group.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filechunk_group.go

## Purpose
This file implements `ChunkGroup`, the read-side structure that organizes file chunks into fixed-size sections, resolves chunk manifests, supports zero-fill holes, parallel section reads, read-ahead tuning, and seek-data/seek-hole style queries.

## Important APIs, Types, and Functions
- `ChunkGroup` stores a volume lookup function, section map, section lock, `ReaderCache`, and concurrency setting.
- `NewChunkGroup` caps/defaults concurrency, creates a reader cache, and calls `SetChunks`.
- `GetPrefetchCount` derives read-ahead count from concurrency.
- `AddChunk` incrementally adds a chunk to affected sections.
- `ReadDataAt`, `readDataAtSequential`, and `readDataAtParallel` read file data into a buffer.
- `sectionReadResult` aggregates parallel read results.
- `SetChunks` resolves manifest chunks and rebuilds the section map.
- `SearchChunks` and `doSearchChunks` implement data/hole search using section visibility.

## Control Flow and State
Chunks are mapped to all 64 MiB sections they overlap. Reads reject offsets at or beyond file size with `io.EOF`, then select sequential or parallel mode based on section count and concurrency. Missing sections are zero-filled up to file size. Existing sections delegate to `FileChunkSection.readDataAt`, returning bytes read, max modified timestamp, and errors. Parallel reads use `errgroup` with a limit, write to disjoint buffer slices, and aggregate results after all goroutines finish. `SetChunks` resolves manifest chunks before building fresh sections.

## State and Persistence Behavior
`ChunkGroup` is in-memory. It reads persisted chunk metadata from `filer_pb.FileChunk` entries and fetches actual chunk data via volume-server lookup/read functions.

## Dependencies and Integration Points
It integrates with `FileChunkSection`, chunk manifest resolution, `ReaderCache`, `chunk_cache.ChunkCache`, volume lookup via `wdclient`, and file metadata from protobuf chunks.

## Risks and Edge Cases
- Parallel result writes rely on each goroutine owning a disjoint buffer slice and result index.
- `errgroup` cancels context on first non-EOF error, which can reduce later read results.
- Missing sections zero-fill, so sparse-file semantics depend on file size boundaries.
- `DataStartOffset` currently returns the offset even when it is before visible data, which should be checked against intended `SEEK_DATA` behavior.
- Manifest resolution in `SetChunks` uses `context.Background`, so construction is not caller-cancellable.

## Test Signals
`filechunk_group_test.go` covers empty group reads, EOF behavior, error-masking regression intent, and context propagation smoke tests. It has a placeholder table for `doSearchChunks`, so seek behavior lacks substantive tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filechunk_group.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filechunk_group_test.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filechunk_group_test.go

## Purpose
This file tests selected `ChunkGroup` read and search behavior, especially error handling and context propagation.

## Important APIs, Types, and Functions
- `TestChunkGroup_ReadDataAt_ErrorHandling` covers empty group zero-fill reads, EOF past file size, issue-style error masking expectations, and cancelled/timeout contexts.
- `TestChunkGroup_SearchChunks_Cancellation` checks cancelled/timeout contexts for empty search.
- `TestChunkGroup_doSearchChunks` is a table-driven skeleton with no cases.

## Control Flow and State
Tests construct `ChunkGroup` instances with empty section maps and call read/search methods with controlled file sizes, offsets, and buffers. Assertions focus on byte counts, zero timestamps, EOF, and lack of panic or unexpected context errors.

## State and Persistence Behavior
No persistence. The tests validate in-memory sparse reads against no-section state.

## Dependencies and Integration Points
It uses `testify/assert`, Go context/time/io/errors, and `ChunkGroup` methods.

## Risks and Edge Cases
- The tests do not create real sections, readers, or failing chunk fetches, so they do not fully prove the error-masking scenario described in comments.
- Seek-data/hole behavior is effectively untested because the table has no cases.
- Context cancellation is only a smoke test for empty groups where no network reads occur.

## Test Signals
Good signal for EOF and zero-fill behavior; weak signal for real chunk read errors, parallel reads, manifest chunks, and seek behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filechunk_group_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filechunk_manifest.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filechunk_manifest.go

## Purpose
This file implements chunk manifest handling for SeaweedFS filer entries. It can detect, separate, resolve, fetch, retry-read, create, and persist manifest chunks that compact large chunk lists into serialized manifest objects.

## Important APIs, Types, and Functions
- `ManifestBatch` controls how many data chunks are merged into one manifest.
- `bytesBufferPool` reuses buffers for manifest fetches.
- Detection/separation: `HasChunkManifest` and `SeparateManifestChunks`.
- Resolution: `ResolveChunkManifest`, `ResolveOneChunkManifest`, `fetchWholeChunk`, `fetchChunkRange`, and `retriedStreamFetchChunkData`.
- Creation: `MaybeManifestize`, `doMaybeManifestize`, and `mergeIntoManifest`.
- `SaveDataAsChunkFunctionType` abstracts saving serialized manifest data as a chunk.

## Control Flow and State
Resolution skips chunks outside the requested byte range, passes data chunks through, fetches manifest chunks from volume servers, unmarshals `FileChunkManifest`, runs post-deserialization fixups, and recurses into nested manifests. Fetch retries across volume URLs and with increasing wait times, checking context cancellation before requests, during streaming callbacks, and while sleeping. Manifestizing refuses to pack SSE-encrypted chunks, separates existing manifests from data chunks, merges full batches through `mergeIntoManifest`, and leaves remainders as regular chunks. `mergeIntoManifest` serializes chunk metadata, saves it as a chunk, marks the returned chunk as a manifest, and sets its offset/size coverage.

## State and Persistence Behavior
Manifest chunks persist as regular chunks whose payload is a protobuf `FileChunkManifest`. Entry metadata stores only the manifest chunk reference, offset, size, and `IsChunkManifest` flag. Resolution fetches persisted manifest payloads to reconstruct data chunks.

## Dependencies and Integration Points
It depends on volume-server lookup functions, JWT generation, HTTP chunk reads, protobuf serialization, `filer_pb` chunk serialization hooks, chunk compaction logic, and save callbacks used by filer write paths.

## Risks and Edge Cases
- Recursive manifest resolution can be expensive or fail if any manifest chunk is unavailable.
- Retried streaming tracks `totalWritten` to avoid duplicate bytes across retries; callback/write errors need careful handling.
- `MaybeManifestize` intentionally skips all SSE chunks to preserve encryption metadata.
- `doMaybeManifestize` returns `dataChunks` on merge error, which may drop existing manifest chunks from the returned value.
- Context cancellation is handled in fetch loops, but `ResolveChunkManifest` itself processes manifests sequentially.

## Test Signals
`filechunk_manifest_test.go` covers manifest grouping, round trip serialization, resolved overlapping manifest compaction, minus/garbage behavior, remainder handling, multi-generation compaction, and bloat detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filechunk_manifest.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filechunk_manifest_test.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filechunk_manifest_test.go

## Purpose
This file tests chunk manifest creation, serialization round trips, manifest resolution using an in-memory store, overlap compaction, garbage identification, remainder handling, and bloat detection.

## Important APIs, Types, and Functions
- `TestDoMaybeManifestize` tests grouping behavior with mock merge.
- `testManifestStore` provides in-memory `saveFunc`, `resolve`, and `resolveAll`.
- `testChunk` creates protobuf chunks for tests.
- Tests include `TestManifestRoundTripPreservesChunks`, `TestCompactResolvedOverlappingManifests`, `TestDoMinusChunksWithResolvedManifests`, `TestManifestizeSmallBatchWithRemainder`, `TestCompactMultipleOverlappingManifestGenerations`, and `TestManifestBloatDetection`.

## Control Flow and State
Tests create chunk lists, manifestize them with either a mock merge or real `mergeIntoManifest`, resolve manifest payloads from the in-memory store, and assert file ids, offsets, sizes, timestamps, survivor chunks, garbage chunks, and merge-trigger expectations.

## State and Persistence Behavior
The in-memory manifest store simulates volume-server persistence of serialized manifest protobuf payloads without external services.

## Dependencies and Integration Points
It uses protobuf marshal/unmarshal, `filer_pb.AfterEntryDeserialization`, compaction helpers such as `CompactFileChunks` and `DoMinusChunks`, and testify assertions.

## Risks and Edge Cases
- Tests exercise manifest metadata but not actual network fetch/retry logic in `ResolveOneChunkManifest`.
- SSE skip behavior in `MaybeManifestize` is not covered here.
- Bloat detection test computes expected merge conditions but does not call a production merge-decision function in the visible code.

## Test Signals
Strong signal for manifest serialization and compaction semantics; moderate gaps around network resolution, nested recursion failures, context cancellation, and encrypted chunks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filechunk_manifest_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filechunk_section.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filechunk_section.go

## Purpose
This file defines `FileChunkSection`, the per-64-MiB section structure used by `ChunkGroup` to track overlapping chunks, compute visible intervals, create chunk views, read data, and locate data/hole boundaries.

## Important APIs, Types, and Functions
- `SectionSize` is 64 MiB and `SectionIndex` identifies section numbers.
- `FileChunkSection` stores section index, raw chunks, visible intervals, chunk views, a `ChunkReadAt`, a lock, and preparation flag.
- `NewFileChunkSection` constructs a section.
- `addChunk` adds a chunk and incrementally updates visibility/views.
- `removeGarbageChunks` removes chunks made obsolete by newer visibility.
- `setupForRead` lazily computes visible intervals, removes garbage chunks, builds chunk views, and creates a reader.
- `readDataAt`, `DataStartOffset`, and `NextStopOffset` serve reads and seek helpers.

## Control Flow and State
Chunks are clipped to section bounds before merging into visible intervals. The first preparation computes visible intervals and chunk views if they do not already exist, creates a `ChunkReadAt` through the group's reader cache, and records the current file size. Later preparations update reader file size. Reads lock for preparation then use the reader under RLock. Seek helpers walk visible intervals to return candidate data or hole offsets.

## State and Persistence Behavior
The section is in-memory derived state from persisted chunk metadata. It may drop garbage chunks from its local list after visibility analysis but does not delete persisted chunks itself.

## Dependencies and Integration Points
It depends on interval-list helpers (`readResolvedChunks`, `MergeIntoVisibles`, `FindGarbageChunks`, `SeparateGarbageChunks`, `ViewFromVisibleIntervals`, `MergeIntoChunkViews`) and `NewChunkReaderAtFromClient`. `ChunkGroup` owns sections and calls these methods.

## Risks and Edge Cases
- Incremental `addChunk` must keep `visibleIntervals`, `chunkViews`, and `chunks` consistent.
- `setupForRead` closes any old reader when garbage separation changes chunks.
- `DataStartOffset` appears to return the requested offset even if the next visible interval starts later; intended seek-data semantics should be verified.
- Locks prevent concurrent mutation/read races within a section, but callers must avoid deadlock with group-level locks.

## Test Signals
No direct tests are listed. Behavior is indirectly exercised by chunk group and manifest tests, but section interval merging, garbage removal, and seek helpers need focused coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filechunk_section.go -->
