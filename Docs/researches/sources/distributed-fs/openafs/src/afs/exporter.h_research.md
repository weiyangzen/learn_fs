# sources/distributed-fs/openafs/src/afs/exporter.h

Purpose: defines the cache-manager exporter abstraction, primarily for the NFS/AFS translator and remote-user request handling.

Important APIs/types: `struct exporterops` contains callbacks for request handling, hold/release, sysname lookup, garbage collection, stats, host validation, and host retrieval. `struct afs_exporter` stores linked-list state, ops, flags, type, stats, and private data. `struct exporterstats`, `struct afs3_fid`, and `struct Sfid` define accounting and exported file-handle layouts. Macros dispatch operation calls and define `EXP_NFS`, `EXP_EXPORTED`, `EXP_UNIXMODE`, `EXP_PWSYNC`, `EXP_SUBMOUNTS`, `EXP_CLIPAGS`, `EXP_CALLBACK`, `AFS_NFSFULLFID`, and `AFS_XLATOR_MAGIC`.

Control flow: compile-time data/dispatch layer. Runtime exporter implementations supply `exporterops`; callers use `EXP_*` macros to invoke them.

State and persistence: exporter instances hold in-memory reference and statistics state. File handle structs encode Cell/Volume/Vnode/Unique for cross-protocol identity but are not persistent storage by themselves.

Dependencies and integration points: ties into `nfsclient.h`, vcache NFS lookup, credential/PAG handling, `@sys` expansion, and platform NFS file-handle limits. `AFS_NFSXLATORREQ` detects translator credentials except on Darwin/XBSD where it is disabled.

Risks: `AFS_XLATOR_MAGIC` size differs on 64-bit kernels to fit NFS handle limits; changing layout can break file-handle compatibility. The first fields of `nfsclientpag` intentionally overlay `afs_exporter`, so struct layout is an ABI-like contract. Credential detection depends on group ID conventions.

Test signals: NFS translator mount/export operations, file-handle decode on 32-bit and 64-bit kernels, PAG/sysname handling, exporter refcount and GC paths, rejected remote-user calls, and host validation callbacks.
