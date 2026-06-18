# sources/compression/zlib/zutil.c

Purpose: zlib target-dependent utility implementation. It provides exported version/compile-flag queries, public error-string conversion, internal debug failure handling, fallback byte memory routines, and default allocation/free hooks used by deflate/inflate state setup.

Important APIs and control flow: `zlibVersion()` returns the compiled `ZLIB_VERSION`. `zlibCompileFlags()` encodes sizes of `uInt`, `uLong`, pointers, and `z_off_t`, plus feature macros such as `ZLIB_DEBUG`, `ZLIB_WINAPI`, `BUILDFIXED`, `DYNAMIC_CRC_TABLE`, gzip disables, workaround/fastest flags, and snprintf availability into a bitfield. `zError()` maps status codes through `ERR_MSG`. When `HAVE_MEMCPY` is absent, `zmemcpy`, `zmemcmp`, and `zmemzero` provide simple byte loops. `zcalloc`/`zcfree` have special 16-bit Turbo C and Microsoft C branches, otherwise use `malloc` for large `uInt` platforms and `calloc` for 16-bit-size arithmetic compatibility.

State and dependencies: normal builds are stateless except for `z_errmsg`. Debug builds add global `z_verbose`. Turbo C 16-bit allocation keeps a static pointer normalization table, so that path is not thread-safe. Dependencies are `zutil.h`, optionally `gzguts.h`, libc allocation/string facilities, and legacy compiler APIs.

Integration points, risks, and test signals: this file underpins zlib public diagnostics and all default internal allocation. Risks are mostly portability: integer multiplication in default `malloc(items * size)`, 16-bit table exhaustion, and compile flag drift if feature macros change. Test signals are indirect through zlib API tests, allocation failure paths, and build matrix coverage across configured macro combinations.
