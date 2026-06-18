<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/mman.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/mman.h

Purpose: defines Xtensa UAPI memory-management protection and mapping constants. Important definitions include `PROT_*`, `MAP_TYPE`, `MAP_FIXED`, legacy non-Linux flags, Linux `MAP_*`, `MS_*`, `MCL_*`, `MLOCK_ONFAULT`, `MADV_*` including guard and collapse flags, `MAP_FILE`, and pkey disable masks.

Control flow is userspace/kernel ABI constant interpretation in mmap, mprotect, msync, mlock, madvise, and pkey paths. Persistent state affected is VMA flags, page protections, locked memory state, and memory advice state. Dependencies are generic MM syscalls and architecture protection support in `pgtable.h`. Integration points include libc, ELF loader, memory allocators, SysV shm mapping, and tests. Risks include ABI constant collisions, unsupported execute/write protection nuance, and stale additions relative to generic MM. Test signals include mmap/mprotect/msync/mlock/madvise selftests, userspace header compile checks, and protection fault tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/mman.h -->
