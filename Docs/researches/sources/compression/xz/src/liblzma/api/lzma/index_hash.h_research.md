# sources/compression/xz/src/liblzma/api/lzma/index_hash.h

Purpose: declares constant-memory Index validation using a hash/check state instead of materializing a full `lzma_index`.

Important APIs/types/functions: opaque `lzma_index_hash`; exports `lzma_index_hash_init`, `lzma_index_hash_end`, `lzma_index_hash_append`, `lzma_index_hash_decode`, and `lzma_index_hash_size`.

Control flow: callers append expected Block records as Blocks are decoded, then feed the encoded Index bytes to `lzma_index_hash_decode()` until it returns `LZMA_STREAM_END` and confirms the Index matches the appended records.

State and persistence: `lzma_index_hash` stores accumulated record/check state and decoder progress. It can be reinitialized in place by passing a non-NULL pointer to `lzma_index_hash_init()`.

Dependencies/integration: implemented in common Index hash code using the best enabled check from internal `check.h` (`SHA256`, `CRC64`, or `CRC32`). Stream decoders use this to validate Index data without retaining all records.

Risks: once decoding has started, appending more records is a programming error. The hash validates consistency but does not provide random-access metadata like a full `lzma_index`.

Test signals: `tests/test_index_hash.c` checks append/decode/CRC behavior and mismatch detection.
