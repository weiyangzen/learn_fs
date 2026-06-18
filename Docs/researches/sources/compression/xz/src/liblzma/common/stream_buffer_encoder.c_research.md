<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/stream_buffer_encoder.c -->
# sources/compression/xz/src/liblzma/common/stream_buffer_encoder.c

Purpose: Implements single-call `.xz` Stream encoding and a bound calculation for caller output buffers.

Important APIs/macros: `lzma_stream_buffer_bound()` returns worst-case output size for one Block plus Stream Header, Index, and Footer. `lzma_stream_buffer_encode()` writes a Stream Header, optional Block, Index, and Stream Footer.

Control flow: The bound uses `lzma_block_buffer_bound()` plus `HEADERS_BOUND`. Encoding validates filters/check/buffers, rejects unsupported checks, reserves Footer space, writes Stream Header, encodes one Block only if input is nonempty, builds an `lzma_index`, appends the Block record when present, encodes the Index, sets `stream_flags.backward_size`, writes Footer, and only then updates `*out_pos_ptr`.

State/dependencies: Uses a local `lzma_stream_flags`, `lzma_block`, and temporary `lzma_index`. Depends on Block buffer encoding, Index APIs, and Stream Header/Footer encoding.

Risks/tests: Empty input produces an empty Index with no Block. Tests should cover empty streams, unsupported checks, small output buffers at each phase, size-bound overflow, exact bound, and failure before `*out_pos_ptr` is committed.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/stream_buffer_encoder.c -->
