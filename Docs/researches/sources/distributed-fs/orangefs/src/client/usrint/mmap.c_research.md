# sources/distributed-fs/orangefs/src/client/usrint/mmap.c

## Purpose
`mmap.c` implements minimal mmap-family behavior for PVFS descriptors. It does not provide kernel-backed shared file mappings; instead it maps anonymous memory, reads file contents into that memory, records mapping metadata, and writes shared mappings back on `munmap` or `msync`. Anonymous mappings bypass PVFS and are delegated directly to `glibc_ops.mmap`.

## Important APIs And Functions
The exported functions are `pvfs_mmap`, `pvfs_munmap`, and `pvfs_msync`, registered in `pvfs_ops` by `posix-pvfs.c`. The file maintains a static `maplist` of `struct pvfs_mmap_s` records, whose fields are defined in `posix-ops.h`: mapping start, length, protection, flags, fd, offset, and quicklist link.

## Control Flow
`pvfs_mmap` checks `MAP_ANONYMOUS` first and delegates to glibc for non-file mappings. For PVFS file mappings, it finds the descriptor with `pvfs_find_descriptor`, creates an anonymous mapping through `glibc_ops.mmap`, reads the requested region with `pvfs_pread`, allocates a mapping-list entry, records metadata, and appends it to `maplist`. `pvfs_munmap` validates page alignment, searches for an exact `(start, length)` mapping, removes it, writes the full mapping back with `pvfs_pwrite` when `MAP_SHARED` was set, delegates unmap to glibc, then frees the metadata. `pvfs_msync` validates alignment, finds an existing mapping that fully covers the requested subrange, and writes that subrange back for shared mappings.

## State And Persistence Behavior
The only local state is the process-global `maplist`; there is no per-descriptor registration. File persistence occurs only through explicit `pvfs_pwrite` on shared mappings during `pvfs_munmap` or `pvfs_msync`. Private mappings never write back. The implementation does not track dirty pages, partial unmaps, protection changes, fork inheritance, or invalidation.

## Dependencies And Integration Points
The file includes `usrint.h`, `posix-ops.h`, `posix-pvfs.h`, `openfile-util.h`, and `<quicklist.h>`. It depends on `glibc_ops.mmap/munmap`, descriptor lookup, and PVFS pread/pwrite wrappers. `PVFS2_SIZEOF_VOIDP` controls pointer-width-specific alignment checks.

## Risks
There appears to be a correctness bug: `pvfs_mmap` stores `mlist->mst = start` rather than the returned mapped address `maddr`, so `munmap`/`msync` lookups can fail whenever the kernel does not map exactly at the requested `start` address, including typical `start == NULL` calls. The call to `glibc_ops.mmap` uses `flags & MAP_ANONYMOUS`, which strips most original mapping flags and may not set `MAP_PRIVATE`/`MAP_SHARED` as required by the platform. `pvfs_munmap` declares `mapl` uninitialized and checks `if (!mapl)` after the loop, which is unsafe if the list is empty or no match is found. The global list is not locked, so concurrent mmap/munmap/msync calls can race. Allocation failure for `mlist` is not checked. Writeback errors from `pvfs_pwrite` in `munmap` are ignored.

## Test Signals
Tests should map with `start == NULL`, verify `munmap` succeeds by returned address, exercise exact and subrange `msync`, check `MAP_SHARED` writeback and `MAP_PRIVATE` non-writeback, validate page-alignment errors, map/unmap multiple regions, run concurrent mapping operations, inject `malloc`/`pread`/`pwrite` failures, and compare behavior against POSIX expectations for anonymous mappings.
