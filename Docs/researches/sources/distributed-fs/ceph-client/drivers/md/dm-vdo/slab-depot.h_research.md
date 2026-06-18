# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/slab-depot.h

## Purpose
`slab-depot.h` defines the in-memory contracts and public APIs for VDO slab allocation, slab journals, reference-count blocks, slab summary blocks, scrubbers, block allocators, and the top-level slab depot.

## Important APIs, Types, And Functions
Key types include `enum reference_status`, `struct journal_lock`, `struct slab_journal`, `struct reference_block`, `struct search_cursor`, `enum slab_rebuild_status`, `struct vdo_slab`, `struct slab_scrubber`, `struct slab_summary_block`, `struct block_allocator`, `enum slab_depot_load_type`, and `struct slab_depot`. Public functions expose load/decode/free/record, reference-count adjustment, provisional allocation, physical block allocation, recovery replay, grow/use/abandon resize paths, drain/resume, forced tail commits, scrub launch, statistics, and dumps.

## Control Flow
The header documents thread ownership: loads and saves originate on the admin thread, normal allocation/reference updates run on the owning physical-zone thread, and recovery-journal tail-commit requests are scheduled from the recovery journal thread into physical-zone threads. Embedded waiters in journal, reference block, and summary structures are used by asynchronous VIO and wait-queue flows implemented in `slab-depot.c`.

## State And Persistence
The structures mirror persistent VDO metadata. `slab_journal` tracks head/unreapable/tail/commit/summarized sequence numbers, recovery locks, thresholds, packed tail block, and on-disk journal locks. `reference_block` tracks dirty/write state and commit points per sector. `vdo_slab` owns physical extents, journal/refcount origins, free counters, search cursor, and admin/rebuild state. `slab_depot` carries slab geometry, summary partition origin, current and resize slab arrays, zone counts, and allocators.

## Dependencies And Integration Points
The header depends on admin state, completions, data VIOs, on-disk encodings, physical-zone configuration, priority tables, recovery journal, statistics, VIOs, wait queues, Linux atomics/lists, and dm-kcopyd.

## Risks
Many fields are deliberately thread-affine rather than lock-protected; changing call sites without respecting physical-zone ownership risks races. Several comments identify persisted values or unit-test-adjusted capacities, so enum values, packed geometry, and journal entry counts must remain compatible. Resize state has two slab arrays and must be cleaned up carefully.

## Test Signals
Tests should verify exported API behavior across normal, recovery, rebuild, suspend/save, read-only, and resize states; validate field initialization and teardown; and assert that thread-affinity assumptions are preserved by callers.
