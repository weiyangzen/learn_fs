# sources/distributed-fs/ceph-client/fs/smb/server/connection.h

Purpose: defines the central KSMBD connection and transport abstractions plus status helpers and exported connection-management APIs.

Important APIs/types/functions: `enum KSMBD_SESS_*` status values describe connection negotiation/setup/good/reconnect/exiting/releasing states. `struct ksmbd_conn` aggregates dialect ops/values, transport pointer, address, request buffers, NLS/unicode state, session xarray, request/async queues, credit state, stats, client GUID, NTLMSSP/preauth/auth negotiation state, async IDA, cipher/compression/signing/multichannel flags, refcount, and release work. `struct ksmbd_conn_ops` provides protocol callbacks. `struct ksmbd_transport_ops` abstracts disconnect/shutdown/read/writev/RDMA/free operations. Inline helpers test and set connection status with `READ_ONCE`/`WRITE_ONCE`.

Control flow: transport code allocates a `ksmbd_conn`, attaches transport ops, and starts `ksmbd_conn_handler_loop()`. Protocol code uses the ops and status helpers during negotiate/session setup. Request code queues/dequeues work through the declared APIs and writes responses through the selected transport.

State and persistence behavior: all fields are volatile per-connection state. Session membership is per-connection in an xarray but can also be represented globally for multichannel. Refcounted final release is asynchronous via `release_work`.

Dependencies and integration points: includes SMB common definitions, KSMBD work state, Linux socket/network/kthread/NLS/unicode/workqueue headers, and transport-specific RDMA descriptor forward declarations. It is included broadly by server, transport, auth, session, and protocol handlers.

Risks: `status` is noted as a temporary multi-session hack, so code assuming per-session status can behave incorrectly under multichannel/reconnect. Transport ops must be complete for the selected transport; NULL RDMA ops are handled by wrappers but other ops are required. Consumers must hold appropriate locks around request lists, session xarrays, and global connection hash traversal.

Test signals: compile both IPv4/IPv6 and RDMA configs, exercise status transitions through negotiate/setup/reconnect/shutdown, test transport write/read wrappers, validate refcounting under async references, and inspect connection procfs output.
