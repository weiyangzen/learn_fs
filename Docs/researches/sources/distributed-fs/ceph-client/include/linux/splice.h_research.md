<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/splice.h -->
# sources/distributed-fs/ceph-client/include/linux/splice.h

Purpose: Declares the kernel splice, tee, vmsplice, and direct file-range transfer interfaces plus descriptors used to move data between files, pipes, sockets, userspace memory, and page arrays.

Important APIs/types/functions: `SPLICE_F_*` flags, `struct splice_desc`, `struct partial_page`, `struct splice_pipe_desc`, `splice_actor`, `splice_direct_actor`, `splice_from_pipe()`, `__splice_from_pipe()`, `splice_to_pipe()`, `add_to_pipe()`, `vfs_splice_read()`, `splice_direct_to_actor()`, `do_splice()`, `do_splice_direct()`, `splice_file_range()`, `splice_copy_file_range()`, `do_tee()`, `splice_to_socket()`, `splice_grow_spd()`, `splice_shrink_spd()`, and pipe buffer ops exports.

Control flow: The header does not implement the splice loops, but its descriptors show the flow: pipe buffers and page descriptors are passed to actor callbacks, `splice_desc` tracks remaining/current length, file position, flags, and wakeup needs, and higher-level helpers route file-to-pipe, pipe-to-file, direct, tee, and socket transfers.

State and persistence behavior: Transfer state is transient in descriptors, file offsets, pipe buffers, page refs, and wakeup flags. No on-disk persistence is managed here.

Dependencies: Depends on `pipe_fs_i.h`, `struct file`, `struct page`, pipe buffer operations, and VFS file-position conventions.

Integration points: VFS `copy_file_range`, `sendfile`, socket splicing, pipes, and filesystem `splice_read`/`splice_write` implementations. Distributed filesystems such as Ceph can interact through VFS read/write/splice paths.

Risks: Mismanaging page ownership with `SPLICE_F_GIFT`, nonblocking semantics, EOF callbacks, or partial-page lengths can leak refs, block unexpectedly, or corrupt transfer accounting.

Test signals: Splice/tee/vmsplice syscall tests, nonblocking pipe tests, file offset preservation tests, socket splice tests, and filesystem-specific splice read/write coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/splice.h -->
