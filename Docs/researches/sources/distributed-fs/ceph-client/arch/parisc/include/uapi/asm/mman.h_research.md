<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/mman.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/mman.h

Source read size: 89 lines, 4003 bytes.

Purpose: defines PA-RISC memory-protection, mapping, msync, mlock, madvise, and pkey constants. Important APIs: `PROT_*`, architecture-specific `MAP_TYPE`, `MAP_FIXED`, `MAP_ANONYMOUS`, `MAP_*` flags, `MS_*`, `MCL_*`, `MLOCK_ONFAULT`, `MADV_*`, `MAP_FILE`, and pkey disable bits. Control flow: mmap/mprotect/msync/mlock/madvise syscalls consume these constants; PA-RISC address-coloring and cache aliasing rules make mapping flags especially visible in MM behavior. State and persistence: mappings and locks persist in VMAs and mm state. Dependencies and integration points: generic mm, PA-RISC `arch_get_unmapped_area`, cache alias flushing in `cache.c`, libc mmap wrappers. Risks: PA-RISC map-type mask includes nonstandard bits; wrong constants break binary mmap behavior and cache-coherency assumptions for executable mappings. Test signals: mmap/mprotect/mremap/munmap tests, executable mapping coherency, shared memory alias tests, mlock/madvise selftests, and 32/64-bit ABI checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/mman.h -->
