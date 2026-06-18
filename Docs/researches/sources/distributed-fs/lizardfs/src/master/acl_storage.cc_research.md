# sources/distributed-fs/lizardfs/src/master/acl_storage.cc

Purpose: implementation of deduplicated RichACL storage keyed by inode.

Important APIs/functions: destructor debug sanity check, `AclStorage::Hash::operator()`, `get`, `set`, `erase`, `setMode`, private `ref` and `unref`.

Control flow: `set` interns an ACL in `storage_` and maps the inode to a reference-wrapped storage entry, unrefing a previous entry if present. `erase` removes an inode mapping and decrements/removes the interned ACL. `setMode` copies the inode ACL, mutates mode bits, and re-interns only if changed. Hashing combines ACL masks, flags, and ACE fields.

State and persistence: in-memory only; `storage_` holds unique ACLs with refcounts and `acl_` maps inode IDs to interned entries.

Dependencies and integration: depends on `RichACL`, `hashCombine`, and master metadata code that stores inode ACLs.

Risks: reference wrappers into an unordered map are safe only while entries are not erased; all lifecycle changes must go through `ref`/`unref`. Destructor assertions are debug-only and not runtime recovery.

Test signals: covered by `acl_storage_unittest.cc`.
