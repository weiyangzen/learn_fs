# sources/distributed-fs/ceph-client/arch/sparc/lib/multi3.S

Purpose: SPARC64 assembly implementation of GCC runtime helper `__multi3`, producing a 128-bit product from two 64-bit operands. It supports compiler-generated `__int128` multiplication in kernel code.

Important APIs/functions: `ENTRY(__multi3)` with operands in `%o0/%o1` and `%o2/%o3`, returns high/low result through `%o0/%o1`. `ENDPROC(__multi3)` and `EXPORT_SYMBOL(__multi3)` integrate it with kernel symbol/linkage conventions.

Control flow: it decomposes operands into 32-bit halves, uses `mulx` for partial products, manages carries with `addcc`, `srlx`, and conditional moves, then adds cross terms and high-half products before returning in the delay slot.

State and persistence: no memory or global state. It is a leaf routine and only consumes caller registers.

Dependencies/integration: includes `linux/export.h` and `linux/linkage.h`. Used by compiler output and potentially modules requiring 128-bit arithmetic support on SPARC64.

Risks: carry propagation is dense and branchless; a single condition-code misuse changes high-word results only on boundary inputs. ABI correctness is critical because helper calls are compiler-generated and not manually audited at call sites.

Test signals: randomized 64x64-to-128 multiplication tests, edge cases such as `0xffffffffffffffff * 0xffffffffffffffff`, powers of two, and high-only/low-only operands. Cross-check with compiler-rt/libgcc reference on SPARC64.
