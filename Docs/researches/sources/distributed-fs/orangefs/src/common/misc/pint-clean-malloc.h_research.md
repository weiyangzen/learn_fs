# sources/distributed-fs/orangefs/src/common/misc/pint-clean-malloc.h

Purpose: Declares escape-hatch allocation functions that call the platform allocator directly instead of the OrangeFS malloc wrappers from `pint-malloc.h`. These are used when code must allocate memory compatible with external ownership or must avoid recursive macro interception.

Important APIs: The header declares clean variants for `malloc`, `calloc`, `posix_memalign`, `memalign`, `valloc`, `realloc`, `strdup`, `strndup`, and `free`. They are implemented in `pint-malloc.c` before the wrapper macros are included and undefined.

Control flow and integration: This header has no runtime logic. It is included by `pint-malloc.c` and can be used by code that needs uninstrumented allocation. The clean functions are especially relevant around stdio/client interfaces or external libraries that free memory outside OrangeFS wrapper conventions.

State and persistence behavior: No state is declared. The called allocator state is the process allocator state. These APIs intentionally bypass wrapper metadata, zeroing, magic checks, and debug tracing.

Risks and test signals: Memory returned by clean allocators must be freed with `clean_free()` or the real allocator, not `PINT_free()`, because it lacks the `extra_t` header used by wrapper allocations. Tests should cover mixed allocation ownership boundaries and ensure wrapper redefinition does not affect these functions.
