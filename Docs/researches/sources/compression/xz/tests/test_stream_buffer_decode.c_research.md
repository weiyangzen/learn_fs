# sources/compression/xz/tests/test_stream_buffer_decode.c

Purpose: tests `lzma_stream_buffer_decode()` success and failure-position behavior.

Important constants and state: `UNCOMP_SIZE` is 13; `xz_data` and `xz_data_size` are loaded from `files/good-1-check-crc32.xz`.

Control flow: `test_success()` decodes the full fixture with `LZMA_CONCATENATED`, expecting `LZMA_OK`, full input consumption, and output size 13. `test_data_error()` truncates input by one byte and expects `LZMA_DATA_ERROR` with both `in_pos` and `out_pos` reset to zero. `test_buf_error()` provides one byte too little output capacity and expects `LZMA_BUF_ERROR`, also with positions reset.

State and persistence: in-memory fixture and stack output buffers only.

Dependencies and integration: depends on decoder support and stream-buffer API. Complements streaming decoder tests by exercising the convenience API's all-or-nothing position semantics.

Risks: comments note the truncated-input case failed in xz 5.8.3 and older, making this an explicit regression guard. Position reset behavior is important for callers that retry or report offsets.

Test signals: clear return-code and position assertions for success, corrupt data, and insufficient output.
