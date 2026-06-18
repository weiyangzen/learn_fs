# sources/distributed-fs/ceph-client/include/linux/ref_tracker.h

## Purpose

`ref_tracker.h` declares optional debugging infrastructure for tracking reference acquisitions and releases. It helps detect leaked, untracked, or double-freed references by keeping active and quarantined tracker records with stack depot support.

## Important APIs, Types, and Functions

`struct ref_tracker_dir` contains real fields only under `CONFIG_REF_TRACKER`: a spinlock, quarantine capacity, `untracked` and `no_tracker` refcounts, a dead flag, active and quarantine lists, and a static class string. Without the config, the struct is empty.

`ref_tracker_dir_init()` initializes lists, lock, quarantine count, counters, class, debugfs, and stack depot. Other active APIs include `ref_tracker_dir_exit()`, `ref_tracker_dir_print_locked()`, `ref_tracker_dir_print()`, `ref_tracker_dir_snprint()`, `ref_tracker_alloc()`, and `ref_tracker_free()`. Debugfs helpers are active only under `CONFIG_DEBUG_FS`.

## Control Flow

Tracked users initialize a directory, allocate a tracker on each reference acquisition, and free the tracker on each reference release. Active trackers stay on the directory list; freed trackers can move to quarantine for postmortem diagnostics. Directory exit reports or validates remaining active entries.

With `CONFIG_REF_TRACKER` disabled, all functions are inline no-ops returning success or zero, allowing instrumentation to remain compiled in callers without runtime cost.

## State and Persistence Behavior

Runtime state is per-directory active/quarantine lists, counters, stack depot handles in implementation-private tracker objects, and optional debugfs entries. There is no persistent storage beyond kernel runtime.

## Dependencies and Integration Points

The header depends on `refcount.h`, spinlocks, list handling, stack depot, debugfs, and GFP allocation flags. It integrates with subsystems that want reference lifecycle diagnostics without changing production behavior when disabled.

## Risks

Forgetting to free trackers creates diagnostic leaks. Calling alloc/free after `ref_tracker_dir_exit()` can race the dead flag or list teardown. Class strings must be static. In no-op builds, bugs are intentionally invisible, so tests that rely on tracker diagnostics need the config enabled.

## Test Signals

Tests should exercise balanced alloc/free, leaked references at dir exit, double-free/untracked paths, quarantine limits, debugfs output, and disabled-config build behavior.
