# sources/distributed-fs/ceph-client/mm/percpu-stats.c

## Purpose
`percpu-stats.c` exposes debugfs statistics for the per-CPU allocator. It reports boot allocation parameters, global allocation/chunk counters, and per-chunk fragmentation and allocation-size distributions.

## Important APIs, Types, And Functions
- `pcpu_stats` and `pcpu_stats_ai` are the global stats structures filled by allocator code.
- `find_max_nr_alloc()` determines a safe temporary buffer size for per-chunk allocation/free fragment accounting.
- `chunk_map_stats()` scans one chunk's allocation and boundary bitmaps and prints fragmentation and current allocation size metrics.
- `percpu_stats_show()` formats the full debugfs output while holding `pcpu_lock` during list and bitmap inspection.
- `init_percpu_stats_debugfs()` creates the `percpu_stats` debugfs file.

## Control Flow
The show path first samples the maximum number of allocations under `pcpu_lock`, allocates a vmalloc buffer large enough for twice that many allocation/free fragments plus one, then reacquires the lock and retries if the maximum grew. It prints allocation info and global stats, then visits the reserved chunk and every slot list. `chunk_map_stats()` finds the last allocated bit, walks from `start_offset` to that point, records positive allocation spans and negative free fragments, sorts them, computes sum/max fragmentation and min/median/max live allocation sizes, and prints chunk metadata hints.

## State And Persistence Behavior
The file only reads runtime allocator state and publishes it through debugfs. It owns the global stats variables but updates happen through inline helpers in `percpu-internal.h`. The temporary buffer is freed after each read. No data persists across reboot.

## Dependencies And Integration Points
It depends on debugfs, seq_file, sort, vmalloc, `pcpu_lock`, chunk lists and slots, reserved/first chunks, allocator bitmaps, and stat helpers. It is compiled only when percpu stats support is enabled.

## Risks
- Debugfs reads can be expensive because they hold `pcpu_lock` while scanning chunks and printing.
- Fragmentation metrics rely on `alloc_map` and `bound_map` semantics; if boundary map maintenance changes, reporting can become misleading.
- The initial buffer sizing must retry on concurrent allocations to avoid overflow.
- Sorting signed sizes intentionally places free fragments first; changing comparison semantics would break metrics.

## Test Signals
- Read `/sys/kernel/debug/percpu_stats` under allocation/free stress and verify no lockdep or buffer retry failures.
- Compare reported global counters with allocation/deallocation activity.
- Create fragmentation patterns and validate sum/max fragment and allocation size metrics.
