# sources/distributed-fs/openafs/src/platform/IRIX/herror.c

## Purpose
Provides a compatibility implementation of BSD `herror` and host lookup error strings for platforms that do not supply them, excluding Darwin.

## Important APIs, Types, And Functions
Defines `h_errlist`, `h_nerr`, and `herror(char *s)`. On Sun environments it defines `h_errno`; elsewhere it expects an external `h_errno`. `herror` emits an optional caller prefix, a host-error message, and newline using `writev` to file descriptor 2.

## Control Flow
`herror` builds a small `struct iovec` array. If the caller provided a non-empty prefix, it adds prefix and `": "`. It then indexes `h_errlist` when `h_errno` is in range, otherwise prints `"Unknown error"`, adds a newline vector, and calls `writev`.

## State And Persistence
Static/global state is limited to the error string table, count, and platform-dependent `h_errno`. The function writes only to stderr and persists nothing.

## Dependencies And Integration Points
Used by legacy remote command code such as `rcmd.c` when `gethostbyname` fails. Depends on BSD-ish `uio.h`, `writev`, `strlen`, and OpenAFS platform macros.

## Risks And Test Signals
Risks include K&R-style implicit `int` return, limited error table coverage, and potential mismatch with modern resolver thread-local `h_errno` semantics. Test signals are successful builds on target legacy platforms and correct diagnostics for failed remote host lookup.
