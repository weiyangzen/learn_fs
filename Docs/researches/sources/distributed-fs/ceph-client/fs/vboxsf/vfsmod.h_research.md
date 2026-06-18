<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/vboxsf/vfsmod.h -->
# sources/distributed-fs/ceph-client/fs/vboxsf/vfsmod.h

Purpose: Central private header for the vboxsf filesystem, defining shared state structures, constants, operation-table declarations, and cross-file helper prototypes.

Important APIs, types, and functions: Defines `DIR_BUFFER_SIZE`, `VBOXSF_SBI()`, `VBOXSF_I()`, `struct vboxsf_options`, `struct vboxsf_fs_context`, `struct vboxsf_sbi`, `struct vboxsf_inode`, `struct vboxsf_dir_info`, and `struct vboxsf_dir_buf`. Declares all vboxsf operation tables and helper/wrapper functions used across `dir.c`, `file.c`, `utils.c`, `super.c`, and `vboxsf_wrappers.c`.

Control flow: This file has no executable control flow. It establishes the module-internal contracts: superblocks own mount options and host root handles, inodes embed VFS inode plus restat and handle-list state, and directory reads produce a list of fixed-size buffers containing variable-sized host entries.

State and persistence: Defines the in-memory state layout for mounted shared folders and cached inodes. Persistent host state is accessed through declared wrapper functions rather than stored here.

Dependencies and integration points: Includes backing-device and IDR support plus the shared-folder host interface. It is the integration point that lets each vboxsf translation unit share private structures without exposing them outside the module.

Risks and test signals: Risks are structure layout changes not reflected in allocation/free code, missing prototypes after API changes, and lock ownership misunderstandings for `handle_list_mutex` and `ino_idr_lock`. Test by building with sparse/lockdep and exercising open/writeback while handles are added and removed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/vboxsf/vfsmod.h -->
