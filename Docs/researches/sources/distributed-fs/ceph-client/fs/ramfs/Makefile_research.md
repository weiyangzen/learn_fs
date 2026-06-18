# sources/distributed-fs/ceph-client/fs/ramfs/Makefile

Purpose: Builds the ramfs object from common inode code and the correct file-operation implementation for MMU or no-MMU kernels.

Important APIs, types, and functions: Uses Kbuild variables `obj-y`, `file-mmu-y`, `file-mmu-$(CONFIG_MMU)`, and `ramfs-objs`.

Control flow: `ramfs.o` is always built into the core kernel object set when this directory is selected. The default `file-mmu-y` points at `file-nommu.o`; when `CONFIG_MMU=y`, Kbuild substitutes `file-mmu.o`. `ramfs-objs` combines `inode.o` with the selected file implementation.

State and persistence: No runtime state. The selected object determines runtime mmap and file operation behavior.

Dependencies and integration points: Integrates with kernel Kbuild and `CONFIG_MMU`. The exported symbols from either file implementation satisfy references in `inode.c` and `internal.h`.

Risks and test signals: Risks are accidentally linking both file-operation implementations or the wrong one for no-MMU builds. Test by building MMU and no-MMU configurations and confirming only one `ramfs_file_operations` definition is linked.
