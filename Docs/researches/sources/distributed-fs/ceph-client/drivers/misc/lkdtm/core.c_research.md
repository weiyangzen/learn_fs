# sources/distributed-fs/ceph-client/drivers/misc/lkdtm/core.c

## Purpose
`core.c` is the LKDTM entry point. It exposes debugfs files under `provoke-crash`, accepts module parameters for crashpoint/crashtype/count selection, wires all LKDTM crash categories together, and optionally arms kprobes so a selected kernel execution point triggers a selected destructive test after a configurable hit count.

## Important APIs, Types, and Functions
Key local types are `struct crashpoint`, the `CRASHPOINT()` macro, and the global `crashpoints[]` table. Main routines are `find_crashtype()`, `lkdtm_do_action()`, `lkdtm_register_cpoint()`, `lkdtm_kprobe_handler()`, `lkdtm_debugfs_entry()`, `direct_entry()`, `lkdtm_debugfs_read()`, `lkdtm_check_bool_cmdline()`, `lkdtm_module_init()`, and `lkdtm_module_exit()`. It consumes the `struct crashtype_category` exports declared in `lkdtm.h`.

## Control Flow
Initialization validates module parameters, resolves requested crashpoint/type names, sets the kprobe hit counter, builds `lkdtm_kernel_info`, calls category init hooks, creates the debugfs directory, and creates one file per crashpoint. A write to `DIRECT` immediately resolves the requested crashtype and calls its function. A write to a kprobe-backed crashpoint registers a kprobe; its pre-handler decrements `crash_count`, resets it on zero, and calls the selected crashtype through `lkdtm_do_action()`.

## State and Persistence
State is in module globals: selected `lkdtm_kprobe`, `lkdtm_crashpoint`, `lkdtm_crashtype`, debugfs root, `crash_count`, module parameters, and allocated `lkdtm_kernel_info`. There is no persistence beyond module lifetime.

## Dependencies and Integration Points
Depends on debugfs, optional kprobes, module parameters, kernel command line parsing for built-in LKDTM, UTS release/machine strings, and category modules for bugs, heap, permissions, refcount, usercopy, stackleak, CFI, fortify, and optional powerpc tests.

## Risks
All paths intentionally provoke crashes or corruption. Incorrect parameter combinations are rejected, but selected tests can panic a system. Kprobe symbol names are configuration and architecture sensitive. Debugfs writable entries are powerful and should be restricted to test kernels.

## Test Signals
Useful signals are debugfs listing of all crash types, valid and invalid writes to `DIRECT`, kprobe registration failure handling, hit-count countdown behavior, module parameter validation, command-line bool parsing when built-in, and cleanup unregistering kprobes and removing debugfs files.
