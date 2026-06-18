# sources/distributed-fs/ceph-client/arch/mips/lib/bswapdi.c

Purpose: supplies GCC/libgcc 64-bit byte-swap helper `__bswapdi2`.

Important APIs/functions: exports `notrace unsigned long long __bswapdi2(unsigned long long u)`.

Control flow: returns `___constant_swab64(u)`.

State and persistence: stateless.

Dependencies and integration: used when compiler emits a libgcc byte-swap call inside the kernel; includes swab and compiler headers.

Risks: must remain `notrace` and exported to satisfy early/runtime compiler-generated calls without recursion surprises.

Test signals: MIPS builds with compilers that emit `__bswapdi2`, byte-swap correctness, and symbol export checks.
