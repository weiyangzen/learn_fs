# sources/distributed-fs/ceph-client/include/uapi/asm-generic/mman-common.h

Purpose: Defines generic memory-protection, mmap, mlock, msync, madvise, guard, and protection-key constants common to architectures.

Important APIs/types/functions: Exports `PROT_*`, common `MAP_*` flags including `MAP_FIXED_NOREPLACE`, `MAP_SYNC`, `MAP_HUGETLB`, `MAP_UNINITIALIZED`, `MLOCK_ONFAULT`, `MS_*`, many `MADV_*` values including hugepage/KSM/pageout/populate/collapse/guard controls, `MAP_FILE`, and `PKEY_*`.

Control flow: Preprocessor constants only; architecture-specific `mman.h` layers add or override other bits.

State/persistence: No runtime state; constants define syscall ABI.

Dependencies/integration: Included by `asm-generic/mman.h` and architecture mmap headers.

Risks: Values must remain non-overlapping with architecture-specific bits and hugetlb encoding. ABI changes break mmap/madvise users.

Test signals: mmap/mlock/madvise headers compile checks and runtime mmap flag tests.
