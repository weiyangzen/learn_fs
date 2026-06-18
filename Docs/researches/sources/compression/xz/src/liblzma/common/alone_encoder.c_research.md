# sources/compression/xz/src/liblzma/common/alone_encoder.c

Purpose: streaming encoder for legacy LZMA_Alone `.lzma` output, writing the 13-byte Alone header and then delegating payload compression to an LZMA1 encoder.

Important APIs/types/functions: `ALONE_HEADER_SIZE`, internal `lzma_alone_coder`, state machine `SEQ_HEADER`/`SEQ_CODE`, `alone_encode()`, `alone_encoder_end()`, `alone_encoder_init()`, and public `lzma_alone_encoder()`.

Control flow: initialization validates options, rejects unsupported preset dictionaries, allocates/reuses coder state, encodes LZMA properties and dictionary size into the header, writes unknown uncompressed size as all `0xFF`, initializes an LZMA1 filter chain, and sets stream actions. `alone_encode()` drains header bytes to output with `lzma_bufcpy()` before forwarding to the nested encoder.

State and persistence: per-stream state includes nested coder, current sequence, header position, and header buffer. It writes no external state beyond encoded output and updates stream counters through `lzma_code()`.

Dependencies/integration: includes `common.h` and `lzma_encoder.h`; public API is declared in `api/lzma/container.h` and used by the `xz` tool for `--format=lzma`.

Risks: LZMA_Alone cannot store all modern options or known size semantics used by XZ Blocks. Header generation must match legacy decoder expectations. The public wrapper supports `LZMA_RUN` and `LZMA_FINISH`, not full XZ stream actions.

Test signals: round trips with `lzma_alone_decoder()`, command-line `.lzma` encode/decode tests, and invalid-option tests for unsupported LZMA options.
