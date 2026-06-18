# sources/distributed-fs/lizardfs/src/master/acl_storage.h

Purpose: declares `AclStorage`, an inode-to-RichACL map with content deduplication.

Important APIs/types/functions: `InodeId`, public noncopyable/nonmovable lifecycle, `get`, `set`, `erase`, `setMode`; private `Hash`, `AclToRefCountMap`, `KeyValue`, `InodeToKVMap`, `ref`, and `unref`.

Control flow: callers manipulate ACLs by inode; implementation interns identical `RichACL` values and tracks references rather than storing duplicates.

State and persistence: owns in-memory `storage_` and `acl_`; persistence is handled by higher-level metadata serialization, not this class.

Dependencies and integration: includes `common/richacl.h`; used by master filesystem metadata.

Risks: intentionally disables copy/move to avoid invalidating reference-wrapper invariants. Public `get` returns a pointer into internal storage that becomes invalid after mutations removing the referenced ACL.

Test signals: `acl_storage_unittest.cc` validates interning, erase, and mode update behavior.
