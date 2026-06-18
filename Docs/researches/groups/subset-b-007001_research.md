# subset-b-007001 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_sal_dbstore.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_sal_dbstore.cc

## Purpose
Implements Ceph RGW's dbstore Storage Abstraction Layer driver declared in `rgw_sal_dbstore.h`. It adapts the generic SAL driver/user/bucket/object/multipart/lifecycle interfaces onto the dbstore backend types under `driver/dbstore`, with an exported `newDBStore()` factory used by RGW driver loading. The implementation is best read as a first-pass dbstore driver: core bucket, user, object IO, lifecycle, and multipart paths call into `DB`, while many advanced RGW features are explicitly stubbed.

## Important APIs, types, and functions
The main integration class is `DBStore`, which holds `DBStoreManager* dbsm`, the active `DB* db`, a synthetic `DBZone`, an `RGWLC* lc`, and Ceph logging/context pointers. `DBStore::initialize()` wires lifecycle processing and creates GC support via the backend. `DBStore::finalize()` destroys db handles through `DBStoreManager`.

User APIs include `DBUser::load_user()`, `read_attrs()`, `store_user()`, `remove_user()`, and lookup helpers `DBStore::get_user_by_access_key()`, `get_user_by_email()`, and `load_owner_by_email()`. These call `DB::get_user()`, `store_user()`, and `remove_user()` and transfer attrs/version trackers into SAL objects.

Bucket APIs include `DBStore::list_buckets()`, `load_bucket()`, `DBBucket::create()`, `remove()`, `load_bucket()`, `list()`, `set_acl()`, `merge_and_store_attrs()`, `put_info()`, and `chown()`. Listing is delegated to `DB::Bucket::List`, while metadata updates go through `DB::update_bucket()`.

Object APIs center on `DBObject`. `load_obj_state()` retrieves an `RGWObjState` from `DB::Object`, while `DBReadOp`, `DBDeleteOp`, `set_obj_attrs()`, `modify_obj_attrs()`, `omap_get_vals_by_keys()`, `omap_set_val_by_key()`, and `transition()` forward to dbstore object operations.

Multipart support is implemented through `DBMultipartUpload`, `DBMultipartWriter`, `DBAtomicWriter`, and `DBMPObj`. The upload meta object uses the multipart namespace, part metadata is tracked by `RGWUploadPartInfo`, and complete validates part order/etags before writing the final target metadata.

## Control flow
Driver construction enters through `newDBStore(CephContext*)`, which creates `DBStore`, creates `DBStoreManager`, obtains the default `DB`, stores both into the driver, sets the dbstore back-reference to the SAL driver, and assigns the Ceph context. Later, `initialize()` creates lifecycle machinery and optionally lifecycle tables/thread before creating the GC subsystem.

Normal bucket flow is direct: SAL calls create or load a `DBBucket`, and bucket methods call dbstore manager APIs with the current `RGWBucketInfo`, attrs, mtime, owner, and object-version tracker. Deletion first reloads the bucket and, unless `delete_children` is requested, lists up to two objects with versions enabled to reject non-empty buckets.

Object read flow creates `DB::Object::Read`, copies read conditions into the backend op, calls `prepare()`, updates the SAL object key and size from backend state, then reads ranges or attrs through the prepared op. Object delete flow copies delete parameters into `DB::Object::Delete`, calls `delete_obj()`, and copies delete marker/version results back to SAL.

Atomic write flow buffers initial bytes in the backend head object until `get_max_head_size()`, then streams remaining data in `get_max_chunk_size()` chunks via `write_data()`. `complete()` records object metadata and writes final meta with total/accounted size. Multipart write flow is similar for part data, but records uploaded part metadata in the meta object with `add_mp_part()`. Multipart complete repeatedly lists uploaded parts, validates requested part ids and etags, computes the multipart etag, then writes the final target object metadata with `completeMultipart` and tail modification flags.

## State and persistence behavior
Persistent state lives in dbstore through `DB`, not in this file. This layer translates SAL state into dbstore calls and caches transient state in SAL wrappers. `DBObject::load_obj_state()` deliberately preserves the current object key, atomic flag, and prefetch flag when replacing cached state from the backend. Bucket ACLs are encoded into `RGW_ATTR_ACL` before `update_bucket()`. Multipart state persists as a meta object named `<object>.<upload_id>` in `RGW_OBJ_NS_MULTIPART`, plus associated part data and `RGWUploadPartInfo` records.

