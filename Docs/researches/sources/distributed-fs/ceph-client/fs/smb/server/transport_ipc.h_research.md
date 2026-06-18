## sources/distributed-fs/ceph-client/fs/smb/server/transport_ipc.h

Purpose: declares the kernel-to-userspace IPC API used by ksmbd authentication, share lookup, tree connect/disconnect, SPNEGO, RPC named pipe operations, and IPC lifecycle management.

Important APIs and types: defines `KSMBD_IPC_MAX_PAYLOAD` as 4096 and declares login, extended-login, tree-connect, tree-disconnect, logout, share-config, SPNEGO, RPC open/close/read/write/ioctl, IPC/RPC id allocation/free, release, soft-reset, and init functions. It forward-declares session/share/tree/socket types to keep consumers decoupled from implementation details.

Control flow: callers use request functions that either return daemon-allocated response payloads to be freed by the caller or integer status for fire-and-forget notifications. Init registers the netlink family; soft reset drops daemon association; release unregisters.

State and persistence behavior: the header owns no state. Implementation state is in `transport_ipc.c`; response payload ownership crosses this API boundary.

Dependencies and integration points: consumed by user/session/share management, SMB2 authentication/session setup, tree connect handling, named pipe/RPC handling, server startup/shutdown, and control reset paths.

Risks: callers must respect payload limits, validate NULL responses as daemon errors/timeouts, and free successful response buffers. RPC handle lifetime is split between generic IPC IDs and pipe/session code, so mismatched `ksmbd_ipc_id_alloc`/`ksmbd_rpc_id_free` can leak handles.

Test signals: build consumers with this header alone, NULL-response handling for every request API, oversize RPC/SPNEGO payload rejection, and init/soft-reset/release lifecycle tests.
