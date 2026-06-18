# sources/compression/zstd/examples/dictionary_decompression.c

Purpose: demonstrates in-memory decompression of one or more zstd frames using a preloaded decompression dictionary.

Important functions/APIs: `createDict_orDie`, `decompress`, `main`, `ZSTD_createDDict`, `ZSTD_getFrameContentSize`, `ZSTD_getDictID_fromDDict`, `ZSTD_getDictID_fromFrame`, `ZSTD_createDCtx`, `ZSTD_decompress_usingDDict`, `ZSTD_freeDCtx`, and `ZSTD_freeDDict`.

Control flow: the last CLI argument is the dictionary; earlier arguments are compressed files. For each file, it loads the compressed buffer, requires a known frame content size, allocates the result buffer, compares the frame dictionary ID to the loaded DDict ID, decompresses, verifies returned size, prints a summary, and frees buffers.

State and persistence: one `ZSTD_DDict` persists across all file decodes. Decompressed output is kept in memory only and not written to disk.

Dependencies/integration: relies on frames that include content size and dictionary ID, which the paired dictionary compression example writes by default. Uses `common.h` fatal checks.

Risks: frames without content size are rejected even though streaming decompression could handle them. Raw dictionaries may have ID zero, which can make ID checks less discriminating. Output is not saved, so this is a validation example rather than a decompression utility.

Test signals: paired dictionary round trip from the Makefile, wrong dictionary ID rejection, unknown content-size rejection, non-zstd input rejection, and multi-file reuse of the same DDict.
