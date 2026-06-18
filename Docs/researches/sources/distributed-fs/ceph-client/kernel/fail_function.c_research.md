# sources/distributed-fs/ceph-client/kernel/fail_function.c

Purpose: implements function-based fault injection using kprobes and debugfs. Users name injectable functions, configure return values, and use common fault-injection policy knobs to force early returns.

Important APIs/types/functions: `struct fei_attr` stores one symbol's list node, kprobe, and forced return value. `adjust_error_retval()` validates return values by injectable error type. `fei_write()` parses debugfs commands. `fei_kprobe_handler()` sets the return value and calls `override_function_with_return()`. `fei_retval_get()`/`fei_retval_set()` back per-symbol `retval` files; `fei_debugfs_init()` creates the debugfs hierarchy.

Control flow: late init creates `fail_function`, adds an `injectable` symlink, and creates the `inject` file. Writing a symbol resolves it, verifies it is injectable, rejects duplicates, allocates/registers a kprobe, creates per-symbol debugfs, and links it into `fei_attr_list`. Writing `!symbol` removes one probe; whitespace removes all. On a probed call, `should_fail()` decides whether to override execution.

State and persistence: runtime state is `fei_attr_list`, guarded by `fei_lock`, plus registered kprobes and debugfs dentries. `fei_fault_attr` stores probability/interval policy. State is debugfs-configured and not persistent across reboot.

Dependencies and integration points: depends on kprobes, kallsyms, error-injection metadata, fault-inject debugfs helpers, `regs_set_return_value()`, and architecture support for `override_function_with_return()`. A dummy post handler prevents jump optimization because optimized paths cannot support return override.

Risks: only annotated injectable functions may be accepted. Forced return values must match `NULL`, `ERRNO`, `ERRNO_NULL`, or boolean semantics. Debugfs callbacks can race with removal, so attr validity is rechecked under `fei_lock`. Kprobe registration may fail for unavailable or blacklisted symbols.

Test signals: tests should add/remove injectable symbols, set valid/invalid retval values, trigger configured failures, clear all probes, and verify duplicate, unknown, or non-injectable symbols return expected errors. Kprobe and fault-injection selftests provide integration coverage.
