# subset-b-006961 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/posix/bucket_cache.h -->
# sources/distributed-fs/ceph/src/rgw/driver/posix/bucket_cache.h

## Purpose
`bucket_cache.h` implements the POSIX RGW driver's ordered bucket listing cache. It materializes per-bucket directory listings into LMDB named databases, orders them by concatenated object name and instance, and keeps the cache approximately current with filesystem notifications. RGW bucket `list()` calls use this layer instead of walking the filesystem for every listing request.

## Important APIs, Types, and Functions
`BucketCacheEntry<D, B>` is the cached bucket object. It stores the bucket name, an xxhash partition key, an LMDB environment/database handle, intrusive AVL linkage, an LRU object base, a mutex/condition variable, and flags for filled/deleted state. `Factory` allocates or recycles entries for the cohort LRU. `reclaim()` marks an entry deleted, removes its notification watch, drops the LMDB database contents, and closes the DBI handle.

`BucketCache<D, B>` owns the LRU, AVL lookup cache, `Lmdbs` partition manager, and `Notify` implementation. Key public methods are `get_bucket()`, `fill()`, `list_bucket()`, `notify()`, `add_entry()`, `remove_entry()`, and `invalidate_bucket()`. `fill_cache_cb_t` and `list_bucket_each_t` are callback types used to serialize `rgw_bucket_dir_entry` values into LMDB and stream them back to callers.

## Control Flow
`list_bucket()` calls `get_bucket()` with create and lock flags. A missing bucket entry is inserted into the LRU/AVL cache, assigned to one LMDB partition by hash, and opened as a named LMDB database. If the entry is not filled, `fill()` asks the SAL bucket to enumerate entries, serializes selected `rgw_bucket_dir_entry` fields with `zpp::bits`, commits them to LMDB, marks the entry filled, and adds an inotify watch.

After fill, listing unlocks the bucket and scans the LMDB cursor from the marker or first key. Each LMDB value is deserialized back to `rgw_bucket_dir_entry`, `mtime` is reconstructed from seconds/nanoseconds, and the caller callback decides whether to continue.

Notification flow enters `notify()`. Existing filled buckets accept ADD, REMOVE, and INVALIDATE events. ADD calls `driver->mint_listing_entry()` to build metadata for a side-loaded file and writes it to LMDB; REMOVE deletes the key; INVALIDATE drops the DB and clears `FLAG_FILLED`, causing the next list to rebuild.

## State and Persistence Behavior
The LMDB cache is explicitly process-local and ephemeral. `Lmdbs` creates `rgw_posix_lmdbs/part_N` under the configured database root and removes all existing contents at construction. Persistent source of truth remains the POSIX filesystem plus xattrs managed by `rgw_sal_posix.cc`.

State is protected by a mix of partition locks from `TreeX`, per-entry mutexes, and LRU references. Every successful `get_bucket()` path must be paired with `lru.unref()`, and the destructor resets the notifier before draining cached entries to avoid callbacks into freed buckets.

## Dependencies and Integration Points
This header depends on LMDB, `lmdb-safe.hh`, `notify.h`, `zpp_bits`, xxhash, Boost intrusive AVL trees, Ceph `cohort_lru`, `scope_guard`, and RGW bucket entry types. It integrates directly with `POSIXDriver::mint_listing_entry()` and `POSIXBucket::fill_cache()` from `rgw_sal_posix.*`.

## Risks
The key format is `name + instance` and omits namespace in serialization comments, so namespacing/version edge cases require care. `invalidate_bucket()` calls `lru.unref()` manually despite also installing an unref scope guard, which looks like a double-unref risk. Notification REMOVE deletes by raw event name, while other paths use `concat_key()`, so versioned or instance-bearing keys can diverge. LMDB exceptions are not caught. Reclaim depends on proper DBI close/drop sequencing and on `safe_link` detecting linked AVL state.

## Test Signals
Useful tests should cover cold fill, marker ordering, prefix/list callback stop behavior, LRU reclaim, destructor drain under active watches, ADD/REMOVE/INVALIDATE notification updates, side-loaded file metadata minting, versioned keys, and double-unref detection under sanitizers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/posix/bucket_cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/posix/lmdb-safe-global.h -->
# sources/distributed-fs/ceph/src/rgw/driver/posix/lmdb-safe-global.h

