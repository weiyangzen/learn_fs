<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/stream_buffer_decoder.c -->
# sources/compression/xz/src/liblzma/common/stream_buffer_decoder.c

Purpose: Provides `lzma_stream_buffer_decode()`, a single-call `.xz` Stream decoder wrapper.

Important API: Validates input/output pointers and positions, rejects `LZMA_TELL_ANY_CHECK` for buffer mode, initializes `lzma_stream_decoder_init()`, runs it with `LZMA_FINISH`, translates `LZMA_STREAM_END` to `LZMA_OK`, reports required memory on memlimit failure, rolls back positions on errors, and frees the decoder.

Control flow/state: Uses local `lzma_next_coder stream_decoder`. On `LZMA_OK` from the streaming decoder, it distinguishes truncated input from too-small output: if all input was consumed, the stream is considered truncated; otherwise output space was too small.

Dependencies/integration: Depends on `stream_decoder.h` and the normal `.xz` stream decoder state machine.

Risks/tests: Position rollback and `memlimit` output are important. Tests should cover exact decode, truncated stream, undersized output, unsupported flags, memlimit too low then retry, and zero-length input/output combinations.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/stream_buffer_decoder.c -->
