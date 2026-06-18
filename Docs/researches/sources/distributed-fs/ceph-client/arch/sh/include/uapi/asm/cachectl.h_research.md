<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/cachectl.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/cachectl.h

Purpose: defines SH cacheflush syscall operation flags.

Important APIs/types/functions: `CACHEFLUSH_D_INVAL`, `CACHEFLUSH_D_WB`, `CACHEFLUSH_D_PURGE`, `CACHEFLUSH_I`, `ICACHE`, `DCACHE`, `BCACHE`.

Control flow: userspace passes these flags to cacheflush/cache control entry points.

State and persistence: state is CPU cache contents affected by syscall handlers elsewhere.

Dependencies/integration: integrates UAPI with SH cacheflush implementation and JIT/self-modifying-code users.

Risks: flag value changes break existing binaries.

Test signals: run userspace cacheflush tests for D/I/both cache cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/cachectl.h -->
