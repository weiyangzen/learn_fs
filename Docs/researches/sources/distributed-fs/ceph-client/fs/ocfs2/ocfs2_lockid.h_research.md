# sources/distributed-fs/ceph-client/fs/ocfs2/ocfs2_lockid.h

Purpose: defines OCFS2 distributed lock identifier format, lock type enumeration, type-to-character mapping, and human-readable lock type names.

Important APIs and types: lock IDs are fixed at `OCFS2_LOCK_ID_MAX_LEN` bytes and encode a type character, six pad characters, a 16-character hex block number, an 8-character generation, and a NUL terminator. `enum ocfs2_lock_type` lists meta, data, super, rename, rw, dentry, open, flock, quota info, NFS sync, orphan scan, refcount, and trim locks. `ocfs2_lock_type_char()` maps enum values to stable single-character lock name prefixes. `ocfs2_lock_type_string()` maps enum values to display strings through `ocfs2_lock_type_strings`.

Control flow: DLM glue and debug code use the enum to construct lock names and print diagnostics. The inline mapping returns NUL for unknown character mappings, while the string accessor asserts under `__KERNEL__` if the type is out of range.

State and persistence: this header has no shared runtime state, but the lock-name format is part of cluster interoperability. Every node must construct identical names for the same resource.

Dependencies and integration: included by `ocfs2.h` and DLM-related implementation files. It integrates with `struct ocfs2_lock_res` and the cluster lock manager. The dentry lock inode field starts at `OCFS2_DENTRY_LOCK_INO_START`, which is a parsing convention for dentry lock IDs.

Risks: changing type characters, string length, padding, or block/generation offsets breaks cross-node lock compatibility. Adding lock types requires keeping enum values, character mapping, strings, and any lock statistics/debug consumers in sync.

Test signals: multi-node lock acquisition across all lock types, lock-name formatting/parsing tests, DLM debug output checks, invalid enum assertions in debug builds, dentry-lock coherence tests, and rolling-upgrade compatibility where older and newer nodes agree on lock IDs.
