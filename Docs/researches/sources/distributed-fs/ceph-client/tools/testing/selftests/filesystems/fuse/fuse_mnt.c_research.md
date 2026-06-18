# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/fuse/fuse_mnt.c

## Purpose

`fuse_mnt.c` is a minimal libfuse filesystem daemon used by the fusectl abort test. It exposes a writable single-file filesystem at `/test`.

## Important APIs, Types, and Functions

Global state is `content`, `content_size`, and `test_path`. FUSE operations are `test_getattr`, `test_readdir`, `test_open`, `test_read`, `test_write`, and `test_truncate`, collected in `memfd_ops` and passed to `fuse_main`.

## Control Flow, State, and Persistence

`main` delegates lifecycle to libfuse. `getattr` reports `/` as a directory and `/test` as a regular file sized from `content_size`. `readdir` lists `.`, `..`, and `test`. `open` rejects non-test paths. `read` clamps by offset and returns current memory content. `write` rejects holes, reallocates when needed, updates `content_size`, and copies bytes. `truncate` frees or resizes content and zero-fills growth. Persistence is in process memory only, lost when the daemon exits or is aborted.

## Dependencies, Integration Points, Risks, and Test Signals

It depends on libfuse API version 26 and a usable `/dev/fuse`. It integrates with `fusectl_test`, which starts this daemon and then aborts the connection through fusectl. Risks include memory allocation failure, no cleanup of `content` at normal exit, non-thread-safe globals if libfuse dispatches concurrently, and no sparse write support. Passing signals are successful mount, `/test` open/read/write/truncate behavior, and subsequent `ENOTCONN` after fusectl abort.
