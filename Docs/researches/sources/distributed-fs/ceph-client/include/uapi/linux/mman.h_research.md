# sources/distributed-fs/ceph-client/include/uapi/linux/mman.h

## Purpose
Adds generic Linux memory-management UAPI definitions around remap flags, overcommit policy, shared/private mmap flags, droppable mappings, hugepage encodings, and `cachestat` structures.

## Important APIs, Types, And Functions
Exports `MREMAP_MAYMOVE`, `MREMAP_FIXED`, `MREMAP_DONTUNMAP`, overcommit constants, `MAP_SHARED`, `MAP_PRIVATE`, `MAP_SHARED_VALIDATE`, `MAP_DROPPABLE`, `MAP_HUGE_*` encodings, `cachestat_range`, and `cachestat`.

## Control Flow
Callers pass flags to `mmap`, `mremap`, or `cachestat`-style interfaces. `MAP_SHARED_VALIDATE` asks the kernel to reject unknown extension flags. `MAP_HUGE_*` bits select a hugetlb size when combined with architecture-defined hugetlb mapping flags.

## State, Persistence, And Dependencies
State is VM-area configuration in the kernel and cached page accounting returned by `cachestat`. Depends on `asm/mman.h`, `asm-generic/hugetlb_encode.h`, and `linux/types.h`.

## Integration Points
Used by libc, memory allocators, databases, shared-memory applications, and page-cache observability tools.

## Risks
Some flags are architecture-dependent through `asm/mman.h`; unsupported hugepage sizes must fail cleanly. `MAP_DROPPABLE` has pressure-related semantics that differ from normal shared/private mappings.

## Test Signals
Exercise mremap flag combinations, unknown flag rejection with `MAP_SHARED_VALIDATE`, hugepage size acceptance/failure, overcommit sysctl values, and `cachestat` range accounting.
