# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/export.h

NFS/export support header for NILFS. It declares `nilfs_export_ops` and defines packed `struct nilfs_fid`.

The file identifier stores checkpoint number, inode number, inode generation, parent generation, and parent inode number. Including checkpoint number is important because NILFS can expose historical checkpoint/snapshot roots.

Risk/notes: packed layout is part of file handle compatibility; field ordering and sizes are externally significant.
