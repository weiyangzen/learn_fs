# File Research: sources/block-storage/lvm2/lib/mm/memlock.c

This file manages memory locking and process priority around device suspension and daemon critical paths.

Build modes:
- Without `DEVMAPPER_SUPPORT`, all APIs are inert stubs.
- With `DEVMAPPER_SUPPORT`, full memory locking, map filtering, priority management, and debug mmap trapping are enabled.

Main APIs:
- Critical sections: `critical_section_inc()`, `critical_section_dec()`, `critical_section()`, `prioritized_section()`.
- Daemon locking: `memlock_inc_daemon()`, `memlock_dec_daemon()`, `memlock_count_daemon()`.
- Lifecycle: `memlock_init()`, `memlock_reset()`, `memlock_unlock()`.

Implementation details:
- Preallocates/touches stack and heap reserves to reduce allocation during suspended-device windows.
- Locks memory either with `mlockall(MCL_CURRENT|MCL_FUTURE)` or by parsing `/proc/self/maps` and calling `mlock()` on selected readable mappings.
- Filters mappings with built-in blacklist or configured `activation_mlock_filter`.
- Skips expected uncommitted anonymous `ENOMEM` regions.
- Can temporarily patch `mmap`/`mmap64` to `hlt` in debug x86 builds to catch mmap during locked sections.
- Raises process priority on prioritized/critical entry and restores when possible.

Dependencies:
- Command context/config, `/proc/self/maps`, `mlock`, `munlock`, `mlockall`, resource limits, glibc `mallinfo`/`mallinfo2`, activation suspended counter, profile loading.

Correctness notes:
- Only reason `"suspending"` enters true critical section and locks memory; other reasons raise priority only.
- Memory remains locked after leaving critical section until `memlock_unlock()` if no daemon lock remains.
- Daemon memlock forces `mlockall()` so future thread memory remains resident.
- `memlock_reset()` is required after fork-like daemon contexts.

Risks:
- Map parsing and blacklist coverage are platform-sensitive.
- Preallocation behavior is glibc-specific and disabled for valgrind.
- Incorrect counter balance can leave memory locked or priority raised.
