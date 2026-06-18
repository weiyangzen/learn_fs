# sources/distributed-fs/ceph/src/rgw/driver/daos/rgw_sal_daos.cc

## Purpose

`rgw_sal_daos.cc` implements an RGW SAL backend for DAOS/CORTX DS3. It maps RGW users, buckets, objects, object metadata, multipart uploads, and basic placement/zone abstractions onto the `ds3_*` C API. The file is explicitly a partial backend: basic user/bucket/object/multipart paths are implemented, while many RGW features return `DAOS_NOT_IMPLEMENTED_LOG()`.

The code acts as a bridge between Ceph RGW's SAL contracts and DS3 handles. It serializes Ceph metadata such as `RGWUserInfo`, `RGWBucketInfo`, `rgw_bucket_dir_entry`, attrs maps, object versions, multipart upload info, and compression metadata into DS3 user, bucket, object, upload, and part info buffers.

## Important APIs and Functions

`DaosStore::initialize()` and `finalize()` manage DS3 process and pool connectivity. Initialization calls `ds3_init()`, accepts `DER_ALREADY`, reads the `daos_pool` config value, and calls `ds3_connect()`. Finalization disconnects `ds3` and calls `ds3_fini()`.

User APIs include `DaosStore::get_user()`, `get_user_by_access_key()`, `get_user_by_email()`, `DaosUser::load_user()`, `store_user()`, `read_user()`, `get_encoded_info()`, `merge_and_store_attrs()`, `remove_user()`, and `create_bucket()`. User info is encoded into `DaosUserInfo` and persisted with `ds3_user_set()`, read with `ds3_user_get()` or indexed lookup helpers, and removed with `ds3_user_remove()`. `store_user()` performs a simple object-version check with `objv_tracker.read_version`.

Bucket APIs include `DaosStore::list_buckets()`, `load_bucket()`, `get_bucket()`, and `DaosBucket::open()`, `close()`, `get_encoded_info()`, `put_info()`, `load_bucket()`, `remove()`, `remove_bypass_gc()`, `merge_and_store_attrs()`, `set_acl()`, `get_object()`, `list()`, `list_multiparts()`, and `get_multipart_upload()`. Bucket metadata is encoded as `DaosBucketInfo` and stored via DS3 bucket info calls. Listing decodes DS3 object or multipart upload info into RGW list results.

Object metadata APIs include `DaosObject::load_obj_state()`, `set_obj_attrs()`, `get_obj_attrs()`, `modify_obj_attrs()`, `delete_obj_attrs()`, `get_dir_entry_attrs()`, `set_dir_entry_attrs()`, and `mark_as_latest()`. The backend stores RGW dir entries and attr maps in DS3 object info xattrs, decoding `rgw_bucket_dir_entry` first and optional attrs after it.

Object data APIs include `DaosObject::lookup()`, `create()`, `close()`, `write()`, `read()`, `get_read_op()`, `DaosReadOp::prepare()`, `read()`, `iterate()`, `get_attr()`, `get_delete_op()`, `DaosDeleteOp::delete_obj()`, and `delete_object()`. They open/create DS3 object handles, use `ds3_obj_read()`/`ds3_obj_write()` for byte IO, use `ds3_obj_destroy()` for deletes, and provide a synchronous read-iterate implementation that reads the requested range then calls the RGW callback once.

`DaosAtomicWriter` implements put-object writes. `prepare()` creates the object, `process()` writes incoming buffers at offsets and accumulates total bytes, and `complete()` builds a `rgw_bucket_dir_entry`, handles object-lock default retention attrs, writes encoded metadata/attrs, and calls `mark_as_latest()` for versioned buckets.

Multipart APIs include `DaosMultipartUpload::init()`, `abort()`, `get_meta_obj()`, `list_parts()`, `complete()`, `cleanup_orphaned_parts()`, `get_info()`, `get_writer()`, and `DaosMultipartWriter::prepare()`, `process()`, `complete()`. Upload init creates a DS3 upload entry with encoded dirent, attrs, and `multipart_upload_info`. Part writers write DS3 parts and store encoded `RGWUploadPartInfo` plus attrs. Completion validates part numbers, etags, sizes, and compression metadata, computes the multipart etag, creates the final object, reads each DS3 part, writes concatenated data into the final object, stores final metadata/attrs, marks latest if versioned, then removes the upload.

Zone/placement APIs are minimal. `DaosZoneGroup` resolves placement targets and tiers from in-memory zone config. `DaosZone` returns the current zonegroup/id/name and always reports writable. `DaosStore::valid_placement()` and `get_compression_type()` delegate to zone params. Role, OIDC, lifecycle, restore, sync, quota, usage, and metadata-listing APIs are mostly stubs.

