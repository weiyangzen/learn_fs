<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/memcmplen.h -->
# sources/compression/xz/src/liblzma/common/memcmplen.h

Purpose: Provides `lzma_memcmplen()`, an inline optimized routine for finding the length of the common prefix between two buffers, starting from a known matching length.

Important APIs/macros: `lzma_memcmplen(buf1, buf2, len, limit)` returns a value in `[len, limit]`. `LZMA_MEMCMPLEN_EXTRA` is defined per implementation path to document how many bytes may be read beyond `limit`.

Control flow: The implementation chooses at compile time between 64-bit unaligned word comparison, SSE2 movemask comparison, generic 32-bit little-endian/big-endian unaligned comparison, and a portable byte loop. Fast paths use ctz/clz or bit scans to locate the first differing byte and clamp to `limit`.

State and dependencies: Header-only, no persistent state. Depends on `common.h`, endian read helpers, compiler intrinsics, `TUKLIB_FAST_UNALIGNED_ACCESS`, and optional `<immintrin.h>`/`<intrin.h>`.

Risks/tests: Callers must provide initialized extra bytes according to `LZMA_MEMCMPLEN_EXTRA`, otherwise fast paths may trip memory sanitizers or fault on invalid padding. Tests should cover equal buffers, first-byte mismatch, mismatches around word boundaries, big/little endian paths where possible, exact limit, nonzero initial `len`, and ASan/Valgrind with required extra padding.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/memcmplen.h -->
