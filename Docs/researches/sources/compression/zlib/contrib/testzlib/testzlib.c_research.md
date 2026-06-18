# sources/compression/zlib/contrib/testzlib/testzlib.c

Purpose: Windows command-line utility that compresses and decompresses a file with zlib while reporting timing from `GetTickCount`, `QueryPerformanceCounter`, and optionally `rdtsc`.

Important APIs, types, and functions: Includes Windows and zlib APIs. `MyDoMinus64()` subtracts `LARGE_INTEGER` values. `BeginCountRdtsc()` / `GetResRdtsc()` provide CPU-cycle timing on x86/x64. `BeginCountPerfCounter()` and `GetMsecSincePerfCounter()` provide wall-clock timing. `ReadFileMemory()` loads a file. `main()` runs `deflateInit`/`deflate`/`deflateEnd` and `inflateInit`/`inflate`/`inflateEnd`, then compares output with `memcmp`.

Control flow: After argument parsing and file loading, it allocates an estimated compression buffer, compresses in chunks using `Z_SYNC_FLUSH` until the final `Z_FINISH`, shrinks the compressed buffer, allocates an uncompressed buffer, inflates in chunks, prints timings and sizes, and reports compare success when lengths and bytes match.

State and persistence: Uses heap buffers for file, compressed, and uncompressed data but does not free them before process exit. It maintains timing state in `LARGE_INTEGER` locals.

Dependencies and integration points: Built by `contrib/testzlib/CMakeLists.txt` against shared or static zlib targets. It is Windows-specific due to `windows.h`, `DWORD`, inline assembly/MSVC intrinsics, `min`, and `%I64x`.

Risks: Minimal zlib return checking; loops assume progress and can misbehave on unexpected errors. Buffer-size estimates may be inadequate for pathological data/settings. Uses `long` for file sizes, limiting large files on some builds. No explicit cleanup on early allocation/read failures.

Test signals: Manual run reports compressed/uncompressed sizes, timings, and `compare ok`; no CTest automation is defined in this directory.
