<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/daos/rgw_sal_daos.h -->
# sources/distributed-fs/ceph/src/rgw/driver/daos/rgw_sal_daos.h

## Purpose
This header declares the RGW Storage Abstraction Layer implementation for the CORTX DAOS backend. It maps Ceph RGW concepts such as users, buckets, objects, zones, multipart uploads, notifications, Lua scripts, placement tiers, and writers onto DAOS/S3 container and object handles. Most behavior is declared here and implemented in companion DAOS source files; the header establishes the class hierarchy, encoded metadata records, and DAOS-specific helper methods used by RGW request code.

## Important APIs, Types, And Functions
- `DaosUserInfo` and `DaosBucketInfo` are encoded persistence records that wrap `RGWUserInfo`, `RGWBucketInfo`, version metadata, mtimes, and attribute maps.
- `DaosUser` implements `StoreUser` for user loading, storing, removal, attributes, stats, usage, and bucket creation.
- `DaosBucket` implements `StoreBucket`; it owns a DAOS bucket/container handle `ds3_bucket_t* ds3b`, bucket ACL state, listing, stats, ownership changes, quota checks, object lookup, multipart discovery, and open/close helpers.
- `DaosObject` implements `StoreObject`; it owns a DAOS object handle `ds3_obj_t* ds3o`, object ACL state, read/delete ops, object state/attrs, copy, transition, OMAP-style methods, and direct DAOS lookup/create/read/write helpers.
- `DaosObject::DaosReadOp` and `DaosObject::DaosDeleteOp` adapt SAL read/delete operation interfaces to DAOS object methods.
- `DaosAtomicWriter` and `DaosMultipartWriter` implement `StoreWriter` for normal object writes and multipart part writes.
- `DaosMultipartUpload` and `DaosMultipartPart` implement RGW multipart metadata and part enumeration/completion/abort contracts.
- `DaosStore` implements `StoreDriver`, exposes backend name `daos`, creates users/buckets/objects/writers/notifications/roles, serves zone and sync interfaces, and owns the root `ds3_t* ds3` handle.
- `DaosZone`, `DaosZoneGroup`, and `DaosPlacementTier` provide minimal zone/placement views backed by Ceph zone structs, with default `STANDARD` storage class setup.
- `DaosLuaManager`, `DaosNotification`, and `MPDaosSerializer` are mostly placeholder implementations that log "not implemented" and return neutral or error values.
- `DAOS_NOT_IMPLEMENTED_LOG()` and `DAOS_NOT_IMPLEMENTED_GDB_BREAK()` provide consistent logging and optional debug breaks for unimplemented paths.

## Control Flow
RGW enters this backend through `DaosStore`, which manufactures SAL objects. User flows call `get_user()` or user lookup helpers, then `DaosUser::load_user()`, `store_user()`, or `create_bucket()`. Bucket flows create or load `DaosBucket`, open DAOS bucket resources with `open()`, list via `list()`, and produce `DaosObject` instances via `get_object()`. Object flows use `DaosObject::load_obj_state()`, `get_read_op()`, `get_delete_op()`, or direct helper methods such as `lookup()`, `create()`, `read()`, and `write()`. Write flows go through `DaosStore::get_atomic_writer()` or multipart upload `get_writer()`, then `prepare()`, repeated `process()`, and `complete()`.

Multipart control flow is represented by `DaosBucket::get_multipart_upload()`, `DaosMultipartUpload::init()`, `list_parts()`, `get_info()`, `get_writer()`, `complete()`, `abort()`, and orphan cleanup. Zone and placement queries route through `DaosStore::get_zone()`, `DaosZone::get_zonegroup()`, and `DaosZoneGroup::get_placement_tier()`. Several optional RGW surfaces, including Lua packages, notifications, append writers, cloud restore, and sync functions, are declared but either stubbed here or likely incomplete in implementation files.

