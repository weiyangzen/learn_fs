# Research: sources/distributed-fs/ceph-client/fs/nls/nls_utf8.c

## Purpose

This module registers UTF-8 as an NLS charset so filesystems can use the same `struct nls_table` interface as legacy byte encodings. Unlike the generated ISO/KOI tables, it delegates conversion to generic UTF helpers.

## Important APIs, Types, and Functions

`identity[256]` is initialized at module load and used for both `.charset2lower` and `.charset2upper`, meaning byte-level case conversion is disabled. `uni2char()` calls `utf32_to_utf8()`. `char2uni()` calls `utf8_to_utf32()` and rejects code points above `MAX_WCHAR_T`. The registered table uses `.charset = "utf8"`.

## Control Flow

`uni2char()` checks output capacity, encodes one `wchar_t` to UTF-8, writes `?` and returns `-EINVAL` on encode failure, and otherwise returns the byte count. `char2uni()` decodes a UTF-8 sequence from bounded input, writes `?` and returns `-EINVAL` if decoding fails or the result is too large for `wchar_t`, and otherwise returns bytes consumed.

## State and Persistence Behavior

The only mutable module state is `identity[256]`, initialized once before registration. There is no per-consumer state. UTF-8 filenames persist according to the kernel UTF helper behavior.

## Dependencies and Integration Points

The file depends on Linux NLS and Unicode conversion helpers. It integrates with filesystems through the NLS registry under `utf8`.

## Risks

The fallback writes `?` on invalid conversion while still returning an error; callers must not consume the fallback as success. Identity case tables mean no Unicode case folding is provided. `MAX_WCHAR_T` bounds make this table dependent on the kernel's `wchar_t` width.

## Test Signals

Round-trip ASCII, two-, three-, and four-byte UTF-8 within `MAX_WCHAR_T`, invalid byte sequences, truncated sequences, too-small output buffers, and case-table identity behavior.
