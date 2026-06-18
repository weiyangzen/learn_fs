# sources/distributed-fs/ceph-client/arch/loongarch/lib/bswapdi.c

Purpose: supplies the compiler runtime helper `__bswapdi2()` for 64-bit byte swaps on LoongArch 32-bit builds.

Important APIs, types, and functions: `unsigned long long notrace __bswapdi2(unsigned long long u)` returns `___constant_swab64(u)` and is exported.

Control flow: direct pure computation with no branches.

State and persistence: no state.

Dependencies and integration points: used when compiler emits `__bswapdi2` rather than inline byte-swap instructions; exported for modules.

Risks: ABI signature must exactly match compiler expectations. `notrace` avoids tracing recursion in low-level runtime helpers.

Test signals: 32-bit build/link coverage and byte-order unit tests.
