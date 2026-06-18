## sources/distributed-fs/ceph-client/fs/smb/server/stats.h

Purpose: provides lightweight ksmbd server counters for procfs reporting and no-op stubs when procfs support is disabled.

Important APIs and types: defines counter indexes for sessions, tree connects, total requests, read/write bytes, and per-command request buckets from `KSMBD_COUNTER_FIRST_REQ` through `KSMBD_COUNTER_LAST_REQ`. `struct ksmbd_counters` wraps an array of `percpu_counter`. Inline helpers increment, decrement, add, subtract, increment a request command bucket, and sum a counter.

Control flow: with `CONFIG_PROC_FS`, call sites update `ksmbd_counters.counters[type]`; request bucket updates are bounded by `KSMBD_COUNTER_MAX_REQS`. Without procfs, all helpers compile to no-ops and sums return zero.

State and persistence behavior: counters are in-memory percpu accounting state only. They are reset by module lifetime and are not persisted.

Dependencies and integration points: used by VFS read/write byte accounting, command dispatch request accounting, session/tree connection management, and procfs status rendering. Depends on the global `ksmbd_counters` object defined outside this header.

Risks: helper callers must pass valid base counter indexes; only the per-command helper bounds checks command numbers. Disabled procfs builds silently remove accounting, so tests that assert stats must account for configuration.

Test signals: procfs-enabled read/write byte increments, session/tree counter changes, command counter bounds at 0 and 18, counter sums under parallel I/O, and procfs-disabled compile coverage.
