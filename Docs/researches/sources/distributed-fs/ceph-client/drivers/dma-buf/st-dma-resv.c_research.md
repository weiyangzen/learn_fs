# sources/distributed-fs/ceph-client/drivers/dma-buf/st-dma-resv.c

Purpose: selftests dma-resv reservation objects across all usage classes for locking, signaling visibility, locked/unlocked iteration, and fence extraction.

Important APIs/types/functions: defines a shared `fence_lock`, mock fence allocation, subtests `sanitycheck`, `test_signaling`, `test_for_each`, `test_for_each_unlocked`, `test_get_fences`, and top-level `dma_resv()`.

Control flow: `dma_resv()` initializes the fence lock and runs the same subtest set for `DMA_RESV_USAGE_KERNEL` through `DMA_RESV_USAGE_BOOKKEEP`. Each subtest allocates a mock fence, enables signaling, initializes a reservation object, reserves one slot under lock, adds the fence with the current usage, then validates the API under test. Unlocked iteration intentionally corrupts the cursor list pointer mid-test to force a restart path. Cleanup signals the fence, finalizes the reservation, drops fence refs, and frees extracted arrays.

State and persistence behavior: reservation and fence state are temporary per subtest. The shared spinlock is initialized once at suite entry and used as external fence lock for allocated fences.

Dependencies and integration points: depends on dma-resv and dma-fence APIs plus the selftest harness. It validates the same reservation semantics used by dma-buf, DRM, and sync-file integration.

Risks and test signals: tests use one fence per usage and do not cover multi-fence compaction or replacement, but they exercise the essential API contracts. Passing signals include successful ww_mutex lock/unlock, unsignaled then signaled reservation status, locked iteration returning the expected usage/fence, unlocked iterator restart detection, and `dma_resv_get_fences()` returning one referenced fence.
