# sources/compression/xz/src/liblzma/api/lzma/index.h

Purpose: declares APIs for building, querying, iterating, concatenating, encoding, decoding, and using `.xz` Index information, including random-access file metadata.

Important APIs/types/functions: opaque `lzma_index`; `lzma_index_iter` with stream and block metadata; `lzma_index_iter_mode`; check mask macros; memory usage, init/end, append, stream flags/padding, checks, stream/block counts, size queries, iterator init/rewind/next/locate, `lzma_index_cat`, `lzma_index_dup`, streamed and buffer Index encoder/decoder, and `lzma_file_info_decoder`.

Control flow: encoders append Block records after coding Blocks, optionally set Stream Flags and padding, then encode the Index. Decoders parse Index into an `lzma_index`, query sizes and checks, and can locate target uncompressed offsets to seek to Blocks. `lzma_file_info_decoder` may return `LZMA_SEEK_NEEDED` through `lzma_code()` to inspect file tails and headers efficiently.

State and persistence: `lzma_index` owns heap structures sized by number of Streams/Blocks. Iterators borrow the index and remain valid across append, but source iterators become invalid when their index is consumed by `lzma_index_cat()`.

Dependencies/integration: relies on VLI, Stream Flags, Block sizes, allocator hooks, and check IDs. Random-access readers, list/test modes, and stream validators depend on this metadata.

Risks: Index memory can be much larger in RAM than on disk, so memlimits are critical. Size growth can return `LZMA_DATA_ERROR`. Thread safety permits concurrent readers only when no thread mutates the same index. File-info decoding requires correct seek handling by applications.

Test signals: `tests/test_index.c`, `tests/test_index_hash.c`, random-access/list tests, and `.xz` decode validation paths.
