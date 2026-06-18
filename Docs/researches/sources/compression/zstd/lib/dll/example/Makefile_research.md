# sources/compression/zstd/lib/dll/example/Makefile

## Purpose
This makefile builds a small Windows-oriented DLL/static-library comparison example for zstd's `fullbench.c` and `datagen.c`. It demonstrates linking the same benchmark source against either `libzstd_static.lib` or `libzstd.dll`.

## Important Targets And Variables
- `ZSTDDIR`, `LIBDIR`, and `DLLDIR` point to sibling include, static library, and DLL output directories.
- `CFLAGS`, `CPPFLAGS`, `LDFLAGS`, `MOREFLAGS`, and `FLAGS` assemble compiler and linker options, including warning flags and `-DXXH_NAMESPACE=ZSTD_`.
- `EXT` becomes `.exe` when `$(OS)` matches `Windows%`, otherwise empty.
- `all` builds `fullbench-dll` and `fullbench-lib`.
- `fullbench-lib` links `fullbench.c datagen.c` against `../static/libzstd_static.lib`.
- `fullbench-dll` defines `ZSTD_DLL_IMPORT=1` and links against `../dll/libzstd.dll`.
- `clean` removes both generated binaries.

## Control Flow
The default target delegates to `all`, which invokes the two concrete build targets. Each target compiles the same sources with shared flags but different link inputs and, for the DLL target, a DLL import macro. Platform-specific executable suffix selection occurs before target evaluation.

## State And Persistence
The makefile writes build artifacts `fullbench-dll$(EXT)` and `fullbench-lib$(EXT)` in the example directory. `clean` removes those artifacts. It does not generate dependency files or persist configuration.

## Dependencies And Integration Points
It expects `fullbench.c` and `datagen.c` to be present in the current directory and zstd include/static/DLL artifacts to exist at the configured relative paths. It integrates with standard `make`, `CC`, `RM`, and platform `OS` variables. `ZSTD_DLL_IMPORT=1` must match zstd's DLL import/export declarations.

## Risks And Edge Cases
- The static and DLL library paths use Windows-style `.lib`/`.dll` names even when `EXT` is empty, so non-Windows use may require adjusted artifacts.
- The `clean` recipe contains a trailing backslash before the `@echo` line, which can join commands unexpectedly depending on make/shell parsing.
- `VOID := /dev/null` is defined but unused.
- The makefile assumes relative directory layout after zstd has already built the static and DLL libraries.

## Test Signals
Build tests should run `make` after producing the expected zstd DLL/static artifacts, verify both binaries link, and run `make clean` to ensure generated files are removed without shell syntax errors. Windows/MSYS and non-Windows dry runs are useful because `EXT` and library naming are platform-sensitive.