## State And Persistence
DAOS persistence is represented by encoded blobs:
- `DaosUserInfo` stores RGW user info, an object version, and user attrs.
- `DaosBucketInfo` stores bucket info, bucket version, mtime, and bucket attrs.
- `DaosBucket` persists bucket/container state through `ds3_bucket_t` and encoded bucket info returned by `get_encoded_info()`.
- `DaosObject` persists object data and attributes through `ds3_obj_t` and helpers for dirent/attrs, latest-version marking, direct reads/writes, and object state loading.

Version and mtime state is explicit in the encoded records and writer completion paths. ACLs are kept in each `DaosBucket` and `DaosObject` instance as `RGWAccessControlPolicy`. `DaosZone` allocates realm, zone, zone params, and period structs in constructors and initializes a default placement map, but its destructor is defaulted, so ownership and cleanup depend on implementation details outside this header.

## Dependencies And Integration Points
The header depends on DAOS C APIs (`daos.h`, `daos_s3.h`), uuid support, and a broad RGW SAL/RADOS surface: `rgw_sal_store.h`, `rgw_rados.h`, `rgw_putobj_processor.h`, `rgw_multi.h`, `rgw_notify.h`, and `rgw_role.h`. It integrates directly with RGW request handling through the SAL virtual interfaces (`StoreDriver`, `StoreUser`, `StoreBucket`, `StoreObject`, `StoreWriter`, `StoreMultipartUpload`, `StoreZone`, and related interfaces). It also integrates with Ceph encoding macros, `bufferlist`, `DoutPrefixProvider`, `optional_yield`, lifecycle/restore/notification APIs, sync policy handling, OIDC provider interfaces, and RGW role management.

## Risks And Edge Cases
- Many methods are declared in the core SAL surface, but several inline implementations return `DAOS_NOT_IMPLEMENTED_LOG()` or `-ENOENT`; callers need clear feature gating to avoid silently unsupported behavior.
- `DaosZone` uses raw `new` for `RGWRealm`, `RGWZone`, `RGWZoneParams`, and `RGWPeriod` while the destructor is defaulted in this header. If not owned elsewhere, repeated store construction can leak.
- `DaosBucket` copy construction explicitly says deep copy is TODO and resets `ds3b` to null. Cloned buckets may lack open DAOS handles until re-opened.
- `DaosObject(DaosObject& _o) = default` is a non-const copy constructor and will copy raw `ds3o` by value unless implementation resets/guards it elsewhere, which risks double close or stale handles.
- Several compatibility methods return null pointers (`get_rgwlc()`, `get_rgwrestore()`, `get_cr_registry()`) or empty identifiers. RGW subsystems that assume these are present need backend-specific checks.
- `get_new_req_id()` returns the integer result of a not-implemented logger through a `uint64_t` API, so all IDs may become zero until implemented.
- Debug logging redefines `ldpp_dout` under `DEBUG`, which can affect included code if header ordering is surprising.
- DAOS-specific direct handles are public (`ds3`, `ds3b`, `ds3o`), making lifetime discipline dependent on callers and implementation files.

## Test Signals
Useful signals include DAOS backend build coverage, RGW SAL interface compilation after upstream virtual method changes, unit or integration tests for user/bucket/object CRUD, multipart upload complete/abort/list, versioning and latest-version behavior, ACL/attrs persistence, bucket listing with prefixes/delimiters, and unsupported-feature tests that assert clear error returns. Leak/ASAN runs around store/zone/bucket/object construction and clone paths would be valuable because of raw DAOS and zone pointers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/daos/rgw_sal_daos.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/dbstore/CMakeLists.txt -->
# sources/distributed-fs/ceph/src/rgw/driver/dbstore/CMakeLists.txt

## Purpose
This CMake file builds the RGW DBStore backend library, optional SQLite support, DBStore manager library, tests, and a small standalone `dbstore-bin` executable. It defines the common source set, links the RGW dependencies, and wires the SQLite backend into the build when `USE_SQLITE` is enabled.

