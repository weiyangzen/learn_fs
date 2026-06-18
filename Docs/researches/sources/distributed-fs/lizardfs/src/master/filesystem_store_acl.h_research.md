# sources/distributed-fs/lizardfs/src/master/filesystem_store_acl.h

Purpose: declares ACL metadata section load/store functions used by `filesystem_store.cc`.

Important APIs/types/functions: exposes `fs_load_legacy_acls()`, `fs_load_posix_acls()`, `fs_load_acls()`, and `fs_store_acls(FILE *)`.

Control flow: the metadata section dispatcher chooses one of the load functions based on section label `ACLS 1.0`, `ACLS 1.1`, or `ACLS 1.2`; storing uses the current ACL writer.

State and persistence behavior: no state in the header; the declared functions mutate/persist `gMetadata->acl_storage` and sometimes node modes during migration.

Dependencies/integration: includes platform, `FILE`, exceptions, and `MetadataDumper`, though the actual ACL interface mostly needs file I/O and metadata types from implementation includes.

Risks and test signals: the declaration says `int fs_store_acls(FILE *fd)` while the implementation defines `void fs_store_acls(FILE *fd)`, a compile/link contract risk if both are included consistently. Tests/builds should compile the implementation with its header and verify store error signaling expectations.
