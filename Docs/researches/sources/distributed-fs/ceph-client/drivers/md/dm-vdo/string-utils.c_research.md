# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/string-utils.c

## Purpose
`string-utils.c` implements a bounded append helper for constructing strings in caller-owned buffers.

## Important APIs, Types, And Functions
`vdo_append_to_buffer(char *buffer, char *buf_end, const char *fmt, ...)` wraps `vsnprintf()`, appends formatted output at the current buffer cursor, and returns the next write cursor. It is annotated as printf-like in the header.

## Control Flow
The function starts a variadic argument list, calls `vsnprintf()` with the remaining buffer length, clamps the returned cursor to `buf_end` on truncation, otherwise advances by the number of bytes written, then ends the variadic list.

## State And Persistence
No global or persistent state exists. The only state is the caller's buffer and cursor. Truncated output is detected by comparing the formatted length against available space.

## Dependencies And Integration Points
It includes `string-utils.h`, which brings kernel string/kernel helpers. Callers can repeatedly chain the returned pointer while preserving a fixed buffer end.

## Risks
Correctness depends on callers passing a valid `[buffer, buf_end]` range. If `buffer > buf_end`, the subtraction passed to `vsnprintf()` is invalid. Truncation is silent except for cursor clamping, so callers that need complete strings must check the returned pointer.

## Test Signals
Tests should cover exact fit, truncation, empty remaining space, multiple chained appends, and printf format checking.
