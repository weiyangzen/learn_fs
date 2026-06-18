# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_icm_pool.c

Purpose: manages SWS ICM device-memory pools for STEs, modify actions, and modify-header patterns, including device-memory allocation, mkey registration, buddy suballocation, hot/free-after-sync handling, and STE software cache setup.

Important APIs/functions/types: `mlx5dr_icm_pool_create/destroy`, `mlx5dr_icm_alloc_chunk`, `mlx5dr_icm_free_chunk`, `mlx5dr_icm_pool_alloc_htbl/free_htbl`, address/key/size helpers (`get_chunk_mr_addr`, `get_chunk_rkey`, `get_chunk_icm_addr`, `get_chunk_byte_size`, `get_chunk_num_of_entries`), and internal `mlx5dr_icm_pool`, `mlx5dr_icm_mr`, and hot chunk records.

Control flow: pool creation sets max chunk size and hot-memory threshold by ICM type, creates a hot chunk array, and later lazily creates buddy memories. Buddy creation allocates SW ICM device memory, registers an mkey, initializes a buddy allocator, and for STE pools preallocates software STE, HW STE byte, and miss-list caches. Chunk allocation finds or creates a buddy with free space, allocates a chunk object, initializes STE cache pointers, and updates used memory. Free moves the segment into a hot array, frees the chunk object, and syncs steering plus returns hot segments to buddies when threshold is exceeded.

State/persistence: pools hold buddy memory lists, hot chunks awaiting hardware sync, mkeys, device-memory object IDs, ICM start addresses, and kmem caches. Hardware may keep reading freed chunks until `sync_steering` completes; hot memory models that delayed reclamation.

Dependencies/integration: depends on buddy allocator, mlx5 SW ICM allocation/deallocation, mkey creation/destruction, domain PD/caps, command sync, and STE/table code that consumes chunks.

Risks: hot chunk array sizing must cover threshold behavior; overflow would corrupt memory. Sync is required before reusing freed hardware-visible memory. Destroy clears hot chunks before destroying buddies, so outstanding users at destroy are unsafe. Alignment and entry-size calculations must match PRM for each ICM type.

Test signals: allocation/free for all ICM types and chunk sizes, threshold-triggered sync and buddy destruction, address/rkey helper correctness, partial failure of DM/mkey/buddy/STE cache allocation, randomized buddy reuse, and destroy with no outstanding chunks.
