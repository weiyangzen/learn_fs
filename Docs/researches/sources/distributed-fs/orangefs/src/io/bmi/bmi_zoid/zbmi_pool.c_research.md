# sources/distributed-fs/orangefs/src/io/bmi/bmi_zoid/zbmi_pool.c

## Purpose

`zbmi_pool.c` adapts dlmalloc's mspace allocator into a tiny fixed-buffer allocator for the ZOID BMI expected shared-memory region. It configures dlmalloc at compile time, includes `dlmalloc.c` directly, stores one global `mspace`, and exports init/fini/malloc/free wrappers used by `server.c`.

## Important APIs and functions

- Compile-time defines: `ONLY_MSPACES=1`, `MSPACES=1`, `MALLOC_ALIGNMENT=16`, `USE_LOCKS=1`, and `HAVE_MMAP=0`.
- Weak pragmas are declared for mspace symbols to avoid duplicate symbol errors with ZeptoOS MPI compilers.
- `static mspace pool = NULL` holds the single allocator instance.
- `zbmi_pool_init(void *start, size_t len)` creates the mspace with `create_mspace_with_base(start, len, 1)`.
- `zbmi_pool_fini(void)` destroys the mspace and clears the global handle.
- `zbmi_pool_malloc(size_t bytes)` delegates to `mspace_malloc(pool, bytes)`.
- `zbmi_pool_free(void *mem)` delegates to `mspace_free(pool, mem)`.

## Control flow

The server calls `zbmi_pool_init` after mapping the ZBMI shared memory and selecting the expected-buffer subrange. Subsequent BMI memory allocation or temporary expected-buffer allocation calls enter `zbmi_pool_malloc`, which returns pointers inside the supplied shared-memory region. Frees return memory through `zbmi_pool_free`. Finalization calls `zbmi_pool_fini` before unmapping the shared memory.

## State and persistence behavior

The only module state is the process-global `pool` pointer. Allocator metadata lives inside the supplied shared-memory range because `create_mspace_with_base` embeds the mspace state in that memory. No state persists after `zbmi_pool_fini` and the server's `munmap`; the ZBMI peer should treat expected-buffer offsets as transient.

## Dependencies and integration points

This file depends on `dlmalloc.c` being available in the same directory and on the compiler accepting direct inclusion of a `.c` file. It is compiled via `module.mk.in` as part of the ZOID BMI module. `server.c` uses the functions through `zbmi_pool.h` for `BMI_memalloc`, `BMI_memfree`, and temporary buffers for `BMI_EXT_ALLOC`.

## Risks and edge cases

- There is no guard for `create_mspace_with_base` failure. If `start`/`len` are invalid or too small, `pool` remains `NULL`, and later malloc/free calls enter dlmalloc with a bad mspace.
- There are no double-init or use-after-fini checks.
- `HAVE_MMAP=0` with `ONLY_MSPACES=1` means the pool cannot grow outside the supplied shared-memory range. This is intended but makes allocation failure a normal server condition.
- Directly including `dlmalloc.c` means all compile definitions above the include are critical; moving them or compiling `dlmalloc.c` separately changes behavior.
- The weak pragmas are toolchain-specific and may be ignored or warned on non-GNU/non-compatible compilers.

## Test signals

Create a fixed aligned buffer, call `zbmi_pool_init`, allocate and free several sizes, verify returned pointers are inside the buffer and 16-byte aligned, exhaust the pool to check `NULL` behavior, and call `zbmi_pool_fini`. Negative tests should cover too-small buffers and accidental malloc/free before init or after fini, since the current code does not protect those cases.
