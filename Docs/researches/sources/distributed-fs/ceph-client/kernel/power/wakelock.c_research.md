# sources/distributed-fs/ceph-client/kernel/power/wakelock.c

## Purpose
Implements the `/sys/power/wake_lock` and `/sys/power/wake_unlock` user-space wakelock compatibility interface. It maps named user-space locks to kernel `wakeup_source` objects so privileged processes can prevent system sleep, optionally with timeouts.

## Important APIs, Types, and Functions
`struct wakelock` stores the user-visible name, red-black tree node, registered `struct wakeup_source *`, and optional LRU node for garbage collection. Global state includes `wakelocks_lock`, `wakelocks_tree`, optional `number_of_wakelocks`, optional `wakelocks_lru_list`, `wakelock_work`, and `wakelocks_gc_count`.

Public entry points are `pm_show_wakelocks(char *buf, bool show_active)`, `pm_wake_lock(const char *buf)`, and `pm_wake_unlock(const char *buf)`. Internal helpers include `wakelock_lookup_add()`, limit tracking helpers, LRU helpers, and optional `__wakelocks_gc()`.

## Control Flow
`pm_wake_lock()` requires `CAP_BLOCK_SUSPEND`, parses a non-empty lock name up to whitespace, optionally parses a timeout in nanoseconds, locks `wakelocks_lock`, finds or creates a wakelock, and calls `__pm_wakeup_event()` for timed locks or `__pm_stay_awake()` for indefinite locks. Timed nanoseconds are rounded up to milliseconds.

`wakelock_lookup_add()` searches the RB tree by name. If missing and creation is allowed, it enforces the configured limit, allocates the wakelock/name, registers a wakeup source, initializes `last_time`, links it into the RB tree, optionally adds it to the LRU list, and increments the count.

`pm_wake_unlock()` also requires `CAP_BLOCK_SUSPEND`, trims a trailing newline, looks up an existing lock, calls `__pm_relax()`, marks it most recent in the LRU list, and triggers optional GC. `pm_show_wakelocks()` walks the RB tree and prints names whose wakeup source active state matches the requested view.

With `CONFIG_PM_WAKELOCKS_GC`, every 100 unlocks schedules work that scans the LRU list from oldest to newest and unregisters inactive wakelocks idle for at least 300 seconds.

## State and Persistence Behavior
Wakelocks are runtime-only kernel objects. Names persist in the RB tree until GC removes inactive old entries or until reboot. Active state and timestamps live in each `wakeup_source`. The sysfs show functions expose active or inactive names through `wake_lock` and `wake_unlock` attributes in `main.c`.

## Dependencies and Integration Points
Depends on capabilities, sysfs PM attributes, `wakeup_source_register()`, wakeup-source active accounting, RB trees, optional LRU/workqueue GC, and autosleep/suspend wakeup checks. It is integrated into `/sys/power` only when `CONFIG_PM_WAKELOCKS` is enabled.

## Risks
Risks include unbounded named lock growth without a configured limit or GC, name parsing surprises around whitespace, timeout unit mismatch for user space, missing capability checks if reused elsewhere, lock contention around sysfs show/store, and stale inactive wakeup sources if GC is disabled. The configured limit check uses the current count before increment, so limit semantics should be verified against expected maximum.

## Test Signals
Write lock names and timed locks to `/sys/power/wake_lock`, unlock through `/sys/power/wake_unlock`, verify active/inactive listings, test `CAP_BLOCK_SUSPEND` denial, invalid empty/timeout inputs, many unique lock names with `CONFIG_PM_WAKELOCKS_LIMIT`, GC behavior after idle timeout, and autosleep prevention while a lock is active.