The driver owns `DBStoreManager` with a raw pointer and deletes it in `~DBStore()`. `finalize()` also destroys db handles. `RGWLC* lc` is allocated with `new` in `initialize()` and used by `get_rgwlc()`. The code assumes `setDB()` has been called before `initialize()` because it dereferences `db` to create lifecycle/GC state.

## Dependencies and integration points
The file depends on `rgw_sal.h`, `rgw_sal_dbstore.h`, `rgw_bucket.h`, dbstore backend classes from `driver/dbstore`, Ceph buffer/time/logging utilities, and selected RADOS RGW constants from `driver/rados/rgw_rados.h`. It integrates with RGW plugin loading through `extern "C" void *newDBStore(CephContext*)`.

## Risks and test signals
The largest risk is feature incompleteness hidden behind success returns. Usage, stats, quota, index checks, bucket shard checks, swift versioning, copy object, roles, topics, account/group APIs, Lua, restore, append writers, and several sync paths either return `0`, `nullptr`, `-ENOTSUP`, or placeholder values. Tests should verify unsupported operations surface the expected user-facing status rather than silent success. Multipart paths need tests for part ordering, etag mismatch, minimum part size, missing meta object, final etag generation, and abort cleanup. Object write tests should cover boundary conditions around `get_max_head_size()` and `get_max_chunk_size()`, especially offset handling noted by comments. Lifecycle/GC initialization should be tested with and without `set_run_lc_thread(true)`, and teardown should confirm no use-after-destroy of `DB` handles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_sal_dbstore.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_sal_dbstore.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_sal_dbstore.h

## Purpose
Declares the dbstore implementation of RGW's Storage Abstraction Layer. The header defines concrete SAL classes for dbstore-backed users, buckets, objects, multipart uploads, writers, lifecycle, notifications, zones, placement tiers, Lua manager, and the `DBStore` driver itself.

## Important APIs, types, and functions
`DBStore` derives from `StoreDriver` and exposes the full RGW driver surface: user lookup/storage, bucket lookup/listing, object factory, lifecycle, notification, topic/account/group/role/OIDC interfaces, usage/stat APIs, metadata listing, sync hooks, quota/rate-limit hooks, writers, placement validation, initialization/finalization, and dbstore-specific `getDBStoreManager()`, `setDB()`, and `getDB()`.

`DBUser`, `DBBucket`, and `DBObject` derive from shared `StoreUser`, `StoreBucket`, and `StoreObject` base classes in `rgw_sal_store.h`. `DBObject` declares nested `DBReadOp` and `DBDeleteOp` wrappers around dbstore object operations. `DBAtomicWriter` and `DBMultipartWriter` derive from `StoreWriter` and hold backend write operation state, accumulated head/tail buffers, offsets, and sizes.

Multipart declarations include `DBMultipartPart`, `DBMPObj`, and `DBMultipartUpload`. `DBMPObj` encapsulates parsing and composing `<oid>.<upload_id>` meta object names. `DBMultipartUpload` exposes init/list/abort/complete/get-info/writer creation and stores owner, mtime, placement, and the parsed multipart identity.

Zone and lifecycle declarations include `DBPlacementTier`, `DBZoneGroup`, `DBZone`, `DBLifecycle`, `LCDBSerializer`, and `MPDBSerializer`. These provide minimal zonegroup/zone behavior, lifecycle table access, and serializer lock facades. `DBNotification` and `DBLuaManager` provide dbstore-specific notification and Lua manager objects.

## Control flow
The header establishes the object graph used by `rgw_sal_dbstore.cc`: `DBStore` creates or returns wrapper objects, wrappers retain a raw `DBStore*`, and method implementations use `store->getDB()` to reach persistence. Buckets create `DBObject` and `DBMultipartUpload` children. Multipart uploads create meta objects through their bucket, and writers carry a prepared `DB::Object::Write` operation across `prepare()`, `process()`, and `complete()`.

