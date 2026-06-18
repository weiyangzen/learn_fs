<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/lzip_decoder.c -->
# sources/compression/xz/src/liblzma/common/lzip_decoder.c

Purpose: Implements `.lz`/lzip member decoding on top of the LZMA1 decoder, including lzip header parsing, CRC32/data/member-size footer validation, concatenated member handling, and memory-limit reporting.

Important APIs/types: `lzma_lzip_coder` stores sequence, version, CRC32, uncompressed and member sizes, memory limits, flags, header/footer position, footer buffer, LZMA options, and nested LZMA decoder. Public `lzma_lzip_decoder()` wraps internal `lzma_lzip_decoder_init()`.

Control flow: `SEQ_ID_STRING` matches `LZIP`. `SEQ_VERSION` accepts versions 0 and 1 and optionally reports `LZMA_GET_CHECK`. `SEQ_DICT_SIZE` decodes the lzip dictionary-size byte into LZMA options with fixed lc/lp/pb. `SEQ_CODER_INIT` checks memory and initializes LZMA1. `SEQ_LZMA_STREAM` forwards data to the nested decoder while updating CRC and observed sizes. `SEQ_MEMBER_FOOTER` validates CRC32, data size, and version-1 member size, then either ends or loops for concatenated members.

State and persistence: Per-member CRC and sizes reset after magic bytes. Concatenated mode uses `first_member` to report non-lzip trailing data as `LZMA_STREAM_END` only after at least one valid member.

Dependencies/integration: Depends on `lzip_decoder.h`, LZMA decoder internals, CRC helpers, and supported liblzma flags (`TELL_ANY_CHECK`, `IGNORE_CHECK`, `CONCATENATED`). It is a format adapter separate from `.xz` stream parsing.

Risks/tests: Trailing-data semantics can discard 1-3 matching magic-prefix bytes after the first member because the API cannot rewind across calls. Tests should cover v0/v1 footers, invalid magic, unsupported version, dictionary byte bounds, CRC and size mismatch, concatenated members, trailing non-lzip data, `IGNORE_CHECK`, and memlimit retry.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/lzip_decoder.c -->