## Purpose
`lmdb-safe-global.h` provides the symbol import/export macros used by the vendored `lmdb-safe` C++ wrapper. In this POSIX RGW driver tree it controls whether `LMDB_SAFE_EXPORT` and `LMDB_SAFE_IMPORT` resolve to cpp-utilities visibility attributes or to empty definitions for static/no-utilities builds.

## Important APIs, Types, and Functions
The only public API is preprocessor-level: `LMDB_SAFE_EXPORT` and `LMDB_SAFE_IMPORT`. If `LMDB_SAFE_NO_CPP_UTILITIES` is not defined, the header includes `<c++utilities/application/global.h>` and maps the macros to `CPP_UTILITIES_GENERIC_LIB_EXPORT` and `CPP_UTILITIES_GENERIC_LIB_IMPORT` unless `LMDB_SAFE_STATIC` is defined. If cpp-utilities is disabled, the header forces `LMDB_SAFE_STATIC` and makes both macros empty.

## Control Flow
There is no runtime control flow. Compile-time flow chooses between dynamic-library visibility and static/no-op visibility based on `LMDB_SAFE_NO_CPP_UTILITIES` and `LMDB_SAFE_STATIC`.

## State and Persistence Behavior
The header owns no state and has no persistence behavior. Its impact is ABI/linkage visibility for classes declared in `lmdb-safe.hh`, such as `LMDBError`, `MDBEnv`, transaction wrappers, and cursors.

## Dependencies and Integration Points
It is included by `lmdb-safe.hh`. When cpp-utilities is available, it depends on that project's generic library visibility macros. The POSIX RGW cache includes `lmdb-safe.hh`, so any build-system mismatch here affects bucket listing cache compilation/linkage.

## Risks
The most likely risk is build portability. A dynamic build without cpp-utilities must define `LMDB_SAFE_NO_CPP_UTILITIES`, otherwise the include will fail. Conversely, incorrect `LMDB_SAFE_STATIC` settings can hide symbols needed by a shared library. The include guard uses `LMDB_SAFE_GLOBAL`, which is simple but could collide with another macro in a broad build.

## Test Signals
Compile the POSIX RGW driver in both static and shared configurations, with and without cpp-utilities visibility macros. Link tests should instantiate exported `LMDBSafe` classes from another translation unit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/posix/lmdb-safe-global.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/posix/lmdb-safe.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/posix/lmdb-safe.cc

## Purpose
`lmdb-safe.cc` implements the vendored RAII wrapper around LMDB environments, named databases, transactions, and cursors. The POSIX bucket cache uses it to store transient ordered bucket listings while avoiding raw LMDB cleanup mistakes in normal paths.

## Important APIs, Types, and Functions
`MDBDbi::MDBDbi()` opens an LMDB named database inside a transaction. `MDBEnv` creates the environment, sets a fixed 4GB map size, sets `maxdbs`, opens the environment with `MDB_NOTLS`, tracks per-thread RO/RW transaction counts, and serializes named database opens with `d_openmut`.

`getMDBEnv()` caches `MDBEnv` instances by `(dev, ino)` and rejects reopening an existing environment with different flags. `MDBRWTransactionImpl` and `MDBROTransactionImpl` implement transaction creation, commit, abort, child transaction creation, cursor cleanup, `clear()`, and cursor factories.

## Control Flow
Environment creation calls `mdb_env_create`, `mdb_env_set_mapsize`, `mdb_env_set_maxdbs`, and `mdb_env_open`. Opening a DB from a writable environment creates a short RW transaction, opens the named DB, commits, and returns the DBI; readonly environments use an RO transaction.

RO/RW transaction begin loops retry `MDB_MAP_RESIZED` by calling `mdb_env_set_mapsize(env, 0)`. RW begin rejects a duplicate same-thread RW transaction. RO begin rejects starting while a same-thread RW transaction is tracked. Destructors call `abort()`/`commit()` through base-class-safe non-virtual calls and close registered cursors before closing transactions.

## State and Persistence Behavior
The wrapper is durable only through LMDB's own environment files. In this repository, `bucket_cache.h` stores ephemeral listing data and wipes its LMDB directories on startup. The wrapper maintains process-local shared environment cache, per-thread transaction counters, open mutexes, cursor registries, and raw LMDB handles.

## Dependencies and Integration Points
It depends on LMDB C APIs, POSIX `stat`, and C++ mutex/shared pointer containers. `bucket_cache.h` calls `getMDBEnv()`, `openDB()`, `getROTransaction()`, `getRWTransaction()`, `put()`, `del()`, cursor scans, and `mdb_drop()` through the raw transaction conversion operator.

