# sources/distributed-fs/openafs/src/WINNT/talocale/tal_string.cpp

## Purpose

`tal_string.cpp` implements TaLocale's localized string, formatting, encoding, path, and utility-string functions. Its central feature is a resource-aware formatter that converts printf-style arguments into strings and substitutes them into message templates using `%1`, `%2`, and similar positional markers.

## Important APIs, Types, and Functions

- `GetString()` loads one or more consecutive string resources, continuing when a resource ends in `+`.
- `GetStringLength()` computes the required buffer length for possibly continued string resources.
- `SearchMultiString()`, `FormatMultiString()`, and `vFormatMultiString()` manage Windows multistring buffers.
- `FormatString()` and `vFormatString()` support literal or resource-ID templates and parse a caller-supplied printf-like argument format.
- The private `vartype` enum classifies arguments as words, dwords, floats/doubles, ANSI/Unicode strings, nested messages, byte counts, system/elapsed time, errors, socket addresses, or `LARGE_INTEGER`.
- Specialized formatters include `FormatSockAddr()`, `FormatElapsed()`, `FormatTime()`, `FormatError()`, `FormatBytes()`, `FormatLargeInt()`, and `FormatDouble()`.
- `SetErrorTranslationFunction()` installs a caller-supplied error-message translator.
- Path helpers are `FindExtension()`, `FindBaseFileName()`, `ChangeExtension()`, `CopyBaseFileName()`, and `lsplitpath()`.
- Encoding/allocation helpers convert and clone ANSI, Unicode, `TCHAR`, and multistring data and free strings allocated through TaLocale allocation macros.
- Additional `lstr*` helpers provide uppercasing, character search, case-insensitive prefix compare, bounded copy, and nul-terminated copy.

## Control Flow

Literal or resource formatting enters `vFormatString(LONG, LPCTSTR, va_list)`. A high-word check decides whether the source is a string pointer or a resource ID. Resource IDs are loaded through `GetStringLength()` and `GetString()`. The function counts `%` entries in the caller's `pszFmt`, parses each format descriptor to determine a `vartype`, consumes the corresponding vararg, formats it into a temporary allocated string, then scans the template to compute output length and substitute positional `%N` references. Temporary argument strings and resource templates are freed before returning the final allocated string.

Multistring formatting calls `vFormatString()` for one entry, substitutes `cszMultiStringNULL` for empty entries, calculates the old multistring byte count including the double terminator, and allocates a new multistring with the new entry at the head or tail.

Error formatting first calls an optional callback, then `FormatMessage()` from the system, then `FormatMessage()` from `NTDLL.DLL`, and appends the hexadecimal status when translated. Encoding helpers allocate appropriately sized buffers and use Win32 conversion APIs or `wsprintfW`/copy helpers depending on `UNICODE`.

## State and Persistence

State is mostly transient allocated strings. Persistent process-local state includes `pfnTranslateError`, plus static conversion buffers in `CopyUnicodeToAnsi()` and `CopyAnsiToUnicode()`. No files or registry keys are written by this file.

## Dependencies and Integration Points

The file depends on `WINNT/talocale.h`, Win32 locale/time/message APIs, Winsock `inet_ntoa`, TaLocale resource lookup from `tal_main.cpp`, and allocation macros from `tal_alloc.h`. It is used by TaLocale dialogs and resource consumers that need localized messages and path/encoding utilities.

## Risks and Edge Cases

- `vFormatString()` consumes `float` with `va_arg(arg, float)`, but C varargs promote `float` to `double`; this is undefined behavior for `%f` inputs classified as `vtFLOAT`.
- Pointer/resource discrimination through `HIWORD(pszSource)` and pointer-to-`LONG` casts is unsafe on 64-bit builds.
- Static conversion buffers make `CopyUnicodeToAnsi()` and `CopyAnsiToUnicode()` non-thread-safe.
- Several helpers assume non-null inputs despite public signatures accepting pointer types.
- `FormatBytes()` always formats megabytes rather than selecting byte/kilobyte/megabyte units dynamically.
- `FormatDouble()` is hand-written and does not round like standard printf.

## Test Signals

Tests should cover resource continuation with `+`, positional template substitution, nested `%m` messages, `%e` error formatting, `%b`/`%B` bytes, `%t` and `%et` time formats, ANSI/Unicode conversions under both Unicode and non-Unicode builds, multistring append/prepend/search, and path helper behavior with drive, extension, and UNC-like paths.
