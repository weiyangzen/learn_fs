<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/shmparam.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/shmparam.h

Purpose: defines shared-memory low boundary alignment `SHMLBA` for Xtensa, choosing the larger of `PAGE_SIZE` and `DCACHE_WAY_SIZE` to avoid cache aliasing for System V shared memory.

Control flow is compile-time only. State affected is userspace shared-memory mapping placement and alignment as enforced by generic IPC/MM code. Dependencies are page size and data-cache geometry. Integration points include `arch_get_unmapped_area`, SysV shared memory attachment, cache alias avoidance, and mmap alignment. Risks are aliasing corruption if `SHMLBA` is too small for a cache configuration, and ABI-visible behavior if changed. Test signals include SysV shm attach tests, mmap alignment checks, cache-alias stress on large-way caches, and noMMU/MMU build validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/shmparam.h -->
