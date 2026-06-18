# sources/compression/zstd/programs/fileio_common.h

## Purpose

This header centralizes common file-I/O macros for the zstd CLI: byte-unit helpers, display/progress macros, zstd error checking wrappers, and portable large-file seeking/telling.

## Important APIs, Types, and Functions

It declares external globals `g_display_prefs` and `g_displayClock`, then defines `DISPLAY*`, `DISPLAY_PROGRESS`, `DISPLAY_SUMMARY`, `DISPLAYUPDATE`, `EXM_THROW`, `CHECK_V`, and `CHECK`. `LONG_SEEK` and `LONG_TELL` resolve to `fseeko`, `ftello`, MSVC 64-bit calls, MinGW variants, or Windows `SetFilePointerEx` helpers depending on platform.

## Control Flow, State, and Persistence

Display updates are gated by verbosity, progress policy, and a refresh interval of roughly one sixth of a second. `EXM_THROW` prints through the display layer and exits, so callers treat failed zstd operations as fatal in paths using `CHECK`.

## Dependencies and Integration Points

It depends on zstd error helpers, `FIO_display_prefs_t`, `platform.h`, and `timefn.h`. It is included by CLI file I/O modules and `zstdcli.c`.

## Risks and Test Signals

Macros evaluate some arguments multiple times (`MAX`, `MIN`, display varargs) and `EXM_THROW` terminates the process. Large-file seeking is platform-sensitive. Tests should include quiet/verbose/progress behavior, 32-bit large-file builds, Windows seek/tell builds, and zstd API error propagation.
