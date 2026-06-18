# sources/distributed-fs/openafs/src/WINNT/afsd/test/convtest.c

## Purpose
Standalone test program for OpenAFS Windows Unicode normalization and UTF-8/UTF-16 conversion helpers from `cm_nls.h`.

## Important APIs, Types, And Functions
Tests `cm_NormalizeStringAlloc`, `cm_Utf16ToUtf8Alloc`, `cm_Utf16ToUtf8`, `cm_Utf8ToUtf16Alloc`, and `cm_Utf8ToUtf16`. Fixtures include normalization pairs, external normalization conformance entries (`norm_tests`), and UTF-8/UTF-16 pairs including private-use, replacement character, and surrogate-pair code points.

## Control Flow
`main` initializes normalization and runs each test. Each loop validates non-null/nonzero conversion, returned length including NUL, and exact byte/wchar output, printing `PASS` or failure diagnostics.

## State And Persistence
No persistent state. Normalization tables may be process-global; allocation tests free returned buffers.

## Dependencies And Integration Points
Depends on `cm_nls.h`, C runtime string APIs, and external normalization fixtures. Validates low-level behavior used by SMB path parsing, directory lookup, case folding, and pioctl conversion.

## Risks
Mostly valid-input coverage. Malformed UTF-8, insufficient buffers, embedded NULs, and locale edge cases are not deeply tested. `cm_NormalizeStringTest` can print failures but still return success.

## Test Signals
Good runs print `PASS` for conversion fixtures and no normalization mismatch messages. CI should treat printed failure counts as failures and add negative/bounds cases.
