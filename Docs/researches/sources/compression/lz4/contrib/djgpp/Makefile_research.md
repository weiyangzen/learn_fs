<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/contrib/djgpp/Makefile -->
# sources/compression/lz4/contrib/djgpp/Makefile

## Purpose
Builds and installs lz4 for the DJGPP DOS toolchain contribution.

## Important APIs, Types, And Functions
- Extracts library version from `lib/lz4.h` into `LIBVER` variables.
- Pattern rules build `.o` from `.c` and `.exe` from objects and the static library.
- Targets include `all`, `clean`, `install`, `uninstall`, `showconfig`, `gstat`, and `gpush`.
- Tracks installed files through `.footprint`.

## Control Flow
`all` builds the static library and executables with DJGPP-compatible compiler/linker settings. `install` copies includes, library, binaries, docs, and license files into prefix paths and records footprints. `uninstall` removes files from `.footprint`.

## State And Persistence
Produces DJGPP object files, libraries, executables, install trees, and `.footprint`. Clean removes local build outputs.

## Dependencies And Integration Points
Depends on DJGPP/GCC tooling, sed, install/rm utilities, and relative paths to lz4 `lib` and `programs` sources.

## Risks And Edge Cases
Version parsing relies on exact `#define` patterns. Install/uninstall can remove wrong files if `.footprint` is stale or prefix changes. DOS/DJGPP constraints differ from normal Unix builds.

## Test Signals
Signals include successful DJGPP compilation, correct `showconfig`, installed files matching `.footprint`, and clean uninstall.
<!-- END_FILE_RESEARCH: sources/compression/lz4/contrib/djgpp/Makefile -->