## Important APIs, Types, And Functions
- `option(USE_SQLITE "Enable SQLITE DB" ON)` controls whether SQLite implementation files and the `sqlite` subdirectory are included.
- `dbstore_srcs` contains common backend logic (`common/dbstore_log.h`, `common/dbstore.h`, `common/dbstore.cc`) plus `config/store.cc`; SQLite mode appends `config/sqlite.cc`, `sqlite/connection.cc`, `sqlite/error.cc`, and `sqlite/statement.cc`.
- `dbstore_lib` is the library for common DBStore implementation and backend-specific SQLite pieces.
- `dbstore` is a static library built from `dbstore_mgr.h` and `dbstore_mgr.cc`, linked against `dbstore_lib`, RGW common code, optional SQLite library, pthread, and optional Jaeger support.
- `dbstore-bin` is a testing executable built from `dbstore_main.cc`.
- `WITH_TESTS` gates `add_subdirectory(tests)`; otherwise it emits a warning that GTest is not enabled.

## Control Flow
CMake config starts by defining include paths and common source lists. If SQLite is enabled, SQLite sources are appended to `dbstore_srcs`, the `sqlite` subdirectory is added, `SQLITE_ENABLED=1` is defined, and `sqlite_db` is linked and ordered after `dbstore_lib`. `dbstore_lib` is created first and linked to Boost context, optional `jaeger_base`, and `rgw_common`. The manager static library `dbstore` is then created and linked to the accumulated `CMAKE_LINK_LIBRARIES`. Finally, `dbstore-bin` is created and linked for testing.

## State And Persistence
The build file itself has no runtime persistence, but it determines which DBStore persistence backend exists in the binary. With `USE_SQLITE=ON`, SQLite connection, statement, and error handling are compiled, and table-backed persistence paths in `dbstore.h`/`dbstore.cc` can be exercised. It also creates static/shared build artifacts and test binaries in the build tree.

## Dependencies And Integration Points
The file depends on the surrounding Ceph CMake environment, `Boost::context`, `rgw_common`, optional `jaeger_base`, optional GTest through `WITH_TESTS`, pthread, and the local `sqlite` subdirectory. Include directories expose `${CMAKE_SOURCE_DIR}/src/rgw`, `${CMAKE_SOURCE_DIR}/src/rgw/store/rados`, and the current DBStore source directory to consumers.

## Risks And Edge Cases
- It mutates global `CMAKE_INCLUDE_DIR` and `CMAKE_LINK_LIBRARIES`, which can make link/include behavior order-dependent and harder to reason about than target-local properties.
- `dbstore_lib` includes header files as sources; this is harmless for IDE visibility but can obscure which files actually compile.
- `dbstore` is static while `dbstore_lib` uses default library type; mixed library type expectations can vary by parent CMake settings.
- `USE_SQLITE=OFF` leaves `dbstore_lib` without SQLite implementation files, so code paths that assume `SQLITE_ENABLED` or `sqlite_db` need compile guards.
- The file calls `find_package(gtest QUIET)` but uses `WITH_TESTS` rather than the package result to decide whether to add tests.
- `add_dependencies(sqlite_db dbstore_lib)` assumes the `sqlite` subdirectory creates a `sqlite_db` target.

## Test Signals
Build `dbstore_lib`, `dbstore`, and `dbstore-bin` with `USE_SQLITE=ON` and `OFF`. Run CMake with `WITH_TESTS=ON` to ensure the `tests` subdirectory compiles and links. Verify `-Werror=vla` coverage when `COMPILER_SUPPORTS_VLA_ERROR` is set. Link failures around `sqlite_db`, `rgw_common`, or `Boost::context` are the main integration signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/dbstore/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/dbstore/common/connection_pool.h -->
# sources/distributed-fs/ceph/src/rgw/driver/dbstore/common/connection_pool.h

## Purpose
This header defines a small generic, thread-safe database connection pool for RGW DBStore backends. It limits the number of open database connections, creates connections on demand through a factory, blocks when the pool is exhausted, and returns borrowed connections automatically through RAII handles.

