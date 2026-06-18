# sources/compression/xz/src/liblzma/check/crc64_fast.c

Purpose: fast CRC64 implementation for the ECMA-182 polynomial, with generic slice-by-four code and optional architecture-optimized dispatch.

Important APIs/types/functions: includes generated `crc64_table_be.h` or `crc64_table_le.h`, defines `lzma_crc64_generic()` unless assembly supplies it, optional `crc64_arch_optimized()` via `crc_x86_clmul.h`, resolver type `crc64_func_type`, `crc64_resolve()`, constructor/lazy dispatch helpers, and exported `lzma_crc64()`.

Control flow: the generic routine complements the incoming CRC, byte-swaps on big-endian, aligns the input to four bytes, processes aligned 32-bit words through four CRC64 table slices, handles trailing bytes, reverses the big-endian swap, and complements the result. If both generic and CLMUL paths are built, a constructor or first-call dispatcher selects the optimized function when CPUID reports CLMUL/SSSE3/SSE4.1 support.

State and persistence: optional process-global function pointer `crc64_func` caches runtime dispatch. Generated tables are immutable program data.

Dependencies/integration: depends on `check.h`, `crc_common.h`, endian read helpers, generated tables, optional i386 assembly, and optional PCLMUL header. Used by check calculation for XZ Blocks when CRC64 is selected.

Risks: runtime dispatch must not call CLMUL on unsupported CPUs. Big-endian byte handling and aligned reads are correctness-sensitive. If unsupported-check policy changes, callers must still verify `lzma_check_is_supported()` before relying on CRC64.

Test signals: CRC64 known vectors, block encode/decode with CRC64 checks, CPU-dispatch tests on CLMUL and non-CLMUL hosts, and cross-endian testing.
