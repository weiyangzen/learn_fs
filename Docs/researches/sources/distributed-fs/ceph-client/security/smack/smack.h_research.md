# sources/distributed-fs/ceph-client/security/smack/smack.h

## Purpose
`smack.h` is the central Smack LSM header. It defines labels, per-object security blobs, access rule structures, network label structures, mount options, access mode flags, audit wrappers, global state declarations, and helper accessors for kernel object blobs.

## Important APIs, Types, and Functions
Core types include `smack_known`, `superblock_smack`, `socket_smack`, `inode_smack`, `task_smack`, `smack_rule`, IPv4/IPv6 network label entries, optional port labels, and audit structs. It declares access APIs from `smack_access.c`: `smk_access_entry()`, `smk_access()`, `smk_tskacc()`, `smk_curacc()`, label import/parse functions, secid lookup, NetLabel population, and privilege helpers. Inline accessors map LSM blob offsets to typed Smack structures for creds, files, inodes, IPC, superblocks, sockets, keys, and tasks.

## Control Flow
Feature macros select IPv6 port labeling versus secmark labeling. `MAY_DELIVER` depends on `CONFIG_SECURITY_SMACK_APPEND_SIGNALS`. Access flags and special labels drive the access algorithm in `smack_access.c` and hooks in `smack_lsm.c`. Audit helpers either initialize `common_audit_data` or compile away when audit is disabled.

## State and Persistence
Smack labels are represented by permanent `smack_known` entries that are added but not deleted. Per-object blobs store pointers to those shared labels and rule lists. Shared globals include known special labels, network lists, onlycap labels, hash slots, and rule cache.

## Dependencies and Integration Points
It integrates with Linux capabilities, LSM hooks/blobs, NetLabel, sockets, IPv6, audit, SysV IPC, keys, superblocks, inodes, tasks, and Smack filesystem configuration.

## Risks
Blob offset helpers must stay synchronized with `smack_blob_sizes`. Label lifetime is intentionally permanent, so import paths must validate labels and avoid unbounded abuse. Configuration-dependent access semantics need tests across option sets.

## Test Signals
Compile with audit, IPv6, netfilter, keys, and append-signal combinations. Runtime tests should cover label import, task/inode/socket blob access, transmute flags, onlycap enforcement, network label paths, and audit-data initialization.