The C ABI factory `newDaosStore()` constructs a `DaosStore` for RGW dynamic loading.

## Control Flow

Startup begins with RGW loading `newDaosStore()`, then calling `initialize()`. DS3 must be initialized and connected to the configured DAOS pool before users, buckets, or objects can be opened. Shutdown calls `finalize()` to disconnect and finalize DS3.

User creation/update flow reads any existing DS3 user, compares object versions, builds old access-id arrays for update semantics, encodes `DaosUserInfo`, and calls `ds3_user_set()`. Bucket creation is routed through `DaosUser::create_bucket()`: it tries `store->load_bucket()`, returns existing bucket metadata when present, or fills `RGWBucketInfo` defaults and calls `ds3_bucket_create()`.

Bucket operations open DS3 bucket handles lazily and idempotently. `load_bucket()` reads and decodes DS3 bucket info, then forces default placement to `default/STANDARD`. `list()` calls `ds3_bucket_list_obj()` with prefix, delimiter, marker, and version-listing flags, decodes entries, filters invisible entries unless listing versions, and sorts unless unordered results are allowed.

Object reads go through `DaosReadOp::prepare()` followed by `read()` or `iterate()`. For versioned buckets without an explicit version, prepare sets the object instance to `DS3_LATEST_INSTANCE`, reads metadata, populates etag attr, object key, and size. `iterate()` opens the object, reads the full requested inclusive range into a bufferlist, and hands it to the RGW callback.

Object writes go through `DaosStore::get_atomic_writer()`. `prepare()` creates the DS3 object. Each `process()` writes the provided buffer at the specified offset and adds to `total_data_size` on success. `complete()` constructs metadata and attr state, persists it with `set_dir_entry_attrs()`, and for versioned buckets updates DS3 latest linkage after downgrading the previous latest object's flags.

Multipart upload flow creates an upload index entry with a generated id, writes parts through DS3 part handles, stores part metadata at part complete, and later completes by listing and validating all parts. Unlike some backends that compose server-side references, this implementation reads every part into RGW memory buffers and writes a newly created final DS3 object sequentially.

## State and Persistence Behavior

The durable state is in DAOS/DS3. `DaosStore` holds the process `CephContext` and `ds3` connection handle. `DaosBucket` holds a DS3 bucket handle `ds3b` that is opened lazily and closed in the destructor. `DaosObject` holds a DS3 object handle `ds3o` that is opened/created lazily and closed in the destructor. Multipart writers hold DS3 part handles and close them in their destructor.

User metadata is encoded as `DaosUserInfo` into `ds3_user_info.encoded`, with access key ids separately exposed through `access_ids`. Bucket metadata is encoded as `DaosBucketInfo` into `ds3_bucket_info.encoded`. Object metadata is encoded as `rgw_bucket_dir_entry` followed by an attrs map into `ds3_object_info.encoded`. Multipart upload metadata is encoded as dirent, attrs, and `multipart_upload_info`; part metadata is encoded as `RGWUploadPartInfo` and attrs.

Versioning support is partial and DS3-specific. Versioned writes set `FLAG_VER | FLAG_CURRENT` and call `mark_as_latest()`, which opens any existing latest object, changes its flags to `FLAG_VER`, then calls `ds3_obj_mark_latest()` on the current object. If a versioned read has no instance, `DaosReadOp::prepare()` sets `DS3_LATEST_INSTANCE`. The delete path explicitly lists versioning TODOs and does not fully implement RGW delete marker semantics.

Object attrs are stored as part of DS3 object info, not separate omap entries. `set_obj_attrs()`, `modify_obj_attrs()`, and `delete_obj_attrs()` read the existing dirent/attrs, mutate the attr map, and rewrite the encoded DS3 object info. `load_obj_state()` only sets size, accounted size, mtime, existence, and etag attr from dirent metadata.

Bucket and object handles are process-local resources. `open()` and `close()` are idempotent, and destructors call close with null dpp. Most methods assume a live `store->ds3` connection and do not try to reconnect after failure.

## Dependencies and Integration Points

The implementation depends on `rgw_sal_daos.h`, Ceph encoding/bufferlist APIs, RGW bucket/object/compression helpers, RGW SAL base types, `std::filesystem` headers, and the C DS3 API: `ds3_init`, `ds3_connect`, user/bucket/object/upload/part operations, and DS3 constants such as `DS3_MAX_ENCODED_LEN`, `DS3_MAX_BUCKET_NAME`, `DS3_MAX_KEY_BUFF`, `DS3_LATEST_INSTANCE`, and multipart id prefixes.