## Important APIs, Types, And Functions
- `ConnectionPoolBase<Connection>` owns the synchronization primitives and `boost::circular_buffer<std::unique_ptr<Connection>>` of idle connections. Its private `put()` returns a connection to the pool and wakes one waiter when transitioning from empty to non-empty.
- `ConnectionHandle<Connection>` is a move-only RAII wrapper around a borrowed `std::unique_ptr<Connection>`. Its destructor and move assignment return the currently held connection to the original pool.
- `factory_of<F, T>` is a C++20 concept requiring `factory(dpp)` to return `std::unique_ptr<T>` and the factory to be move constructible.
- `ConnectionPool<Connection, Factory>` combines a factory and maximum capacity. `get(dpp)` borrows an idle connection, creates a new one while under capacity, or waits on a condition variable until another handle returns a connection.

## Control Flow
Callers construct `ConnectionPool` with a factory and a maximum connection count. On `get()`:
1. The pool mutex is locked.
2. If an idle connection exists, it is popped from the circular buffer.
3. Else if `total < capacity`, a new connection is created by the factory and `total` is incremented.
4. Else the caller waits on `cond` until a returned connection is available, logs wait/done messages, and pops the returned connection.
5. A `ConnectionHandle` is returned. When destroyed or overwritten by move assignment, the handle calls `pool->put()` to make the connection reusable.

## State And Persistence
The pool keeps only process-local state: idle connection objects, a count of total created connections, a mutex, and a condition variable. It does not persist connection state itself. Failed or poisoned connections are not distinguishable from healthy connections in the current API, so every returned connection is reused.

## Dependencies And Integration Points
The header depends on C++20 concepts, mutex/condition variable primitives, `std::unique_ptr`, `boost::circular_buffer`, and Ceph logging through `common/dout.h`. It is intended for DBStore backend implementations such as SQLite connection pools that can provide a factory returning database connection objects.

## Risks And Edge Cases
- The factory is called while holding the pool mutex. Slow connection creation blocks unrelated borrowers and returners.
- `total` is incremented even if `factory(dpp)` returns `nullptr`; this can permanently consume capacity with invalid handles.
- There is a TODO for reporting connection errors. A handle cannot tell the pool to discard a broken connection.
- `ConnectionHandle` move assignment returns its current connection, then copies `o.pool`, but it does not clear `o.pool`. This is acceptable because `o.conn` is moved away, yet the moved-from handle still carries a stale pool pointer.
- `ConnectionHandle` relies on `pool` being valid whenever `conn` is non-null. Destroying a pool before all handles is unsafe.
- `get()` has no timeout, cancellation, or `optional_yield` support; exhausted pools can block RGW request threads indefinitely.
- A zero-capacity pool will always enter the wait path and can never be signaled with a real connection.

## Test Signals
Tests should cover borrowing and automatic return, capacity enforcement, concurrent wait and wake behavior, move construction/assignment, zero or one capacity behavior, factory failure returning null, and destruction ordering. Stress tests should verify that the number of simultaneously created connections never exceeds capacity and that returned handles are reusable across threads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/dbstore/common/connection_pool.h -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/dbstore/common/dbstore.h -->
# sources/distributed-fs/ceph/src/rgw/driver/dbstore/common/dbstore.h

## Purpose
This header defines the common RGW DBStore data model, SQL schema templates, operation classes, dispatch containers, and the abstract `DB` interface used by concrete DB-backed RGW stores. It translates RGW user/account/bucket/object/lifecycle concepts into generic `DBOpParams` structures and per-operation SQL schemas while leaving prepare/bind/execute mechanics to backend-specific subclasses.

