# sources/compression/xz/src/liblzma/common/alone_decoder.c

Purpose: streaming decoder for legacy `.lzma`/LZMA_Alone files, parsing the 13-byte Alone header and then delegating payload decoding to the LZMA1EXT decoder.

Important APIs/types/functions: internal `lzma_alone_coder`, state machine `SEQ_PROPERTIES`, `SEQ_DICTIONARY_SIZE`, `SEQ_UNCOMPRESSED_SIZE`, `SEQ_CODER_INIT`, `SEQ_CODE`; functions `alone_decode()`, `alone_decoder_end()`, `alone_decoder_memconfig()`, `lzma_alone_decoder_init()`, and public `lzma_alone_decoder()`.

Control flow: `alone_decode()` reads property byte, decodes dictionary size little-endian, optionally rejects unlikely dictionary sizes in picky mode, reads uncompressed size, rejects huge known sizes in picky mode, configures `LZMA_FILTER_LZMA1EXT` with end-marker allowance and size, checks memory usage against the memlimit, initializes the raw LZMA decoder, then forwards subsequent calls to it.

State and persistence: per-stream coder stores nested decoder, header parse position, decoded options, memlimit/memusage, uncompressed size, and picky flag. No persistent external state.

Dependencies/integration: includes `alone_decoder.h`, `lzma_decoder.h`, and `lz_decoder.h`. Used directly by `lzma_alone_decoder()` and by `auto_decoder.c` for format probing.

Risks: format probing uses picky heuristics to avoid false positives; too strict rejects unusual but decodable files, too loose misclassifies random input. Memory limit checks happen after header parse. Unknown sizes use `UINT64_MAX` conventions through LZMA1EXT.

Test signals: `.lzma` decode tests via `xz`, `xzdec`, and auto decoder; edge tests for invalid properties, dictionary sizes, known/unknown sizes, memlimit errors, and truncated headers.
