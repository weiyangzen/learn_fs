# sources/distributed-fs/ceph-client/drivers/md/dm-table.c

## Purpose
Implements DM table construction, target parsing, btree lookup indexes, device references, queue type selection, mempool allocation, queue-limit stacking, inline encryption profile aggregation, target lifecycle callbacks, and sector-to-target lookup.

## Important APIs, Types, And Functions
Core APIs include `dm_table_create()`, `dm_table_add_target()`, `dm_table_complete()`, `dm_table_destroy()`, `dm_table_find_target()`, `dm_get_device()`, `dm_put_device()`, `dm_calculate_queue_limits()`, and `dm_table_set_restrictions()`. Argument helpers include `dm_split_args()`, `dm_read_arg()`, `dm_read_arg_group()`, `dm_shift_arg()`, and `dm_consume_args()`.

## Control Flow
Table load creates a table, adds contiguous nonzero targets, resolves target modules, splits constructor args, invokes target `ctr`, and records high sectors. Completion determines bio/request/DAX table type, builds a compact btree over target high sectors, constructs a crypto profile, and allocates mempools. Queue-limit setup stacks child limits, applies target hints, validates device ranges, zoned constraints, logical block alignment, feature support, and then commits queue limits and crypto/DAX settings.

## State And Persistence
Tables are in-memory objects containing targets, highs, btree indexes, device refcounts, mempools, event callbacks, queue mode, integrity state, and transient crypto profile. No table state is persisted by this file.

## Dependencies And Integration Points
Depends on DM core, target registry, request-based DM, blkdev queue limits, blk-integrity, DAX, zoned block support, blk-mq, block crypto, and path lookup. Every target integrates through callbacks such as `ctr`, `dtr`, `iterate_devices`, `io_hints`, `preresume`, `resume`, `presuspend`, and `postsuspend`.

## Risks
Incorrect table type selection can allow unsupported request-based mixes or reject valid hybrid targets. Queue-limit stacking must preserve alignment, zoned, integrity, discard, write-zeroes, DAX, crypto, and atomic-write semantics. Device refcount upgrades and target destructors must remain balanced.

## Test Signals
Load valid and invalid tables covering gaps, singleton targets, immutable request-based targets, partitions, non-mq devices, DAX and non-DAX devices, zoned devices, integrity, inline crypto, suspend/resume callbacks, queue-limit reloads, and target lookup across boundaries.
