# sources/distributed-fs/ceph-client/fs/smb/server/mgmt/ksmbd_ida.h

Purpose: declares KSMBD IDA helper APIs and documents SMB2 TID/UID reserved-value rules.

Important APIs/types/functions: exposes `ksmbd_acquire_smb2_tid()`, `ksmbd_acquire_smb2_uid()`, `ksmbd_acquire_async_msg_id()`, `ksmbd_acquire_id()`, and `ksmbd_release_id()`. Comments cite SMB2 TID and UID constraints, especially reserved TID `0xFFFF` and UID `0xFFFE`.

Control flow: management code includes this header to allocate identifiers at object creation and release them at object destruction.

State and persistence behavior: the header owns no state. State lives in the caller-provided `struct ida`.

Dependencies and integration points: depends on Linux slab/IDR headers and integrates with user session, tree connect, and async work management.

Risks: callers must use the protocol-specific helper for protocol-visible IDs instead of the generic allocator, or reserved values may leak onto the wire.

Test signals: compile coverage and identifier allocation tests around reserved values, release/reuse, and exhaustion.
