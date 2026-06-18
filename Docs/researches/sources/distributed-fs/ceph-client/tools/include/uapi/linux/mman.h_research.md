# sources/distributed-fs/ceph-client/tools/include/uapi/linux/mman.h

Purpose: defines Linux memory-mapping and memory-advice UAPI flags layered on architecture-generic mmap constants.

Important APIs/types: includes architecture generic mman definitions and adds/normalizes flags for shared mappings, validation, fixed mappings, locked mappings, huge pages, sync mappings, stack growth, populate/nonblock, noreserve, denywrite/executable/file placeholders, and huge-page size encodings. It also defines `MREMAP_*`, `MLOCK_ONFAULT`, `MADV_*` advice values, `MAP_HUGE_SHIFT/MASK`, and related constants where present.

Control flow, state, and persistence: userspace passes flags to `mmap`, `mprotect`, `mremap`, `mlock2`, and `madvise`. Kernel creates or mutates VMA state, page fault behavior, locking, huge page selection, and advisory memory policy. Mapping state persists until munmap, process exit, or further VMA changes.

Dependencies and integration points: depends on architecture generic mman and hugetlb encoding headers. It integrates mm/VMA management, hugetlbfs, tmpfs, device mappings, DAX, allocators, runtimes, and databases.

Risks and test signals: risks include architecture-specific flag differences, `MAP_FIXED` replacement hazards, `MAP_SHARED_VALIDATE` feature rejection, huge page size mismatch, lock-limit failures, and advice values being advisory rather than guaranteed. Tests should mmap shared/private/fixed/huge mappings, validate unknown flag rejection with shared-validate, exercise mremap growth/move, mlock-on-fault, and key madvise modes.
