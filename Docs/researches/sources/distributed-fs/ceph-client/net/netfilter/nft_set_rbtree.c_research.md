
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_set_rbtree.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_set_rbtree.c

## Purpose

`nft_set_rbtree.c` implements an interval-capable nftables set backend using an rb-tree for updates and a compact RCU-published sorted interval array for fast lookups.

## Important APIs, Types, and Functions

`struct nft_rbtree` owns the rb root, rwlock, active interval array, pending array, GC state, and overlap cookies. `struct nft_rbtree_elem` stores each interval boundary. Lookup uses `nft_rbtree_lookup()` and `bsearch()` over `struct nft_array_interval`. Updates use `nft_rbtree_insert()`, `__nft_rbtree_insert()`, `nft_rbtree_deactivate()`, `nft_rbtree_remove()`, and `nft_rbtree_commit()`. GC uses `nft_rbtree_gc_scan()` and `nft_rbtree_gc_queue()`.

## Control Flow

Insert allocates or resizes the pending interval array, then takes the write lock and walks the rb-tree to detect exact duplicates and partial overlaps, collecting expired elements as needed. Accepted elements are linked into the rb-tree in reversed ordering. Commit rebuilds `array_next` by reverse-walking the tree from smallest to largest logical interval, publishes it with RCU, frees the old array later, and queues expired elements. Read lookup never walks the tree; it binary-searches the current array and rejects expired starts.

## State and Persistence Behavior

Persistent state exists in both the mutable rb-tree and immutable lookup array. `array_next` is transaction state and is discarded on abort. Expired elements are moved to `expired` and freed after a new array is public. Start cookies correlate paired start/end operations for interval validation across a transaction timestamp.

## Dependencies and Integration Points

The backend integrates with rbtrees, rwlocks, RCU, bsearch, nf_tables interval semantics, generation masks, timeout GC, and set size hiding via `ksize`, `usize`, and `adjust_maxsize`.

## Risks and Test Signals

Risks include overlap detection mistakes, array rebuild capacity errors, reversed ordering confusion, stale array readers, anonymous adjacent interval packing, and GC removing interval ends before starts. Test interval add/delete, anonymous packed intervals, duplicate and partial overlap errors, timeout expiry, abort/commit, read lookup during updates, and max-size accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_set_rbtree.c -->
