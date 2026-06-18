# sources/distributed-fs/ceph-client/fs/backing-file.c

Purpose: provides common backing-file helpers for stackable filesystems, including open/tmpfile wrappers, credential override, read/write/splice/mmap forwarding, and async I/O completion adaptation.

Important APIs/types/functions: exported `backing_file_open`, `backing_tmpfile_open`, `backing_file_read_iter`, `backing_file_write_iter`, `backing_file_splice_read`, `backing_file_splice_write`, and `backing_file_mmap`. Internal `struct backing_aio` clones caller `kiocb` state for async forwarding.

Control flow: open helpers allocate an FMODE_BACKING file, attach the user-visible path, and call `vfs_open()` or `vfs_tmpfile()` under supplied creds. Read/write helpers reject non-backing files, empty iterators, unsupported direct I/O, and then run the real VFS operation under `ctx->cred`. Async write completion is queued to the superblock DIO workqueue so size/mtime updates are serialized before calling the original completion.

State and persistence: no persistent data; file references, user paths, cloned kiocbs, and slab-allocated `backing_aio` objects carry transient state. Writes remove privileges on the user-facing file and invoke callback hooks for access/end-write accounting.

Dependencies and integration: used by overlay-like filesystems; integrates with Linux security hooks (`security_mmap_backing_file`), VFS iter/splice/mmap APIs, `scoped_with_creds`, superblock DIO workqueues, and `linux/backing-file.h`.

Risks: credential context and user-vs-real file attribution are security-sensitive. Async refcounting and completion ordering must avoid use-after-free and stale `ki_pos`. Direct I/O capability checks must remain aligned with lower file capabilities.

Test signals: overlay/stacked filesystem xfstests for read/write/splice/mmap; async direct I/O completion; privilege stripping on writes; LSM mmap hook denial; WARN coverage for non-FMODE_BACKING misuse.