## Important APIs, Types, And Functions
- `DBOpAccountInfo`, `DBOpUserInfo`, `DBOpBucketInfo`, `DBOpObjectInfo`, `DBOpObjectDataInfo`, `DBOpLCHeadInfo`, and `DBOpLCEntryInfo` are mutable operation payloads for account, user, bucket, object metadata, object data, and lifecycle records.
- `DBOpInfo` groups all operation payloads plus `query_str` and `list_max_count`.
- `DBOpParams` carries runtime table names, `CephContext`, and `DBOpInfo`.
- `DBOp*PrepareInfo`, `DBOpPrepareInfo`, and `DBOpPrepareParams` define placeholder names used in generated prepared statements.
- `DBOps` holds shared operation objects for global tables; `ObjectOp` holds per-bucket object and object-data operations.
- `DBOp` is the base operation class, with static table creation/drop/list schema helpers and virtual `Prepare()`, `Bind()`, and `Execute()`.
- Concrete operation classes such as `InsertUserOp`, `GetBucketOp`, `PutObjectOp`, `UpdateObjectOp`, `DeleteStaleObjectDataOp`, and lifecycle ops expose static `Schema()` methods that format SQL statement templates from `DBOpPrepareParams`.
- `DBOLHInfo` is an encodable structure mirroring RGW OLH info concepts.
- `DB` is the abstract backend facade. It owns table naming, context, object operation map, object sizing defaults, public CRUD methods, raw object helpers, nested bucket/object read/write/delete classes, lifecycle helpers, and a GC thread.
- `DB::raw_obj` maps tail data chunks to object data table operations.
- `DB::Bucket::List` and `DB::Object::{Read,Write,Delete}` model higher-level RGW list/read/write/delete flows independent of a concrete database.

## Control Flow
Concrete DB backends derive from `DB`, implement database open/close, table creation, operation initialization, prepare-parameter initialization, lifecycle table creation, and list-all helpers. Runtime methods in `dbstore.cc` fill `DBOpParams`; operation classes in this header define which SQL statement should run for a given operation and query mode.

Schema control flow starts with `DBOp::CreateTableSchema(type, params)` for account, user, bucket, object, object data, quota, lifecycle head, and lifecycle entry tables. Data operation flow uses the relevant `*Op::Schema()` method. `UpdateBucketOp` and `UpdateObjectOp` branch on `params.op.query_str` to choose narrower update statements, while `GetUserOp`, `GetAccountOp`, `ListUserBucketsOp`, and `GetLCEntryOp` choose query variants. Object operations are separated into metadata rows (`PutObject`, `GetObject`, `UpdateObject`, listing, version listing, delete) and data rows (`PutObjectData`, `GetObjectData`, `DeleteObjectData`, stale delete).

Nested `DB::Object` classes define the abstract RGW object request sequence: `Read::prepare()`/`read()`/`iterate()`, `Write::prepare()`/`write_data()`/`write_meta()`, and `Delete::delete_obj()`/`delete_obj_impl()`/`create_dm()`. The header declares these flows, while `dbstore.cc` implements them using operation dispatch.

## State And Persistence
The SQL schema templates define persistent tables:
- Account table keyed by `AccountID`.
- User table keyed by `UserID`, including primary access-key columns plus blob fields for richer RGW user maps and attrs.
- Bucket table keyed by `BucketName`, including owner, placement, quota, website, object lock, sync policy, attrs, version, and mtime.
- Object table keyed by `(ObjName, ObjInstance, BucketName)`, storing RGW dirent-like metadata, object state fields, attrs, manifest blobs, omap, multipart part list, object id, and head data.
- Object data table keyed by object identity, multipart part string, and part number, storing tail data blobs and mtimes.
- Quota, lifecycle entry, and lifecycle head tables.

Process-local state in `DB` includes table-name prefixes, a raw database handle, Ceph context, bucket id counter, object head/chunk sizes, static per-bucket object operation map, and GC state. `raw_obj` names and identities encode bucket, object name, instance, object id, multipart part string, and part number.

