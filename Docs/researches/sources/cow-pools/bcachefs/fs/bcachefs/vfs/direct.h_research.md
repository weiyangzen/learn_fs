# File Research: sources/cow-pools/bcachefs/fs/bcachefs/vfs/direct.h

## Summary
Declares bcachefs direct I/O state structures and public direct read/write APIs.

## Main Contents
- `struct dio_read`: closure, request pointer, return value, dirty-page flag, and embedded `bch_read_bio`.
- `struct dio_write`: request, mapping, inode, mm, optional copied iovec storage, state flags, quota reservation, written sector count, iterator, inline iovecs, and trailing `bch_write_op`.
- Declarations for direct read, direct write, and `read_iter`.

## Risks
Both structures rely on embedded/trailing bio/write-op layout for `container_of()` recovery. Async write continuation depends on `mm` and copied iovec lifetime being valid until completion.
