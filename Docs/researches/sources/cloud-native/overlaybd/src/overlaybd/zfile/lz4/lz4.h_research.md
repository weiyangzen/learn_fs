## sources/cloud-native/overlaybd/src/overlaybd/zfile/lz4/lz4.h

Purpose: public C header for the vendored LZ4 block API. It exports version constants, symbol-visibility macros, compression bounds, one-shot compression/decompression, advanced stateful APIs, streaming APIs, static-linking-only internals, and deprecated compatibility entry points.

Important APIs/types: version macros report 1.8.3. `LZ4_MAX_INPUT_SIZE` and `LZ4_COMPRESSBOUND` define caller allocation constraints. `LZ4_stream_t` and `LZ4_streamDecode_t` are exposed as unions for static allocation but documented as ABI-unstable. Internal structs hold hash tables, offsets, dictionary pointers, and decode prefix/external dictionary metadata.

Control flow contract: callers allocate destination buffers, pass exact compressed sizes to safe decompression, pass known original output size to fast decompression, and manage one block at a time. Streaming compression requires previous 64KB source data to remain stable unless `LZ4_saveDict` is used. Streaming decompression requires previously decoded data to remain available or supplied through `LZ4_setStreamDecode`.

State/persistence: the header defines in-memory stream state only. It deliberately avoids container metadata; any file format must store compressed block sizes, original sizes, checksums, and framing externally.

Dependencies/integration: included by `lz4.c`, `lz4/test.c`, and compressor adapters. It uses `stddef.h` and optionally `stdint.h`, with `extern "C"` guards for C++ consumers.

Risks: static-linking-only definitions are not stable API/ABI; deprecated functions remain available but should not guide new code. `LZ4_decompress_fast` is explicitly unsafe for untrusted input because compressed size is not bounded. Test signals come from the basic sample and from zfile exercising LZ4 through OverlayBD's persisted block format.