## State and persistence behavior
The declarations show that dbstore SAL wrappers are stateful adapters. User, bucket, and object state is inherited from `Store*` base classes; dbstore-specific classes add backend pointers, ACL caches, multipart identity, placement, and writer buffering state. `DBStore` owns a `DBStoreManager*`, stores a non-owning/default `DB*`, embeds `DBZone`, stores lifecycle and context pointers, and has a `use_lc_thread` flag. Persistence itself is delegated to `DB` and `DBStoreManager`, while this header defines the cached state and the method contracts that mutate it.

## Dependencies and integration points
The header depends on generic SAL declarations from `rgw_sal_store.h`, role/lifecycle/multisite headers, and dbstore backend headers `common/dbstore.h` and `dbstore_mgr.h`. It is the compile-time bridge between RGW front-end code and the dbstore driver implementation.

## Risks and test signals
The contract is broad, but many declared methods are only partially implemented in the `.cc`. That makes conformance drift a risk whenever SAL adds new virtual methods. Raw `DBStore*`, `DBStoreManager*`, `DB*`, and `RGWLC*` pointers require clear lifetime discipline. Serializer classes currently provide minimal lock behavior, so concurrency-sensitive multipart/lifecycle tests should verify actual guarantees expected by callers. Header-level tests are indirect: build failures catch signature drift, while integration tests should exercise user/bucket/object/multipart/lifecycle APIs through the generic SAL interface against the dbstore driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_sal_dbstore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_sal_filter.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_sal_filter.cc

## Purpose
Implements a generic SAL filter/decorator driver. A `FilterDriver` wraps another `Driver`, and returned users, buckets, objects, multipart uploads, serializers, lifecycle, restore, notification, writer, Lua manager, zone, and placement tier objects are wrapped in matching filter classes. The default filter does not alter behavior; it forwards calls while preserving a hook point for future filters.

## Important APIs, types, and functions
The file defines helper unwrappers `nextPlacementTier()`, `nextUser()`, `nextBucket()`, and `nextObject()` that dynamic-cast filter wrappers and return the underlying object pointer, while tolerating null. `FilterDriver` implements the driver interface by forwarding to `next` and wrapping returned polymorphic objects. `newBaseFilter(rgw::sal::Driver*)` exports the factory for constructing this decorator.

Important wrapping points include `FilterDriver::get_user*()`, `get_object()`, `get_bucket()`, `load_bucket()`, `get_zonegroup()`, `get_lifecycle()`, `get_restore()`, `get_notification()`, `get_lua_manager()`, `get_append_writer()`, and `get_atomic_writer()`. `FilterBucket::get_object()` returns a `FilterObject` bound back to the filter bucket. `FilterMultipartUpload::list_parts()` converts the backend parts map into filter-wrapped parts. `FilterObject::FilterReadOp` and `FilterDeleteOp` copy SAL params/results across the filter boundary.

## Control flow
Initialization clones the next driver's current zone into a `FilterZone`, so `get_zone()` returns a wrapper rather than exposing the backend zone directly. Most calls follow a simple pattern: unwrap any filter arguments needed by the backend, call the same method on `next`, and wrap newly returned objects before returning to the caller.

Object and multipart methods are where unwrapping matters most. Copy, transition, cloud transition, restore-from-cloud, notifications, writers, and multipart complete pass backend-facing bucket/object pointers by calling `nextBucket()` and `nextObject()`. Read/delete ops copy caller parameters into the backend op before execution, then copy changed params or result fields back out.

## State and persistence behavior
This file owns no persistent state. All persistent behavior remains in the wrapped driver. Runtime state consists of ownership of wrapped objects through `std::unique_ptr`, a cached `FilterZone` in `FilterDriver`, a `Bucket*` back-reference in `FilterObject`, and a filter-owned parts map in `FilterMultipartUpload`. The decorator must preserve identity and state visibility: calls like `FilterObject::set_bucket()` update both the wrapper's bucket pointer and the underlying object's bucket pointer.

## Dependencies and integration points
The implementation depends only on `rgw_sal_filter.h` plus the generic SAL object model. It integrates as an exported C factory `newBaseFilter()` and can sit above any concrete SAL driver, including RADOS or dbstore, as long as the wrapped objects are the expected filter classes when passed back through this layer.

