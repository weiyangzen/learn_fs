# sources/compression/xz/src/liblzma/lzma/lzma2_encoder.c Research

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/lzma/lzma2_encoder.c -->
## sources/compression/xz/src/liblzma/lzma/lzma2_encoder.c

### Purpose
`lzma2_encoder.c` implements LZMA2 chunk emission on top of the generic LZ encoder and LZMA encoder core. It decides when to emit compressed chunks, uncompressed chunks, reset markers, properties, and the end marker.

### Important APIs, Types, And Functions
Private `lzma_lzma2_coder` tracks sequence, embedded LZMA encoder, current options, reset/property flags, chunk sizes, copy position, and a header/compressed-data buffer. Key functions are `lzma2_header_lzma()`, `lzma2_header_uncompressed()`, `lzma2_encode()`, `lzma2_encoder_options_update()`, `lzma2_encoder_init()`, `lzma_lzma2_encoder_init()`, `lzma_lzma2_encoder_memusage()`, `lzma_lzma2_props_encode()`, and `lzma_lzma2_block_size()`.

### Control Flow
`lzma2_encode()` starts in `SEQ_INIT`; if no data remains and flushing/finishing is requested, it writes the LZMA2 end marker on finish and returns stream end. Otherwise it resets LZMA state if needed, encodes up to LZMA2 chunk limits into an internal buffer, and checks whether compressed size is smaller than uncompressed size. Incompressible chunks are emitted as uncompressed chunks by copying bytes back from the match-finder history with `mf_read()` and marking that the next chunk needs an LZMA state reset. Compressed chunks get a control byte encoding dictionary/state/property reset class, uncompressed and compressed sizes, and optional LZMA properties, then are copied to output.

### State, Persistence, And Dependencies
State is per-stream chunk sequence, current LZMA properties, reset flags, and internal chunk buffer. It depends on the generic LZ encoder, LZMA encoder core, `fastpos.h`, and LZMA2 constants from the header. Persistent output is emitted through caller buffers.

### Integration Points
`lzma_lzma2_encoder_init()` registers with `lzma_lz_encoder_init()`. Option updates can change only `lc/lp/pb` at chunk boundaries and force new properties plus state reset. Property encoding maps dictionary size to the `.xz` one-byte LZMA2 property. Block size estimation is used by multithreaded encoder defaults.

### Risks
The code must keep enough match-finder history to output incompressible chunks, so initialization adjusts `before_size`. Chunk-size arithmetic and read-ahead handling are subtle. Option updates reject incomplete chunks; callers must flush first. Dictionary-size property rounding must match decoder expectations.

### Test Signals
Tests should cover compressible and incompressible chunks, exact 64 KiB/2 MiB chunk boundaries, finish end marker, sync/full flush behavior through the generic LZ layer, option updates at legal/illegal points, property round trips, and block-size estimation for dictionary boundaries.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/lzma/lzma2_encoder.c -->
