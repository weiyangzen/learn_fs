# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/enumerated_ref.c

This file implements enumerated references: a refcount abstraction that collapses to `percpu_ref` in normal builds and tracks refs per named user in debug builds.

Debug-mode behavior:
- `enumerated_ref_get()` increments a specific indexed ref.
- `__enumerated_ref_tryget()` increments if nonzero.
- `enumerated_ref_tryget()` also rejects dying refs.
- `enumerated_ref_put()` decrements a specific index, checks underflow, and completes shutdown only when all indexed refs are zero.
- Debug refs are allocated as an array of `atomic_long_t`.

Normal-mode behavior:
- Uses a single `percpu_ref`.
- `enumerated_ref_kill_cb()` invokes optional stop callback and completes shutdown.

Lifecycle:
- `enumerated_ref_init()` initializes completion, stop callback, and backend storage/refcount.
- `enumerated_ref_start()` reinitializes live refs.
- `enumerated_ref_stop_async()` begins shutdown.
- `enumerated_ref_stop()` waits for completion, printing outstanding refs every 10 seconds.
- `enumerated_ref_exit()` frees backend resources.
- `enumerated_ref_to_text()` prints indexed refs only in debug mode.

Important invariants:
- Debug mode requires `idx < ref->nr`.
- Stop completion is reinitialized on every stop.
- Debug start expects all indexed refs are zero before seeding each index.

Research notes:
- This is used where bcachefs wants production-fast refs but debug builds need attribution for leaks or stuck shutdowns.
