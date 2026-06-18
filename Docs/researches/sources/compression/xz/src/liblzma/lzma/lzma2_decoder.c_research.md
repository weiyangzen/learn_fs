# sources/compression/xz/src/liblzma/lzma/lzma2_decoder.c Research

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/lzma/lzma2_decoder.c -->
## sources/compression/xz/src/liblzma/lzma/lzma2_decoder.c

### Purpose
`lzma2_decoder.c` implements the LZMA2 chunk decoder on top of the generic LZ dictionary decoder and the LZMA decoder core.

### Important APIs, Types, And Functions
Private `lzma_lzma2_coder` tracks chunk parse sequence, embedded `lzma_lz_decoder`, uncompressed/compressed sizes, property/reset requirements, and current LZMA options. Key functions are `lzma2_decode()`, `lzma2_decoder_end()`, `lzma2_decoder_init()`, `lzma_lzma2_decoder_init()`, `lzma_lzma2_decoder_memusage()`, and `lzma_lzma2_props_decode()`.

### Control Flow
The decoder reads a control byte, handles `0x00` end marker, enforces dictionary reset before first chunk, distinguishes LZMA chunks from uncompressed chunks, parses size fields, optionally decodes new properties, resets the LZMA state when required, and either calls the LZMA decoder or copies raw bytes into the dictionary. LZMA chunks validate that the inner decoder consumes exactly the declared compressed size and that uncompressed size constraints are enforced by the inner decoder. Dictionary reset requests are signaled to the generic LZ layer with `dict_reset()`.

### State, Persistence, And Dependencies
State includes sequence, size counters, current properties, and reset flags (`need_properties`, `need_dictionary_reset`). Persistent stream history is in the generic `lzma_dict`. Dependencies include `lz_decoder.h`, `lzma_decoder.h`, and LZMA property helpers.

### Integration Points
Raw/Block decoder filter tables initialize this through `lzma_lz_decoder_init()`. LZMA2 is asserted to be the last filter in a chain. Property decoding is used when parsing filter flags.

### Risks
The control-byte state machine is format-critical. Accepting LZMA chunks before properties or before dictionary reset would permit invalid streams. Size counters are `size_t`, so initialization validates through surrounding code for platform limits. Preset dictionaries bypass the initial dictionary-reset requirement.

### Test Signals
Tests should cover every legal control-byte class, invalid control bytes, missing properties, dictionary reset rules, uncompressed chunks, truncated size fields, compressed-size mismatch, end marker handling, and property values 0 through 40.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/lzma/lzma2_decoder.c -->
