# sources/distributed-fs/ceph-client/io_uring/truncate.c

Purpose: implements io_uring `ftruncate` against the request file.

Important APIs/types/functions: `struct io_ftrunc` stores the file and desired length. Entry points are `io_ftruncate_prep()` and `io_ftruncate()`.

Control flow: prep rejects all unsupported SQE fields, reads the length from `sqe->off`, and forces async. Issue asserts blocking context, calls `do_ftruncate(req->file, len, 0)`, and completes.

State and persistence: request state is transient; successful execution persists file size changes and filesystem metadata updates.

Dependencies/integration: depends on VFS `do_ftruncate()` and io_uring async issue/completion.

Risks/test signals: risks are invalid field validation, negative/large length behavior delegated to VFS, and accidental nonblocking issue. Test successful truncate/extend, permission errors, sealed files, invalid SQE fields, and async-only execution.
