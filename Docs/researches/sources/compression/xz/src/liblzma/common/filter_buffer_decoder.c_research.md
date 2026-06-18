<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/filter_buffer_decoder.c -->
# sources/compression/xz/src/liblzma/common/filter_buffer_decoder.c

Purpose: Provides `lzma_raw_buffer_decode()`, the single-call buffer-to-buffer API for raw filter chains. It wraps the streaming raw decoder and normalizes completion and partial-buffer failures for callers that want all work done in one call.

Important APIs: The only public function validates input/output pointers and positions, initializes a temporary `lzma_next_coder` with `lzma_raw_decoder_init()`, runs it with `LZMA_FINISH`, and always releases it with `lzma_next_end()`.

Control flow and state: The function snapshots `in_pos` and `out_pos` before decoding. `LZMA_STREAM_END` is translated to `LZMA_OK`. If the decoder returns `LZMA_OK`, the wrapper distinguishes truncated input from too-small output; in the ambiguous case where both input and output end together, it probes one extra output byte through the same decoder.

Dependencies and integration: Depends on `filter_decoder.h` and the raw coder chain builder in `filter_common.c`. It is used by higher-level APIs and tests that need raw decoding without owning a persistent `lzma_stream`.

Risks and tests: Error rollback is the key contract: on any non-success result, both positions must be restored. Tests should include invalid pointers, unsupported filter chains, truncated input, undersized output, exact output size, and the ambiguous all-input/all-output case.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/filter_buffer_decoder.c -->
