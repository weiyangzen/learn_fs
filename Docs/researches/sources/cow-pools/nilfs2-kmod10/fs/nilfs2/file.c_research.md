# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/file.c

Regular-file operations for NILFS. It defines fsync behavior, mmap write-fault handling, file operations, and inode operations.

Key behavior:
- `nilfs_sync_file` constructs a data-sync segment for datasync fsync or a normal segment otherwise, then flushes the device.
- `nilfs_page_mkwrite` handles mmap write faults: checks disk-full state, validates the folio, fills holes inside a NILFS transaction via `block_page_mkwrite`, marks file dirty, commits, and waits for writeback before allowing modification.
- Exports `nilfs_file_operations` with generic read/write/splice, ioctl, mmap, open, and fsync hooks.
- Exports `nilfs_file_inode_operations` for setattr, permission, fiemap, and file attributes.

Risk/notes: mmap write faults must wait for writeback because NILFS recovery validates log checksums including data blocks. Disk-full returns `VM_FAULT_SIGBUS`.
