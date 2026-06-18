# Research: sources/distributed-fs/ceph-client/tools/perf/bench/mem-memset-x86-64-asm.S

Purpose: wraps kernel x86_64 `memset_64.S` so perf bench can benchmark kernel-style memset implementations in user space.

Important APIs/types/functions: exports local symbols by redefining `SYM_FUNC_START_LOCAL()`, renames `memset` to `MEMSET`, remaps `altinstr_replacement`, defines `globl`, includes `../../arch/x86/lib/memset_64.S`, and emits `.note.GNU-stack`.

Control flow: actual memset control flow is in the included kernel assembly; this file supplies build adaptation.

State and persistence: no state. Non-executable stack note is emitted.

Dependencies and integration: depends on kernel x86 memset assembly and symbol names referenced by `mem-memset-x86-64-asm-def.h`.

Risks: user-space wrapper can break if kernel assembly gains new macro dependencies. It intentionally avoids glibc symbol collision by renaming.

Test signals: x86_64 assembly build/link, stack note check, and perf bench memset using `x86-64-unrolled` and `x86-64-stosq`.
