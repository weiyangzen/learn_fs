# sources/distributed-fs/ceph-client/drivers/misc/lkdtm/lkdtm.h

## Purpose
`lkdtm.h` is the shared LKDTM internal interface. It defines crash type descriptors, category descriptors, category exports, init/exit hooks, and helper macros for expected configuration reporting.

## Important APIs, Types, and Functions
Primary types are `struct crashtype` and `struct crashtype_category`. The `CRASHTYPE()` macro maps a symbolic test name to `lkdtm_<NAME>`. `pr_expected_config()` and `pr_expected_config_param()` format hardening expectation messages using `lkdtm_kernel_info`. Built-in kernels also expose `lkdtm_check_bool_cmdline()`.

## Control Flow
Category C files build static arrays with `CRASHTYPE()` and export one `struct crashtype_category`. `core.c` iterates those categories to list and dispatch tests. Expected-config helpers branch on `IS_ENABLED(kconfig)` and, for built-in kernels, parsed boot parameters.

## State and Persistence
The header declares the shared `lkdtm_kernel_info` string and all category symbols, but owns no storage except macro expansions in users.

## Dependencies and Integration Points
Depends on `<linux/kernel.h>`, LKDTM category object files, and module-vs-built-in compilation. The `lkdtm_rodata_do_nothing()` declaration is used by permissions tests to execute code placed in rodata through build tricks.

## Risks
The macro naming convention must match function definitions exactly. Missing category objects or mismatched init/exit declarations would fail link-time integration. Expected-config messages are diagnostic only and do not enforce hardening.

## Test Signals
Signals are successful linking of all category exports, debugfs listing containing all declared crashtypes, meaningful expected-config logs for positive and negative hardening cases, and built-in command-line parameter handling.
