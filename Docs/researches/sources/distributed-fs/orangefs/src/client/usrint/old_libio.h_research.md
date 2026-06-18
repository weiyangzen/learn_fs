# sources/distributed-fs/orangefs/src/client/usrint/old_libio.h

## Purpose
`old_libio.h` supplies legacy glibc/libio flag and marker definitions needed by the OrangeFS stdio/over-under interposition code. It avoids relying on private system `libio` headers while preserving constants expected by code that manipulates `_IO_FILE`-style fields.

## Important APIs, Types, And Constants
The file defines old stream mode bits such as `_IOS_INPUT`, `_IOS_OUTPUT`, `_IOS_ATEND`, `_IOS_APPEND`, `_IOS_TRUNC`, `_IOS_NOCREATE`, `_IOS_NOREPLACE`, and `_IOS_BIN`. It defines `_IO_MAGIC`, `_OLD_STDIO_MAGIC`, `_IO_MAGIC_MASK`, and many `_IO_*` flag bits for buffer ownership, read/write permission, EOF/error state, linked streams, backup state, line buffering, append/current-put mode, filebuf identity, delete/close behavior, and user locking. It also defines `_IO_FLAGS2_*` bits and formatting flags such as `_IO_SKIPWS`, `_IO_LEFT`, `_IO_DEC`, `_IO_HEX`, `_IO_SHOWBASE`, `_IO_FIXED`, `_IO_STDIO`, and `_IO_BOOLALPHA`. The only type is `struct _IO_marker`, which links markers to an `_IO_FILE` buffer and stores a relative position.

## Control Flow
This header has no functions and no control flow. It is included by usrint stdio-related code so that stream setup and compatibility logic can read or set flag bits using the historical names expected by glibc-derived code.

## State And Persistence Behavior
The constants describe in-memory stream state stored in `_IO_FILE`-like objects. The header itself owns no storage and writes no persistent state. Stream flags influence runtime buffering, read/write permissions, EOF/error reporting, append behavior, and cleanup decisions wherever included code applies them.

## Dependencies And Integration Points
`stdio.c` and `overunder.c` include this header. It forward-references `struct _IO_FILE` inside `struct _IO_marker`, relying on libc headers or local declarations to define the full stream type elsewhere. Several constants are guarded by `#ifndef` so they do not conflict if a platform header already provided `_IO_EOF_SEEN` or `_IO_ERR_SEEN`.

## Risks
These are private glibc compatibility constants, so they are sensitive to libc version and platform differences. Code that assumes `_IO_FILE` layout or flag semantics may break on non-glibc or newer glibc implementations. The header intentionally does not include full libio declarations, so includers must arrange compatible declarations. Typos or stale values in these constants could produce subtle stdio behavior rather than compile errors.

## Test Signals
Build tests should compile `stdio.c` and `overunder.c` against current target libc headers. Runtime stdio tests should verify EOF/error propagation, append/write/read mode restrictions, buffering behavior, standard-stream setup, close/delete behavior, and compatibility with `flockfile`/`funlockfile` paths that also use `locks.h`.
