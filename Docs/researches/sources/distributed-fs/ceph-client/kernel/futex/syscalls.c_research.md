<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/futex/syscalls.c -->
# sources/distributed-fs/ceph-client/kernel/futex/syscalls.c

Purpose: provides user-facing futex syscall dispatch, robust-list syscalls, futex2 syscalls, timeout parsing, compat robust-list handling, and 32-bit time syscall support. It translates ABI arguments into internal flags and delegates actual wait/wake/requeue/PI behavior to the other futex files.

Important APIs/types/functions: syscall entry points include `set_robust_list`, `get_robust_list`, `futex`, `futex_waitv`, `futex_wake`, `futex_wait`, `futex_requeue`, compat robust-list variants, and `futex_time32`. Internal helpers include `do_futex()`, `futex_cmd_has_timeout()`, `futex_init_timeout()`, `futex_parse_waitv()`, `futex2_setup_timeout()`, and `futex_get_robust_list_common()`.

Control flow: legacy `sys_futex()` parses a timeout only for commands that use one, converts relative `FUTEX_WAIT` timeouts and absolute bitset/PI timeouts, and calls `do_futex()`. `do_futex()` maps opcodes to `futex_wait()`, `futex_wake()`, `futex_requeue()`, `futex_wake_op()`, `futex_lock_pi()`, `futex_unlock_pi()`, or `futex_wait_requeue_pi()`, while limiting `FUTEX_CLOCK_REALTIME` to supported commands. Futex2 calls validate `FUTEX2_VALID_MASK`, size/private/NUMA/MPOL flags, value width, timeout clock, and then call shared helpers.

State and persistence behavior: robust-list syscalls store per-task user pointers (`robust_list` or `compat_robust_list`) that are later consumed during exit/exec cleanup. Futex waits allocate transient `futex_vector` arrays and stack hrtimer sleepers. No durable storage is written.

Dependencies and integration points: depends on task lookup and ptrace permission checks for `get_robust_list`, time namespaces for monotonic timeout conversion, uaccess copying, compat ABI structs, futex2 UAPI structs, and all internal futex subsystem APIs. Robust-list registration is consumed by `core.c` during `futex_exit_release()`.

Risks: ABI validation mistakes can allow unsupported sizes, bad clocks, invalid masks, or misinterpreted timeouts. `get_robust_list` must serialize against exec credentials. Passing `(unsigned long)utime` as legacy `val2` for requeue-like commands preserves historical ABI but is easy to misunderstand. Futex2 currently validates only 32-bit futex sizes despite generic flag names.

Test signals: futex syscall ABI selftests, robust-list permission tests, compat and time32 coverage, futex2 wait/wake/requeue/waitv validation tests, realtime vs monotonic timeout tests under time namespaces, faulting user-pointer tests, and negative tests for unsupported command/flag combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/futex/syscalls.c -->
