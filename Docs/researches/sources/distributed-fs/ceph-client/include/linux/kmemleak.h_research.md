# sources/distributed-fs/ceph-client/include/linux/kmemleak.h

## Purpose

`kmemleak.h` declares allocation/free annotation hooks for the kernel memory leak detector. It lets allocators, percpu/vmalloc paths, physical-memory users, and special objects register, ignore, scan, or erase tracked pointers. The source was read as a complete 129-line file.

## Important APIs, Types, and Functions

With `CONFIG_DEBUG_KMEMLEAK`, APIs include `kmemleak_init()`, `kmemleak_alloc()`, `kmemleak_alloc_percpu()`, `kmemleak_vmalloc()`, `kmemleak_free()`, `kmemleak_free_part()`, `kmemleak_free_percpu()`, `kmemleak_update_trace()`, `kmemleak_not_leak()`, `kmemleak_transient_leak()`, `kmemleak_ignore()`, `kmemleak_ignore_percpu()`, `kmemleak_scan_area()`, `kmemleak_no_scan()`, `kmemleak_alloc_phys()`, `kmemleak_free_part_phys()`, and `kmemleak_ignore_phys()`. Recursive helpers skip caches marked `SLAB_NOLEAKTRACE`.

## Control Flow

Allocation paths annotate new memory, free paths remove it, and scanner configuration helpers adjust what kmemleak treats as roots or ignored objects. In disabled builds all hooks compile away.

## State and Persistence Behavior

Tracked allocations are kept in kmemleak's in-memory object database. `kmemleak_erase()` clears stored pointers to avoid false retention. No state persists across reboot.

## Dependencies and Integration Points

It integrates with slab, percpu, vmalloc, memblock/physical allocations, and debug scanning.

## Risks and Edge Cases

Missing annotations cause false positives or false negatives. `SLAB_NOLEAKTRACE` must be respected for recursive allocation paths. Partial frees and physical allocations need exact size/address accounting.

## Test Signals

Kmemleak selftests, allocator annotation tests, false-positive regression tests for ignored objects, partial-free tests, and disabled-config build coverage are useful.
