# sources/compression/xz/src/liblzma/lz/Makefile.inc Research

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/lz/Makefile.inc -->
## sources/compression/xz/src/liblzma/lz/Makefile.inc

### Purpose
`lz/Makefile.inc` lists generic LZ encoder/decoder source files for Automake builds.

### Important APIs, Types, And Functions
Under `COND_ENCODER_LZ`, it includes `lz_encoder.c`, `lz_encoder.h`, hash helpers, hash table, and match-finder implementation. Under `COND_DECODER_LZ`, it includes `lz_decoder.c` and `lz_decoder.h`.

### Control Flow
Build-time conditionals select encoder and decoder support independently. There is no runtime behavior.

### State, Persistence, And Dependencies
The file affects build metadata only and depends on configure-generated conditionals.

### Integration Points
LZMA1/LZMA2 filters depend on these generic LZ layers, so their build options must imply the corresponding LZ encoder/decoder condition.

### Risks
Misconfigured conditionals can omit shared LZ files while LZMA filters still reference them. The generated hash table is included only through the encoder source dependency list.

### Test Signals
Configure/build matrix tests for encoder-only, decoder-only, and full builds validate this file.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/lz/Makefile.inc -->
