## sources/distributed-fs/openafs/src/vol/common.h

Purpose: public declarations for the volume package logging and fatal-exit helpers implemented in `common.c`.

Important APIs/types/functions: declares `Log(const char *format, ...)`, `Abort(const char *format, ...)`, and `Quit(const char *format, ...)`. Format attributes request compile-time printf checking; `Abort` and `Quit` are marked `AFS_NORETURN`.

Control flow: no runtime flow; annotations communicate non-returning behavior and format contracts to compilers and static analysis.

State and persistence: no state declared here. `Statistics` is defined in `common.c` but not exposed by this header.

Dependencies: expects OpenAFS attribute macros such as `AFS_ATTRIBUTE_FORMAT` and `AFS_NORETURN` to be available from included configuration headers in consumers.

Integration points: included by volume code needing shared logging or fatal helpers. It is part of the volume source tree rather than an installed public AFS header in this Makefile.

Risks: consumers that include it without prior OpenAFS attribute definitions may fail to compile. Since `Abort`/`Quit` are non-returning, incorrect annotations would affect optimizer/static-analysis assumptions.

Test signals: compile checks with GCC/Clang format warnings, splint/static-analysis coverage, and link checks against `common.o`.
