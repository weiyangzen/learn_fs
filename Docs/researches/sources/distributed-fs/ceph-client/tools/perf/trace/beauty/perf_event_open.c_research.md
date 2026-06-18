# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/perf_event_open.c

Purpose: Beautifies `perf_event_open(2)` flags and, when available, the user `perf_event_attr` structure captured by syscall augmentation.

Important APIs/types/functions: `syscall_arg__scnprintf_perf_flags` formats `PERF_FLAG_*`; `perf_event_attr___scnprintf` formats a `struct perf_event_attr` by calling `perf_event_attr__fprintf`; `syscall_arg__scnprintf_perf_event_attr` prints augmented attributes or falls back to the pointer value. `SCA_PERF_ATTR_FROM_USER` marks augmented user memory arguments.

Control flow: Flag formatting is manual bit clearing with hex fallback. Attribute formatting builds `{ name: value, ... }` through an `attr__fprintf` callback that writes into the caller buffer. The syscall argument formatter first checks `arg->augmented.args`.

State and persistence: No persistent state. It reads augmented syscall capture buffers and honors `trace->show_zeros`.

Dependencies and integration points: Depends on perf event attr printing utilities and the syscall augmentation path that copies user memory.

Risks: Without augmentation the attr pointer is opaque. Buffer truncation behavior depends on cumulative `scnprintf` accounting. New `PERF_FLAG_*` values need updates.

Test signals: Trace `perf_event_open` with augmentation enabled and disabled; verify flag names and structured attr output for common event attributes.
