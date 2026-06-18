<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/debug/sync_flush.c -->
# sources/compression/xz/debug/sync_flush.c

Purpose: debug encoder that emits a stream using repeated `LZMA_SYNC_FLUSH` operations, with commented code for testing filter updates.

Important APIs/types/functions: same structure as `full_flush.c`, but uses explicit `lzma_options_lzma`, optional `lzma_options_delta`, `lzma_stream_encoder`, `lzma_code`, and possible `lzma_filters_update`.

Control flow: configure LZMA2 with a 64 KiB dictionary and HC3 match finder, initialize stream encoder, perform zero/small-size sync flushes, then finish. `encode` handles chunked reads, output draining, and return-code checks.

State and persistence: persistent global `lzma_stream` across flush calls; stdout contains the encoded stream.

Dependencies and integration: targets liblzma streaming behavior around sync flush and filter boundary handling.

Risks: optional input `fopen` is unchecked, write errors are ignored, and short reads are not treated as errors. The unused delta options exist only to silence warning-sensitive builds.

Test signals: generated output should decompress successfully; modifying the commented filter-update block can probe dynamic filter update regressions.
<!-- END_FILE_RESEARCH: sources/compression/xz/debug/sync_flush.c -->