## Risks and test signals
The helper functions use unchecked `dynamic_cast<Filter*>()->get_next()` after a null check. Passing a non-filter SAL object through a filter method that expects a filter wrapper would dereference null. This is mitigated by the filter's own wrapping discipline but should be tested for mixed-layer paths such as copy, notification, transition, writer creation, and multipart completion. `FilterDriver::get_restore()` wraps whatever `next->get_restore()` returns; if a backend returns null, subsequent `FilterRestore` calls would dereference null. `FilterMultipartUpload::complete()` currently does not forward `if_match`/`if_nomatch` to `next->complete()`, so conditional multipart completion behavior should be covered. Tests should verify params/results propagation for read/delete ops, object bucket identity after wrapping, parts wrapping after `list_parts()`, and finalization/shutdown forwarding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_sal_filter.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_sal_filter.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_sal_filter.h

## Purpose
Declares the full filter/decorator layer for RGW SAL. It mirrors the generic SAL interface with wrapper classes that hold an underlying `next` object and forward calls. This provides a reusable base for filters that need to intercept, observe, or transform SAL behavior without implementing a storage backend.

## Important APIs, types, and functions
`FilterDriver` is the root wrapper and holds a raw `Driver* next` plus a cached `FilterZone`. It declares forwarding overrides for user, account, group, bucket, object, zone, lifecycle, restore, notification, topic, usage, metadata, sync, Lua, role, OIDC, writer, placement, admin, and context APIs.

Wrapper classes include `FilterPlacementTier`, `FilterZoneGroup`, `FilterZone`, `FilterUser`, `FilterBucket`, `FilterObject`, `FilterMultipartPart`, `FilterMultipartUpload`, `FilterMPSerializer`, `FilterLCSerializer`, `FilterRestoreSerializer`, `FilterLifecycle`, `FilterRestore`, `FilterNotification`, `FilterWriter`, and `FilterLuaManager`. Most store `std::unique_ptr<T> next` and expose `get_next()` for internal unwrapping.

`FilterObject` declares nested `FilterReadOp` and `FilterDeleteOp` to wrap object read and delete operations while preserving params and results. `FilterMultipartUpload` stores its own wrapper-level `parts` map so callers receive `FilterMultipartPart` objects even though the backend owns concrete parts.

## Control flow
The header's structure encodes a transparent decorator pattern. Factory methods in the driver and bucket layers return filtered versions of backend objects. Calls that return child objects allocate a wrapper around the backend child. Calls that accept objects or buckets are implemented in the `.cc` by unwrapping before forwarding.

## State and persistence behavior
The filter layer should not own persistence. It owns wrapper lifetimes with `unique_ptr` and maintains small amounts of adapter state: cached zone wrappers, a bucket pointer on `FilterObject`, and a copied/wrapped multipart parts map. All durable metadata, object content, usage, lifecycle, and sync state remains in the underlying driver.

## Dependencies and integration points
The header depends on `rgw_sal.h` and `rgw_role.h` and must track the evolving SAL virtual interface. It is used by `rgw_sal_filter.cc` and by any filter factory or derived custom filter that wants to extend the base forwarding behavior.

## Risks and test signals
Because this header mirrors many SAL methods, interface drift is the main maintenance risk. Missing an override can bypass filter behavior or fail compilation when SAL changes. The raw `Driver* next` is non-owning, so the wrapped driver must outlive the filter. Any derived filter must preserve wrapping/unwrapping rules or mixed backend/filter pointers can break. Build tests catch signature mismatches; runtime tests should instantiate a filter over a fake driver and assert that returned user/bucket/object/multipart/lifecycle/writer objects are wrapped and that forwarded method parameters are unchanged.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_sal_filter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_sal_fwd.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_sal_fwd.h

## Purpose
Provides lightweight forward declarations and small shared aliases for RGW SAL consumers. It lets headers refer to SAL classes and common attribute/filter types without including the full `rgw_sal.h` interface.

## Important APIs, types, and functions
At namespace `rgw`, `AccessListFilter` is a `std::function<bool(const std::string&, std::string&)>` used by listing paths to decide whether a listed name/key is accepted. `AccessListFilterPrefix(std::string prefix)` returns a lambda that accepts entries whose key starts with the captured prefix.

