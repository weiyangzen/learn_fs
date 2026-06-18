# sources/compression/lz4/programs/util.h

Purpose: shared utility header for program code: integer typedefs, file/stat abstractions, allocation/string helpers, sleep/priority macros, metadata preservation, sizes, and recursive file listing.

Important APIs/types: `BYTE/U16/S16/U32/S32/U64/S64`, `UTIL_fseek`, `UTIL_countCores()`, `stat_t`, `UTIL_realloc()`, `UTIL_sameString()`, file type/stat/size helpers, `UTIL_setFileStat()`, `UTIL_createFileList()`, and `UTIL_freeFileList()`.

Control flow: mostly `UTIL_STATIC` header functions. Recursive listing grows a contiguous string buffer and pointer table, using Windows `FindFirstFileA` or POSIX `opendir/readdir` when available.

State and persistence: stateless except filesystem metadata updates and allocated file-list ownership returned to callers.

Dependencies/integration: depends on `platform.h` and system APIs. Used by CLI recursion and I/O metadata/size/sparse-seek behavior.

Risks: `0` can mean error or zero-size/non-regular file; `UTIL_realloc()` frees old memory on failure; recursive traversal can be sensitive to filesystem topology; metadata copy can partially fail.

Test signals: multiple/recursive tests, huge-file/list/sparse behavior, build-variable checks, and memory tests exercise these utilities.
