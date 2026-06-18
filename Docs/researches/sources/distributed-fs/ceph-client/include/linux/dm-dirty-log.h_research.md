<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dm-dirty-log.h -->
# sources/distributed-fs/ceph-client/include/linux/dm-dirty-log.h

## Purpose
Defines the Device Mapper dirty region log interface used by mirror-like targets to track clean, dirty, in-sync, and resync-needed regions.

## Important APIs, Types, And Functions
Defines `region_t`, `struct dm_dirty_log`, and `struct dm_dirty_log_type`. Log implementations provide constructor/destructor, suspend/resume hooks, region-size query, `is_clean()`, `in_sync()`, `flush()`, mark/clear, resync work assignment, region sync updates, sync counts, status, and remote-recovery checks. Registry and factory APIs are `dm_dirty_log_type_register()`, `dm_dirty_log_type_unregister()`, `dm_dirty_log_create()`, and `dm_dirty_log_destroy()`.

## Control Flow
DM targets create a named log type during table construction, mark regions dirty during writes, flush log state when needed, query which regions are synchronized, assign resync work, mark resync completion, and destroy the log when the target is removed.

## State And Persistence
Dirty log state may be in memory, on disk, or clustered depending on the implementation. It tracks region dirtiness, sync state, recovering regions, and callback context. Persistent log implementations must commit state through `flush()`.

## Dependencies And Integration Points
Depends on Device Mapper target types, module registration, status reporting, and mirror recovery workers. Cluster logs integrate with remote recovery and may block.

## Risks And Edge Cases
`in_sync()` can return `-EWOULDBLOCK` when state is unknown without blocking, requiring daemon handling. Mark/clear may rarely block. `get_resync_work()` assigns work and must not be confused with `in_sync()`. Cluster recovery must avoid local writes racing with remote resync.

## Test Signals
Tests should cover log type registration conflicts, constructor failure, suspend/resume, dirty marking, persistent flush, resync work assignment, region sync count, status output, remote recovery detection, and blocking vs nonblocking `in_sync()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dm-dirty-log.h -->
