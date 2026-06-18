# sources/compression/xz/src/liblzma/common/block_buffer_encoder.h

Purpose: internal header exposing the 64-bit Block buffer bound helper for encoder code that needs bounds beyond public `size_t` limits.

Important APIs/types/functions: declares `uint64_t lzma_block_buffer_bound64(uint64_t uncompressed_size)`.

Control flow: no implementation flow. The declared helper returns the worst-case encoded Block size for an uncompressed input size or zero on overflow/invalid size.

State and persistence: no state.

Dependencies/integration: includes `common.h`. Implemented by `block_buffer_encoder.c`; public API `lzma_block_buffer_bound(size_t)` wraps it with 32-bit `SIZE_MAX` protection.

Risks: callers relying on the 64-bit bound must still handle zero as failure and must not truncate to `size_t` on 32-bit systems. Changes to LZMA2 uncompressed chunk overhead or Block header limits must update the implementation.

Test signals: compile coverage in main encoder builds and bound comparisons around `SIZE_MAX`, `COMPRESSED_SIZE_MAX`, zero-length input, and large chunk-count boundaries.
