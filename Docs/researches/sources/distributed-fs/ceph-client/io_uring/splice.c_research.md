# sources/distributed-fs/ceph-client/io_uring/splice.c

Purpose: implements io_uring `splice` and `tee` operations, including fixed-file input support.

Important APIs/types/functions: `struct io_splice` stores output file, input/output offsets, length, input fd, flags, and optional fixed-resource node. Entry points are `io_tee_prep()`, `io_tee()`, `io_splice_prep()`, `io_splice()`, and `io_splice_cleanup()`.

Control flow: prep validates splice flags, records `splice_fd_in`, stores offsets, and forces async. Issue gets the input file either through normal fd lookup or fixed-file table lookup under the submit lock, calls `do_tee()` or `do_splice()` with offsets or NULL for current position, releases normal fd refs, and completes. Cleanup drops a held fixed resource node.

State and persistence: transient state is the input file reference/resource-node reference and offsets. External effects are pipe/file data movement and file offset updates when offsets are `-1`.

Dependencies/integration: depends on VFS splice helpers, fixed-file resources, io_uring file lookup, and cleanup hooks.

Risks/test signals: risks are fixed resource ref leaks, unsupported flag acceptance, input/output offset semantics, and treating short splice/tee as failure. Test with pipes/files, fixed input fd, zero length, invalid flags, faulted/closed input fds, and cleanup after cancellation.
