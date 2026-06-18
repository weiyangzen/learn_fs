# sources/distributed-fs/ceph-client/fs/ramfs/internal.h

Purpose: Provides the minimal private ramfs declaration shared between `inode.c` and the selected file-operation implementation.

Important APIs, types, and functions: Declares external `ramfs_file_inode_operations`.

Control flow: `inode.c` includes this header to assign regular-file inode operations in `ramfs_get_inode()`. The symbol is defined by either `file-mmu.c` or `file-nommu.c`, selected by Kbuild.

State and persistence: No state or persistence is defined here.

Dependencies and integration points: Depends on VFS `struct inode_operations` declarations from included kernel headers through users. It is part of the build-time contract between ramfs inode and file implementations.

Risks and test signals: Risk is symbol mismatch if Kbuild selection changes or one file implementation stops exporting the declaration. Test both MMU and no-MMU builds for clean linkage.
