# sources/distributed-fs/ceph-client/include/linux/decompress/mm.h

Purpose: Provides allocation wrappers for decompressor code in two environments: early/pre-boot static decompression and normal in-kernel ramdisk decompression.

Important APIs, types, and functions: In `STATIC` builds it defines `malloc_ptr`, `malloc_count`, `malloc()`, `free()`, `large_malloc()`, `large_free()`, `STATIC_RW_DATA`, `MALLOC_VISIBLE`, and `INIT`. In normal builds it maps `malloc/free` to `kmalloc/kfree`, large allocation to `vmalloc/vfree`, marks `INIT` as `__init`, and defines `STATIC`.

Control flow: Early boot allocation starts from external `free_mem_ptr`, aligns allocations to eight bytes, advances a bump pointer, checks `free_mem_end_ptr` when available, and resets the pointer only when nested allocation count returns to zero. Normal kernel code uses slab/vmalloc allocators.

State and persistence: Early boot mode maintains global allocator cursor and allocation nesting count. Allocations are temporary for decompression; no persistent state is intended.

Dependencies and integration points: Depends on boot decompressor-provided `free_mem_ptr/free_mem_end_ptr` in static mode and on kernel memory APIs in normal mode. Included by format implementations to avoid duplicating environment-specific allocation logic.

Risks and test signals: Risks include early memory overflow, negative size handling, allocation nesting leaks preventing pointer reset, and accidental local data where an architecture needs relocatable pre-boot code. Test static decompressor builds, bounded free-memory regions, nested allocations/frees, large allocation users, and normal initramfs decompression.
