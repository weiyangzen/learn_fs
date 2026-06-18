<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/list_bl.h -->
# sources/distributed-fs/ceph-client/include/linux/list_bl.h

## Purpose
This header implements bit-locked hlist buckets. It packs a bucket lock bit into the low bit of the first-node pointer so hash tables can have compact per-bucket locking without a separate spinlock per bucket.

## Important APIs, Types, and Functions
`struct hlist_bl_head` stores `first`, whose low bit is `LIST_BL_LOCKMASK`; `struct hlist_bl_node` stores `next` and `pprev`. APIs include `INIT_HLIST_BL_HEAD`, `INIT_HLIST_BL_NODE`, `hlist_bl_first`, `hlist_bl_empty`, `hlist_bl_add_head`, `hlist_bl_add_before`, `hlist_bl_add_behind`, `hlist_bl_del`, `hlist_bl_del_init`, `hlist_bl_lock`, `hlist_bl_unlock`, `hlist_bl_is_locked`, and traversal macros.

## Control Flow
Readers mask the lock bit before dereferencing the first node. Writers acquire the bit spinlock on the bucket head, update hlist links, and preserve lock-bit encoding when replacing `first`. Deletion mirrors hlist deletion and poisons or reinitializes nodes depending on the public helper.

## State and Persistence Behavior
State is caller-owned bucket heads and nodes. The lock bit is transient synchronization state and must never leak into node pointers after masking. The header has no persistence behavior.

## Dependencies and Integration Points
It depends on `linux/list.h` and `linux/bit_spinlock.h`. Typical integration is memory-sensitive hash tables where each bucket needs local exclusion.

## Risks and Test Signals
Risks include forgetting to hold the bucket lock for mutation, dereferencing an unmasked first pointer, and alignment assumptions that would make the low bit unavailable. Test signals include debug list assertions, lockdep coverage around bucket locking, hash-table insertion/deletion stress, and KASAN reports for corrupted links.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/list_bl.h -->
