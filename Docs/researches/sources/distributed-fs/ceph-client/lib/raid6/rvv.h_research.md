## sources/distributed-fs/ceph-client/lib/raid6/rvv.h

Purpose: defines the RISC-V vector support glue for RAID-6 vector backends, including capability detection and the macro that wraps raw inline-assembly implementations in kernel vector-state management.

Important APIs/types: `rvv_has_vector()` returns `has_vector()`. In kernel builds it includes `<asm/vector.h>`; in userspace tests it stubs `kernel_vector_begin/end()` and implements `has_vector()` with `getauxval(AT_HWCAP) & COMPAT_HWCAP_ISA_V`. `RAID6_RVV_WRAPPER(_n)` generates public `raid6_calls const raid6_rvvx##_n` structures plus wrapper functions for `gen_syndrome` and `xor_syndrome`.

Control flow: generated wrappers enter vector context with `kernel_vector_begin()`, call the corresponding `_real()` implementation in `rvv.c`, then call `kernel_vector_end()`. The `valid` callback is `rvv_has_vector`, and the cache-hint priority field is zero.

State and persistence: the header creates no persistent mutable state. Its main side effect is defining exported algorithm descriptors at compile time wherever the macro is used.

Dependencies/integration: ties `rvv.c` to the generic RAID-6 selection ABI in `linux/raid/pq.h`. It also bridges kernel and userspace test environments by choosing different vector capability definitions.

Risks/test signals: correctness depends on wrapper prototypes matching `_real()` function names and signatures exactly. Userspace detection depends on platform headers exposing compatible HWCAP definitions. RAID-6 userspace tests validate that the wrappers call into vector code only on supported hardware.
