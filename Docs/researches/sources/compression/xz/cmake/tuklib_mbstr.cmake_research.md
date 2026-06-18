# sources/compression/xz/cmake/tuklib_mbstr.cmake

## Purpose
This module detects multibyte and formatting helper functions used by tuklib command-line presentation code.

## Important Control Flow
`tuklib_mbstr(TARGET_OR_ALL)` checks for `mbrtowc` and `wcwidth` in `wchar.h`, and `vasprintf` in `stdio.h`, adding `HAVE_MBRTOWC`, `HAVE_WCWIDTH`, and `HAVE_VASPRINTF` definitions when present.

## State, Dependencies, and Integration
It uses `CheckSymbolExists` and `tuklib_common.cmake`. It is applied to tools like `xz`, `xzdec`, and `lzmainfo`, where display width and printable string handling matter.

## Risks and Test Signals
Feature-test macro ordering matters because `wcwidth` and `vasprintf` require extension macros on some systems. The module relies on `tuklib_use_system_extensions()` having been called earlier in the top-level build.
