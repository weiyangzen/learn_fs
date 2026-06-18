# sources/distributed-fs/openafs/src/afs/VNOPS/afs_vnop_open.c

## Purpose
Implements `afs_open`, the vnode open path for files, directories, symlinks, and mountpoint fakestat targets.

## Important APIs, Types, and Functions
`afs_open` creates a `vrequest`, resolves fakestat mountpoints with `afs_EvalFakeStat`, verifies status with `afs_VerifyVCache`, checks directory and NFS-translator access with `afs_AccessOK`, flushes text/pages for non-directories, updates open and writer counters, and optionally queues background prefetch with `afs_BQueue(BOP_FETCH)`.

## Control Flow and State
The function gets the current vcache from platform-specific arguments, enters the disconnected lock, evaluates fakestat, verifies cache status, rejects disconnected opens when chunks are missing, classifies write intent using `FWRITE` and `FTRUNC`, and applies directory-specific rules. Directories cannot be opened for write and require lookup or read access depending on `CForeign`. Regular files and symlinks have text and pages flushed before use. Truncating opens update the cached mtime and mark `CDirty`. Finally it increments `opens` and, for write opens, `execsOrWriters`; read opens can trigger a first-chunk asynchronous prefetch.

Mutates `tvc->opens`, `tvc->execsOrWriters`, `tvc->f.m.Date`, `CDirty`, and platform credential fields such as `tvc->cred` or `tvc->credp`. It may set `DFFetchReq` on a dcache entry and enqueue a background fetch. It does not persist file data to the server; later write, close, and fsync paths handle that.

## Dependencies and Integration Points
Integrates with fakestat helpers from lookup, disconnected-mode checks, dcache chunk presence checks, access cache logic, page/text flushing OS hooks, background daemon request queues, dcache locks, and platform vnode wrappers for SGI/Linux/FreeBSD/AIX behavior.

## Risks and Test Signals
The function relies on other vnode paths for permission checks before open, except for directory and NFS translator cases. Missing chunks during disconnected mode fail even for otherwise valid status. Open-truncate marks metadata dirty but does not itself store data. Background prefetch must correctly transfer the dcache reference to the daemon only when queued.

Test directory read/write opens, regular file read/write/truncate opens, mountpoints under fakestat, disconnected files with complete and missing chunks, NFS translator read access, first-chunk prefetch when daemons are idle, busy background queue fallback, and matching close counter decrements.
