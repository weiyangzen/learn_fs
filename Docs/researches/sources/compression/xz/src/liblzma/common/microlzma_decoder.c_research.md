<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/microlzma_decoder.c -->
# sources/compression/xz/src/liblzma/common/microlzma_decoder.c

Purpose: Decodes the MicroLZMA format, a compact LZMA1-based stream format with a negated properties byte and externally supplied compressed and uncompressed sizes.

Important APIs/types: `lzma_microlzma_coder` stores nested LZMA decoder, remaining compressed size, remaining/untrusted uncompressed size, dictionary size, exact-size mode, and whether properties have been decoded. Public `lzma_microlzma_decoder()` wraps internal init.

Control flow: Before initializing LZMA, the decoder limits input by remaining `comp_size` and, when uncompressed size is not exact, limits output by remaining `uncomp_size`. It reads one properties byte, negates it, decodes lc/lp/pb, configures LZMA1EXT with exact size when known, initializes the nested decoder, and feeds a dummy leading zero byte expected by the LZMA decoder. Subsequent calls forward to LZMA and update remaining sizes. Exact-size mode requires stream end exactly when compressed bytes are exhausted; inexact mode forbids LZMA EOPM and returns `LZMA_STREAM_END` when the requested output amount has been produced.

State/dependencies: Depends on LZMA decoder internals and LZ decoder size-extension helpers. State persists nested decoder progress and size counters across calls.

Risks/tests: Exact and inexact modes have different end conditions. Tests should cover missing properties byte, invalid properties, compressed-size leftovers, too-small compressed size, inexact output limit, unexpected EOPM, oversized `uncomp_size`, and dummy-byte initialization.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/microlzma_decoder.c -->
