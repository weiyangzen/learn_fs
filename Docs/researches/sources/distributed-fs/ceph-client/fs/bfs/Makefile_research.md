# sources/distributed-fs/ceph-client/fs/bfs/Makefile

Purpose: declares BFS driver build composition.

Important APIs/types/functions: `obj-$(CONFIG_BFS_FS) += bfs.o` and `bfs-objs := inode.o file.o dir.o`.

Control flow: Kbuild links superblock/inode, file mapping, and directory operation objects into one BFS module/object.

State and persistence: build metadata only.

Dependencies and integration: mirrors runtime split between mount/inode persistence, file block allocation, and directory mutation.

Risks: missing any object breaks required VFS operation tables.

Test signals: BFS built-in/module compile coverage.
