# sources/distributed-fs/ceph-client/fs/ocfs2/suballoc.h

Purpose: defines the suballocator API used by OCFS2 allocation, inode creation, extent growth, local alloc, and free paths. It exposes `struct ocfs2_alloc_context` as the reservation/claim state object passed across reservation and journaled claim phases.

Important APIs and types: declares `group_search_t`, `struct ocfs2_alloc_context`, allocation context modes `OCFS2_AC_USE_LOCAL`, `OCFS2_AC_USE_MAIN`, `OCFS2_AC_USE_INODE`, `OCFS2_AC_USE_META`, and `OCFS2_AC_USE_MAIN_DISCONTIG`, plus reservation, claim, free, descriptor, allocator-locking, and inode-bit test functions. Inline helpers compute remaining reserved bits, suballocator group block, cluster group start, and whether an inode is the global cluster bitmap.

Control flow: callers reserve resources with functions such as `ocfs2_reserve_new_inode`, `ocfs2_reserve_new_metadata`, or `ocfs2_reserve_clusters`, then consume them under a journal handle with `ocfs2_claim_*`, and finally release the context with `ocfs2_free_alloc_context`. The special find-location APIs split inode location choice from final claim to support orphan/reflink ordering.

State and persistence behavior: `ocfs2_alloc_context` holds referenced and locked allocator inode state, allocator buffer head, slot, requested and granted bits, search function, chain, last group hint, max block limit, optional reservation map, and deferred inode-location result. It is runtime-only but points at persistent allocator dinodes and group descriptors.

Dependencies and integration points: includes OCFS2 allocator consumers across `alloc.c`, file growth, inode creation, local alloc, and truncate/free logic. It relies on OCFS2 superblock fields for bitmap geometry and on chain allocator on-disk structures declared elsewhere.

Risks: callers must respect the reserve-then-claim lifetime and release locks through `ocfs2_free_alloc_context`. `ac_bits_given` must never exceed `ac_bits_wanted`. The inline group math assumes standard OCFS2 block group placement, with a special case for the first cluster group. Misusing `ocfs2_is_cluster_bitmap` changes journal undo behavior.

Test signals: compile coverage of all allocator consumers, allocation-context leak checks, reserve/claim/free under failures, inode location preclaim followed by exact-location claim, cluster group translation at first and later bitmap groups, and local alloc callers using `ocfs2_reserve_cluster_bitmap_bits`.