At namespace `rgw::sal`, `Attrs` aliases `std::map<std::string, ceph::buffer::list>`, the common representation for RGW metadata attributes. The file forward declares the core SAL classes and structs: `Driver`, `User`, `UserList`, `Bucket`, `BucketList`, `Object`, `MultipartUpload`, `Lifecycle`, `Restore`, `Notification`, `Writer`, `PlacementTier`, `ZoneGroup`, `Zone`, `LuaManager`, `RGWRole`, role/group/topic lists, data/object processors, stats callbacks, and config writer types.

## Control flow
There is no runtime control flow beyond `AccessListFilterPrefix()`. The returned lambda captures `prefix` by value and checks `key.substr(0, prefix.size())`.

## State and persistence behavior
This header owns no state and performs no persistence. Its only runtime state is the prefix captured inside a filter lambda. `Attrs` describes in-memory attribute maps used by concrete drivers to pass metadata to and from persistence layers.

## Dependencies and integration points
The header includes standard functional/map/string headers and `include/buffer_fwd.h` for buffer forward declarations. It is a dependency-management helper for code that needs SAL names or attrs without pulling in larger RGW headers.

## Risks and test signals
`AccessListFilterPrefix()` ignores the `name` argument and uses `key`; callers must pass the intended comparison string as `key`. Prefix filtering should be tested with empty prefixes, shorter keys, exact matches, and non-matches. Because this is a forward declaration header, compile coverage is the primary signal: stale declarations or alias changes surface as build failures in includers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_sal_fwd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_sal_store.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_sal_store.h

## Purpose
Defines shared base classes for store-backed SAL implementations. These classes provide common in-memory state and default behavior for concrete drivers such as dbstore or RADOS-derived stores, reducing duplication across user, bucket, object, multipart, serializer, notification, writer, placement, zone, restore, and Lua manager implementations.

## Important APIs, types, and functions
`RGWObjState` is the central object-state structure. It stores object identity, atomic/prefetch/compression flags, existence and delete-marker flags, size/accounted size, mtime, epoch, tags, shadow object, optional prefetched data, OLH state, version tracker, and attribute map. Its copy constructor intentionally copies selected fields and warns maintainers to keep it updated.

`StoreDriver` derives from `Driver`, supplies random request ids, and gives default unsupported topic/pubsub methods. `StoreUser` owns `RGWUserInfo`, `RGWObjVersionTracker`, and `Attrs`, and implements basic getters/setters. `StoreBucket` owns `RGWBucketInfo`, attrs, version, and mtime, and implements bucket identity, owner, placement, versioning, comparison, topic/logging defaults, and metadata accessors.

`StoreObject` owns `RGWObjState`, an optional `Bucket*`, and tracing context. It implements generic object getters/setters, state invalidation that preserves selected flags, attr access, bucket binding, object identity updates, cloud-transition default failures, torrent attr lookup, version tracker access, and printing.

Other base classes include `StoreMultipartPart`, `StoreMultipartUpload`, `StoreMPSerializer`, `StoreLCSerializer`, `StoreRestoreSerializer`, `StoreRestore`, `StoreNotification`, `StoreWriter`, `StorePlacementTier`, `StoreZoneGroup`, `StoreZone`, and `StoreLuaManager`.

## Control flow
This header is mostly inline methods. Concrete drivers inherit the base state containers and override storage operations. Common operations such as object attr lookup, bucket equality, request-id generation, and Lua path/background setters execute directly in the base classes.

## State and persistence behavior
The file defines cached SAL state but does not persist by itself. Concrete drivers decide when to load or store `RGWUserInfo`, `RGWBucketInfo`, `RGWObjState`, attrs, versions, multipart parts, and serializer locks. `StoreObject::invalidate()` is important state control: it clears loaded object state while preserving object identity and selected caller-set flags. `StoreMultipartUpload` owns a map of part wrappers and a trace context.

## Dependencies and integration points
The header includes `rgw_sal.h` and is included by concrete store implementations such as `rgw_sal_dbstore.h`. It relies on RGW types for users, buckets, objects, lifecycle, pubsub, logging, tracing, restore, and Lua.

## Risks and test signals
The `RGWObjState` copy constructor omits some fields present in the struct, including `is_dm`, `tail_tag`, `has_attrs`, and some zone/data fields, so changes to object state require careful review. Base defaults returning success for bucket topics/logging can mask unsupported persistence if a concrete driver forgets to override them. `StoreBucket::operator!=()` returns false on differing dynamic types, mirroring `operator==()` behavior and deserving caller scrutiny. Tests should cover state invalidation, attr lookup, object copy behavior, bucket equality across same/different dynamic types, torrent attr lookup, and concrete driver override coverage for any default success methods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_sal_store.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_signal.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_signal.cc