## Risks
The wrapper throws exceptions for most LMDB errors, while POSIX RGW cache callers generally do not catch them. The same-thread transaction count policy prevents RO while RW is open, which can surprise callers trying nested reads. The global environment cache is keyed by inode after creation and stores only flags, not mode or max DB count. Fixed map size and max DB settings may not match large deployments. DBI close is mostly left to callers, so callers must respect LMDB lifetime rules.

## Test Signals
Tests should cover environment reuse, flag mismatch rejection, DB open serialization, RO/RW transaction lifecycle, duplicate RW prevention, cursor auto-close on commit/abort, `MDB_MAP_RESIZED` retry behavior, child transaction cleanup, and bucket-cache listing writes/scans under concurrent list and notify traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/posix/lmdb-safe.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/posix/lmdb-safe.hh -->
# sources/distributed-fs/ceph/src/rgw/driver/posix/lmdb-safe.hh

## Purpose
`lmdb-safe.hh` declares the C++ RAII API used to access LMDB from the POSIX RGW listing cache. It wraps LMDB environments, DBI handles, transactions, cursors, and input/output values with typed helpers and exception-based error handling.

## Important APIs, Types, and Functions
`LMDBError` carries an LMDB error code and message. `MDBDbi` is a lightweight DBI value wrapper. `MDBEnv` exposes `openDB()`, `getRWTransaction()`, `getROTransaction()`, raw `MDB_env*` conversion, and transaction counters.

`MDBInVal` builds `MDB_val` inputs from arithmetic values, strings, string views, output values, or structs. `MDBOutVal` exposes typed getters for arithmetic values, structs, `std::string`, and `string_view`. `MDBROTransactionImpl` implements `get()`, readonly DB open, and readonly cursor creation. `MDBRWTransactionImpl` adds `put()`, `del()`, `clear()`, RW cursor creation, and child transaction creation. `MDBGenCursor` implements cursor movement, find, lower_bound, current/first/last/next/prev, close, and move-only registration. `MDBROCursor` and `MDBRWCursor` specialize cursor behavior, with RW cursor `put()` and `del()`.

## Control Flow
Callers obtain a shared environment with `getMDBEnv()`, open a named DB with `openDB()`, start a transaction, and operate through `get`, `put`, `del`, or cursor methods. Cursors register themselves with their owning transaction so transaction commit/abort can close outstanding cursors before closing the transaction. `MDB_NOTLS` is required so readonly transactions can be managed explicitly.

## State and Persistence Behavior
The header's classes wrap LMDB persistent environment state but do not define a schema. State in the wrapper includes raw LMDB handles, transaction pointers, cursor registries, per-thread transaction counters, input value scratch storage for arithmetic types, and output values pointing into LMDB-managed memory valid only for the transaction lifetime.

## Dependencies and Integration Points
It depends on `lmdb.h`, `lmdb-safe-global.h`, standard C++ containers, mutexes, thread IDs, and either standard or Boost string view. `bucket_cache.h` uses string keys and serialized string values for `rgw_bucket_dir_entry` records.

## Risks
`MDBOutVal::string_view` points into LMDB memory and must not outlive the transaction. `MDBInVal::fromStruct()` references caller-owned memory, so the caller must keep it alive through the LMDB call. Move registration in `MDBGenCursor` is delicate; incorrect registry updates can double-close or leak cursors. Some raw LMDB conversions expose lower-level APIs, allowing callers to bypass wrapper invariants. Exception behavior must be acceptable to all integration paths.

## Test Signals
Compile and runtime tests should cover typed value conversion, missing key returns, exception paths, cursor move construction/assignment, cursor close during transaction close, lower_bound listing semantics, write/delete/clear behavior, and misuse cases such as using closed transactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/posix/lmdb-safe.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/posix/notify.cpp -->
# sources/distributed-fs/ceph/src/rgw/driver/posix/notify.cpp

## Purpose
`notify.cpp` implements the factory for the POSIX driver's filesystem notification abstraction. It currently requires Linux inotify and returns an `Inotify` instance for bucket listing cache invalidation/update.

## Important APIs, Types, and Functions
The only function is `file::listing::Notify::factory(Notifiable* n, const std::string& bucket_root)`. On `__linux__`, it constructs `new Inotify(n, bucket_root)` and wraps it in `std::unique_ptr<Notify>`. On non-Linux platforms it emits a preprocessor error stating that the RGW POSIX driver requires inotify.

