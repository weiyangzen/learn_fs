# sources/compression/xz/src/liblzma/common/Makefile.inc

Purpose: Automake source manifest for `src/liblzma/common`, controlling which common liblzma implementation files are compiled under feature conditions.

Important APIs/types/functions: no C APIs; it appends paths to `liblzma_la_SOURCES`. Conditional groups include always-common sources, `COND_THREADS`, `COND_MAIN_ENCODER`, `COND_MAIN_DECODER`, `COND_MICROLZMA`, and `COND_LZIP_DECODER`.

Control flow: build-time conditionals add encoder files, decoder files, threading helpers, MicroLZMA support, and lzip decoder support. Common base files such as `common.c`, `common.h`, `block_util.c`, `easy_preset.c`, index/stream flag helpers, and VLI size code are always included.

State and persistence: build-system state only. It persists as source-control configuration and influences resulting library symbols and objects.

Dependencies/integration: consumed by liblzma's Automake build. It must stay aligned with Meson/CMake or other build descriptions if present, public symbol maps, and conditional headers.

Risks: omitting a source under the wrong condition causes link failures or missing APIs; adding decoder/encoder files outside their feature gates can bloat restricted builds. Header/source pairs must remain grouped correctly so internal declarations are available.

Test signals: configure/build matrix for encoder-only, decoder-only, threads on/off, microlzma on/off, and lzip on/off. Link tests should verify public symbols in `liblzma_*`.map are backed by compiled objects.
