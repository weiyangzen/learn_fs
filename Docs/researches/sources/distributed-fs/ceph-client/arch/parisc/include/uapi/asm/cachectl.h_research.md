<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/cachectl.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/cachectl.h

Source read size: 12 lines, 354 bytes.

Purpose: exposes PA-RISC `cacheflush` syscall cache selector bits to userspace. Important APIs: `ICACHE`, `DCACHE`, and `BCACHE`. Control flow: userspace passes these bits to `SYSCALL_DEFINE3(cacheflush)` in `cache.c`, which flushes data and/or instruction cache ranges. State and persistence: no persistent header state; syscall mutates CPU cache state. Dependencies and integration points: JITs, dynamic code generators, and libc wrappers depend on these constants. Risks: bit changes break self-modifying code and JIT cache synchronization. Test signals: userspace JIT/self-modifying-code tests and invalid-pointer/range `cacheflush` syscall tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/cachectl.h -->
