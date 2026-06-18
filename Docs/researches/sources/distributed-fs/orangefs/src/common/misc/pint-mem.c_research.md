# sources/distributed-fs/orangefs/src/common/misc/pint-mem.c

Purpose: Provides portable aligned allocation/free helpers used by OrangeFS code that needs a pointer divisible by a requested alignment. It also zeroes allocated memory before returning it.

Important APIs and functions: `PINT_mem_aligned_alloc(size, alignment)` returns a zero-filled aligned region or `NULL` with `errno` set. `PINT_mem_aligned_free(ptr)` frees memory allocated by the aligned helper using `_aligned_free()` on Windows or `free()` elsewhere.

Control flow: On Windows it calls `_aligned_malloc()` and converts null to `ENOMEM`. With Electric Fence it falls back to plain `malloc()` because Electric Fence cannot support the usual aligned allocator. Otherwise it calls `posix_memalign()`. After successful allocation it zeroes the requested byte range. Free dispatches to the platform-specific matching free.

State and persistence behavior: No module-level state. The only persistent effect is process heap allocation until the caller frees it.

Dependencies and integration points: Depends on `pvfs2-config.h`, standard allocation APIs, optional `malloc.h`, and Windows support headers. It is a smaller aligned-memory utility separate from the more invasive `pint-malloc` macro wrappers.

Risks and test signals: `ptr` is uninitialized before `posix_memalign()` failure unless callers only use the returned value. Alignment validity follows the platform allocator contract. Tests should cover power-of-two alignments, invalid alignments, zero sizes, Electric Fence configuration, Windows build paths, and verifying returned memory is zeroed and correctly aligned.
