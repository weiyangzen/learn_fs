# sources/distributed-fs/ceph-client/include/linux/ucs2_string.h

## Purpose
Declares helpers for handling UCS-2 strings and converting them to UTF-8.

## Important APIs, Types, And Functions
Defines `typedef u16 ucs2_char_t` and exports `ucs2_strnlen()`, `ucs2_strlen()`, `ucs2_strsize()`, `ucs2_strscpy()`, `ucs2_strncmp()`, `ucs2_utf8size()`, and `ucs2_as_utf8()`.

## Control Flow
Implementations measure bounded or unbounded UCS-2 strings, copy/compare UCS-2 character arrays, calculate required UTF-8 size, and emit UTF-8 bytes up to a maximum.

## State, Persistence, And Dependencies
No state is held. Dependencies are base types and NULL definition.

## Integration Points
Used by firmware/EFI/device-name paths that receive UCS-2 strings but expose UTF-8 text to kernel/userspace.

## Risks And Test Signals
Risks include truncation, malformed surrogate handling depending on implementation, off-by-one termination, and byte-vs-character size confusion. Test signals include bounded string tests, UTF-8 conversion vectors, truncation behavior, and comparisons with embedded NULs.
