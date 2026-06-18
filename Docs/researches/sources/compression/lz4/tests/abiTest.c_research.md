# sources/compression/lz4/tests/abiTest.c

Purpose: ABI compatibility smoke test that links against liblz4 and performs a streaming round trip over an input file.

Important APIs/functions: global `LZ4_stream_t` and `LZ4_streamDecode_t`; `roundTripTest()` uses `LZ4_compress_fast_continue()`, `LZ4_setStreamDecode()`, and `LZ4_decompress_safe_continue()`. Helpers load files and compare buffers.

Control flow: `main()` prints header and linked library versions, requires a filename, loads it, compresses/decompresses, validates size and bytes, and reports success or exits non-zero.

State and persistence: uses global stream structs to exercise ABI-visible layout; reads input only and writes no output artifact.

Dependencies/integration: includes `xxhash.h`, `lz4.h`, `lz4frame.h`; Makefile links target with `-llz4` and `abiTests` uses Python orchestration.

Risks: whole-file memory load; size helper conflates some errors with zero size; directory handling has platform-sensitive `fclose` behavior.

Test signals: successful run prints linked versions and no problem detected.