## Control Flow
`BucketCache` constructs `Notify::factory(this, bucket_root)` during initialization. The resulting `Inotify` object owns the event loop thread and calls back into `BucketCache::notify()` through the `Notifiable` interface declared in `notify.h`.

## State and Persistence Behavior
This file owns no runtime state. It selects the concrete notification implementation. Notification state is held in `Inotify` fields in `notify.h`.

## Dependencies and Integration Points
It includes `notify.h` and Linux `<sys/inotify.h>` when compiled for Linux. Its integration point is `BucketCache`, which depends on the factory to create a watcher before any bucket cache fills can register watches.

## Risks
The driver is intentionally non-portable here. Any build that includes this source on non-Linux platforms fails at preprocessing. The file has a dead `return nullptr` after the preprocessor branch, but it is unreachable for supported builds.

## Test Signals
Linux build coverage should verify the factory returns a non-null `Inotify`. Non-Linux build jobs should either exclude this driver or intentionally assert that the driver is unsupported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/posix/notify.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/posix/notify.h -->
# sources/distributed-fs/ceph/src/rgw/driver/posix/notify.h

## Purpose
`notify.h` defines the notification abstraction used by the POSIX bucket listing cache and implements the Linux inotify backend inline. It converts filesystem create/delete/move and overflow signals into bucket-cache events.

## Important APIs, Types, and Functions
`Notifiable` declares `EventType::{ADD, REMOVE, INVALIDATE}`, `Event`, and virtual `notify(bucket_name, opaque, events)`. `Notify` stores the callback object and bucket root path, and declares `factory()`, `add_watch()`, and `remove_watch()`.

`Inotify` owns the Linux implementation. It has watch and event fds, a mutex-protected descriptor-to-`WatchRecord` map and name-to-descriptor map, an atomic shutdown flag, and a background thread. `add_watch()` calls `inotify_add_watch()` on `bucket_root / dname`; `remove_watch()` calls `inotify_rm_watch()` and erases both maps. `ev_loop()` polls the inotify fd and eventfd, reads batches into an aligned buffer, maps each watch descriptor to a bucket name/opaque pointer, and calls `Notifiable::notify()`.

## Control Flow
The constructor initializes inotify/eventfd and starts `ev_loop()`. The loop waits in `poll()`, reads inotify events, skips stale watch descriptors, translates create and moved-to events into ADD, delete and moved-from into REMOVE, and queue overflow into INVALIDATE. Each translated batch is sent to the registered `Notifiable`.

The destructor sets shutdown, writes to eventfd to wake the poll, joins the thread, and closes fds. `BucketCache` resets the notifier before draining entries so callbacks do not race with cache destruction.

## State and Persistence Behavior
All state is in memory and kernel watch state. There is no durable persistence. Watch records store the logical bucket name and an opaque cache-entry pointer so callbacks can reject stale events after recycling.

## Dependencies and Integration Points
The file depends on Linux inotify/eventfd/poll APIs, `unordered_dense.h`, `fmt`, threads, mutexes, atomics, and filesystem paths. It integrates with `BucketCache::fill()` to add watches and `BucketCacheEntry::reclaim()` to remove watches.

## Risks
The eventfd is only used as a wakeup fd; `ev_loop()` does not read/drain it, which is acceptable for shutdown but would matter for repeated signals. `aw_mask` excludes many event types and ignores modifications, so metadata-only or write-only changes may not update cached listings. Duplicate `add_watch()` uses unordered-dense `insert()` and will not update an existing mapping. `event->name` is a string view into the read buffer and is safe only during immediate notification processing. Constructor starts the thread after member initialization, but failures call `exit(1)`.

## Test Signals
Tests should create/remove/move files in watched bucket directories and assert ADD/REMOVE delivery, force overflow or direct INVALIDATE handling, add/remove watches repeatedly, test duplicate watches, run under thread sanitizer for destructor races, and verify stale descriptor events are ignored.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/posix/notify.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/posix/posixDB.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/posix/posixDB.cc

## Purpose
`posixDB.cc` implements the SQLite-backed user and account database adapters used by the POSIX RGW driver. It delegates actual operations to DBStore/SQLite operation objects while adding POSIX-driver initialization, logging setup, and a temporary default user bootstrap.

