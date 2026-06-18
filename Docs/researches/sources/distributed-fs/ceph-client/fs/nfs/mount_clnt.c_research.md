# sources/distributed-fs/ceph-client/fs/nfs/mount_clnt.c

## Purpose
`mount_clnt.c` is the in-kernel client for the auxiliary MOUNT protocol used by NFSv2 and NFSv3 mounts. It contacts mountd, sends an export path, receives the root filehandle, decodes server-supported authentication flavors for MOUNTv3, and normalizes MOUNT protocol status codes to Linux errno values.

## Important APIs, Types, And Functions
The public entry point is `nfs_mount(struct nfs_mount_request *info, int timeo, int retrans)`. It validates path length, builds an `rpc_create_args` for program `NFS_MNT_PROGRAM`, initializes timeout values, optionally uses a non-privileged source port, selects either `MOUNTPROC_MNT` or `MOUNTPROC3_MNT`, performs a soft synchronous RPC, and fills `info->fh` plus auth flavor output arrays.

Private helpers encode the directory path (`encode_mntdirpath()`, `mnt_xdr_enc_dirpath()`), decode MOUNTv1 status and filehandles (`decode_status()`, `decode_fhandle()`, `mnt_xdr_dec_mountres()`), and decode MOUNTv3 status, variable-length filehandles, and auth flavors (`decode_fhs_status()`, `decode_fhandle3()`, `decode_auth_flavors()`, `mnt_xdr_dec_mountres3()`). Procedure tables `mnt_procedures` and `mnt3_procedures` drive SunRPC dispatch.

## Control Flow And Integration Points
Mount setup code passes an `nfs_mount_request` from `internal.h`. `nfs_mount()` creates a temporary RPC client, makes exactly one mount call using caller-provided retry policy, shuts down the client, and returns either a populated filehandle or errno. If a MOUNTv3 server returns no auth flavor list, or if using older MOUNT protocol, the code fakes a permissive one-entry list with `RPC_AUTH_NULL`, allowing later NFS security negotiation to continue.

## State And Persistence Behavior
The file itself keeps only static RPC metadata and per-procedure counters. Runtime state is transient: a temporary mount RPC client, stack `struct mountres`, caller-owned filehandle, and caller-owned auth flavor arrays. The resulting filehandle becomes persistent mount state outside this file.

## Dependencies
Dependencies include SunRPC client creation/call/shutdown, XDR stream helpers, kernel socket address structures, `nfs_init_timeout_values()`, `NFS_MAX_SECFLAVORS`, `NFS2_FHSIZE`, `NFS3_FHSIZE`, and mount protocol constants.

## Risks And Edge Cases
Path length is capped at `MNTPATHLEN` before RPC. Unknown status values map to `-EACCES`, which is conservative but may hide server-specific details. MOUNTv3 filehandles with size zero or too large are rejected and translated to `-EBADHANDLE` through `res->errno`. Auth flavor decoding caps the server-provided list to `NFS_MAX_SECFLAVORS` and the caller-provided buffer; callers must initialize `auth_flav_len` correctly.

## Test Signals
Exercise NFSv2 and NFSv3 mounts, long export paths, servers returning no auth flavors, more auth flavors than the cap, malformed or zero-length handles, `noresvport`, TCP/UDP timeout parameters, and mountd errors such as access denied, not directory, unsupported, and stale export paths.
