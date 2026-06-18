# sources/compression/xz/src/liblzma/common/stream_encoder.c Research

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/stream_encoder.c -->
## sources/compression/xz/src/liblzma/common/stream_encoder.c

### Purpose
`stream_encoder.c` implements the single-threaded `.xz` Stream encoder. It wraps Block encoding, Index encoding, Stream Header/Footer generation, filter-chain updates, and Index record accounting behind the public `lzma_stream_encoder()` entry point.

### Important APIs, Types, And Functions
The private `lzma_stream_coder` holds the stream sequence, a Block encoder, copied filters, Block options, Index encoder, `lzma_index`, and a small header/footer buffer. `block_encoder_init()` validates Block options and initializes `lzma_block_encoder_init()`. `stream_encode()` is the main `lzma_next_coder.code` callback. `stream_encoder_update()` supports `lzma_filters_update()`. `stream_encoder_init()` prepares a fresh stream, and `lzma_stream_encoder()` exposes supported actions.

### Control Flow
Encoding proceeds through `SEQ_STREAM_HEADER`, `SEQ_BLOCK_INIT`, `SEQ_BLOCK_HEADER`, `SEQ_BLOCK_ENCODE`, `SEQ_INDEX_ENCODE`, and `SEQ_STREAM_FOOTER`. The header and Block header are copied from the internal buffer. Nonempty input starts a Block; empty input with `LZMA_FINISH` skips directly to Index encoding, allowing empty Streams. Block actions map full flush/barrier/finish to `LZMA_FINISH` for the Block layer, except `LZMA_SYNC_FLUSH` is passed through. When a Block ends, its unpadded and uncompressed sizes are appended to the Index. Finishing initializes the Index encoder, writes the Index, computes `backward_size`, emits the Footer, and returns `LZMA_STREAM_END`.

### State, Persistence, And Dependencies
State is entirely in-memory in `lzma_stream_coder`; the persistent output is the byte stream written through caller buffers. The Index persists Block size records until the Footer can be generated. The file depends on Block/Header/Index helpers, stream flag encoding, filter-copy/free helpers, allocator discipline, and `lzma_next_coder` callbacks.

### Integration Points
This is used by the high-level liblzma stream API and by applications that need `.xz` output with a single encoding thread. It supports `LZMA_RUN`, `LZMA_SYNC_FLUSH`, `LZMA_FULL_FLUSH`, `LZMA_FULL_BARRIER`, and `LZMA_FINISH`, and integrates with runtime filter updates via `next->update`.

### Risks
Filter updates are valid only before the Index/Footer phase; mid-Block updates depend on downstream filter support. `block_encoder_is_initialized` is subtle: it avoids reinitializing a Block after validation/update, but must be cleared after use. Incorrect Index accounting would corrupt Footer backward size. Header/footer buffer reuse relies on every sequence setting `buffer_size` and `buffer_pos` correctly.

### Test Signals
Useful tests are round-trip `.xz` Streams with empty input, multiple full flushes, sync flush, filter update before and during Blocks, unsupported Check IDs, and output buffers that force partial header/footer copies.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/stream_encoder.c -->