## Important APIs, Types, and Functions
`POSIXUserDB::ProcessOp()` and `POSIXAccountDB::ProcessOp()` resolve an operation name with `getDBOp()` and call `Execute()`. `Initialize()` for each DB configures Ceph RGW logging, opens the SQLite database, initializes operation tables via `InitializeDBOps()`, and logs success. `Destroy()` delegates to `DB::Destroy()`.

`POSIXUserDB::Initialize()` also installs a default `test` user with a hard-coded access key if that user is absent. It fills `DBOpParams` table names and `RGWUserInfo`, runs `GetUser`, then `InsertUser` on `-ENOENT`.

## Control Flow
Initialization checks for a valid `CephContext`, applies optional log level/file overrides, calls `openDB()`, then `InitializeDBOps()`. Failure closes the DB and clears `db`. Runtime operations use `ProcessOp()` as a generic dispatcher, returning `-1` when no operation object is found and logging errors for failed `Execute()`.

## State and Persistence Behavior
Persistent state lives in the SQLite database opened by the inherited `SQLiteDB` base. User rows and account rows are defined by DBStore operation classes and table names supplied by `POSIXUserDB`/`POSIXAccountDB`. The default user bootstrap mutates persistent user metadata on first initialization.

## Dependencies and Integration Points
This file depends on `posixDB.h`, Ceph logging, DBStore common APIs, and SQLiteDB inherited methods. `rgw_sal_posix.cc` constructs these DBs in `POSIXDriver`, calls `Initialize()` from `newPOSIXDriver()`, and uses `get_user`, `store_user`, `remove_user`, `get_account`, `store_account`, and `remove_account` through inherited SQL operations.

## Risks
The hard-coded default user and secret are explicitly temporary and unsafe outside development. `POSIXAccountDB` construction declares several table-name members in the header but only initializes some, which should be checked against compiler warnings. `ProcessOp()` returns generic `-1` for missing operations instead of a precise errno. Operation mutexes exist in op classes but are not used directly here.

## Test Signals
Tests should initialize fresh and existing DBs, verify default user insertion is idempotent, exercise user lookup by id/access key/email, account store/load/delete, invalid operation names, DB open failure, logging configuration, and destroy/reinitialize behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/posix/posixDB.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/posix/posixDB.h -->
# sources/distributed-fs/ceph/src/rgw/driver/posix/posixDB.h

## Purpose
`posixDB.h` declares POSIX RGW database adapter types over the DBStore SQLite backend. It provides user and account DB classes plus operation marker/subclass types that let the POSIX driver reuse SQL user/account operation implementations.

## Important APIs, Types, and Functions
The file defines POSIX-specific aliases/subclasses for DB operation parameter/info structures, including `POSIXUserDBOpUserInfo`, `POSIXUserDBOpPrepareParams`, `POSIXAccountDBOpAccountInfo`, and related types. `POSIXUserDBOp` and `POSIXAccountDBOp` inherit `DBOp`, include static SQL create-table strings matching RGW user/account structures, and carry a mutex intended to protect prepared statements.

`InsertPOSIXUserOp`, `RemovePOSIXUserOp`, `InsertPOSIXAccountOp`, `RemovePOSIXAccountOp`, and `GetPOSIXAccountOp` inherit existing SQL operation classes. `POSIXUserDB` and `POSIXAccountDB` inherit `SQLiteDB` and expose `Initialize()`, `ProcessOp()`, `Destroy()`, `ctx()`, and no-op overrides for lifecycle and listing methods not implemented here.

## Control Flow
The classes are constructed with a database name/path and `CephContext`. Constructors call `DB::set_context(cct)` and derive table names from the database name for account/user tables. Runtime behavior is implemented in `posixDB.cc` and inherited `SQLiteDB`/DBStore methods.

## State and Persistence Behavior
`POSIXUserDB` persists user metadata, access keys, quotas, caps, temp URL keys, MFA IDs, attrs, and versioning fields in SQLite columns, with several maps stored as blobs. `POSIXAccountDB` persists account metadata, quotas, max limits, tenant/name/email fields, and account ID primary key. Several list-all methods are stubs returning success without filling results.

## Dependencies and Integration Points
The header depends on RGW DBStore SQLite/common APIs, Ceph context/logging, RGW common types, multisite headers, and `rgw_obj_manifest.h` for a noted subclass dependency. `POSIXDriver` owns one user DB and one account DB, and POSIX users/accounts call through these adapters.

