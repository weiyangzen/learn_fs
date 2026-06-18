# sources/distributed-fs/ceph-client/arch/loongarch/lib/bswapsi.c

Purpose: supplies the compiler runtime helper `__bswapsi2()` for 32-bit byte swaps.

Important APIs, types, and functions: `unsigned int notrace __bswapsi2(unsigned int u)` returns `___constant_swab32(u)` and is exported.

Control flow: direct pure computation.

State and persistence: no state.

Dependencies and integration points: used for compiler-emitted byte-swap helper calls and exported to modules.

Risks: ABI mismatch would break links or corrupt byte-order conversions. `notrace` prevents instrumentation in a compiler helper.

Test signals: 32-bit builds, module link tests, and byte-swap correctness checks.
