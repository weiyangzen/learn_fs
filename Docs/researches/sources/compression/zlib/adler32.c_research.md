# sources/compression/zlib/adler32.c

Purpose: implements Adler-32 checksum calculation and checksum combination for zlib streams.

Important APIs/functions: exports `adler32_z`, `adler32`, `adler32_combine`, and `adler32_combine64`; internal `adler32_combine_`. Uses constants `BASE` 65521 and `NMAX` 5552 plus unrolled macros `DO1` through `DO16` and modulo macros that can avoid division under `NO_DIVIDE`.

Control flow: `adler32_z` splits the incoming checksum into low/high sums, fast-paths one-byte inputs, returns initial checksum `1` for `Z_NULL`, handles short buffers, processes long buffers in `NMAX` chunks with unrolled 16-byte loops, then recombines sums. Combine functions validate `len2`, reduce it modulo `BASE`, and apply the Adler concatenation formula.

State and persistence: stateless; all work is local to each call.

Dependencies and integration: includes `zutil.h` for zlib types/macros. Called by public zlib checksum APIs and used by compression/decompression consumers needing stream integrity.

Risks: performance and correctness depend on avoiding 32-bit overflow via `NMAX` and modulo scheduling. `buf == Z_NULL` is checked after the `len == 1` fast path, so callers must not pass null with length one. Negative combine lengths return `0xffffffffUL` as a debugging clue, not a normal error code.

Test signals: covered indirectly by zlib example tests, checksum tests elsewhere, and broad CI standard/platform builds.
