# Research: sources/distributed-fs/ceph-client/fs/nls/nls_ucs2_utils.h

## Purpose

This header provides inline UCS-2 string utility functions and uppercase conversion helpers for kernel filesystems. Its semantics mirror C string routines but operate on `wchar_t`/little-endian UCS-2 units.

## Important APIs, Types, and Functions

The header defines private-use Unicode constants for Windows-reserved filename characters such as `UNI_ASTERISK`, `UNI_QUESTION`, `UNI_COLON`, `UNI_GRTRTHAN`, `UNI_LESSTHAN`, `UNI_PIPE`, and `UNI_SLASH`. Inline routines include `UniStrcat`, `UniStrchr`, `UniStrcmp`, `UniStrcpy`, `UniStrlen`, `UniStrnlen`, `UniStrncat`, `UniStrncmp`, `UniStrncmp_le`, `UniStrncpy`, `UniStrncpy_le`, `UniStrstr`, `UniToupper`, and `UniStrupr`.

## Control Flow

The string helpers use simple NUL-terminated loops analogous to libc routines. The `_le` variants convert little-endian `__le16` values with endian helpers. `UniToupper()` first uses `NlsUniUpperTable` for low code points, then scans `NlsUniUpperRange` until the input falls within a range or passes all ranges. `UniStrupr()` walks a little-endian string in place, uppercasing each code unit.

## State and Persistence Behavior

The header contains inline code only. It mutates caller-provided buffers for copy, concat, strncpy, and uppercase-in-place operations. It assumes NUL-terminated UCS-2 input unless a length-limited function is used.

## Dependencies and Integration Points

It depends on byteorder helpers, `linux/types.h`, `linux/nls.h`, `linux/unicode.h`, and `nls_ucs2_data.h`. Filesystems can include it to share NTFS/CIFS-style UCS-2 string behavior.

## Risks

Most routines do not know destination buffer sizes beyond the explicit `n` parameters, so callers must guarantee space. `UniStrnlen()` increments before checking the limit, matching its local implementation but requiring careful caller interpretation. `UniStrncpy_le()` names suggest little-endian output but uses `__le16_to_cpu()` while writing to `wchar_t *`, so type expectations should be checked by consumers. `UniToupper()` is uppercase-only and does not implement locale-sensitive or full Unicode case folding.

## Test Signals

Unit tests should cover empty strings, exact-length bounded operations, unterminated inputs guarded by length, substring matches at start/middle/end, little-endian comparisons/copies, uppercase of ASCII/Greek/Cyrillic/fullwidth ranges, and reserved-character private-use constants.
