# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/seccomp.c

Purpose: Beautifies `seccomp(2)` operation and flag arguments.

Important APIs/types/functions: `syscall_arg__scnprintf_seccomp_op` maps `SECCOMP_SET_MODE_STRICT` and `SECCOMP_SET_MODE_FILTER`; `syscall_arg__scnprintf_seccomp_flags` maps `SECCOMP_FILTER_FLAG_TSYNC`.

Control flow: The op formatter uses a switch with hex fallback. The flag formatter clears known bits and appends unknown leftovers.

State and persistence: Stateless formatting.

Dependencies and integration points: Local fallback definitions avoid depending on newer system headers. Bound through `SCA_SECCOMP_OP` and `SCA_SECCOMP_FLAGS`.

Risks: This snapshot only names `TSYNC`; newer seccomp filter flags will show as hex until updated.

Test signals: Trace strict/filter operations, zero flags, `TSYNC`, and unknown flags.
