# sources/distributed-fs/ceph-client/fs/nfs/callback.h

## Purpose
This header defines the NFSv4 callback ABI used between callback XDR decoding, callback procedure handlers, and the callback service. It provides procedure numbers, buffer sizing, compound state, operation argument/result structures, and callback function prototypes.

## Important APIs, types, and functions
Core definitions include `NFS4_CALLBACK`, `NFS4_CALLBACK_XDRSIZE`, `NFS4_CALLBACK_BUFSIZE`, `enum nfs4_callback_procnum`, and `struct cb_process_state`. Operation structures cover `CB_GETATTR`, `CB_RECALL`, `CB_SEQUENCE`, `CB_RECALL_ANY`, `CB_RECALL_SLOT`, `CB_LAYOUTRECALL`, `CB_NOTIFY_DEVICEID`, `CB_NOTIFY_LOCK`, and optional v4.2 `CB_OFFLOAD`.

The header declares procedure handlers such as `nfs4_callback_getattr()`, `nfs4_callback_recall()`, `nfs4_callback_sequence()`, `nfs4_callback_layoutrecall()`, `nfs4_callback_devicenotify()`, and service lifecycle functions `nfs_callback_up()`/`nfs_callback_down()`.

## Control flow
The structures here are populated by `callback_xdr.c`, consumed by `callback_proc.c`, and referenced by `callback.c` service setup. `cb_process_state` is the per-compound carrier for the matched `nfs_client`, backchannel slot, network namespace, minor version, duplicate-reply-cache status, and referring-call count.

## State and persistence behavior
The header defines transient RPC argument/result and per-compound state only. Constants such as callback slot limits shape runtime session/backchannel behavior but do not persist.

## Dependencies and integration points
It depends on SUNRPC svc types and NFS/pNFS state types pulled indirectly through NFS headers. It is the shared contract among callback service, XDR, procedure, delegation, pNFS, and NFSv4.2 copy-offload code.

## Risks and test signals
Risks are ABI drift between decode structures and procedure handlers, incorrect callback buffer sizing, and conditional compilation mismatches for v4.2 offload. Compile-time coverage across `CONFIG_NFS_V4` and `CONFIG_NFS_V4_2` plus callback operation interoperability tests are the primary signals.
