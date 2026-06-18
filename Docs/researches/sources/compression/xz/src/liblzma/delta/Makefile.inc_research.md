# sources/compression/xz/src/liblzma/delta/Makefile.inc Research

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/delta/Makefile.inc -->
## sources/compression/xz/src/liblzma/delta/Makefile.inc

### Purpose
`delta/Makefile.inc` lists liblzma Delta filter sources for Automake builds, separating common, encoder, and decoder files by feature condition.

### Important APIs, Types, And Functions
It appends common Delta files to `liblzma_la_SOURCES` unconditionally, then conditionally appends `delta_encoder.c/.h` under `COND_ENCODER_DELTA` and `delta_decoder.c/.h` under `COND_DECODER_DELTA`.

### Control Flow
There is no runtime flow. Build-time conditionals determine whether encoder and/or decoder code is compiled.

### State, Persistence, And Dependencies
The file affects build metadata only. It depends on configure-generated Automake conditionals.

### Integration Points
The top-level liblzma build includes this file to assemble the library source list according to enabled filters.

### Risks
Common files are always included, so disabling both encoder and decoder still compiles shared Delta validation/state code. Missing condition alignment with headers would cause unresolved symbols in filter registration code.

### Test Signals
Build matrix tests should cover encoder-only, decoder-only, both, and neither where supported by configure options.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/delta/Makefile.inc -->
