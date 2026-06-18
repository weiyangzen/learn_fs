<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/dbstore/common/dbstore.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/dbstore/common/dbstore.cc

## Purpose
This file implements the common RGW DBStore backend behavior declared in `dbstore.h`. It provides backend-independent operation routing, user/account/bucket lifecycle methods, object listing, object metadata/data read and write paths, versioned delete behavior, lifecycle entry/head storage helpers, and a background GC thread that removes stale tail object data. Concrete database backends, such as SQLite, supply the actual `DBOp::Execute()` implementations and operation initialization.

## Important APIs, Types, And Functions
- `DB::Initialize()` configures RGW logging, opens the backend database with `openDB()`, and calls `InitializeDBOps()`.
- `DB::Destroy()` stops GC, closes the database, deletes per-bucket `ObjectOp` dispatch objects, and clears the static object operation map.
- `DB::getDBOp()` maps string operation names to `DBOps` or per-bucket `ObjectOp` operation objects.
- `DB::InitializeParams()` seeds `DBOpParams` with `CephContext` and table names.
- `DB::ProcessOp()` resolves an operation by name and invokes its `Execute()` method.
- User/account methods implement `get_user()`, `store_user()`, `remove_user()`, `list_users()`, `get_account()`, `store_account()`, and `remove_account()`.
- Bucket methods implement `get_bucket_info()`, `create_bucket()`, `remove_bucket()`, `list_buckets()`, and `update_bucket()`.
- `DB::Bucket::List::list_objects()` performs ordered object listing, version filtering, delimiter/common-prefix handling, truncation, and next-marker selection.
- `DB::Object` methods implement object state lookup, omap operations, multipart part lists, attr updates, storage-class transition, version listing, read prepare/read/iterate, write prepare/write data/write metadata, and delete/delete-marker behavior.
- `DB::raw_obj` reads/writes rows in the object data table through `GetObjectData` and `PutObjectData`.
- Lifecycle helpers implement `get_entry()`, `get_next_entry()`, `set_entry()`, `list_entries()`, `rm_entry()`, `get_head()`, and `put_head()`.
- `DB::GC::entry()` periodically lists buckets and calls `delete_stale_objs()` to remove object data rows whose head object no longer exists.

## Control Flow
Backend startup calls `Initialize()`, which opens the database handle and initializes concrete operation objects. High-level methods create a local `DBOpParams`, call `InitializeParams()`, populate the relevant `params.op.*` fields, and dispatch a string operation through `ProcessOp()`. For object operations, `getDBOp()` first looks up the bucket name in the static `objectmap`; bucket creation/loading must therefore initialize per-bucket `ObjectOp` instances before object requests can succeed.

User and account stores use optimistic version checks: they read current state, compare provided read versions, initialize or increment `obj_version`, then call insert operations. Bucket creation reads by name, generates a bucket id/marker with `next_bucket_id()` if needed, fills `RGWBucketInfo`, and inserts the bucket. Bucket update reads current info and attrs, checks version, selects one of `attrs`, `owner`, or `info` update modes, then dispatches `UpdateBucket`.

Object reads call `get_state()`/`get_obj_state()`. If an instance is provided, the exact object is fetched. If no instance is provided, `list_versioned_objects()` selects the most recent version and rejects a top delete marker as `-ENOENT`. `Read::prepare()` applies ETag conditional checks and returns attrs, size, and mtime to the caller. `Read::read()` serves head data from `RGWObjState::data` when possible, otherwise constructs a `raw_obj` and reads tail data. `Read::iterate()` walks chunks through `iterate_obj()` and calls the client callback for each chunk.

Object writes call `Write::prepare()` to choose an object id, then `write_data()` for tail chunks and `write_meta()`/`_do_write_meta()` for metadata and head data. `_do_write_meta()` merges attrs, object retention defaults, manifests, storage class attrs, size/accounted size, owner/category, and version flags before `PutObject`.

