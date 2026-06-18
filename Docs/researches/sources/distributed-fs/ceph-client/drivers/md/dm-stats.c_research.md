# sources/distributed-fs/ceph-client/drivers/md/dm-stats.c

## Purpose
Implements Device Mapper statistics regions and message commands for IO counts, sectors, merges, service time, in-flight time, queue time, optional precise timestamps, and optional latency histograms.

## Important APIs, Types, And Functions
`struct dm_stat` describes a stats region with id, range, step, flags, histogram boundaries, program/aux strings, allocation sizes, per-CPU counters, and shared entries. `struct dm_stat_percpu` stores counters; `struct dm_stat_shared` stores in-flight atomics and temporary totals. Public entry points are `dm_stats_init()`, `dm_stats_cleanup()`, `dm_stats_account_io()`, `dm_stats_message()`, `dm_statistics_init()`, and `dm_statistics_exit()`.

## Control Flow
Messages implement `@stats_create`, `@stats_delete`, `@stats_clear`, `@stats_list`, `@stats_print`, `@stats_print_clear`, and `@stats_set_aux`. Creation validates ranges, steps, histogram bounds, allocation sizes, and memory limits, allocates per-CPU/shared arrays, suspends the mapped device for exact insertion, assigns an id, and enables the stats static key. IO accounting splits each IO across matching region entries under RCU and updates per-CPU counters at start and end. Print aggregates per-CPU totals into shared temporary counters and can subtract those totals for clear-after-print.

## State And Persistence
Stats are volatile per mapped device. Region definitions, counters, histograms, program IDs, and aux data vanish on deletion or device cleanup. Global `shared_memory_amount` limits aggregate stats memory and is checked at module exit.

## Dependencies And Integration Points
Depends on DM core message dispatch, internal suspend/resume callbacks, RCU, per-CPU allocation, static keys, jiffies/ktime, NUMA allocation, and block READ/WRITE directions. Bio-based and request-based IO paths call `dm_stats_account_io()`.

## Risks
Large regions and histograms can consume substantial memory, so overflow and shared memory checks are important. Counter updates are intentionally low overhead and partly racy on 64-bit. Deletion must respect RCU and vmalloc freeing constraints. Message parsing has many edge cases.

## Test Signals
Use `dmsetup message` for create/list/print/clear/print_clear/delete/set_aux, including whole-device and divided ranges, precise timestamps, histograms, invalid parameters, large allocation rejection, concurrent IO, and cleanup checks that allocated bytes return to zero.
