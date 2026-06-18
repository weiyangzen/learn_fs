# sources/distributed-fs/ceph-client/lib/earlycpio.c

## Purpose
Provides `find_cpio_data()`, an early-boot helper for locating an uncompressed `newc` cpio member at the head of an initramfs blob before the normal initramfs decompression path runs. It is used for kernel-consumed early data that package tooling places before compressed payloads.

## Important APIs, Types, and Functions
The exported interface is `struct cpio_data find_cpio_data(const char *path, void *data, size_t len, long *nextoff)`. It returns a `cpio_data` with data pointer, size, and a path-relative name, or `{ NULL, 0, "" }` when not found or parsing fails. Internal enum `cpio_fields` names the fixed `newc` header fields.

## Control Flow
The parser walks the buffer while enough bytes remain for a header. It skips zero padding in 4-byte steps, parses the 6-character magic field and subsequent 8-character hex fields, validates magic `070701` or `070702`, aligns the filename and data boundaries, and rejects overruns. Regular-file entries whose name starts with `path` are returned; `nextoff`, when supplied, receives the offset of the next member so callers can iterate.

## State and Persistence
The function is stateless and performs no allocation. It returns direct pointers into the caller's archive buffer and copies only the matched suffix into the fixed-size `cd.name` array with `strscpy()`.

## Dependencies and Integration Points
Depends on `linux/earlycpio.h`, alignment macros, kernel string helpers, and `MAX_CPIO_FILE_NAME`. It integrates with early boot/initramfs consumers that know the archive is uncompressed at the current offset.

## Risks
The parser exits on the first malformed header or overrun, so a bad early member can hide later valid data. It only returns regular files and only supports uncompressed `newc` content. Filename suffixes longer than `MAX_CPIO_FILE_NAME` are warned and truncated. The zero-padding skip always subtracts four bytes; callers must provide correctly aligned remaining lengths.

## Test Signals
Tests should cover exact-file and directory-prefix lookups, repeated iteration with `nextoff`, zero padding, both accepted magic values, truncated headers, invalid hex, oversized names, non-regular entries, and malformed size/name combinations that would overrun the buffer.
