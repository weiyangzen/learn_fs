# File Research: sources/block-storage/vdo/utils/vdo/fileLayer.c

Implements `PhysicalLayer` over a regular file or block device using direct I/O.

Key details:
- `FileLayer` stores the `PhysicalLayer` vtable, block count, block offset, fd, alignment, and name.
- Allocates direct-I/O-compatible buffers aligned to the underlying file/device block size.
- `fileReader()` and `fileWriter()` apply `fileOffset`, bounds-check against `blockCount`, repair unaligned caller buffers with temporary aligned buffers, and use `pread`/`pwrite`.
- `setupFileLayer()` validates existence, opens read-only or read-write direct, detects block device status, reads size through `BLKGETSIZE64` or `stat`, and enforces requested block-count consistency.
- Read-only layers use `noWriter()`, returning `EPERM`.

Risk notes:
- `performIO()` handles short I/O by looping, but any zero-length result becomes `VDO_UNEXPECTED_EOF`.
- Alignment is taken from `st_blksize`, which is pragmatic for direct I/O but may not capture every device-specific alignment constraint.
