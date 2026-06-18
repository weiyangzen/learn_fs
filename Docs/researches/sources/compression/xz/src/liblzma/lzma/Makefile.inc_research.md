# sources/compression/xz/src/liblzma/lzma/Makefile.inc Research

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/lzma/Makefile.inc -->
## sources/compression/xz/src/liblzma/lzma/Makefile.inc

### Purpose
`lzma/Makefile.inc` lists LZMA-family sources for Automake builds, including shared preset/common files and conditional LZMA1/LZMA2 encoder/decoder sources.

### Important APIs, Types, And Functions
It always includes `lzma_common.h` and `lzma_encoder_presets.c`, distributes `fastpos_tablegen.c`, conditionally includes LZMA1 encoder/decoder files, includes `fastpos_table.c` for non-small LZMA1 encoder builds, and conditionally includes LZMA2 encoder/decoder files.

### Control Flow
Build-time conditionals choose which codec directions and table implementations are compiled.

### State, Persistence, And Dependencies
The file affects build metadata only. It depends on configure-generated `COND_ENCODER_LZMA1`, `COND_DECODER_LZMA1`, `COND_ENCODER_LZMA2`, `COND_DECODER_LZMA2`, and `COND_SMALL`.

### Integration Points
Top-level liblzma build includes this file to assemble LZMA source sets. The LZMA2 files in this subset depend on LZ encoder/decoder layers from `lz/`.

### Risks
The shared `lzma_encoder_presets.c` is included unconditionally despite being encoder-oriented, so build condition assumptions should be verified. Table generation and `COND_SMALL` must stay aligned with `fastpos.h`.

### Test Signals
Build matrix coverage across small/non-small and LZMA1/LZMA2 encoder/decoder toggles validates this file.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/lzma/Makefile.inc -->
