# sources/compression/xz/src/liblzma/lz/lz_decoder.c Research

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/lz/lz_decoder.c -->
## sources/compression/xz/src/liblzma/lz/lz_decoder.c

### Purpose
`lz_decoder.c` implements the generic LZ output window used by LZ77-derived decoders such as LZMA and LZMA2. It owns dictionary allocation/wrapping and bridges filter-specific LZ decoders to the liblzma filter-chain API.

### Important APIs, Types, And Functions
Private `lzma_coder` stores `lzma_dict`, a filter-specific `lzma_lz_decoder`, optional next coder, completion flags, and a temporary buffer for non-last filters. `lz_decoder_reset()`, `decode_buffer()`, `lz_decode()`, `lz_decoder_end()`, `lzma_lz_decoder_init()`, and `lzma_lz_decoder_memusage()` are the key functions.

### Control Flow
`decode_buffer()` wraps the dictionary when it reaches the allocated end by copying the last repeat window to the front. It sets a write limit based on caller output space, calls the filter-specific decoder, copies newly decoded bytes to caller output, and honors `dict.need_reset`. If this LZ decoder is not the last chain element, `lz_decode()` fills a temporary buffer from the next filter, decodes from that buffer into the dictionary, and enforces that this decoder and the next decoder finish consistently. Initialization creates or reuses the base coder, asks the filter-specific initializer for dictionary options, rounds small dictionaries up to 4096 bytes, aligns size, allocates repeat/extra space, seeds preset dictionaries, and initializes the next filter.

### State, Persistence, And Dependencies
State is the dictionary buffer, `full` count, wrap flag, reset flag, filter-specific coder, and optional temporary upstream data. There is no persistence beyond streaming history. Dependencies include `lz_decoder.h`, allocator helpers, and filter-specific LZ decoder factories.

### Integration Points
LZMA and LZMA2 decoder modules call `lzma_lz_decoder_init()` with their own `lz_init` callback. Inline dictionary helpers from `lz_decoder.h` are used by those filter-specific decoders.

### Risks
Dictionary sizing is security-critical: distance validation relies on `full` and repeat-window layout. The small-dictionary round-up may accept some corrupt files that use distances between the true dictionary size and 4096. Non-last-filter mode has strict finish ordering and can report `LZMA_DATA_ERROR` if extra bytes remain.

### Test Signals
Tests should exercise tiny dictionaries, preset dictionaries, dictionary wrap, repeated matches crossing wrap boundaries, reset requests, chained filter mode, truncated streams, and memory-usage overflow boundaries.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/lz/lz_decoder.c -->
