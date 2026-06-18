# sources/distributed-fs/orangefs/src/common/misc/pint-mem.h

Purpose: Declares OrangeFS aligned memory allocation helpers. It is a simple header for callers that need portable aligned allocation without directly depending on platform-specific allocator names.

Important APIs: `PINT_mem_aligned_alloc()` accepts a byte size and alignment and returns zero-filled aligned memory. `PINT_mem_aligned_free()` frees memory returned by that allocator.

Control flow and integration: The header has no logic. It is included by modules that need aligned buffers and delegates implementation to `pint-mem.c`.

State and persistence behavior: No state is declared. The allocated memory belongs to the caller until explicitly freed.

Dependencies and risks: The prototypes use `size_t`, so including contexts must provide the standard type through other headers or the compile environment. Test signals are basic compile/link coverage and allocator pairing checks.
