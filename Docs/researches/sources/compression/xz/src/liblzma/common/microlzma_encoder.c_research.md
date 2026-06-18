<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/microlzma_encoder.c -->
# sources/compression/xz/src/liblzma/common/microlzma_encoder.c

Purpose: Encodes input into MicroLZMA format using LZMA1 and overwriting the first output byte with the bitwise-negated LZMA properties byte.

Important APIs/types: `lzma_microlzma_coder` stores nested LZMA encoder and encoded properties byte. Public `lzma_microlzma_encoder()` supports only `LZMA_FINISH`.

Control flow: Init encodes lc/lp/pb properties from `lzma_options_lzma`, initializes an LZMA1 encoder, and stores the properties. Encoding asks the nested encoder's `set_out_limit()` how many uncompressed bytes fit in the available compressed output, runs the encoder to `LZMA_STREAM_END`, writes `~props` at the first byte of this MicroLZMA chunk, and rewinds `*in_pos` to the number of bytes actually encoded according to `uncomp_size`.

State/dependencies: Depends on LZMA encoder internals and the nested coder's `set_out_limit` capability. It borrows caller options during init and persists only nested encoder state plus properties.

Risks/tests: The nested LZMA encoder may read ahead beyond bytes that fit; correcting `*in_pos` is a critical contract. Tests should cover invalid options, too-small output for `set_out_limit`, multiple calls, exact output boundaries, and property-byte negation.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/microlzma_encoder.c -->
