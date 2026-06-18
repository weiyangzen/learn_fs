<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/gcov/base.c -->
# sources/distributed-fs/ceph-client/kernel/gcov/base.c

Purpose: maintains global gcov event state and utility serialization helpers for kernel coverage data. It enables delayed event replay once the gcov filesystem side is ready and removes module-owned profiling entries during module unload.

Important APIs/types/functions: globals are `gcov_events_enabled` and `gcov_lock`. Public helpers include `gcov_enable_events()`, `store_gcov_u32()`, and `store_gcov_u64()`. With modules enabled, `gcov_module_notifier()` and `gcov_init()` register a module notifier.

Control flow: `gcov_enable_events()` takes `gcov_lock`, enables event reporting, iterates all existing `gcov_info` records via `gcov_info_next()`, emits `GCOV_ADD` for each through `gcov_event()`, and periodically reschedules. `store_gcov_u32()` and `store_gcov_u64()` optionally write native-endian gcov words to a caller buffer and always return the byte count. On `MODULE_STATE_GOING`, the notifier walks gcov info entries, unlinks records belonging to the unloading module, and emits `GCOV_REMOVE` if events are enabled.

State and persistence behavior: state is runtime-only: a global event-enabled flag, a mutex, and linked gcov info records managed by compiler backends. Coverage counters themselves live in instrumented objects/modules; this file coordinates events and serialization, not durable storage.

Dependencies and integration points: depends on `gcov.h` backend callbacks such as `gcov_info_next()`, `gcov_event()`, `gcov_info_within_module()`, and `gcov_info_unlink()`, plus module notifier infrastructure. It integrates with the debugfs gcov filesystem, compiler-specific gcov backends, and module load/unload lifecycle.

Risks: missing locking can race debugfs readers, event replay, and module unload. Failing to unlink module gcov records before unload would leave dangling pointers. Buffer serialization assumes aligned writable caller buffers when non-NULL and native gcov endianness. Event replay must tolerate early registrations before the filesystem callback path is ready.

Test signals: gcov debugfs smoke tests, enabling events after early boot records exist, module load/unload coverage removal tests, lockdep under concurrent reads and unloads, GCC/Clang backend serialization checks, and coverage file comparison against userspace gcov tooling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/gcov/base.c -->