## Purpose
Implements RGW signal helpers for log reopening and graceful shutdown wakeups. The file bridges asynchronous process signals to synchronous server shutdown code with a socketpair and exposes handlers used by RGW main process setup.

## Important APIs, types, and functions
`signal_fd` is a static two-element socketpair descriptor array. `sig_handler_noop()` intentionally does nothing. `sighup_handler()` reopens the RGW ops log if present and then asks the global Ceph context to reopen logs. `signal_fd_init()` creates the socketpair, and `signal_fd_finalize()` closes both descriptors.

`signal_shutdown()` writes an integer token to `signal_fd[0]`. `wait_shutdown()` blocks reading the token from `signal_fd[1]` using `safe_read_exact()`. `handle_sigterm()` logs signal handling, calls `signal_shutdown()` for signals other than `SIGUSR1`, and arms an `alarm()` using `rgw_exit_timeout_secs` as a safety net for orderly shutdown.

## Control flow
Startup code calls `signal_fd_init()` before installing handlers. When a terminating signal arrives, `handle_sigterm()` writes to the socketpair to wake code waiting in `wait_shutdown()` or blocked in frontend accept loops. If shutdown stalls, the alarm provides a later forced wakeup/termination path. SIGHUP follows a separate control flow that reopens log files without initiating shutdown.

## State and persistence behavior
The only local state is the socketpair descriptors. Persistent effects are external: log files are reopened, shutdown waiters are woken, and process alarm state is modified. The code uses global `g_ceph_context` and `rgw::AppMain::ops_log_file`.

## Dependencies and integration points
The file includes Ceph signal handling, safe IO, errno formatting, RGW main/log headers, and optional `sys/prctl.h`. It uses `derr`, `dout`, and the RGW logging subsystem. It integrates with process-level signal registration and frontend shutdown loops.

## Risks and test signals
`signal_shutdown()` writes to `signal_fd[0]` and `wait_shutdown()` reads from `signal_fd[1]`; tests should confirm this direction matches the created socketpair usage. Calling shutdown before successful `signal_fd_init()` would write to descriptor `0`, so initialization ordering matters. Signal handlers perform operations such as logging, reopening logs, and writing through wrappers, which should be reviewed against async-signal-safety expectations for the actual registration path. Tests should cover socketpair init/finalize, a shutdown write waking a waiter, error handling when descriptors are invalid, SIGHUP log reopen behavior with and without an ops log, and `SIGUSR1` avoiding `signal_shutdown()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_signal.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_signal.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_signal.h

## Purpose
Declares the RGW signal helper interface implemented by `rgw_signal.cc`. It gives RGW startup and signal-registration code a small API for no-op handling, log reopening, shutdown notification, and socketpair lifecycle.

## Important APIs, types, and functions
The namespace `rgw::signal` declares `sig_handler_noop(int)`, `sighup_handler(int)`, `signal_shutdown()`, `wait_shutdown()`, `signal_fd_init()`, `signal_fd_finalize()`, and `handle_sigterm(int)`. `handle_sigterm(int)` is declared twice, which is harmless for matching declarations but indicates header cleanup is needed.

## Control flow
Consumers initialize the signal fd pair, install handlers, then use `wait_shutdown()` on the synchronous side and `signal_shutdown()`/`handle_sigterm()` on the signal side. SIGHUP is routed to `sighup_handler()` for log reopen rather than shutdown.

## State and persistence behavior
The header owns no state. It exposes functions that manipulate static state in the implementation file and external process/logging state.

## Dependencies and integration points
The header has no includes beyond `#pragma once`, keeping it lightweight for RGW main-process code. It integrates with Ceph's global signal handling setup and RGW frontend shutdown coordination.

## Risks and test signals
The duplicate `handle_sigterm()` declaration should be removed to reduce noise. Build coverage validates declaration/definition agreement. Runtime tests should include code that includes only this header and links against `rgw_signal.cc`, then verifies init, shutdown wakeup, finalize, SIGHUP, and SIGTERM handler behavior through the public API.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_signal.h -->
