<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/doc/examples/04_compress_easy_mt.c -->
# sources/compression/xz/doc/examples/04_compress_easy_mt.c

Purpose: documented sample for multi-threaded `.xz` compression using preset-based LZMA2.

Important APIs/types/functions: `lzma_mt`, `lzma_cputhreads`, `lzma_stream_encoder_mt`, `preset`, `threads`, `block_size`, `timeout`, `check`, and the shared streaming `compress` loop.

Control flow: configure threaded encoder defaults, detect CPU threads, fall back to one thread when unknown, cap at eight threads, initialize the MT encoder, then stream stdin to stdout.

State and persistence: liblzma owns worker/block state behind `lzma_stream`; no persistent files beyond stdout.

Dependencies and integration: depends on liblzma built with threading and the CPU thread detection path.

Risks: one-thread MT mode is not equivalent to normal single-threaded mode and can use more memory. The arbitrary thread cap may be wrong for some RAM/preset combinations.

Test signals: compile against threaded liblzma, compress/decompress large files, and test builds without thread support for expected initialization failure.
<!-- END_FILE_RESEARCH: sources/compression/xz/doc/examples/04_compress_easy_mt.c -->
