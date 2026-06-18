# sources/compression/xz/cmake/tuklib_progname.cmake

## Purpose
This module detects support for obtaining the program invocation name through a glibc extension.

## Important Control Flow
`tuklib_progname(TARGET_OR_ALL)` checks whether `program_invocation_name` exists in `errno.h` and adds `HAVE_PROGRAM_INVOCATION_NAME` when available.

## State, Dependencies, and Integration
It uses `CheckSymbolExists` and `tuklib_common.cmake`. The top-level build applies it to command-line tools that use `src/common/tuklib_progname.c`.

## Risks and Test Signals
The symbol requires `_GNU_SOURCE` on glibc, so this module depends on prior system-extension setup. If unavailable, C code must use fallback program-name handling.
