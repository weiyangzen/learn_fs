# sources/distributed-fs/lizardfs/src/master/filesystem_store_acl.cc

Purpose: serializes and deserializes ACL metadata, including migration from legacy extended/default ACL encodings to current `RichACL` storage.

Important APIs/types/functions: `fs_store_acls()` iterates all nodes and writes present `RichACL` entries followed by a zero marker; `fs_load_legacy_acls()` loads old combined extended/default ACL records and converts them; `fs_load_posix_acls()` loads separate access and default POSIX ACL streams; `fs_load_acls()` loads current `RichACL` records. Helper loaders validate entry size, inode existence, and default-ACL directory constraints.

Control flow: each loader repeatedly reads a serialized-size prefix; size zero ends the stream. For legacy/POSIX entries it resolves the inode, deserializes ACL content, merges with any existing `RichACL`, and updates node mode for access ACLs. Current ACL loading directly sets `gMetadata->acl_storage`.

State and persistence behavior: ACLs are persisted in the metadata `ACLS` section. Loading mutates `gMetadata->acl_storage` and may mutate `FSNode::mode` during legacy/POSIX conversion. It does not emit changelog entries because it is part of metadata image loading.

Dependencies/integration: depends on serialization, `FSNode` lookup, `RichACL`, POSIX/legacy ACL classes, metadata singleton, and the store section dispatcher in `filesystem_store.cc`.

Risks and test signals: bad entry sizes above 10,000,000 are rejected; ignore mode can skip recoverable exceptions. Setting a default ACL on a non-directory is fatal unless ignored. Header/API mismatch risk exists because the header declares `fs_store_acls()` as `int` while the implementation returns `void`. Tests should cover all three section versions, mode recalculation, merge ordering of access/default ACLs, missing inode behavior, and the header/implementation type contract.
