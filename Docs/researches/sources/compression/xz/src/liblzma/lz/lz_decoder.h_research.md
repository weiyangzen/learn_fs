# sources/compression/xz/src/liblzma/lz/lz_decoder.h Research

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/lz/lz_decoder.h -->
## sources/compression/xz/src/liblzma/lz/lz_decoder.h

### Purpose
`lz_decoder.h` defines the generic LZ decoder dictionary API and optimized inline helpers used by LZMA/LZMA2 decoders.

### Important APIs, Types, And Functions
It defines decoder configuration macros, `LZ_DICT_EXTRA`, `LZ_DICT_REPEAT_MAX`, `LZ_DICT_INIT_POS`, `lzma_dict`, `lzma_lz_options`, `lzma_lz_decoder`, `LZMA_LZ_DECODER_INIT`, `lzma_lz_decoder_init()`, `lzma_lz_decoder_memusage()`, and inline helpers such as `dict_get()`, `dict_repeat()`, `dict_put()`, `dict_write()`, and `dict_reset()`.

### Control Flow
The main inline flow is dictionary access. `dict_repeat()` validates available output space, computes the back-reference source, copies byte-by-byte for overlaps, otherwise uses `memcpy()` or SSE2 32-byte chunks depending on configuration, updates `pos` and `full`, and reports whether bytes remain. `dict_write()` copies raw bytes into the dictionary and decrements a remaining counter.

### State, Persistence, And Dependencies
`lzma_dict` holds buffer position, fill level, limit, allocation size, wrap state, and reset requests. Compile-time CPU/endian features choose the copy strategy. Dependencies include `common.h` and optionally `<immintrin.h>`.

### Integration Points
Filter-specific decoders call these helpers to output literals, repeated matches, raw chunks, and reset requests into the generic dictionary window.

### Risks
The SSE2 path may intentionally copy extra bytes, so allocation must include `LZ_DICT_EXTRA`. Distance validity must be checked by callers before `dict_repeat()`. Changes to `LZ_DICT_REPEAT_MAX` must stay aligned with LZMA maximum match length and extra-copy size.

### Test Signals
Sanitizer tests around `dict_repeat()` overlap/non-overlap paths, SSE2/non-SSE builds, dictionary wrap, invalid distances, and raw chunk writes are strong coverage.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/lz/lz_decoder.h -->
