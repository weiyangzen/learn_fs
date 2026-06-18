# sources/distributed-fs/moosefs/mfsmaster/filesystem.h

## Purpose
`filesystem.h` is the public contract for the MooseFS master metadata filesystem engine. It exposes the operations that client service code, metadata load/store, changelog replay, chunk management, quota/xattr/ACL subsystems, trash/sustained handling, and diagnostic tooling use to inspect and mutate the in-memory filesystem namespace.

This header is broad by design: it does not implement behavior, but it defines the master-side API surface for regular namespace operations, metadata-replication replay (`fs_mr_*`), metadata serialization, consistency checking, and runtime reporting.

## Important APIs, Types, And Constants
The header depends on `bio.h` for binary metadata I/O and `MFSCommunication.h` for shared protocol constants such as `MFS_NAME_MAX`, `MFS_PATH_MAX`, `ATTR_RECORD_SIZE`, `MAXSCLASS`, and `EATTR_BITS`.

The `fs_mr_*` family is the metadata-replay surface. These functions apply already-authorized, logged mutations such as create, symlink, unlink, move, link, length/truncate/write/rollback, lock unlocks, storage-class changes, trash-retention changes, extended attributes, ACLs, quotas, archiving status, trash operations, and free-inode housekeeping. Many accept a timestamp and exact inode/checksum/counter values, indicating that they are replaying deterministic changelog records rather than making policy decisions.

The live namespace API includes lookup and permission operations (`fs_path_lookup`, `fs_lookup`, `fs_getattr`, `fs_access`, `fs_opencheck`), creation/mutation operations (`fs_mknod`, `fs_mkdir`, `fs_symlink`, `fs_unlink`, `fs_rmdir`, `fs_rename`, `fs_link`, `fs_snapshot`, `fs_append_slice`), and chunk/length operations (`fs_try_setlength`, `fs_end_setlength`, `fs_do_setlength`, `fs_readchunk`, `fs_writechunk`, `fs_writeend`, `fs_filechunk`, `fs_rollback`, `fs_repair`). These functions typically take a `rootinode`, session flags, caller uid/gid/group list information, and output buffers for attributes or resulting chunk IDs.

Metadata feature APIs cover storage classes (`fs_getsclass`, `fs_setsclass`), trash retention (`fs_gettrashretention_prepare`, `fs_gettrashretention_store`, `fs_settrashretention`), extra attributes (`fs_geteattr`, `fs_seteattr`), xattrs (`fs_listxattr_leng`, `fs_listxattr_data`, `fs_setxattr`, `fs_getxattr`), ACLs (`fs_setfacl`, `fs_getfacl_size`, `fs_getfacl_data`), archive markers (`fs_archget`, `fs_archchg`), quotas (`fs_quotacontrol`, `fs_getquotainfo`), and additional attributes (`fs_set_additional_attributes` and replay counterpart `fs_mr_additionalattr`).

The metadata lifecycle API includes `fs_new`, `fs_afterload`, `fs_check_consistency`, `fs_importnodes`, `fs_loadnodes`, `fs_loadedges`, `fs_loadfree`, `fs_loadquota`, `fs_storenodes`, `fs_storeedges`, `fs_storefree`, `fs_storequota`, `fs_cleanup`, `fs_get_memusage`, and `fs_strinit`. These are the hooks used by the metadata manager for startup, restore, persistence, validation, and shutdown.

## Control Flow
The header separates policy-time operations from replay-time operations. Client-facing paths usually receive root/session context, user identity, group lists, and output buffers, then return MooseFS status codes. Replay paths generally receive exact mutation data and are expected to reproduce prior metadata changes while preserving versioning and consistency.

Several APIs use two-step buffer construction: a `*_size` or `*_prepare` call computes size and stores an opaque cursor pointer, followed by a `*_data` or `*_store` call that serializes records into the caller-provided buffer. This pattern appears for directory reads, xattr listing, trash/sustained directory views, ACL retrieval, parent/path retrieval, and trash retention reporting.

Chunk modification flows are explicitly staged. `fs_try_setlength` prepares a length change and returns indexes/chunk IDs, `fs_end_setlength` completes chunk-side coordination, and `fs_do_setlength` commits metadata and returns the previous length. Similarly, write flow starts with `fs_writechunk`, finishes with `fs_writeend`, and can use `fs_rollback` if chunk allocation/write coordination fails.

## State And Persistence Behavior
This header represents the master filesystem's authoritative in-memory namespace state and its serialized metadata image. Persistence is exposed through `bio`-based load/store functions for nodes, edges, free inode state, and quota state. Changelog replay is represented by the `fs_mr_*` entry points, and emergency version synchronization from the chunks module is exposed via `fs_incversion`.

The API also tracks derived state such as statistics, charts data, memory usage, trash/sustained views, quota counters, xattr/ACL flags, and detached metadata for trash and sustained nodes. Functions like `fs_set_xattrflag`, `fs_del_xattrflag`, `fs_set_aclflag`, and `fs_del_aclflag` show that auxiliary subsystems update inode-level feature flags in the core filesystem structures.

## Dependencies And Integration Points
Primary integration points are the master client protocol service (`matoclserv`), metadata manager (`metadata.c`), restore/changelog handling, chunkserver/chunk modules, open-file/session modules, quota and ACL/xattr modules, and master tools that list trash/sustained/quota/path information.

The API is protocol-shaped: many functions serialize into `ATTR_RECORD_SIZE` records or lists defined by `MFSCommunication.h`, and return `uint8_t` status values from the MooseFS error/status code space. It also integrates with `bio` for binary metadata persistence rather than plain file descriptors.

## Risks
The main risk is contract drift. Because this header is a large central API with many output buffers and pointer parameters, mismatched buffer sizes, wrong ownership expectations for returned pointers, or inconsistent replay/live semantics can corrupt metadata or expose protocol bugs.

Authorization and root/session scoping are also sensitive. Many live operations accept both effective and auxiliary identities (`uid`, `gids`, `gid`, `auid`, `agid`) plus session flags, so callers must pass the correct identity model for permission checks, setuid/setgid clearing, and trash/snapshot behavior.

Metadata replay functions are high risk because they bypass normal user-facing decision paths and rely on exact logged inputs. Any caller that invokes `fs_mr_*` outside restore/replication semantics could skip validation or desynchronize counters/checksums.

## Test Signals
Useful tests include metadata save/load round trips, changelog replay equivalence against live operations, permission/ACL/xattr/quota behavior at protocol boundaries, chunk write/truncate rollback scenarios, trash/sustained lifecycle tests, and consistency checks through `fs_check_consistency`. Fuzzing or property tests around path lookup, rename/link/unlink, and staged chunk-length flows would be especially valuable because those paths combine namespace state, permissions, persistence, and external chunk IDs.
