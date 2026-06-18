# sources/distributed-fs/ceph-client/fs/ceph/io.h

## Purpose
`io.h` is the small public header for CephFS I/O mode exclusion helpers. It lets Ceph file code bracket buffered read, buffered write, and direct I/O sections without exposing the internal flag and locking implementation in `io.c`.

## Important APIs, types, and functions
The header declares `ceph_start_io_read`, `ceph_end_io_read`, `ceph_start_io_write`, `ceph_end_io_write`, `ceph_start_io_direct`, and `ceph_end_io_direct`. The start functions are annotated `__must_check`, which forces callers to handle lock-acquisition failures such as killable waits interrupted by signals.

## Control flow
There is no runtime control flow in the header. Its role is to define the compile-time contract: callers call a checked `ceph_start_io_*` function before entering the corresponding data path and call the matching `ceph_end_io_*` after the protected operation.

## State and persistence behavior
The header owns no state. It abstracts the in-memory I/O mode state maintained by `io.c` on `struct ceph_inode_info` and `inode->i_rwsem`.

## Dependencies and integration points
It includes `linux/compiler_attributes.h` for `__must_check` and relies on users having `struct inode` visible through the surrounding Ceph/VFS includes. It is included by `io.c` and Ceph file data-path code.

## Risks
The main risks are API misuse: ignoring a failed start call, mismatching direct/read/write end helpers, or entering data paths without the bracket. Since this header does not encode ownership types, correctness depends on call-site discipline and review.

## Test signals
Build warnings for ignored `__must_check` returns, static analysis for paired start/end calls, and runtime stress tests covering interrupted lock acquisition and all read/write/direct call paths are the best signals.
