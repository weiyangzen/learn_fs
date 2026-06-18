# sources/compression/lz4/programs/Makefile

## Purpose
This Makefile builds, installs, and cleans the LZ4 command-line programs: `lz4`, `lz4c`, `unlz4`, `lz4cat`, no-multithread variants, and selected platform-specific binaries.

## Important APIs, Types, And Functions
It derives library version macros from `../lib/lz4.h`, gathers library and program C sources, sets warning and optimization flags, includes shared make definitions from `../build/make`, detects pthread support, and defines targets for release builds, 32-bit builds, symlink aliases, manpage generation, installation, and uninstall.

## Control Flow
The default target is `lz4-release`, which disables debug flags and defines `NDEBUG`. `all` builds the main aliases. The `c_program` macro from included makefiles creates link rules. Thread support is detected by compiling a small `pthread.h` test; if available, `lz4` receives `-DLZ4IO_MULTITHREAD` and `-pthread`.

## State, Persistence, And Dependencies
Build state includes object files, executables, symlinks or copies, generated Windows resources, and generated manpage `lz4.1`. Install/uninstall writes under `DESTDIR`, `bindir`, and `man1dir`. It depends on sed, make helpers, compiler tooling, optional pthreads, optional ronn, and platform variables.

## Integration Points
This is the build surface for the user-facing CLI and benchmark code. It links lib sources directly by default and has `lz4-wlib` for dynamic-library linkage that exposes unstable symbols.

## Risks
Thread detection writes `have_pthread.c` in the working directory and may race under concurrent builds. Platform branches depend on included makefiles. `lz4-wlib` warns that it needs an extended dynamic library exposing unstable symbols.

## Test Signals
Run `make`, `make all`, `make lz4-nomt`, `make clean`, `make install DESTDIR=...`, `make uninstall DESTDIR=...`, and platform builds with and without pthread support.
