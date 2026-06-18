# sources/compression/zstd/zlibWrapper/Makefile

## Purpose
This Makefile builds and tests the zstd zlib-wrapper examples. It can compile the examples in normal zlib-compatible mode or with `ZWRAP_USE_ZSTD=1`, producing paired binaries that exercise zlib API calls routed through zstd-backed compression.

## Important APIs, Types, and Functions
The important targets are `all`, `release`, `test`, `test-valgrind`, `clean`, `example`, `example_zstd`, `fitblk`, `fitblk_zstd`, `minigzip`, `minigzip_zstd`, `zwrapbench`, `zstd_zlibwrapper.o`, `zstdTurnedOn_zlibwrapper.o`, and zstd library build targets. Variables include `ZLIB_LIBRARY`, `ZLIB_PATH`, `ZSTDLIBDIR`, `ZSTDLIBRARY`, `ZLIBWRAPPER_PATH`, `GZFILES`, `EXAMPLE_PATH`, `PROGRAMS_PATH`, `TEST_FILE`, `CPPFLAGS`, `STDFLAGS`, `DEBUGFLAGS`, `CFLAGS`, `LDLIBS`, and Windows `EXT`.

## Control Flow, State, and Persistence
The default path is `release`, which clears strict debug flags and builds `all`. Strict builds otherwise use C89/pedantic compatibility flags plus warning flags and include paths for zlib, zstd lib/common, programs, and wrapper sources. The zstd-enabled object is built from `zstd_zlibwrapper.c` with extra `-DZWRAP_USE_ZSTD=1`, letting the same example object link against either wrapper mode. `test` runs both normal and zstd variants, compresses/decompresses example binaries with `minigzip`, and runs `zwrapbench` on a format document and source directories. `test-valgrind` repeats core examples under valgrind. `clean` removes wrapper/example object files and generated binaries/data.

## Dependencies and Integration Points
It depends on a zlib library selected by `ZLIB_LIBRARY`/`ZLIB_PATH`, the local zstd static library under `../lib/libzstd.a`, wrapper sources in `zlibWrapper`, example sources under `examples`, gzip wrapper objects (`gzclose.o`, `gzlib.o`, `gzread.o`, `gzwrite.o`), and program utilities (`util.o`, `timefn.o`, `datagen.o`) for `zwrapbench`. It delegates building zstd libraries to `make -C ../lib`.

## Risks and Test Signals
Risks include linking against mismatched zlib headers/libraries, stale generated objects when switching `MOREFLAGS`, platform differences in executable suffixes, and tests that modify/delete local example binaries through `minigzip`. Useful signals are successful `make test`, successful `make test-valgrind`, correct production of both normal and `_zstd` variants, and clean rebuilds after `make clean`.
