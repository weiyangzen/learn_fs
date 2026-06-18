# sources/compression/zstd/examples/common.h

Purpose: shared helper header for zstd examples. It provides fatal-check macros and small file/memory utilities so example source files can focus on zstd API usage.

Important APIs/types: `COMMON_ErrorCode`, `CHECK`, `CHECK_ZSTD`, `fsize_orDie`, `fopen_orDie`, `fclose_orDie`, `fread_orDie`, `fwrite_orDie`, `malloc_orDie`, `loadFile_orDie`, `mallocAndLoadFile_orDie`, and `saveFile_orDie`. `HEADER_FUNCTION` marks helpers static and optionally unused.

Control flow: helpers either return successful results or print an error and exit with a specific code. File helpers use `stat`, `fopen`, `fread`, `fwrite`, and `fclose`. `mallocAndLoadFile_orDie()` sizes a file, allocates exactly that much memory, then loads it. `CHECK_ZSTD` wraps zstd return codes with `ZSTD_isError()` and `ZSTD_getErrorName()`.

State and persistence: no persistent state. File helpers read and write named paths and allocate caller-owned memory. Error paths terminate the process.

Dependencies/integration: includes libc headers, `sys/stat.h`, and public `zstd.h`. Every examples `.c` file includes it, making its static functions local to each translation unit.

Risks: fatal exits are appropriate for examples but not reusable library helpers. `malloc_orDie(0)` may fail on implementations returning NULL for zero-byte allocation, affecting empty-file cases through `mallocAndLoadFile_orDie`. `fread_orDie` allows short reads on EOF, which is useful for streaming loops but can hide unexpectedly short fixed reads if misused. `saveFile_orDie` and `loadFile_orDie` duplicate some low-level checks instead of using the wrapper functions consistently.

Test signals: examples test suite, large-file size conversion checks, missing files, write-permission failures, zero-length files, and zstd error wrapping.
