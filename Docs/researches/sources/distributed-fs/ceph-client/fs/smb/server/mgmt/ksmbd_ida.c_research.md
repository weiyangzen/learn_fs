# sources/distributed-fs/ceph-client/fs/smb/server/mgmt/ksmbd_ida.c

Purpose: wraps Linux IDA allocation for SMB-visible identifiers: tree IDs, user/session IDs, async message IDs, and generic internal IDs.

Important APIs/types/functions: `ksmbd_acquire_smb2_tid()` allocates SMB2 tree IDs from 1 through `0xFFFFFFFE`. `ksmbd_acquire_smb2_uid()` allocates SMB2 user/session IDs from 1 while avoiding reserved `0xFFFE`. `ksmbd_acquire_async_msg_id()` allocates async IDs from 1. `ksmbd_acquire_id()` and `ksmbd_release_id()` provide generic allocation/free wrappers.

Control flow: session and tree-connect management call these helpers during creation and release IDs during disconnect/session teardown. The UID helper retries if IDA returns the reserved LAN Manager value.

State and persistence behavior: ID state is stored in caller-owned `struct ida` instances, such as the global session IDA and per-session tree-connection IDAs. IDs are volatile and not persisted across server restart.

Dependencies and integration points: depends on Linux IDA and KSMBD allocation flags. It integrates with session creation, tree connect creation, async request handling, and RPC/IPC ID allocation wrappers elsewhere.

Risks: leaking IDs on error paths can exhaust per-session or global ID spaces. Returning `0xFFFE` handling in UID allocation retries once; callers still must handle negative allocation errors. TID allocation starts at 1 even though SMB2 permits zero, which is a deliberate compatibility choice that callers should not assume is exhaustive.

Test signals: repeated session/tree connect create/destroy, reserved UID avoidance, ID exhaustion/failure injection, async request ID release, and reconnect after many prior allocations.
