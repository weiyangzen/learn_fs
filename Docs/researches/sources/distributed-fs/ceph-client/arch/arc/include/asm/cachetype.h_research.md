# sources/distributed-fs/ceph-client/arch/arc/include/asm/cachetype.h

Purpose: exposes ARC cache aliasing properties to generic MM code. Important APIs/types/functions: defines `cpu_dcache_is_aliasing()` as false and `cpu_icache_is_aliasing()` as true. Control flow: constant inline-like macros only. State and persistence: none. Dependencies/integration: consumed by generic cache/TLB and MM decisions. Risks: incorrect aliasing claims cause either stale instruction fetches or unnecessary flushes. Test signals: executable page coherency tests and cacheflush path coverage.
