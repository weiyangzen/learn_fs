# Research: sources/distributed-fs/ceph-client/tools/perf/bench/mem-memcpy-arch.h

Purpose: declares architecture-specific memcpy benchmark implementations for x86_64 builds.

Important APIs/types/functions: under `HAVE_ARCH_X86_64_SUPPORT`, temporarily defines `MEMCPY_FN()` to emit prototypes and includes `mem-memcpy-x86-64-asm-def.h`.

Control flow: preprocessor-only expansion.

State and persistence: no state.

Dependencies and integration: consumed by `mem-functions.c`; declarations must match assembly symbols supplied by `mem-memcpy-x86-64-asm.S`.

Risks: macro contract must stay synchronized with definition header and assembly symbol names.

Test signals: x86_64 perf bench build and selecting `x86-64-unrolled` / `x86-64-movsq` memcpy functions.
