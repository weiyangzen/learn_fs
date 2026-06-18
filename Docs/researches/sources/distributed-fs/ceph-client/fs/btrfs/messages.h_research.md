# sources/distributed-fs/ceph-client/fs/btrfs/messages.h

## Purpose
`messages.h` declares and defines the Btrfs diagnostic API: printk wrappers, dynamic debug hooks, assertions, debug warnings, filesystem error handling, fatal panic handling, and 32-bit address-limit helpers. The source was read as a complete 207-line header.

## Important APIs, Types, and Functions
It declares `_btrfs_printk()`, `__btrfs_handle_fs_error()`, `btrfs_decode_error()`, `__btrfs_panic()`, and 32-bit limit helpers. Macros include `btrfs_crit/err/warn/info`, ratelimited variants, `btrfs_debug`, `btrfs_debug_rl`, `ASSERT()`, `DEBUG_WARN()`, `btrfs_handle_fs_error()`, and `btrfs_panic()`. `ASSERT()` supports optional printf-style context under `CONFIG_BTRFS_ASSERT` and compiles only the expression otherwise.

## Control Flow
Callers use severity macros that wrap `_btrfs_printk()` in RCU read-side protection when printk is enabled, or compile to no-op/no-printk paths when disabled. Ratelimited macros create static per-callsite ratelimit state. `btrfs_handle_fs_error()` injects function and line into the implementation. `btrfs_panic()` calls the implementation and then BUGs unless the implementation panicked first.

## State and Persistence Behavior
The header defines no durable state. It shapes runtime behavior through callsite ratelimit states, assertions that can BUG, and error/panic wrappers that may force readonly or crash the kernel via the implementation.

## Dependencies and Integration Points
The header depends on Linux printk and bug APIs and forward-declares `struct btrfs_fs_info`. It is a ubiquitous dependency for Btrfs modules that need diagnostics or invariants.

## Risks and Edge Cases
The debug branch contains a typo-like `LOGLEVEl_DEBUG` in the non-dynamic `DEBUG` `btrfs_debug_rl` path, which would matter only under that compile path. Assertion varargs are carefully constructed around `__VA_OPT__`; compiler support assumptions matter. Panic and ASSERT macros intentionally stop the kernel, so they must be reserved for impossible invariants.

## Test Signals
Build matrices with `CONFIG_PRINTK`, `CONFIG_DYNAMIC_DEBUG`, `DEBUG`, `CONFIG_BTRFS_ASSERT`, and 32-bit builds are the strongest signals. Runtime signals come from injected errors, assertion-only debug builds, ratelimited logging, and fatal error mount-option tests.
