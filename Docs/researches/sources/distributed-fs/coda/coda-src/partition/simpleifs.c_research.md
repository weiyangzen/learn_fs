# sources/distributed-fs/coda/coda-src/partition/simpleifs.c

Purpose: simple userspace inode backend that stores each synthetic inode as a regular file named by inode number and a sidecar resource file named `.<inode>` containing `i_header`.

APIs and flow: `s_init` validates directory and stores device. `s_icreate` finds the next free numeric filename, creates the payload file, creates sidecar header with link count one and `VICEMAGIC`. `s_iopen`, `s_iread`, and `s_iwrite` operate on payload files. `s_iinc`/`s_idec` update header link count and delete payload/sidecar at final decrement. `s_list_coda_inodes` scans numeric directory entries and writes `ViceInodeInfo` records for valid headers.

State/persistence: persistent state is payload plus sidecar header files; in-memory state is only next inode hint. Risks include a bug in `set_link` comparing the pointer `count <= 0`, leaked file descriptors on lseek failure, no locking around inode allocation, and sidecar/header drift if creation fails mid-way. Tests are partition basic/create/delete/scan tools.
