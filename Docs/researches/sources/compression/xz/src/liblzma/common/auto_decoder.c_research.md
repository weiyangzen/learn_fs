# sources/compression/xz/src/liblzma/common/auto_decoder.c

Purpose: automatic container decoder that detects XZ Stream, LZMA_Alone, and optionally lzip formats from the first input bytes, then delegates to the matching decoder.

Important APIs/types/functions: internal `lzma_auto_coder`, `auto_decode()`, `auto_decoder_end()`, `auto_decoder_get_check()`, `auto_decoder_memconfig()`, `auto_decoder_init()`, and public `lzma_auto_decoder()`.

Control flow: `auto_decode()` buffers/probes initial bytes. It first checks XZ magic and initializes `lzma_stream_decoder_init()` when matched. If lzip support is compiled in, it checks lzip magic and initializes `lzma_lzip_decoder_init()`. Otherwise it tries the Alone decoder in picky mode when enough bytes are available or input end requires a decision. After initialization, all calls forward to the selected decoder.

State and persistence: per-stream state tracks nested coder, memlimit, flags, and probe state. Memory configuration and check queries proxy to the selected decoder when available.

Dependencies/integration: includes `stream_decoder.h`, `alone_decoder.h`, and optionally `lzip_decoder.h`. Public `lzma_auto_decoder()` validates supported decoder flags and enables `LZMA_RUN`/`LZMA_FINISH`.

Risks: format sniffing must balance false positives against compatibility. Picky Alone mode intentionally rejects many unlikely files. Lzip support is compile-time optional. Memory limit changes before and after nested decoder selection must remain coherent.

Test signals: auto-decoder tests should cover XZ, `.lzma`, lzip enabled/disabled, empty/truncated inputs, unsupported flags, memlimit errors, and check reporting after XZ header decode.
