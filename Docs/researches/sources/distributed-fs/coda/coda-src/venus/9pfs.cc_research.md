# sources/distributed-fs/coda/coda-src/venus/9pfs.cc

## Purpose
This file implements the Venus 9P server. It parses 9P2000, 9P2000.u, and 9P2000.L messages from a `mariner` connection, maps fids to Venus cnodes and attachments, invokes Venus VFS-style operations, and serializes protocol responses.

## Important APIs, Types, and Functions
Static pack/unpack helpers encode little-endian integers, strings, qids, legacy stats, dotl stats, statfs data, and directory entries with strict buffer accounting. `attachment` stores a mount root, user/aname strings, uid, and refcount. `fidmap` maps a client fid to a cnode, open flags, and root attachment. `plan9server` implements request dispatch plus handlers for version, attach, walk, open/create/read/write/clunk/remove/stat/wstat and dotl operations including getattr, setattr, lopen, lcreate, symlink, mkdir, readdir, readlink, statfs, fsync, unlinkat, link, rename, and renameat. Unsupported mknod/xattr/locking handlers consume request fields and return `ENOTSUP`.

## Control Flow
`main_loop()` processes an optional initial magic buffer, then repeatedly reads a 9P header and calls `handle_request()`. `handle_request()` validates message size, reads the remainder, initializes the mariner user context, and dispatches by opcode. Most handlers unpack request fields, look up fids, set `conn->u.u_uid` from the attachment, call a Venus operation, translate `conn->u.u_error` into protocol errors, and pack a response into the fixed server buffer.

## State and Persistence Behavior
Persistent filesystem changes are delegated to Venus operations: create, remove, rename, link, mkdir, rmdir, symlink, setattr, write, and local cache file IO. The file's own state is transient protocol state: negotiated `max_msize`, protocol variant, fid list, open flags, and attachment refcounts. `del_fid()` closes open cnodes and frees attachment user strings when the last fid disappears. `fidmap_replace_cfid()` updates active fids when temporary local Venus Fids are replaced by server Fids.

## Dependencies and Integration Points
It depends on `mariner`, `fsobj`/`FSDB`, Venus cnodes, `vproc`-style file operations, directory enumeration, `VenusRetStr`, `SpookyHash` for qid paths, and worker downcalls that repair fid mappings. `mariner.cc` enables this server after detecting a 9P version request, and `worker.cc` calls `fidmap_replace_cfid`.

## Risks and Test Signals
Risks include memory leaks on error paths, incorrect dotl response opcodes, use-after-yield when operations drop fids, missing write-back semantics after raw `pwrite`, hard-coded `P9_BUFSIZE`, incomplete fsync, unsupported flags, and directory offset handling. Tests should mount through 9P in all three protocol variants, exercise fid reuse, clunk/remove semantics, symlink/hardlink/rename paths, large messages, partial readdir offsets, disconnected writes, temporary Fid replacement, and unsupported dotl operations.
