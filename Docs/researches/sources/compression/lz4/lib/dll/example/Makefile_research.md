# sources/compression/lz4/lib/dll/example/Makefile

## Purpose
This Makefile builds a DLL-linking example on Windows-like environments, producing one executable linked against a static import library and one linked against the DLL.

## Important Targets and Variables
`LZ4DIR`, `LIBDIR`, and `DLLDIR` point at headers, static library, and DLL locations relative to the example. `CFLAGS`, `CPPFLAGS`, and `FLAGS` define warning and include settings. Targets are `default`, `all`, `fullbench-lib`, `fullbench-dll`, and `clean`.

## Control Flow
`default` invokes `all`. `fullbench-lib` compiles `fullbench.c` and `xxhash.c` and links with `../static/liblz4_static.lib`. `fullbench-dll` compiles the same sources with `-DLZ4_DLL_IMPORT=1` and links with `../dll/liblz4.dll`. `clean` removes both executables.

## State and Persistence
The persistent outputs are `fullbench-lib(.exe)` and `fullbench-dll(.exe)`. No state files are created.

## Dependencies and Integration Points
It depends on prepared `../include`, `../static`, and `../dll` directories, plus `fullbench.c` and `xxhash.c` in the example directory. `LZ4_DLL_IMPORT=1` integrates with `lz4.h`'s Windows import declaration behavior.

## Risks
The `clean` command has a trailing backslash before the echo line, which can fold commands in unintended ways. Linking directly to `liblz4.dll` may depend on toolchain conventions; many Windows builds link against an import library instead. Relative directory assumptions are strict.

## Test Signals
Build both targets and run them with the DLL present on the runtime search path. Confirm the DLL build imports LZ4 symbols and the static build runs without the DLL dependency.
