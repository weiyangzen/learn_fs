# sources/compression/xz/tests/test_bcj_exact_size.c

Purpose: regression tests for BCJ decoding when the exact output size is known or zero, historically failing in older xz releases.

Important functions: `test_exact_size()` compresses a small buffer with PowerPC BCJ plus LZMA2, then decodes with exactly one byte of input/output exposed at a time. `test_empty_block()` decodes a fixture containing an empty PowerPC BCJ+LZMA2 block with zero output capacity.

Control flow: tests skip when encoder/decoder or PowerPC BCJ support is disabled. `test_exact_size()` uses `lzma_stream_buffer_encode()` to build input, initializes `lzma_stream_decoder()`, loops until `LZMA_STREAM_END`, and asserts total input/output sizes. `test_empty_block()` uses `lzma_stream_buffer_decode()` with output limit zero and expects success with zero output.

State and persistence: uses stack buffers and one fixture loaded from `files/good-1-empty-bcj-lzma2.xz`. No files are written.

Dependencies and integration: depends on `tests.h`, liblzma stream buffer APIs, PowerPC BCJ filter support, LZMA2 preset setup, and test fixture loading.

Risks: exact-size bugs often appear at filter boundaries, especially BCJ alignment and empty output. Feature skips can leave this regression untested in minimal builds.

Test signals: successful assertions prove no extra output space is needed at stream end and empty BCJ blocks decode cleanly.
