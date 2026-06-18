# sources/distributed-fs/orangefs/src/io/bmi/bmi_zoid/dlmalloc.c

## Purpose

`dlmalloc.c` is Doug Lea malloc 2.8.4 embedded as a single translation-unit allocator implementation. In this OrangeFS directory it is not normally compiled as a standalone `malloc` replacement; `zbmi_pool.c` includes this file directly after defining `ONLY_MSPACES=1`, `MSPACES=1`, `MALLOC_ALIGNMENT=16`, `USE_LOCKS=1`, and `HAVE_MMAP=0`. That means the active integration path is the mspace allocator API over an externally supplied shared-memory range, not the global `dlmalloc`/`dlfree` path.

The allocator provides boundary-tag heap management, small-bin lists, large-bin size tries, a designated-victim chunk, a top chunk, optional segment tracking, optional locking, and optional diagnostics. It is used by the ZOID BMI server to suballocate the expected-message portion of the shared memory block exchanged with the ZBMI plugin.

## Important APIs, types, and functions

- Public global APIs when `ONLY_MSPACES` is false: `dlmalloc`, `dlfree`, `dlcalloc`, `dlrealloc`, `dlmemalign`, `dlvalloc`, `dlpvalloc`, `dlmallopt`, `dlmalloc_trim`, `dlmalloc_stats`, `dlmalloc_footprint`, `dlmalloc_max_footprint`, `dlmalloc_usable_size`, `dlindependent_calloc`, and `dlindependent_comalloc`.
- Public mspace APIs when `MSPACES` is true: `create_mspace`, `destroy_mspace`, `create_mspace_with_base`, `mspace_track_large_chunks`, `mspace_malloc`, `mspace_free`, `mspace_realloc`, `mspace_calloc`, `mspace_memalign`, `mspace_independent_calloc`, `mspace_independent_comalloc`, `mspace_trim`, `mspace_malloc_stats`, `mspace_footprint`, `mspace_max_footprint`, `mspace_mallinfo`, `mspace_usable_size`, and `mspace_mallopt`.
- Internal heap structures include `struct malloc_chunk`, `struct malloc_tree_chunk`, `struct malloc_segment`, `struct malloc_state`, and `struct malloc_params`.
- `init_mparams()` initializes process-wide allocator parameters such as page size, granularity, mmap threshold, trim threshold, default flags, lock state, and a magic value.
- `init_user_mstate()` initializes a per-mspace `malloc_state` inside the supplied arena.
- `create_mspace_with_base()` is the key function for this tree: it creates an allocator state inside the caller-provided buffer, marks the segment with `EXTERN_BIT`, and optionally enables the mspace lock.
- `mspace_malloc()` selects a chunk from small bins, tree bins, the designated-victim chunk, the top chunk, or `sys_alloc()`.
- `mspace_free()` validates, coalesces backward and forward, returns top space where possible, and reinserts free chunks into small or tree bins.

## Control flow

Allocation first normalizes the request to an internal chunk size. Small requests prefer exact or near-exact small-bin chunks, then the designated-victim chunk, then tree-bin fallback, then top chunk splitting, and finally `sys_alloc()`. Large requests search tree bins for best fit, fall back to the designated-victim chunk, top chunk, or system allocation. Freeing converts the user pointer back to a chunk, checks mspace magic and in-use bits, coalesces adjacent free chunks, updates `dv` or `top` when applicable, and otherwise links the consolidated chunk into a small bin or tree bin.

For the OrangeFS `zbmi_pool.c` embedding, the allocator is initialized with `create_mspace_with_base(start, len, 1)`. The provided shared-memory region holds the `malloc_state` and all chunks. Because `HAVE_MMAP=0` and `ONLY_MSPACES=1` makes `HAVE_MORECORE` default to 0, normal growth through `sys_alloc()` is effectively unavailable after the supplied arena is exhausted. Allocation failure returns `NULL` after `MALLOC_FAILURE_ACTION`; the server then queues some operations until memory is freed.

## State and persistence behavior

Allocator state is process-local metadata stored inside the shared-memory expected-buffer region. It is not persistent across server restarts and should not be interpreted by the external ZBMI plugin except as opaque memory offsets for posted buffers. `destroy_mspace()` skips unmapping `EXTERN_BIT` segments, so final arena lifetime remains owned by the caller (`server.c`, through `munmap`). With locks enabled and `locked=1`, public mspace calls acquire the per-mspace mutex embedded in `struct malloc_state`.

The allocator also has global process state in `mparams` and, if global malloc mode is compiled, `_gm_`. In this usage, `mparams` still initializes and stores page/alignment/magic/tuning data, but `_gm_` and global allocation APIs are compiled out by `ONLY_MSPACES`.

## Dependencies and integration points

This file depends on standard C/POSIX headers selected by compile-time macros: `errno.h`, `stdlib.h`, `string.h`, `unistd.h`, `pthread.h`, and optionally `sys/mman.h`/`fcntl.h` when mmap support is enabled. The active OrangeFS integration comes from direct inclusion in `zbmi_pool.c`, not from linking `dlmalloc.c` as its own object. `module.mk.in` lists `zbmi_pool.c` but not `dlmalloc.c`, which is consistent with the inclusion model.

The exported mspace APIs are wrapped by `zbmi_pool_init`, `zbmi_pool_malloc`, `zbmi_pool_free`, and `zbmi_pool_fini`, which are then called by `server.c` for BMI shared-memory allocation.

## Risks and edge cases

- This is old vendored allocator code with many macro-heavy pointer operations. It assumes `size_t` has pointer width, chunk alignment is a power of two, and compiler/platform behavior matches its supported matrix.
- The OrangeFS build defines `HAVE_MMAP=0` and does not define a custom `MORECORE`, so the mspace is a fixed-capacity arena. Any allocator path that reaches system allocation will fail; server-side queuing must handle that correctly.
- `create_mspace_with_base()` stores allocator metadata inside the caller-supplied arena, reducing usable space by the padded `malloc_state` and top-foot overhead.
- With `FOOTERS=0`, freeing to the wrong mspace is not strongly checked. The wrapper must never pass non-pool pointers to `mspace_free`.
- Default corruption and usage error actions call `abort()` unless overridden. A pool metadata overwrite can terminate the BMI server process.
- The direct include model means compile definitions in `zbmi_pool.c` are part of the allocator ABI. Compiling `dlmalloc.c` independently with different options would create a different symbol and behavior surface.

## Test signals

Useful test signals include building the ZOID-enabled OrangeFS target, initializing a pool over a fixed buffer, checking 16-byte alignment of returned pointers, exhausting the pool and verifying `NULL` is returned rather than writing past the arena, freeing and reallocating varied small/large sizes to exercise small bins and tree bins, and running concurrent `zbmi_pool_malloc/free` calls to validate the locked mspace path. AddressSanitizer or valgrind can help catch wrapper misuse, but allocator-internal metadata in shared memory may require suppressions or focused harnesses.
