# File Research: sources/cow-pools/bcachefs/fs/bcachefs/vfs/buffered.h

## Summary
Declares the buffered I/O interface and writepage I/O container.

## Main Contents
- `struct bch_writepage_io`, containing the target inode and trailing `struct bch_write_op`.
- Declarations for folio read, readahead, writepages, write_begin/write_end, and write_iter.
- Kernel-version-dependent `write_begin`/`write_end` signatures.

## Risks
`struct bch_writepage_io` relies on `bch_write_op` being last because bios are allocated from a bioset and recovered with `container_of()`. Signature guards must match the kernel version being built.
