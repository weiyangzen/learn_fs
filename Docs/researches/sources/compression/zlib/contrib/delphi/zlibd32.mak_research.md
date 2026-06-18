# sources/compression/zlib/contrib/delphi/zlibd32.mak

Purpose: Borland C++/Delphi-compatible Win32 makefile for building zlib with Delphi calling conventions.

Important variables/targets: sets `LOC = -DZEXPORT=__fastcall -DZEXPORTVA=__cdecl`, `CC=bcc32`, `AR=tlib`, `ZLIB_LIB=zlib.lib`, object lists split into `OBJ1`/`OBJ2` and `OBJP1`/`OBJP2`, targets `all`, pattern `.c.obj`, `test`, `example.exe`, `minigzip.exe`, and `clean`.

Control flow: compiles C sources to `.obj`, archives objects into `zlib.lib` in two `tlib` commands to satisfy old MS-DOS command-line limits, links example and minigzip, and tests by running `example` and piping text through `minigzip`.

State and persistence: creates `.obj`, `.exe`, `.lib`, `.tds`, `zlib.bak`, and `foo.gz` artifacts; clean deletes them with DOS-style `del`.

Dependencies and integration: targets legacy Borland C++ Builder and Delphi Win32 consumers using register/fastcall conventions. Uses core zlib sources and test programs.

Risks: legacy toolchain-specific; flags and calling conventions are unsuitable for normal C ABI builds. Command-line splitting reflects old make limitations and should be preserved if maintaining this file.

Test signals: `make test` validates example and minigzip under the Borland-produced library.
