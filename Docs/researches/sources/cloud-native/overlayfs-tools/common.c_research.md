# sources/cloud-native/overlayfs-tools/common.c

Purpose: provides common output, allocation, duplication, and version helpers for overlayfs-tools.

Important APIs/types/functions: `print_debug`, `print_info`, `print_err`, `smalloc`, `srealloc`, `sstrdup`, `sstrndup`, and `version`. Uses global `program_name`.

Control flow: debug output is compiled only when `DEBUG` is defined; info prints to stdout; errors are prefixed with program name and printed to stderr. Allocation wrappers exit on failure after printing translated diagnostics.

State and persistence: no persistent data except reading `program_name`. It can terminate the process on allocation failure.

Dependencies/integration: used by both `overlay` and `fsck.overlay`; depends on `config.h` for package version and `common.h` for gettext macro.

Risks: allocation wrappers make memory failures fatal. `print_debug` signature is compiled even when empty, so format errors may be less visible without debug builds.

Test signals: version output and diagnostics are indirectly covered by CLI tests.
