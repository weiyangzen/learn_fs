<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/invalidDictionaries.c -->
## sources/compression/zstd/tests/invalidDictionaries.c

Purpose: Standalone C test ensuring malformed dictionary bytes are rejected by both compression and decompression dictionary constructors.

Important APIs and types: Defines `dictionary { const char *data; size_t size; }`, a static `invalidRepCode` byte array, and a sentinel-terminated `dictionaries` array. Uses `ZSTD_createCDict`, `ZSTD_freeCDict`, `ZSTD_createDDict`, and `ZSTD_freeDDict`.

Control flow: `main` iterates over dictionaries until `data == NULL`. For each invalid dictionary, it attempts to create a `ZSTD_CDict` at compression level `1`; if creation succeeds, it frees it and returns `1`. It then attempts to create a `ZSTD_DDict`; if creation succeeds, it frees it and returns `2`. Success is returning `0` after all invalid dictionaries are rejected.

State and persistence: No persistent state. Allocations are internal to libzstd dictionary creation and freed on unexpected success.

Dependencies and integration points: Includes public `zstd.h` and links against libzstd. The invalid fixture targets dictionary parsing validation around repeat codes.

Risks: If libzstd starts accepting this byte sequence as a raw content dictionary instead of a zstd dictionary, the test will fail. Return codes distinguish compressor dictionary acceptance from decompressor dictionary acceptance.

Test signals: Process exit `0` means both constructors rejected the invalid dictionary; exit `1` or `2` identifies the side that incorrectly accepted it.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/invalidDictionaries.c -->
