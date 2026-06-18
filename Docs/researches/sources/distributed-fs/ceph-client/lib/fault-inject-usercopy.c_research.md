# sources/distributed-fs/ceph-client/lib/fault-inject-usercopy.c

## Purpose
Defines a usercopy-specific fault-injection attribute and exposes `should_fail_usercopy()` so user-copy paths can be forced to fail under boot-parameter or debugfs control.

## Important APIs, Types, and Functions
The file owns a static `fail_usercopy` object containing `struct fault_attr attr` initialized by `FAULT_ATTR_INITIALIZER`. `setup_fail_usercopy()` parses the `fail_usercopy=` boot parameter. `fail_usercopy_debugfs()` creates debugfs controls when `CONFIG_FAULT_INJECTION_DEBUG_FS` is enabled. `should_fail_usercopy()` is exported GPL-only.

## Control Flow
At boot, `__setup("fail_usercopy=", setup_fail_usercopy)` lets users configure interval, probability, space, and times via the shared fault-attr parser. During late init, optional debugfs setup creates `/sys/kernel/debug/fail_usercopy` style controls through `fault_create_debugfs_attr()`. Runtime callers invoke `should_fail_usercopy()`, which delegates to `should_fail(&fail_usercopy.attr, 1)`.

## State and Persistence
All mutable state is in the static `fault_attr`: probability, interval, counters, remaining failures/space, verbosity, and optional filters. Settings persist only for the running kernel.

## Dependencies and Integration Points
Depends on the generic fault-injection framework in `fault-inject.c`, debugfs when enabled, and usercopy call sites that check `should_fail_usercopy()`. It integrates through a boot parameter and exported symbol.

## Risks
Misconfiguration can cause broad usercopy failures and noisy diagnostics. Debugfs setup is optional and late, so boot parameter coverage is needed for early behavior. A size of `1` means space accounting is per usercopy decision rather than actual copy length.

## Test Signals
Boot with `fail_usercopy=` combinations, toggle debugfs attributes, verify probability/times/interval semantics, and confirm usercopy call sites fail only when the predicate returns true. Disable debugfs builds should still honor boot parameters.
