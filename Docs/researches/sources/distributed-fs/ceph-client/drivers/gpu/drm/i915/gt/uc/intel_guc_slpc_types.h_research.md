## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_slpc_types.h

Purpose: defines `struct intel_guc_slpc`, the persistent host-side state for GuC SLPC.

Important APIs, types, and functions:
- `SLPC_RESET_TIMEOUT_MS` sets the wait timeout for SLPC reset/start.
- `struct intel_guc_slpc` fields include shared-data VMA/address, support and selection booleans, server-min marker, platform frequencies, boost frequency, min/max softlimits, efficient-frequency ignore flag, power profile, media ratio mode, mutex, boost work, waiter count, and boost count.

Control flow:
- The struct is initialized early for support/selection, allocated/configured in full init, used by enable and runtime setters, and released in fini.

State and persistence:
- Softlimits, boost frequency, efficient-frequency flag, media ratio mode, and power profile are cached across SLPC re-enable/reset so enable can reapply policy to firmware.
- `num_waiters` and `boost_work` coordinate transient waitboost state.

Dependencies and integration points:
- Includes atomic, workqueue, mutex, and type headers. Uses forward-declared kernel/i915 types through pointers from users.

Risks:
- Locking around `boost_freq` and `num_waiters` is documented in the struct; callers that bypass SLPC APIs could race waitboost min-frequency changes.
- Cached policy fields must be kept in sync with successful firmware updates.

Test signals:
- Reset/re-enable tests should verify cached policy replay.
- Concurrency tests around waitboost and sysfs boost/min changes should verify locking and correct `num_waiters` transitions.
