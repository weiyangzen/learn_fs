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
