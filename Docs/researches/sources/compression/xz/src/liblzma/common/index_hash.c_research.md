<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/index_hash.c -->
# sources/compression/xz/src/liblzma/common/index_hash.c

Purpose: Validates an `.xz` Index against Block sizes observed while decoding, without building a full `lzma_index`.

Important APIs/types: `lzma_index_hash_info` tracks padded Block size sum, uncompressed sum, record count, index-list byte size, and an integrity check state over size pairs. `struct lzma_index_hash_s` holds separate `blocks` and `records` info plus decode sequence, remaining count, current VLI fields, VLI position, and CRC32. APIs include `lzma_index_hash_init/end/size/append/decode()`.

Control flow: Callers append each decoded Block with `lzma_index_hash_append()`, which updates sums and hashes and validates global limits. `lzma_index_hash_decode()` then parses Index Indicator, count, records, padding, and CRC. It checks record count equality, ensures decoded record sums never exceed observed Block sums, compares final sums and best-check hashes, then verifies CRC32.

State and persistence: The object persists between Block decoding and Index decoding. Once `lzma_index_hash_decode()` starts, its sequence leaves `SEQ_BLOCK`, and further append calls are programming errors.

Dependencies/integration: Depends on `index.h`, `check.h`, VLI decode, CRC32, and `LZMA_CHECK_BEST`. Used by single-threaded and multithreaded Stream decoders to verify Index integrity with O(1) memory.

Risks/tests: Hashing raw `lzma_vli` arrays means producer and verifier run in the same library ABI, not an interchange format. Tests should cover count mismatch, size mismatch, padding mismatch, CRC failure, zero Blocks, append overflows, invalid unpadded sizes, and incremental Index input boundaries.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/index_hash.c -->
