# sources/distributed-fs/coda/coda-src/librepair/resolve.h

Purpose: declares the directory-resolution data model and public helper functions for librepair. It defines ACL structures, user repair preferences, directory entry snapshots, replica metadata, conflict counters, and repair-list builders.

Important types/APIs: `Acl`/`AclEntry` model positive and negative ACLs; `repinfo` carries non-interactive repair choices; `resdir_entry` captures child name, FID, version vector, mount-point flag, replica index, and looked-at marker; `resreplica` captures a parent directory replica with entry range, FID, path, mode, ACL, and owner. Exports include `getunixdirreps`, `dirresolve`, `resClean`, `GetParent`, and repair-list manipulation helpers.

State and integration: exposes globals allocated/filled by `resolve.cc`, which couples callers to a single active resolution pass. Dependencies include Coda FID/version-vector types and `struct listhdr` from `repio.h`. Risk centers on global mutable state and opaque ownership of arrays/pointers. Tests should validate multi-replica grouping, ACL parsing, and cleanup.
