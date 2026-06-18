# sources/distributed-fs/orangefs/src/common/misc/pint-malloc.h

Purpose: Declares OrangeFS allocation wrappers and, when configured, redefines standard allocation calls to those wrappers. It centralizes allocation debugging, zeroing, magic validation, and direct-libc operation-table declarations.

Important APIs and macros: `struct glibc_malloc_ops_s` holds real libc allocator and small I/O function pointers. Configuration macros include `PVFS_MALLOC_DEBUG`, `PVFS_MALLOC_REDEF`, `PVFS_MALLOC_MAGIC`, `PVFS_MALLOC_CHECK_ALIGN`, `PVFS_MALLOC_ZERO`, and `PVFS_MALLOC_FREE_ZERO`. Public wrappers include `PINT_malloc`, `PINT_calloc`, `PINT_posix_memalign`, `PINT_memalign`, `PINT_valloc`, `PINT_realloc`, `PINT_strdup`, `PINT_strndup`, `PINT_free`, and `PINT_free2`. Macro blocks redirect `malloc`, `calloc`, `posix_memalign`, `memalign`, `valloc`, `realloc`, `strdup`, `strndup`, `free`, and `cfree` to wrapper calls with optional file/line metadata.

Control flow and integration: Including this header can alter subsequent allocator calls at preprocessing time. On non-Windows systems it also declares the constructor `init_glibc_malloc()`. On Windows, wrapper redefinition is disabled. The non-redef branch maps direct `PINT_*` use back to system allocators or `PINT_malloc_minimum()`.

State and persistence behavior: The header itself owns no state, but its macros decide whether allocations carry wrapper metadata and whether memory is zeroed on allocation/free. These choices affect all included translation units.

Dependencies and risks: Header inclusion order is critical because it intentionally redefines common allocator names. Mixed clean/system/wrapped allocation families must be kept separate. Test signals include preprocessor smoke tests under all config combinations, Windows builds, debug file/line macro coverage, and external-library memory ownership cases.
