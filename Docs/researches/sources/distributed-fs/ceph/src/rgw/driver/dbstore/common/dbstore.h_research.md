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
