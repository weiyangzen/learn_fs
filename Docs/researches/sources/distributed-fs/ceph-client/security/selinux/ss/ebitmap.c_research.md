<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/ebitmap.c -->
# sources/distributed-fs/ceph-client/security/selinux/ss/ebitmap.c

## Purpose
Implements extensible bitmaps used for SELinux type, role, category, and class sets. The representation is a sorted linked list of fixed-size bitmap nodes, allowing sparse arbitrary-size bitsets and binary policy serialization.

## Important APIs, Types, and Functions
Public APIs include `ebitmap_equal()`, `ebitmap_cpy()`, `ebitmap_and()`, `ebitmap_contains()`, `ebitmap_get_bit()`, `ebitmap_set_bit()`, `ebitmap_destroy()`, `ebitmap_read()`, `ebitmap_write()`, `ebitmap_hash()`, `ebitmap_cache_init()`, and optional NetLabel import/export functions. The implementation uses `ebitmap_node_cachep`.

## Control Flow
Set/get operations walk sorted nodes by `startbit`; setting a bit allocates a node aligned to `EBITMAP_SIZE`, and clearing the last bit in a node removes it. Copy duplicates every node. `ebitmap_and()` iterates positive bits in the first bitmap and sets bits present in the second. Policy read validates map unit size, highbit/count consistency, aligned starts, nonempty maps, ordering, and final highbit. Write compacts positive bits into 64-bit serialized maps.

## State and Persistence
State is per-`struct ebitmap` linked nodes plus `highbit`. Nodes are slab allocated. Persisted state is policy-file bitmap records. NetLabel export/import converts between SELinux ebitmap nodes and NetLabel category maps.

## Dependencies and Integration Points
Depends on bit operations, jhash, policy I/O helpers, NetLabel category maps, and callers in MLS, constraints, roles/types, and policydb symbol data.

## Risks
Serialized bitmap validation is critical; accepting out-of-order or empty maps could corrupt policy state. `highbit` is rounded to node boundaries internally but written as last set bit rounded to 64-bit units. NetLabel import copies category maps into both MLS levels elsewhere, so ownership and destruction must be correct on failure.

## Test Signals
Test sparse and dense bitmaps, set/clear node creation and removal, copy/and/contains/equality, policy read rejection for bad mapunit/alignment/empty map/truncation, write/read round trips, NetLabel category import/export, and hash consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/ebitmap.c -->
