<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/longmatch.c -->
## sources/compression/zstd/tests/longmatch.c

Purpose: Stress test for long-match compression paths that historically risked crashes when compressing more than 8 GiB with repeated distant matches.

Important APIs and functions: `compress()` wraps `ZSTD_compressStream` and `ZSTD_flushStream` on a `ZSTD_CStream`. `main()` creates a compression context, sets parameters with `ZSTD_CCtx_setParameter`, fills a window-sized buffer with fixed matching prefixes/suffixes and random middle bytes, and repeatedly compresses variable slices.

Control flow: It configures `windowLog=18`, chain/hash/search/minmatch/targetLength, and `ZSTD_fast`. It creates a buffer containing a repeated marker at both ends to encourage long matches. It compresses one full window, then loops until `compressed` reaches `1 << 33`, choosing random block lengths from the current position and wrapping when the position reaches the window size.

State and persistence: Uses heap source and destination buffers and a single streaming compression context. No decompression or file persistence is performed.

Dependencies and integration points: Includes `mem.h` for `U64`, static zstd parameters, and libc `rand`. Exercises streaming compression state across many calls.

Risks: The test name `compressed` actually tracks source bytes consumed, not compressed byte count. Destination output buffer reuse assumes each flush drains fully into a buffer sized for one window. No output correctness is checked beyond absence of zstd errors or crashes.

Test signals: Prints setup/progress messages and exits `0` after "Compression completed successfully"; exits `1` for compression/flush error and `2` for parameter setup error.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/longmatch.c -->
