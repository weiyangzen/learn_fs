# sources/distributed-fs/eos/namespace/utils/DataHelper.cc

## Purpose
`DataHelper.cc` implements checksum and ownership-copy utility functions declared in `DataHelper.hh`.

## Important APIs, Types, and Functions
`computeCRC32()` and `updateCRC32()` wrap zlib CRC32. `computeCRC32C()`, `updateCRC32C()`, and `finalizeCRC32C()` wrap EOS's CRC32C implementation. `copyOwnership()` copies UID/GID from a source path to a target path, optionally ignoring non-root callers.

## Control Flow
CRC helpers call the underlying checksum functions with appropriate initialization or existing CRC state. `copyOwnership()` checks `getuid()`: non-root callers return silently when `ignoreNoPerm` is true, otherwise throw `MDException(EFAULT)`. Root callers `stat()` the source path, then `chown()` the target to the source UID/GID, throwing `MDException(errno)` on either failure.

## State and Persistence Behavior
Checksum helpers are pure. `copyOwnership()` mutates filesystem metadata on the target path when run as root. It does not change file contents and does not roll back partial failures.

## Dependencies and Integration Points
The implementation depends on zlib, EOS CRC32C code, POSIX `getuid`, `stat`, and `chown`, and `MDException`. It is a low-level namespace/common utility for data conversion and ownership preservation workflows.

## Risks and Edge Cases
`void*` buffer parameters allow mutable-looking access even though checksum functions only read. `copyOwnership()` silently no-ops for non-root by default, which is convenient but can mask ownership preservation failures. It uses `stat()` rather than `lstat()`, so source symlinks are followed. Permission and filesystem errors are surfaced as metadata exceptions.

## Test Signals
Tests should compare CRC32/CRC32C against known vectors, incremental update equivalence, finalize behavior, root/non-root `copyOwnership()` behavior, missing source errors, and target `chown()` failures.