## Risks
The SQL create-table strings are private static constants but table creation appears delegated to inherited SQLiteDB paths, so schema alignment needs build/runtime verification. Blob-packed complex fields limit queryability. `ListAllBuckets`, `ListAllUsers`, and `ListAllObjects` returning `0` without output can mislead callers if wired in. Table name construction embeds the DB path/name prefix, which may produce awkward SQL identifiers if not sanitized by lower layers.

## Test Signals
Compile tests should instantiate all operation types and DB classes. Integration tests should verify schema creation, insert/get/remove user/account operations, blob round trips for keys/attrs/quotas, version tracker behavior, list-all stub expectations, and table-name handling for configured DB prefixes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/posix/posixDB.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/posix/rgw_sal_posix.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/posix/rgw_sal_posix.cc

## Purpose
`rgw_sal_posix.cc` implements the Ceph RGW Store Abstraction Layer backend that stores buckets and objects directly on a POSIX filesystem. Bucket directories, object files/directories/symlinks, extended attributes, a SQLite user/account DB, and the LMDB listing cache together emulate enough RGW behavior for the POSIX driver.

## Important APIs, Types, and Functions
Helper functions encode object filenames (`get_key_fname()`), bucket directory names (`bucket_fname()`), random instance/upload names, xattr reads/writes/removals, owner decode, and recursive directory deletion. `FSEnt` implements common stat/xattr/fill-cache behavior. `File`, `Directory`, `Symlink`, `MPDirectory`, and `VersionedDirectory` implement concrete filesystem object shapes.

`POSIXDriver::initialize()` creates the bucket cache, opens or creates the root directory, and initializes quota handling. User/account methods delegate to `POSIXUserDB` and `POSIXAccountDB`. `POSIXBucket` implements create/load/list/remove/stats/xattrs/multipart listing. `POSIXObject` implements stat/open/read/write/delete/copy/xattrs/version selection. `POSIXAtomicWriter`, `POSIXMultipartUpload`, and `POSIXMultipartWriter` implement write paths and multipart completion.

## Control Flow
Object names are URL-encoded for filenames; namespaced objects are hidden by a leading dot. Buckets are directories under `rgw_posix_base_path`. Bucket metadata is stored as xattrs, including encoded `RGWBucketInfo`. Objects store RGW attrs as `user.X-RGW-*` xattrs and have a `POSIX-Object-Type` xattr.

Reads call `POSIXReadOp::prepare()`, stat the object, load attrs, generate an MD5 ETag once for side-loaded files if missing, validate conditional headers, then stream data with `read()`. Atomic writes create an unnamed `O_TMPFILE`, write buffers, write xattrs including `POSIXOwner`, link the temp file into the bucket, rename it to the final object, update the bucket cache, and update quota stats.

Versioned objects are directories. A version file is named with the encoded oid including instance; a symlink named like the base object points to the current version. Removing a base object creates a delete marker by moving the current symlink to a generated missing target; removing a specific version deletes the matching file and repoints or removes the symlink. Multipart uploads use hidden `.multipart_*` shadow buckets containing part files and a metadata object; completion validates parts/ETags, computes final multipart ETag, writes manifest attrs, and renames the shadow directory to the final object.

Bucket listing flows through `POSIXBucket::list()`, which normalizes marker/prefix and delegates to `BucketCache::list_bucket()`. The callback applies visibility, version, namespace, prefix, delimiter, marker, truncation, and common-prefix logic.

## State and Persistence Behavior
Durable state is filesystem entries plus xattrs and SQLite user/account DB rows. The LMDB bucket listing cache is transient and rebuilt from directories. Quota stats are updated through `RGWQuotaHandler`, but many stats/index APIs are stubs. File close fsyncs regular files. Directory operations use fd-relative syscalls (`openat`, `mkdirat`, `unlinkat`, `renameat2`, `statx`) to reduce path races.

## Dependencies and Integration Points
The file depends on Linux/POSIX syscalls, xattrs, Ceph RGW SAL interfaces, quota, MD5, bufferlist encoding, DBStore, `bucket_cache.h`, `posixDB.h`, and RGW notification/lifecycle/multipart interfaces. It exports `newPOSIXDriver(CephContext*)` for dynamic driver creation.

