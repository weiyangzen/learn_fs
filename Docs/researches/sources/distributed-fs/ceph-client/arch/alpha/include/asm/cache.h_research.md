# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/cache.h

This header defines L1 cacheline sizing for Alpha. Generic and EV6 builds use 64-byte lines; older EV4/EV5 style systems use 32-byte lines. `SMP_CACHE_BYTES` is set equal to `L1_CACHE_BYTES`.

There is no control flow or persistence. The values affect structure alignment, per-CPU layout, DMA/cache assumptions, and generic kernel cacheline padding. Risks are false sharing or ABI/layout changes if CPU selection and actual hardware diverge. Test signals are compile-time layout checks and runtime stability on both EV5-like and EV6-like systems.
