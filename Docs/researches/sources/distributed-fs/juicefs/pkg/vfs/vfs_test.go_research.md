# sources/distributed-fs/juicefs/pkg/vfs/vfs_test.go

## Purpose
This test file validates the JuiceFS VFS operation surface against an in-memory object store and multiple metadata engines. It is not a mock-only unit suite; it builds a real `VFS` using `meta.NewClient`, `chunk.NewCachedStore`, a memory object backend, and a wrapped Prometheus registry, then exercises namespace, I/O, xattr, lock, internal-file, and readdir paths.

## Important APIs, Types, and Functions
`createTestVFS` is the shared fixture builder. It creates a metadata format, initializes the metadata client, constructs `Config`, creates a memory object store, wraps metrics labels, builds a cached chunk store, and returns `NewVFS`. Tests include `TestVFSBasic`, `TestVFSIO`, `TestVFSXattrs`, `TestAccessMode`, `TestSetattrStr`, `TestVFSLocks`, `TestInternalFile`, `TestHideInternal`, `TestReaddirCache`, `TestVFSReadDirSort`, `TestReadDirBatch`, and `TestReaddir`. Helper functions include `assertEqual`, `testReaddirCache`, `testVFSReadDirSort`, `testReaddirBatch`, and `testReaddir`.

## Control Flow and State
Each test creates files and directories through VFS calls and then observes metadata effects through lookups, attributes, reads, and errors. I/O tests write sparse and large ranges, force `Fsync` and `Flush`, read through holes and copied ranges, and manipulate handles to validate `EBADF` paths. The internal-file test reads generated `.config`, `.stats`, and `.accesslog` data, then writes structured control messages with binary command and size headers, polling for progress and response frames.

The readdir tests intentionally mutate directories between batched reads and offset updates to validate cache invalidation and deterministic pagination. Several tests run against `memkv://`, `sqlite3://:memory:`, and Redis URIs, so the suite is designed to reveal backend-specific directory iteration differences when those backends are available.

## Dependencies and Integration Points
The suite depends on `pkg/meta`, `pkg/chunk`, `pkg/object`, `pkg/utils`, Prometheus, `golang.org/x/sys/unix`, and `stretchr/testify/require`. It exercises integration between metadata, chunk storage, VFS handle management, xattr/ACL filtering, lock operations, internal control handlers, and metrics generation.

## Risks and Edge Cases
Some tests assume local services or optional drivers: Redis-backed cases can fail if Redis is unavailable, and SQLite behavior depends on build tags or driver availability elsewhere in the project. Timing-sensitive checks include background flush waits and lock wait timeouts. The tests directly mutate handle internals to force invalid states, which is useful for coverage but couples the suite to private implementation details.

## Test Signals
This file is itself the primary test signal for `vfs.go`, `vfs_unix.go`, and `writer.go`. It confirms expected errnos for long names, invalid fds, too-large offsets, read-only/write-only handles, internal nodes, malformed xattrs, unsupported ACL xattrs, lock conflicts, and malformed control messages.
