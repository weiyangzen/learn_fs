# sources/compression/xz/src/liblzma/lz/lz_encoder_hash.h Research

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/lz/lz_encoder_hash.h -->
## sources/compression/xz/src/liblzma/lz/lz_encoder_hash.h

### Purpose
`lz_encoder_hash.h` provides hash-table selection and hash calculation macros for LZ match finders.

### Important APIs, Types, And Functions
It selects `hash_table` from `lzma_crc32_table[0]` or hidden `lzma_lz_hash_table`, defines hash table sizes/masks and fixed hash offsets, and defines macros such as `hash_2_calc()`, `hash_3_calc()`, `hash_4_calc()`, and multi-thread-oriented `mt_hash_*` variants.

### Control Flow
The macros compute small rolling hashes from the current input pointer `cur` and `mf->hash_mask`, producing hash indices and shorter-prefix hash values used by HC/BT match finders.

### State, Persistence, And Dependencies
There is no mutable state. The chosen table depends on build flags (`HAVE_SMALL`, `CRC32_GENERIC`, `WORDS_BIGENDIAN`, and `TUKLIB_FAST_UNALIGNED_ACCESS`). It may require `lz_encoder_hash_table.h` to provide a little-endian CRC table.

### Integration Points
`lz_encoder.c` includes this header and conditionally includes the generated table. `lz_encoder_mf.c` uses the macros in every match-finder implementation.

### Risks
Endianness determinism is critical: compressed output must not depend on host byte order. The unused `hash_5_calc()` macro appears malformed but is not compiled unless used; future use would need review.

### Test Signals
Cross-endian or simulated-endian builds, small/non-small builds, and comparing compressed output hashes across platforms validate this layer.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/lz/lz_encoder_hash.h -->
