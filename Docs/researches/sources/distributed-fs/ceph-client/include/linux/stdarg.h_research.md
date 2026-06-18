<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/stdarg.h -->
# sources/distributed-fs/ceph-client/include/linux/stdarg.h

Purpose: Provides kernel-local varargs definitions backed by compiler builtins.

Important APIs/types/functions: `va_list`, `va_start`, `va_end`, `va_arg`, and `va_copy`.

Control flow: Macro wrappers expand directly to compiler builtins.

State and persistence behavior: `va_list` state is local to a variadic function call frame.

Dependencies: Compiler support for builtin varargs.

Integration points: Formatting, logging, scanning, and any variadic kernel APIs such as `sprintf.h`.

Risks: ABI correctness depends on compiler builtin behavior; callers must still pair `va_start`/`va_end` and use matching argument types.

Test signals: Variadic formatting build/tests and compiler portability checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/stdarg.h -->
