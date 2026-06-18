# sources/compression/lz4/contrib/gen_manual/Makefile

## Purpose
This Makefile builds the `gen_manual` C++ utility and uses it to regenerate the HTML manuals for `lz4.h` and `lz4frame.h`. It is a maintenance/build helper rather than part of the runtime compressor.

## Important APIs, Targets, and Variables
The main targets are `default`, `gen_manual`, `manuals`, `$(LZ4MANUAL)`, `$(LZ4FMANUAL)`, and `clean`. `LZ4API`, `LZ4FAPI`, `LZ4MANUAL`, and `LZ4FMANUAL` point at the headers and generated documentation under `../../lib` and `../../doc`. The version is extracted from `lz4.h` with three `sed` commands and joined into `LZ4VER`. `CXXFLAGS`, `CPPFLAGS`, `LDFLAGS`, `MOREFLAGS`, and Windows `EXT` drive compiler behavior.

## Control Flow
`default` builds the `gen_manual` executable from `gen_manual.cpp`. The HTML manual targets depend on both the generator and the corresponding API header, then call `./gen_manual $(LZ4VER) <header> <output>`. The `manuals` phony target builds both HTML outputs. `clean` removes the generator binary.

## State and Persistence
The only persistent build outputs are `gen_manual` or `gen_manual.exe` and the two generated HTML files in `../../doc`. Version state is read dynamically from `lz4.h`; no state file is maintained.

## Dependencies and Integration Points
The Makefile depends on a working C++ compiler, POSIX-style `sed`, `rm`, and the local `gen_manual.cpp`. It integrates with the library headers and documentation tree, and its generated output format is dictated by `gen_manual.cpp`.

## Risks
The version extraction assumes the `#define LZ4_VERSION_*` lines retain the expected whitespace and numeric shape. The Makefile invokes `./gen_manual`, so cross-builds or out-of-tree builds need compatible execution on the build host. Generated manuals can become stale if header dependencies or version parsing fail silently.

## Test Signals
Useful checks are `make -C contrib/gen_manual manuals`, a clean rebuild after `make clean`, and reviewing the generated HTML for expected sections from `lz4.h` and `lz4frame.h`.
