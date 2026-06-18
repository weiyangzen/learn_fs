# sources/distributed-fs/openafs/src/util/fileutil.h

Purpose: Public declaration of file path normalization and descriptor-buffered I/O helpers.

Important APIs and types: Defines `FPN_FORWARD_SLASHES`, `FPN_BACK_SLASHES`, `BUFIO_FD`, `BUFIO_INVALID_FD`, `BUFIO_BUFSIZE`, and `bufio_t`/`bufio_p`. Declares `FilepathNormalizeEx()`, `FilepathNormalize()`, `BufioOpen()`, `BufioGets()`, and `BufioClose()`.

Control flow and state: Header-only declarations. The `bufio_t` structure exposes file descriptor, buffer offsets, EOF flag, and fixed-size internal buffer to callers that include the header.

Dependencies and integration: Used by path initialization, config parsing, and other utilities that need old-style fd I/O. The design avoids stdio for environments where `FILE` descriptor width or CRT behavior is problematic.

Risks and test signals: Because `bufio_t` is public, callers can mutate internal fields and break invariants. The fixed 4096-byte buffer and integer offsets are simple but not appropriate for binary streaming or explicit long-line handling. Compile-time coverage and `dirpath_test` are the available local signals.
