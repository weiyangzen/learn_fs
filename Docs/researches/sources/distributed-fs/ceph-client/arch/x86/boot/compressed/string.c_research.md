# sources/distributed-fs/ceph-client/arch/x86/boot/compressed/string.c

Purpose: supplies decompressor-safe memory primitives before the normal kernel runtime exists and avoids compiler-generated builtins that might use unsupported instructions.

Important APIs and state: defines `memset()`, `memmove()`, and `memcpy()`, with KASAN aliases for `__memset`, `__memmove`, and `__memcpy`. It includes the generic boot `string.c` for non-memory string/parse helpers and keeps a private optimized `____memcpy()` using `rep movsl` on 32-bit or `rep movsq` on 64-bit.

Control flow: `memcpy()` detects a destination-after-source overlap and delegates to backward-copying `memmove()` after warning. Non-overlap uses the optimized copy path. `memset()` is a simple byte loop to remain predictable in the decompressor environment.

Dependencies and integration: used throughout compressed boot, decompression, SEV/TDX setup, EFI parsing, and page-table setup. It depends on `error.h` for `warn()`.

Risks and test signals: a compiler optimization that bypasses these functions could introduce FPU/SIMD or runtime dependencies too early. The overlap check changes unsafe `memcpy()` into `memmove()`, which avoids corruption but signals a bug. Test by decompressor builds across GCC/Clang, KASAN compressed builds, overlapping-copy cases, and early boot under minimal CPU feature conditions.
