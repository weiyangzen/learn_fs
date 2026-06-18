# sources/distributed-fs/orangefs/src/client/windows/client-test/test-support.h

Purpose: Declares the shared client-test support interface and cross-platform compatibility macros for Windows-style test code.

Important APIs/types: `global_options` carries `root_dir`, `tab_file`, filesystem selector, output flags, and report stream. Constants define fatal sentinel `CODE_FATAL`, expected result enums, comparison operation indexes, and output sinks. Function prototypes cover string/path helpers, file creation, error/result/performance reporting.

Control flow: This header does not implement behavior, but it defines the operation index contract consumed by `test-support.c` and test modules.

State/persistence: The only state shape is `global_options`, whose `freport` pointer is used by report functions to persist logs.

Dependencies/integration: On non-Windows builds it maps `_rmdir`, `_mkdir`, `_strdup`, `_unlink`, `_stricmp`, `_stat`, and `_snprintf` to POSIX equivalents, and defines slash constants. It expects `FILE` to be visible through included standard headers in consumers.

Risks: The include guard name `__TESTS_H` is generic. Function prototypes use mutable `char *` for some input strings even when implementations do not modify them. The non-Windows compatibility macros may hide signature differences, especially `_mkdir(dir)` expanding to `mkdir(dir, 0777)`.

Test signals: Compile both Windows and POSIX client-test paths, and verify operation constants still match the `ops[]` array order in `test-support.c`.
