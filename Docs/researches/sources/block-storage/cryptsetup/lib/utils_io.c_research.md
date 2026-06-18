# File Research: sources/block-storage/cryptsetup/lib/utils_io.c

## Purpose
Provides reliable read/write and aligned blockwise I/O helpers.

## Key Responsibilities
- Reads or writes exact buffer lengths while handling `EINTR`.
- Provides interruptible read/write variants controlled by a volatile quit flag.
- Performs blockwise writes and reads that preserve partial trailing blocks.
- Performs blockwise read/write at possibly unaligned logical offsets by padding the front block.
- Allocates aligned temporary buffers when caller buffers are not sufficiently aligned.

## Important Details
- `write_blockwise()` preserves trailing block content by reading the existing block, modifying the prefix, seeking back, and writing a full block.
- `read_blockwise()` reads full aligned blocks and copies partial trailing content out.
- `write_lseek_blockwise()` and `read_lseek_blockwise()` handle negative offsets relative to file end.
- Functions return byte counts or negative/error sentinel values rather than logging.

## Dependencies
Uses POSIX `read`, `write`, `lseek`, `posix_memalign`, and declarations from `utils_io.h`.
