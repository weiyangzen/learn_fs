<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/lib/getopt-cdefs.h -->
# sources/compression/xz/lib/getopt-cdefs.h

Purpose: compatibility shim providing glibc-style cdefs macros expected by shared getopt headers.

Important APIs/types/functions: defines `__BEGIN_DECLS`, `__END_DECLS`, `__GNUC_PREREQ`, and `__THROW`, optionally including `<sys/cdefs.h>`.

Control flow: preprocessor-only; each macro is defined only if absent.

State and persistence: compile-time declarations only.

Dependencies and integration: included by `getopt.in.h` before `getopt-core.h` and `getopt-ext.h`.

Risks: feature detection uses compiler macros and must remain compatible with C and C++. Incorrect exception macro handling can alter C++ prototypes.

Test signals: compile getopt users as C and C++ on non-glibc systems, including MSVC/Clang/GCC variants.
<!-- END_FILE_RESEARCH: sources/compression/xz/lib/getopt-cdefs.h -->
