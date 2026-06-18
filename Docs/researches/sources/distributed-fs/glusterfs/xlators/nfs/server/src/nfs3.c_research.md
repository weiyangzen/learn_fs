# sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs3.c

## Purpose
Implements the GlusterFS NFSv3 RPC program. It translates NFSv3 RPC procedures into Gluster translator FOPs, manages per-request continuation state, resolves NFS file handles to Gluster `loc_t`/`inode_t` objects, serializes XDR replies, and initializes/reconfigures per-export NFSv3 runtime state.

## Important APIs, Types, and Functions
The file exports service setup and reconfiguration through `nfs3svc_init`, `nfs3_init_state`, `nfs3_reconfigure_state`, and option helpers such as `nfs3_init_options`, `nfs3_init_subvolume_options`, and `nfs3_iosize_roundup_4KB`. Export lookup helpers include `__nfs3_get_export_by_index`, `__nfs3_get_export_by_volumeid`, `__nfs3_get_export_by_exportid`, `nfs3_fh_to_xlator`, `nfs3_export_access`, `nfs3_export_sync_trusted`, and `nfs3_export_write_trusted`.

The main RPC handlers are the `nfs3svc_*` entry points for `NULL`, `GETATTR`, `SETATTR`, `LOOKUP`, `ACCESS`, `READLINK`, `READ`, `WRITE`, `CREATE`, `MKDIR`, `SYMLINK`, `MKNOD`, `REMOVE`, `RMDIR`, `RENAME`, `LINK`, `READDIR`, `READDIRPLUS`, `FSSTAT`, `FSINFO`, `PATHCONF`, and `COMMIT`. Each service wrapper decodes XDR arguments with `xdr_to_*`, calls the protocol-level `nfs3_*` function, and maps unrecoverable failures to RPC errors.

Per-request state is allocated by `nfs3_call_state_init` from `nfs3_state_t.localpool`, reference-counted with `GF_REF_*`, and released by `__nfs3_call_state_wipe`. Reply helpers include `nfs3_serialize_reply`, `nfs3svc_submit_reply`, `nfs3svc_submit_vector_reply`, and operation-specific `*_reply` functions that fill NFSv3 response structures using `nfs3_fill_*` helpers.

## Control Flow
The dominant control flow is decode, validate, resolve, dispatch, callback, reply. A service actor decodes the request into local stack buffers, validates the NFSv3 program state and file handle, maps the export ID to a child xlator, checks that the volume is started, and allocates `nfs3_call_state_t`. File-handle resolution is delegated to `nfs3_fh_resolve_and_resume`; the resume function performs operation-specific auth and resolve checks, starts the Gluster FOP, and the callback serializes the NFS reply and wipes the call state.

Read-only operations dispatch to `nfs_stat`, `nfs_lookup`, `nfs_access`, `nfs_readlink`, `nfs_read`, `nfs_readdirp`, `nfs_statfs`, or `nfs_fstat`. Mutating operations additionally check `nfs3_check_rw_volaccess`, then dispatch to `nfs_setattr`, `nfs_truncate`, `nfs_write`, `nfs_create`, `nfs_mkdir`, `nfs_symlink`, `nfs_mknod`, `nfs_unlink`, `nfs_rmdir`, `nfs_rename`, `nfs_link`, or `nfs_flush`. Multi-step operations keep intermediate `loc_t`, `iatt`, file-handle, pathname, or fd data in `nfs3_call_state_t`; examples include guarded `SETATTR`, exclusive `CREATE`, two-phase `RENAME`/`LINK`, and directory read plus `fstat`.

The RPC dispatch table `nfs3svc_actors` binds NFS procedure numbers to actors and duplicate-request-cache classes. `WRITE` uses `nfs3svc_write_vecsizer` so payload data can be received as a separate vector and then submitted with no-copy XDR reply behavior.

## State and Persistence Behavior
Process-lifetime state lives in `struct nfs3_state`: the NFS xlator pointer, iobuf pool, export list, per-request mempool, server start timestamp used as the write verifier, configurable read/write/readdir sizes, fd LRU bookkeeping, and occasional log counter. Per-export state lives in `struct nfs3_export`: child xlator, volume ID or indexed export identity, read-only/read-write access, trusted sync/write flags, and root lookup status.

Persistent storage is mostly delegated to Gluster FOPs and lower translators. NFSv3 itself remains mostly stateless, but it encodes protocol-visible persistence signals: the write verifier is `serverstart`, exclusive create verifiers are stored by mapping the cookie into atime/mtime before create/setattr, and readdir cookie validation uses helper state associated with directory fd/cookies. `trusted-sync` and `trusted-write` control whether COMMIT/WRITE can trust lower-layer durability rather than forcing flush semantics.

## Dependencies and Integration Points
This file sits between the RPC service layer (`rpcsvc`, `rpc_transport`, iobuf/iobref), NFSv3 XDR marshalling (`xdr-nfs3.h`, `xdr_serialize_*`, `xdr_to_*`), NFS helper logic (`nfs3-helpers`, `nfs3-fh`, `nfs-inodes`, `nfs-generics`, `nfs-fops`), mount/WebNFS helpers (`mount3`, `mnt3_parse_dir_exports`), Gluster translator APIs (`xlator_t`, `inode_t`, `fd_t`, `loc_t`, `dict_t`), ACL/NLM shared call-state fields, and global NFS configuration in `struct nfs_state`.

Notable integration behavior includes zero-length Solaris/WebNFS file-handle handling through `nfs3_funge_webnfs_zerolen_fh`, dynamic volume mode export IDs versus UUID volume IDs, volume start checks that disconnect pre-start clients, and option keys under `nfs3.*` and `nfs3.<volume>.*`.

## Risks and Edge Cases
The highest-risk paths are the async continuation paths where every error branch must send exactly one reply and release `nfs3_call_state_t` exactly once. Multi-step operations are sensitive to stale `loc_t` contents, saved pathname ownership, inode linking/unlinking, and callback ordering. Protocol risk also exists around exact NFSv3 status mapping, write-stability semantics, exclusive-create verifier storage in timestamps, directory cookie verification, and DRC classifications.

Other risks include stale file handles after export removal, DVM/index export mismatches, buffer-size rounding that changes advertised `FSINFO` limits, no-copy WRITE payload length handling, read-only export checks missed on mutation paths, and root lookup/self-heal generation logic producing surprising lookups or stale replies.

## Test Signals
Useful signals include NFSv3 connect/mount tests across multiple exports, GETATTR/LOOKUP self-heal and stale-handle cases, all mutation procedures on read-write and read-only exports, exclusive create retransmission behavior, WRITE/COMMIT with `trusted-sync` and `trusted-write` combinations, READDIR/READDIRPLUS cookie verifier tests, WebNFS zero-length-handle lookup, volume stop/start races that should disconnect clients, option reconfigure tests for IO sizes and per-volume access, and memory/refcount checks under failed FOP callbacks.
