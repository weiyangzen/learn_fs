# sources/distributed-fs/ceph-client/drivers/md/dm-stats.h

## Purpose
Defines the internal DM statistics API and lightweight state embedded in mapped devices and per-IO contexts.

## Important APIs, Types, And Functions
`struct dm_stats` owns the mutex, region list, per-CPU last-position merge tracking, and `precise_timestamps` flag. `struct dm_stats_aux` carries per-IO merge and duration state. The header declares stats lifecycle, message dispatch, and IO accounting functions plus inline helpers `dm_stats_used()` and `dm_stats_record_start()`.

## Control Flow
Mapped-device setup initializes `dm_stats`; IO paths record precise start time when needed and call `dm_stats_account_io()` at start and end; control messages route `@stats_*` commands through `dm_stats_message()`.

## State And Persistence
Only volatile in-kernel structures are defined. No stats persist beyond mapped-device lifetime.

## Dependencies And Integration Points
Depends on Linux types, mutexes, lists, and a forward declaration for `struct mapped_device`. It is included by DM core and request-based DM code.

## Risks
`dm_stats_used()` is a lockless hot-path list check and relies on `dm-stats.c` RCU/list discipline. `dm_stats_record_start()` requires the same aux object to be passed to end accounting.

## Test Signals
Compile bio-based and request-based DM with stats enabled. Runtime tests should toggle precise timestamp regions and confirm IO start/end accounting receives consistent `dm_stats_aux` data.
