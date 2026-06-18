<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/hashtab.h -->
# sources/distributed-fs/ceph-client/security/selinux/ss/hashtab.h

## Purpose
Declares a small generic hash table abstraction for SELinux policy data. It stores opaque key/datum pointers and relies on caller-provided hash and comparison functions.

## Important APIs, Types, and Functions
Types are `struct hashtab_key_params`, `struct hashtab_node`, `struct hashtab`, and `struct hashtab_info`. Inline APIs are `hashtab_insert()` and `hashtab_search()`. External APIs cover init, low-level insertion, destroy, map, duplicate, and optional stats. `HASHTAB_MAX_NODES` caps element count at `U32_MAX`.

## Control Flow
Insertion reschedules if needed, hashes the key, walks the sorted chain using the caller comparison, rejects exact duplicates, and inserts before the first greater key. Search uses the same ordering and stops early if comparison becomes negative.

## State and Persistence
The header defines in-memory table shape only. Keys and data remain caller-owned unless a specific destroy/map callback frees them. The table's sorted chains make deterministic traversal possible within hash buckets.

## Dependencies and Integration Points
Depends on Linux errno/types/scheduler APIs. Used by policy symbol tables, conditional boolean duplication, and other security-server structures that need generic keyed storage.

## Risks
Correctness depends entirely on hash and comparison functions being stable and mutually consistent. Callers must not insert into uninitialized or zero-sized tables. Ownership is not encoded in the type system, making leaks or double-frees possible in map/destroy users.

## Test Signals
Use multiple key types, duplicate insertion, sorted early-stop search, max-node/zero-size errors, callback abort from `hashtab_map()`, and copy/destroy ownership tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/hashtab.h -->
