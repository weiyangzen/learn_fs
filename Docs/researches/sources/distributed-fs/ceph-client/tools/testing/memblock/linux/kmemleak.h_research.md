<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/linux/kmemleak.h -->
# sources/distributed-fs/ceph-client/tools/testing/memblock/linux/kmemleak.h

## Purpose

`linux/kmemleak.h` stubs kmemleak hooks for the user-space memblock simulator. Memblock can notify kmemleak in the kernel, but the simulator does not run the kernel leak detector.

## Important APIs, Types, and Functions

The header defines no-op `kmemleak_free_part_phys(phys, size)`, no-op `kmemleak_alloc_phys(phys, size, gfp)`, and no-op `dump_stack()`.

## Control Flow

All functions return immediately. They preserve call compatibility while intentionally discarding leak-tracking side effects.

## State and Persistence Behavior

No kmemleak state is stored. Alloc/free events are not persisted or inspected by this simulator layer.

## Dependencies and Integration Points

It relies on kernel-style `phys_addr_t`, `size_t`, and `gfp_t` declarations from other included headers. It integrates with `mm/memblock.c` call sites that would normally inform kmemleak.

## Risks and Edge Cases

Leak detector behavior is outside test coverage. Bugs involving kmemleak notification ordering, flags, or stack dumps will not be caught by these memblock simulator tests.

## Test Signals

Compilation without kmemleak symbols and sanitizer-clean execution are expected. New memblock code that depends on kmemleak return values would require this stub to change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/linux/kmemleak.h -->