RGW integration is through SAL virtual methods. Admin/user paths use `DaosUser`; bucket and object S3 paths use `DaosBucket`, `DaosObject`, and writer/read/delete op classes; multipart S3 paths use `DaosMultipartUpload` and `DaosMultipartWriter`; notifications return `DaosNotification`; Lua returns `DaosLuaManager`.

Placement integration is minimal and mostly in-memory. `DaosZoneGroup` and `DaosZone` rely on zone params available on the store, but multisite, sync policy, period metadata, service-map registration, lifecycle, restore, usage logging, quota, rate limiting, and metadata listing are not fully implemented.

The implementation returns DS3 error codes directly in many paths while mapping a few specific cases to RGW errors, such as multipart upload `-ENOENT` to `-ERR_NO_SUCH_UPLOAD` and invalid multipart inputs to S3-style errors. Consistent error-code translation is an integration concern.

## Risks and Edge Cases

Feature coverage is the largest risk. Many SAL methods return `DAOS_NOT_IMPLEMENTED_LOG()`, including user stats/usage, bucket stats/quota/index repair, chown, transitions/cloud restore, omap helpers, copy object, Swift versioning, roles, OIDC, append writer, lifecycle/restore, sync, metadata listing, service map, and usage logging. RGW configurations that expect these features will fail or degrade.

Delete and versioning semantics are incomplete. `DaosDeleteOp::delete_obj()` deletes a DS3 object by key and comments that versioning, delete params, empty directories, and missing-file handling are TODOs. This can diverge from S3/RGW behavior for versioned buckets, delete markers, conditional deletes, and lifecycle expiration.

Read and multipart completion are synchronous and potentially memory-heavy. `DaosReadOp::iterate()` reads the entire requested range into one bufferlist before invoking the callback. Multipart completion reads every part into memory one at a time and writes it to the final object, rather than using server-side composition or streaming callbacks. Large objects and high concurrency need stress testing.

Metadata buffer handling relies on fixed `DS3_MAX_ENCODED_LEN` buffers. Large attrs, ACLs, multipart metadata, compression metadata, or user/bucket info can exceed the fixed buffer and cause DS3 failures or truncated/undecodable metadata depending on DS3 behavior.

There are correctness issues worth inspecting. `DaosReadOp::get_attr()` returns `-ENODATA` when `get_dir_entry_attrs()` succeeds because it checks `if (!ret) return -ENODATA;`, which appears inverted. `DaosBucket::set_acl()` builds updated attrs but does not persist them with `put_info()`. `DaosBucket::merge_and_store_attrs()` calls `put_info(dpp, y, ceph::real_time())`, passing `optional_yield` where the signature's second parameter is `bool exclusive`, relying on implicit conversion or compile behavior. Some string copies use `strncpy()` without explicit null termination. `DaosMultipartWriter::complete()` checks `if (ret == ENOENT)` instead of `-ENOENT`.

Concurrency/atomicity is limited. `DaosAtomicWriter` comments that concurrent writes need unique ids or DAOS transactions. User versioning has a simple read-version check, but object writes, metadata rewrites, multipart completion, and latest-version promotion are not transactional at the RGW semantic level.

Error handling often logs and returns raw DS3 codes, but cleanup on partial multipart completion, failed final object writes, or failed metadata updates is limited. `DaosMultipartUpload::complete()` can create/write a final object before metadata or upload removal fails.

## Test Signals

Basic backend tests should cover DS3 initialization/finalization, missing or invalid `daos_pool`, user create/load/update/remove, access-key and email lookup, bucket create/load/list/remove, bucket ACL persistence expectations, and bucket list markers/prefix/delimiter/common prefixes.

Object tests should cover create/write/read/iterate/load state, attr set/modify/delete/get, etag propagation, zero-length writes, missing object lookup, fixed-buffer overflow behavior for large attrs, object expiration attr decoding, and handle idempotent open/close/destructor paths.

Versioning tests should cover versioned write/latest lookup, overwriting latest, reading explicit and latest instances, non-versioned `"null"` instance clearing, and known delete gaps. Tests should make failures explicit so unsupported versioning semantics do not appear accidentally supported.

Multipart tests should cover upload init id uniqueness, part write/complete/list, complete validation for missing parts, wrong order, etag mismatch, too-small parts, compression metadata consistency, final etag calculation, final object metadata, upload removal, abort, and error cleanup. Large multipart tests should measure memory behavior during part concatenation.

Feature-gating tests should assert expected `-ENOTSUP` or not-implemented returns for unsupported SAL methods, including quota/stats/usage, copy object, lifecycle, cloud transition, OIDC/roles, append writer, and metadata listing. Integration tests should verify RGW surfaces these failures predictably rather than crashing.
