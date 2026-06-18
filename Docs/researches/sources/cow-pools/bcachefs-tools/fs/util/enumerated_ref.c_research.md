# File Research: sources/cow-pools/bcachefs-tools/fs/util/enumerated_ref.c

Implements enumerated refs. In normal builds it wraps `percpu_ref` and invokes an optional stop callback when killed. In debug builds it keeps one atomic refcount per enumerated user, allowing diagnostics to show which users are still holding refs.

Stop logic kills refs asynchronously, waits with periodic 10-second diagnostic dumps, supports restart/reinit, and frees debug arrays/percpu refs on exit. Text output lists per-user counts in debug mode or notes that debug mode is disabled.
