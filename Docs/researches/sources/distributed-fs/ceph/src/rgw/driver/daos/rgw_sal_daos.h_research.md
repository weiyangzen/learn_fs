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
