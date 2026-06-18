<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_bio_io.c -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_bio_io.c

Purpose: Provides a synchronous metadata-oriented block-device read/write helper that can handle both linear and vmalloc-backed buffers.

Important APIs: `xfs_rw_bdev` performs a read or write to a block device at a sector/count/data tuple with `REQ_META | REQ_SYNC`. `bio_max_vecs` computes bio vector demand from byte count.

Control flow: Non-vmalloc buffers are passed to `bdev_rw_virt`. Vmalloc buffers allocate a bio, add vmalloc chunks until full, chain and submit prior bios as needed, then wait for the final bio. After reads, it invalidates the kernel vmap range so CPU mappings see device data.

State and persistence: Writes synchronously persist caller-provided metadata buffer contents to the block device; reads fill the caller buffer. The helper itself stores no long-lived state.

Dependencies and integration: Uses Linux block layer bios, vmalloc helpers, bio chaining, `submit_bio_wait`, and block-device direct virtual I/O helper. It is suitable for XFS metadata paths needing synchronous device access outside the normal buffer cache.

Risks: Correct behavior depends on bio chaining and chunk accounting; a zero `bio_add_vmalloc_chunk` triggers a new chained bio. The final `if (op == REQ_OP_READ)` comparison is fragile because `op` has flags ORed into it, so tests should verify read invalidation behavior or inspect expected semantics.

Test signals: Synchronous read/write with kmalloc and vmalloc buffers, multi-bio vmalloc transfers, error propagation from `submit_bio_wait`, and read-side vmap invalidation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_bio_io.c -->
