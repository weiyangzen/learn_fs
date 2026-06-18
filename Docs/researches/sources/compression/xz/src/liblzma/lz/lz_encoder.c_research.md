# sources/compression/xz/src/liblzma/lz/lz_encoder.c Research

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/lz/lz_encoder.c -->
## sources/compression/xz/src/liblzma/lz/lz_encoder.c

### Purpose
`lz_encoder.c` implements the generic LZ input window and match-finder allocation layer used by LZMA-family encoders. It fills the sliding window, manages match-finder buffers, and delegates symbol encoding to a filter-specific LZ encoder.

### Important APIs, Types, And Functions
Private `lzma_coder` contains a filter-specific `lzma_lz_encoder`, `lzma_mf`, and optional next coder. Key functions are `move_window()`, `fill_window()`, `lz_encode()`, `lz_encoder_prepare()`, `lz_encoder_init()`, `lzma_lz_encoder_memusage()`, `lz_encoder_end()`, `lz_encoder_update()`, `lz_encoder_set_out_limit()`, `lzma_lz_encoder_init()`, and `lzma_mf_is_supported()`.

### Control Flow
`lz_encode()` repeatedly fills the match-finder window when `read_pos` reaches `read_limit`, then calls the filter-specific encoder. `fill_window()` either copies caller input directly or pulls data through the next filter, zeroes extra comparison bytes, adjusts `read_limit`, and handles flush completion by allowing the encoder to consume all remaining bytes. `lz_encoder_prepare()` validates dictionary and match-finder settings, computes keep-before/after and reserve sizes, selects HC/BT match-finder callbacks, calculates hash/son table sizes, and sets depth defaults. `lz_encoder_init()` allocates buffers/tables, resets positions, initializes hash tables, and seeds preset dictionaries through the skip function.

### State, Persistence, And Dependencies
State lives in `lzma_mf`: sliding input buffer, read/write positions, read-ahead, pending bytes after sync flush, hash/son tables, cyclic position, match limits, action, and depth. Dependencies include `lz_encoder_hash.h`, optional generated hash table, `memcmplen.h`, CRC initialization in small builds, and filter-specific encoder factories.

### Integration Points
LZMA1/LZMA2 encoders call `lzma_lz_encoder_init()` with their own initializer. `lz_encoder_update()` enables filter option updates where the LZ-specific encoder supports them. `set_out_limit` is exposed for block-buffer size limiting when no additional filters are chained.

### Risks
Memory sizing has several integer-overflow and 32-bit constraints; dictionary size is limited to 1.5 GiB. Preset dictionary setup runs through the match finder, so callback selection must already be valid. Sync flush restart relies on `pending` and `read_pos` rewind. Incorrect reserve sizing can cause excessive memmove or insufficient lookahead.

### Test Signals
Tests should cover all enabled match finders, dictionary-size boundaries, preset dictionaries, sync flush with continued input, chained filters, output limits, memory-usage overflow, and fuzzing with tiny input/output buffers.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/lz/lz_encoder.c -->
