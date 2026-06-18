# sources/compression/zlib/contrib/pascal/zlibd32.mak

## Purpose
`zlibd32.mak` is a legacy Borland C++ makefile for building zlib as `zlib.lib` plus `example.exe` and `minigzip.exe` under Win32 for Delphi/C++ Builder use.

## Important APIs, Types, and Functions
The makefile defines tool variables `CC=bcc32`, `LD=bcc32`, `AR=tlib`, calling convention flags `-DZEXPORT=__fastcall` and `-DZEXPORTVA=__cdecl`, object lists for zlib sources, explicit object dependencies, targets `all`, `test`, executable links, and `clean`.

## Control Flow
The default target builds the static library and sample executables. Pattern rule `.c.obj` compiles C sources with Borland options. The library target deletes any existing `zlib.lib`, then invokes `tlib` twice with split object lists to fit old command-line limits. `test` runs `example` and pipes text through `minigzip` and decompression. `clean` deletes generated object, executable, library, debug, backup, and sample gzip files.

## State and Persistence
Build outputs are `.obj`, `.lib`, `.exe`, `.tds`, backup, and `foo.gz` files in the working directory. No runtime state is managed by the makefile.

## Dependencies and Integration Points
Targets the Borland/Delphi Win32 toolchain and zlib source layout. It integrates zlib's C ABI with Delphi calling conventions through preprocessor definitions.

## Risks and Edge Cases
The file is toolchain-specific and likely stale for modern compilers. The command-line splitting reflects historical DOS limits. Cleanup uses Windows `del` syntax and assumes local build output. Source dependency lists must be maintained manually when zlib source files change.

## Test Signals
The `test` target provides a basic library smoke test through zlib's sample programs. There is no automated signal in the CMake MiniZip tests for this makefile.
