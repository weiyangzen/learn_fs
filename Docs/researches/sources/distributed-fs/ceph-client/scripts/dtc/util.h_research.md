# sources/distributed-fs/ceph-client/scripts/dtc/util.h

Purpose: Public utility header for dtc support code, including compiler attributes, fatal error handling, allocation wrappers, string helpers, libfdt I/O helpers, option-parsing helpers, and usage macros.

Important APIs/types: Defines `PRINTF`, `NORETURN`, `ARRAY_SIZE`, stringification macros, inline `die()`, `xmalloc()`, and `xrealloc()`. Declares string, path, escape, FDT read/write, data print, version, and usage functions. Provides `USAGE_COMMON_*`, `usage(errmsg)`, `util_getopt_long()`, and `case_USAGE_COMMON_FLAGS` helpers.

Control flow: Header inlines allocation failure into process termination via `die()`. getopt helpers assume local variables named `argc`, `argv`, and `usage_*`.

State/persistence: No state, but `die()`, `util_version()`, and `util_usage()` exit the process. Allocation wrappers return heap memory that callers own.

Dependencies/integration: Includes standard headers and `getopt.h`. Used by dtc C files and libfdt utilities for consistent error handling and CLI behavior.

Risks: Macros assume naming conventions and can obscure control flow because common option cases do not `break` after exit-only calls. Allocation wrappers cannot represent recoverable allocation failure. `PRINTF` format selection has platform-specific behavior for MinGW.

Test signals: Compile under GCC and non-GCC-like compilers, exercise shared CLI common options, and verify format-attribute warnings on supported toolchains.
