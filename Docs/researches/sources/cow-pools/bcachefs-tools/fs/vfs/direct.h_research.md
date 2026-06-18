# File Research: sources/cow-pools/bcachefs-tools/fs/vfs/direct.h

Purpose: Public direct-IO structures and function declarations.

Key APIs and behavior:
- `struct dio_read` contains closure, kiocb, return value, dirty-page decision, and embedded read bio.
- `struct dio_write` tracks request, mapping, inode, mm, iov copy, async/sync flags, quota reservation, written sectors, iterator, inline vectors, and trailing write op.
- Declares direct read, direct write, and read_iter entry points.

Integration:
- Implemented by `direct.c`.
- Depends on bcachefs read/write and VFS IO types.

Risks and invariants:
- `bch_write_op op` must remain last in `dio_write` for allocation/container layout.
- Async write continuation depends on saved iterator/iovec lifetime.