Deletes first try to fetch the object. With an explicit version id they physically delete that object row. Without a version id, versioned buckets create a delete marker, suspended buckets delete the current object and create a null-version delete marker, and unversioned/non-main entries are physically deleted. Physical delete also updates tail object data mtimes so the GC thread can later remove rows after a minimum wait.

## State And Persistence
The file persists RGW state through backend `DBOp` tables described in `dbstore.h`: account, user, bucket, object, object data, lifecycle entry, and lifecycle head tables. It keeps process-local state in the static `DB::objectmap`, `max_bucket_id`, object instances, cached object state, and GC markers. Object metadata and optional head data are stored in object table rows; tail data is stored separately by bucket/object/instance/object id/multipart part/part number. Lifecycle state is stored as LC entries and heads keyed by lifecycle index and bucket.

Version state is maintained with Ceph `obj_version` for users/accounts/buckets and with object instance/version fields for objects. Delete markers are represented as object rows with `rgw_bucket_dir_entry::FLAG_DELETE_MARKER`. Tail data cleanup is delayed by mtime to avoid races with readers/writers.

## Dependencies And Integration Points
This file depends on Ceph RGW types from `dbstore.h`, `RGWUserInfo`, `RGWAccountInfo`, `RGWBucketInfo`, `RGWObjState`, `rgw_bucket_dir_entry`, `RGWObjManifest`, lifecycle SAL types, Ceph `bufferlist`, `DoutPrefixProvider`, logging, time utilities, and random id generation helpers. Concrete backend integration is through virtual methods (`openDB()`, `closeDB()`, `InitializeDBOps()`, `InitPrepareParams()`, table creation/listing APIs) and concrete `DBOp::Execute()` implementations.

## Risks And Edge Cases
- `getDBOp()` does not dispatch `InsertAccount`, `RemoveAccount`, or `GetAccount`, although `store_account()`, `remove_account()`, and `get_account()` call those operation names. Unless a subclass overrides routing elsewhere, account operations will fail with "No db_op found".
- `getDBOp()` checks `objectmap` under a mutex but uses the returned `ObjectOp*` after releasing the lock. Concurrent bucket/objectmap deletion can race with operation dispatch.
- `DB::objectmap` is static across all `DB` instances and keyed only by bucket name, so multiple DBStore instances or tenants with the same bucket name can collide.
- `next_bucket_id()` is process-local and not persisted; after restart, generated bucket ids can repeat unless concrete backend reconciliation updates `max_bucket_id`.
- `DB::Object::set_attrs()` uses `if (ret && !state->exists)` after `get_state()`. If `get_state()` fails before setting `state`, this can dereference an invalid pointer.
- `raw_obj::read()` computes `read_bl.length() - ofs` using unsigned arithmetic after no explicit bounds check; offsets beyond available data can underflow.
- `Write::write_data()` computes `len = std::min(end, max_chunk_size)` instead of remaining bytes (`end - write_ofs`), which can overstate later chunk lengths.
- `ListVersionedObjects` is capped at `MAX_VERSIONED_OBJECTS` of 20. Reads/deletes without explicit instance may miss older versions beyond that fixed limit.
- Object listing uses SQL LIKE prefix strings and delimiter post-processing; special SQL wildcard characters in object names/prefixes need correct backend escaping.
- Delete marker creation does not populate all metadata fields as richly as normal writes, so listing/read semantics depend on backend binding defaults.
- GC deletion is eventually consistent and based on a join query plus mtime threshold. It acknowledges possible read/delete races and suggests locks or transactions as future work.
- Lifecycle helpers use `get_def_dpp()` and global DB state rather than caller-provided request context, which can reduce traceability.

## Test Signals
Important tests include initialization failure paths, operation routing for every string op, account CRUD dispatch, user version mismatch handling, bucket create/update/list/remove, object put/read with head and tail data, range reads, iterate callbacks, attr/omap updates, multipart part list updates, versioned and suspended delete semantics, delete marker listing, GC stale tail cleanup, lifecycle entry/head persistence, concurrent objectmap insert/delete versus operations, and restart scenarios for bucket id generation. SQL backend tests should assert generated rows and version fields after each high-level method.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/dbstore/common/dbstore.cc -->
