<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/hashtable.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/hashtable.h

## Purpose
This header implements statically sized hash tables backed by `hlist_head` buckets for tools code.

## APIs And Flow
It exposes `DEFINE_HASHTABLE`, `DECLARE_HASHTABLE`, `HASH_SIZE`, `HASH_BITS`, `hash_min()`, `hash_init()`, `hash_add()`, `hash_hashed()`, `hash_empty()`, `hash_del()`, and iteration macros including safe and bucket-specific variants. Flow is simple: table size is inferred at compile time, keys are reduced with `hash_min()`, and entries are linked into or walked through the selected hlist bucket.

## State, Dependencies, Risks, Tests
State lives in caller-owned hlist bucket arrays and embedded `hlist_node` members. Dependencies include `list.h`, `bitops.h`, `hash.h`, `kernel.h`, `log2.h`, and `types.h`. Unlike the kernel header, RCU variants are absent, so concurrent readers need external synchronization. Tests should cover initialization, empty detection, add/delete, safe deletion during iteration, bucket lookup collisions, and compile failures when a pointer is passed where a fixed array is required.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/hashtable.h -->
