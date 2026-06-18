# sources/distributed-fs/ceph-client/include/linux/seccomp_types.h

Purpose: `seccomp_types.h` isolates the task seccomp state structure so scheduler and task headers can carry seccomp fields without pulling in the full seccomp API.

Important APIs/types/functions: With `CONFIG_SECCOMP`, `struct seccomp` contains `mode`, `atomic_t filter_count`, and `struct seccomp_filter *filter`. The comment documents that `filter` must be valid or NULL and is accessed without locking during syscall entry. Disabled builds define empty `struct seccomp` and `struct seccomp_filter`.

Control flow: No functions are defined. Syscall entry and seccomp management code read and update this structure through APIs in `seccomp.h` and implementation files.

State and persistence behavior: This is per-task state. `mode` controls disabled/strict/filter behavior, `filter_count` tracks installed filter layers, and `filter` points to the active filter chain. The filter lifetime is managed by reference helpers outside this header.

Dependencies and integration points: It depends on basic types and atomic counters through `linux/types.h` and seccomp implementation code. It integrates with `task_struct`/thread state, clone, exec, and syscall entry.

Risks: Because `filter` is read locklessly, writers must preserve ordering and lifetime. Empty-struct disabled builds require callers to avoid assuming storage layout or fields under `!CONFIG_SECCOMP`.

Test signals: Build seccomp-enabled and disabled kernels, clone/exec task state propagation, stacked filters, lockless syscall-entry reads under concurrent task teardown, and filter reference accounting.
