<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/dos/Makefile -->
# sources/compression/xz/dos/Makefile

Purpose: hand-written DJGPP makefile to build `xz.exe` for DOS without the Autotools generated build.

Important APIs/types/functions: defines compiler/link flags, large `SRCS_C` source list covering getopt, tuklib, liblzma, and xz frontend, assembler CRC sources, object derivation, generated `getopt.h`, and final `xz.exe` recipe with `exe2coff`/CWSDPMI stub.

Control flow: build all C/assembly objects with include paths and `HAVE_CONFIG_H`, link them into `xz.exe`, strip, convert to COFF, prepend DPMI stub, and clean intermediate executable forms.

State and persistence: persists objects in source-adjacent paths and final DOS executable.

Dependencies and integration: depends on DJGPP, DOS commands (`del`, `copy`), `update`, `exe2coff`, `CWSDSTUB.EXE`, and curated source list consistency.

Risks: source list must be manually kept in sync with liblzma/xz changes. Object outputs live outside `dos/`, increasing cleanup risk. It hard-codes full feature selection via `dos/config.h`.

Test signals: build under DJGPP, run `xz.exe --version`, compress/decompress fixtures, and verify x86 assembly CRC linkage.
<!-- END_FILE_RESEARCH: sources/compression/xz/dos/Makefile -->
