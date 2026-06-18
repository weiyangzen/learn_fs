# sources/distributed-fs/ceph-client/fs/nfsd/nfsproc.c

Purpose: `nfsproc.c` implements NFS version 2 procedure handlers and the `svc_version` dispatch table for program version 2. It maps the old RFC 1094 procedure set to shared NFSD VFS, filehandle, and XDR helpers. The source was read as a complete 850-line file.

Important APIs/types/functions: handlers include `nfsd_proc_null`, `nfsd_proc_getattr`, `nfsd_proc_setattr`, `nfsd_proc_root`, `nfsd_proc_lookup`, `nfsd_proc_readlink`, `nfsd_proc_read`, `nfsd_proc_writecache`, `nfsd_proc_write`, `nfsd_proc_create`, `nfsd_proc_remove`, `nfsd_proc_rename`, `nfsd_proc_link`, `nfsd_proc_symlink`, `nfsd_proc_mkdir`, `nfsd_proc_rmdir`, `nfsd_proc_readdir`, and `nfsd_proc_statfs`. `nfsd_map_status` converts newer/internal status values into NFSv2-compatible errors. `nfsd_procedures2` is the procedure metadata table, and `nfsd_version2` publishes it to SunRPC.

Control flow: SunRPC dispatch decodes arguments using the table's `pc_decode`, calls the handler, then encodes via `pc_encode`. Each handler validates filehandles with `fh_verify` or delegates to shared VFS functions such as `nfsd_lookup`, `nfsd_read`, `nfsd_write`, `nfsd_create`, `nfsd_unlink`, `nfsd_rename`, `nfsd_link`, `nfsd_symlink`, `nfsd_readdir`, and `nfsd_statfs`. Create has extra legacy semantics: it locks the parent during lookup/create, overloads `ATTR_SIZE` for device numbers, handles existing regular files as truncate-on-create, and treats some special-file creates as permission checks. All statuses are normalized through `nfsd_map_status`.

State and persistence: this file owns no persistent storage. It manages per-request `svc_fh` references, result buffers, pages for read/readlink/readdir payloads, and duplicate-reply-cache policy through `pc_cachetype` in the procedure table. Non-idempotent operations use reply caching (`RC_REPLBUFF` or `RC_REPLSTAT`) to satisfy retransmits consistently.

Dependencies and integration points: integrates `cache.h`, `xdr.h`, `vfs.h`, `trace.h`, filehandle validation, SunRPC service dispatch, NFSv2 XDR encode/decode functions, and shared VFS operation implementations. It is selected by `nfssvc.c` when NFSv2 is compiled and enabled.

Risks: NFSv2 lacks modern error granularity, so status mapping can hide important server-side distinctions. The overloaded CREATE path is compatibility-heavy and sensitive to special-file and mode interpretation. Handlers must balance `fh_put` exactly as indicated by comments and table release callbacks. Read/write paths mark `RQ_DROPME` on jukebox/delay-like errors.

Test signals: NFSv2 connectathon/pynfs-style procedure tests, retransmit duplicate-reply-cache tests for non-idempotent ops, create/truncate/special-file compatibility cases, symlink target length and multi-page payload tests, readdir cookie/toosmall behavior, error mapping checks, and filehandle release leak detection under failure paths.
