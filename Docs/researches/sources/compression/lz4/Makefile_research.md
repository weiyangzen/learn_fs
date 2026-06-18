<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/Makefile -->
# sources/compression/lz4/Makefile

## Purpose
Top-level GNU Make orchestration for building, testing, installing, and validating lz4 libraries, CLI, examples, manuals, and auxiliary build systems.

## Important APIs, Types, And Functions
- Main targets include `default`, `all`, `allmost`, `lib`, `lz4`, `examples`, `manuals`, `build_tests`, `clean`, `install`, `uninstall`, `test`, and `check`.
- Integration targets include `cmakebuild`, `mesonbuild`, and `test-install`.
- Quality/portability targets include `usan`, `ubsan`, `usan32`, `staticAnalyze`, `cppcheck`, `platformTest`, `versionsTest`, `test-freestanding`, C/C++ compatibility, and `c_standards`.
- Propagates standard variables such as `CC`, `CFLAGS`, `CPPFLAGS`, `LDFLAGS`, and `LDLIBS` into subdirectories.

## Control Flow
Targets mostly delegate to subdirectory Makefiles in `lib`, `programs`, `examples`, `tests`, and build-system directories. Clean/test targets reset or rebuild relevant subtrees. Sanitizer and standard targets override compiler flags before invoking clean/build/test flows.

## State And Persistence
Produces libraries, binaries, manuals, examples, test artifacts, install trees, and temporary build directories. `clean` removes generated artifacts across subprojects.

## Dependencies And Integration Points
Integrates all major lz4 build surfaces and is the common entry point for CI workflows. Depends on GNU make, C/C++ compilers, shell tools, CMake/Meson for specific targets, and static-analysis tools when requested.

## Risks And Edge Cases
Variable propagation is critical; broken forwarding can make CI misleading. Some targets require optional tools or 32-bit libraries. Install/uninstall targets can affect system paths if `PREFIX`/`DESTDIR` are not controlled.

## Test Signals
Passing `make`, `make test`, sanitizer targets, build-system targets, and `test_stdvars` indicate core build, tests, and variable propagation are healthy.
<!-- END_FILE_RESEARCH: sources/compression/lz4/Makefile -->