## Risks
Many SAL surfaces return `0`, `nullptr`, or `-ENOTSUP`, including lifecycle, sync, roles, Lua, cloud transition, omap, usage, and some stats/index operations. `if_nomatch == "*"` logic in atomic complete appears inverted relative to "must not exist" semantics. `std::string value; value.reserve(); vp = &value[0]` in xattr read writes into un-sized storage, which is unsafe. `copy_file_range()` is called once and may not copy full files. `renameat2(RENAME_EXCHANGE)` and `O_TMPFILE` are Linux-specific. Version/delete marker behavior is subtle and needs broad tests.

## Test Signals
High-value tests include bucket create/load/list/remove, xattr round trips, side-loaded file ETag generation, atomic writer conditionals, quota delta updates, list prefix/delimiter/marker/version cases, inotify cache coherence, versioned put/delete/specific-version delete/copy, multipart init/upload/list/complete/abort, recursive removal, fsync/error paths, and sanitizer coverage for xattr buffer handling and cache reference lifetimes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/posix/rgw_sal_posix.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/posix/rgw_sal_posix.h -->
# sources/distributed-fs/ceph/src/rgw/driver/posix/rgw_sal_posix.h

## Purpose
`rgw_sal_posix.h` declares the POSIX-backed RGW SAL driver, filesystem entity hierarchy, bucket/object/user/account wrappers, multipart classes, writers, and lightweight zone/notification/lua stubs. It is the public contract for `rgw_sal_posix.cc`.

## Important APIs, Types, and Functions
`ObjectType` encodes the filesystem representation: file, directory, versioned directory, multipart directory, symlink, or unknown. `FSEnt` is the abstract base for filesystem entries and declares create/open/close/stat/remove/read/write/xattr/copy/cache-fill operations. `File`, `Directory`, `Symlink`, `MPDirectory`, and `VersionedDirectory` specialize those operations.

`POSIXDriver` inherits `StoreDriver` and owns `CephContext`, `POSIXUserDB`, `POSIXAccountDB`, `POSIXZone`, `BucketCache`, root directory, sync module, and quota handler. It declares user/account lookup and store methods, bucket/object factories, listing and metadata APIs, writer factories, notification creation, and internal helpers such as `mint_listing_entry()`.

`POSIXBucket` inherits `StoreBucket` and declares object lookup, list, attrs, stats, remove/create/load, multipart operations, quota checks, and filesystem helpers. `POSIXObject` inherits `StoreObject` and declares delete/copy/read ops, attrs, object state, transitions, multipart serializer, file entity construction, temp linking, cache filling, version handling, and ETag generation. Multipart support is declared through `POSIXMPObj`, `POSIXUploadPartInfo`, `POSIXMultipartPart`, `POSIXMultipartUpload`, `POSIXMultipartWriter`, and `POSIXAtomicWriter`.

## Control Flow
The header establishes the object model used by the implementation. Driver initialization creates roots and caches. Buckets wrap `Directory` instances. Objects wrap an `FSEnt` selected by object type and bucket versioning. Writers create file or versioned-directory entities and later link temp files into place. Multipart uploads create hidden shadow buckets and eventually rename them into the target namespace.

## State and Persistence Behavior
Class state mirrors persisted filesystem state: filenames, parent directories, fds, `statx` data, xattrs, bucket info, object attrs, version instance IDs, multipart parts, and manifest metadata. `POSIXDriver` also owns SQLite DB handles for users/accounts and an ephemeral bucket listing cache.

## Dependencies and Integration Points
The header depends on Ceph SAL base classes, RGW quota, RGW common types, `bucket_cache.h`, and `posixDB.h`. It is used by the dynamic driver entrypoint, RGW frontend code through SAL virtual methods, the bucket cache through `POSIXDriver`/`POSIXBucket` template parameters, and DBStore for identity metadata.

## Risks
The declaration surface is much broader than the implementation maturity: many virtual methods are stubs or partial. Ownership relies heavily on raw parent pointers plus cloned `unique_ptr` entries, so lifetime assumptions matter. File descriptors are cached inside mutable objects and many methods implicitly open them. The driver is Linux/POSIX-specific despite implementing generic SAL interfaces. Versioned and multipart object representations are non-obvious and require strict filename/xattr compatibility.

## Test Signals
Compile coverage should validate all SAL overrides against current RGW interfaces. Behavioral tests should instantiate the driver, exercise each `FSEnt` subclass, user/account DB paths, bucket and object lifecycle, writers, multipart classes, versioned directories, bucket cache integration, and unsupported APIs returning expected errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/posix/rgw_sal_posix.h -->
