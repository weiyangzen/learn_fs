<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_sync.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_sync.c

## Purpose
`radeon_sync.c` builds per-submission synchronization state from Radeon fences and reservation objects. It decides when to use GPU semaphores for cross-ring ordering and when to fall back to CPU waits.

## Important APIs, types, and functions
The file operates on `struct radeon_sync`, with arrays of target fences per ring and temporary semaphores. Public functions are `radeon_sync_create`, `radeon_sync_fence`, `radeon_sync_resv`, `radeon_sync_rings`, and `radeon_sync_free`. It relies on `radeon_fence_later`, `radeon_fence_need_sync`, `radeon_fence_note_sync`, `radeon_fence_wait`, DMA reservation iteration, and semaphore creation/emission.

## Control flow
Creation clears all semaphore and fence slots. `radeon_sync_fence` keeps only the later fence per ring and separately tracks the latest VM update fence. `radeon_sync_resv` iterates a DMA reservation object: Radeon fences from the same device are recorded, while foreign fences are waited on by CPU. `radeon_sync_rings` walks all ring fences, skips ones that do not require sync to the target ring, rejects disabled source rings, creates semaphores while capacity remains, emits a signal on the source ring and a wait on the target ring, then commits the source ring and records that the fence is synced to the target ring. If semaphore capacity or emission fails, it waits manually. `radeon_sync_free` releases semaphores using the final submission fence.

## State, dependencies, and integration points
The sync object is transient per IB/submission and does not persist beyond cleanup. It integrates with command submission, VM updates, BO reservation validation, and multi-ring scheduling. It assumes the caller already holds the target ring lock and has allocated enough wait-ring space before `radeon_sync_rings`.

## Risks and test signals
Risks include disabled rings causing invalid dependencies, too few semaphore slots, missed foreign-fence waits, uncommitted source-ring signal packets, and deadlock if ring locks are held incorrectly. Test signals include multi-ring sync tests, BO reservation sharing tests, VM update ordering, semaphore/fence tracepoints, and stress submissions across GFX, DMA, UVD, and VCE rings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_sync.c -->
