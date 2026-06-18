# Research: sources/distributed-fs/ceph-client/tools/perf/bench/mem-memcpy-x86-64-asm.S

Purpose: wraps the kernel x86_64 `memcpy_64.S` implementation so it can be built into user-space perf bench.

Important APIs/types/functions: redefines `SYM_FUNC_START_LOCAL()` to export local kernel symbols globally, renames `memcpy` to `MEMCPY` to avoid hiding glibc, stubs exception-table macros, remaps `altinstr_replacement`, and includes `../../arch/x86/lib/memcpy_64.S`.

Control flow: assembly inclusion supplies actual memcpy implementations; this file only adapts build macros.

State and persistence: no state. Adds `.note.GNU-stack` to request a non-executable stack.

Dependencies and integration: depends on kernel x86 assembly source and Linux assembly macro conventions. Provides symbols referenced by `mem-memcpy-x86-64-asm-def.h`.

Risks: fragile against changes in kernel assembly macro names or required sections. User-space build stubs exception handling, so only benchmark-safe paths are expected.

Test signals: x86_64 assembly build/link, non-executable stack note in object, and successful execution of both x86 memcpy variants.
