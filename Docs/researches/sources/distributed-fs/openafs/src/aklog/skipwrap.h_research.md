# sources/distributed-fs/openafs/src/aklog/skipwrap.h

## Purpose
`skipwrap.h` declares the ticket wrapper extraction helper used by `klog`.

## Important APIs, types, and functions
The single API is `int afs_krb5_skip_ticket_wrapper(char *tix, size_t tixlen, char **enc, size_t *enclen)`, returning zero on success and nonzero on parse failure.

## Control flow
There is no control flow in the header.

## State and persistence
No state is defined. The API contract implies output aliases into the input buffer.

## Dependencies and integration points
The header is included by `skipwrap.c` and `klog.c`.

## Risks
The declaration uses mutable `char *` for DER data even though parsing does not modify it, so const-correctness is weak. Callers must not free or overwrite the ticket before using the returned encrypted-part pointer.

## Test signals
Compile-time coverage is enough for the header; behavioral tests belong to `skipwrap.c` callers.
