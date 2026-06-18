## sources/distributed-fs/lizardfs/src/mount/polonaise/main.cc

Purpose: implements `lizardfs-polonaise-server`, a Thrift `Polonaise` service that maps remote Polonaise filesystem requests to `LizardClient` operations without using FUSE as the transport.

Important APIs/types: conversion helpers map errno to `StatusCode`, Thrift contexts to `LizardClient::Context`, Polonaise flags/modes/stat structs to Unix/LizardFS equivalents, and LizardFS replies back to Polonaise structs. `PolonaiseHandler` implements lookup/getattr/setattr/mknod/mkdir/opendir/readdir/releasedir/rmdir/access/create/open/read/write/fsync/flush/release/statfs/symlink/readlink/link/unlink/rename/xattr operations. `BigBufferedTransportFactory` supplies 512 KiB read and 4 KiB write buffers.

Control flow: `main` parses options, installs signal handlers, optionally daemonizes, initializes `LizardClient::fs_init` with master, cache, write-buffer, subfolder, password, and mode settings, then starts a threaded Thrift server on a TCP socket or Windows pipe. Each RPC uses `OPERATION_PROLOG/EPILOG` to translate LizardFS request exceptions into Polonaise statuses and conversion failures into Polonaise failures. Open/create allocate descriptors in a guarded map containing `LizardClient::FileInfo`; release/releasedir erase descriptors.

State and persistence: server state is in memory: global server pointer/termination flag, global setup, descriptor map, and the initialized LizardFS client state. It persists no files itself. Descriptor ids are monotonic per handler.

Dependencies and integration: depends on Thrift, generated Polonaise headers, Boost, `LizardClient`, read/write data initialization through `fs_init`, symlink cache, master communication, and platform stat definitions.

Risks: `toInt32` returns `uint32_t` despite documenting int32 conversion, though values are range checked. Descriptor insertion before successful create/open may leak descriptors if a later client call throws before return. `getFileInfo` returns a pointer after releasing the mutex, so concurrent release of the same descriptor can invalidate it in a threaded server. Write trusts the caller's `size` against `data.size()`. Unsupported or unknown errno values become Failure exceptions.

Test signals: needs integration tests with generated Polonaise clients for descriptor lifecycle, concurrent read/write/release, xattr two-step size queries, special inode reads, Windows pipe path, daemon signal shutdown, and error mapping.