## Dependencies And Integration Points
The header depends on Ceph RGW SAL and RADOS-facing types (`rgw_sal_store.h`, `rgw_common.h`, `driver/rados/rgw_bucket.h`, `driver/rados/rgw_obj_manifest.h`), global Ceph context/init headers, `fmt::format`, STL containers, filesystem, mutex/condition variables, and Ceph encoding/logging support. It is designed to be consumed by DBStore manager/config files and concrete database implementations such as SQLite statement/binding code.

## Risks And Edge Cases
- `DBOp::CreateTableSchema("ObjectView")` formats `CreateObjectTableQ` instead of `CreateObjectViewQ`, so object view creation appears wrong and can emit an object table schema under the view name.
- `DB::ObjChunkSize` is initialized as `get_blob_limit() - 1000` in the base constructor. Because virtual dispatch in constructors calls the base `get_blob_limit()` returning `0`, this can underflow to a huge `uint64_t` unless corrected later by subclasses.
- `DB::from_oid()` splits on underscores and the comment notes this breaks if object names contain underscores. It also indexes split fields without validating length.
- The object table primary key omits `ObjNS` and tenant, and comments note tenant handling is incomplete. Namespaces or multi-tenant use can collide.
- User and account schemas simplify access keys and quotas into a mixture of searchable scalar fields and blobs. Queries across multiple keys or structured quotas are limited.
- Many operation SQL templates use `INSERT OR REPLACE`, which can trigger delete/insert behavior and foreign-key cascades instead of in-place updates.
- The object data table has a foreign key only on `BucketName`; stale tail rows are cleaned by GC rather than strict object-row referential integrity.
- Prepared statement placeholder names are backend-flavored strings. Backends with different placeholder conventions must fully and consistently override `InitPrepareParams()`.
- Several virtual lock methods are declared but no common implementation is visible here, so callers cannot assume DB-level mutual exclusion.

## Test Signals
Schema-generation tests should compare generated SQL for every table and every operation/query mode, including the object view case. Backend tests should verify prepare/bind/execute coverage for all fields in `DBOpParams`, blob encoding/decoding of attrs/manifests/quotas/lifecycle state, object table primary key behavior for versions/namespaces, object data chunk keys, lifecycle tables, and stale data deletion. Construction tests should assert sane `ObjChunkSize` for concrete backends. Fuzz or property tests for `to_oid()`/`from_oid()` should include underscores and malformed object ids.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/dbstore/common/dbstore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/dbstore/common/dbstore_log.h -->
# sources/distributed-fs/ceph/src/rgw/driver/dbstore/common/dbstore_log.h

## Purpose
This small header centralizes the DBStore logging prefix for Ceph `dout` logging. Including it changes `dout_prefix` so log messages from DBStore code are prefixed with `rgw dbstore:`.

## Important APIs, Types, And Functions
- Includes common C/C++ headers and `common/dout.h`.
- Undefines any existing `dout_prefix`.
- Defines `dout_prefix` as `*_dout << "rgw dbstore: "`.

## Control Flow
There is no runtime control flow beyond preprocessor behavior. Files that include this header before issuing `dout` logs inherit the DBStore-specific prefix.

## State And Persistence
The header has no persistent state. Its only state effect is compile-time macro replacement of `dout_prefix` in the including translation unit.

## Dependencies And Integration Points
It integrates with Ceph's `dout` logging infrastructure via `common/dout.h`. It is listed as part of the DBStore library sources in `CMakeLists.txt` for visibility, but it is a header-only logging helper.

## Risks And Edge Cases
- Redefining `dout_prefix` is global within the including translation unit and can affect later includes or code in surprising ways.
- The header includes several standard headers (`cerrno`, `cstdlib`, `string`, `cstdio`, iostream/fstream) that are not needed for the macro itself, increasing incidental dependencies.
- It depends on `_dout` being valid in the logging context, as expected by Ceph logging macros.

## Test Signals
Compile DBStore translation units that include this header and verify log output includes `rgw dbstore:`. Also check include ordering with other components that define `dout_prefix`, because macro conflicts are the main failure mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/dbstore/common/dbstore_log.h -->
