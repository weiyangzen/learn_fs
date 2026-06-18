# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/statistics.h

## Purpose
`statistics.h` defines the stable VDO statistics payload reported by the driver. It groups allocator, journal, packer, block-map, dedupe, error, bio, memory, and index counters under `struct vdo_statistics`.

## Important APIs, Types, And Functions
The file is type-only. `STATISTICS_VERSION` is `36`. Important structs include `block_allocator_statistics`, `commit_statistics`, `recovery_journal_statistics`, `packer_statistics`, `slab_journal_statistics`, `slab_summary_statistics`, `ref_counts_statistics`, `block_map_statistics`, `hash_lock_statistics`, `error_statistics`, `bio_stats`, `memory_usage`, `index_statistics`, and `vdo_statistics`.

## Control Flow
There is no executable control flow. Producers throughout the VDO codebase fill subsets of `vdo_statistics`; for this subset, `slab-depot.c` fills allocator, ref-count, slab-journal, slab-summary, and recovery percentage fields.

## State And Persistence
The structs represent runtime/accounting state rather than on-disk metadata, but consumers may treat their layout/version as a user-visible ABI. Counter widths vary between `u32`, `u64`, and VDO block-count typedefs. `mode[15]` and nested bio stats are fixed-size reporting fields.

## Dependencies And Integration Points
The file includes `types.h` for block-count typedefs. It integrates with sysfs/dm statistics collection and VDO component-specific aggregation functions.

## Risks
Changing field order, field type, or `STATISTICS_VERSION` without coordinating readers can break user-space tooling. Mixed thread updates mean consumers should expect approximate snapshots unless producers add synchronization.

## Test Signals
Tests should check version changes when layout changes, complete population of nested counters, overflow behavior for high-volume counters, and compatibility with user-space parsers.
