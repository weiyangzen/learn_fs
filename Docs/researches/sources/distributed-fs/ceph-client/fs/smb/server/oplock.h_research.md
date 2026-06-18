# sources/distributed-fs/ceph-client/fs/smb/server/oplock.h

## Purpose
Declares ksmbd oplock, lease, durable handle, and create-context helpers. It defines the shared state structures used by `oplock.c` and consumers in SMB2 create/open, close, write/truncate, lease break, and durable reconnect handling.

## Important APIs, Types, and Functions
- Constants define `OPLOCK_WAIT_TIME`, internal opinfo states (`OPLOCK_STATE_NONE`, `OPLOCK_ACK_WAIT`, `OPLOCK_CLOSING`), and transition reason bits.
- `struct lease_ctx_info` captures parsed request lease context, including lease key, requested state, flags, duration, parent key, epoch, version, and directory indicator.
- `struct lease_table` groups leases by client GUID and owns an RCU traversed `lease_list` plus spinlock.
- `struct lease` stores active lease key/state/new_state/flags/duration/parent key/version/epoch/dir flag/table pointer.
- `struct oplock_info` is the central open-file cache state: connection, session, triggering work, file pointer, level, state, pending break bit, FID/TID, break counters/refcount, lease flag, truncation flag, lease pointer, inode/global list entries, wait queues, and RCU head.
- Break message structs `lease_break_info` and `oplock_break_info` carry notification payload state.
- Public functions cover grant/break/close/refcount, lease parsing/mapping/buffer creation, durable response buffers, create context lookup, lease lookup, parent lease breaks, and durable oplock reconnect validation.

## Control Flow
SMB2 create/open code parses lease contexts into `lease_ctx_info`, calls `smb_grant_oplock()`, and uses response buffer creators to include granted lease/durable/POSIX/max-access/disk-id contexts. Write/truncate paths call break helpers. Close paths call `close_id_del_oplock()`. Lease break ack paths use `lookup_lease_in_table()` and transition helpers. Durable reconnect code calls `smb2_check_durable_oplock()`.

## State and Persistence
The structures describe in-memory cache-coherency state for open files. State is tied to kernel objects and protected with locks/RCU/atomics initialized in `oplock.c`. Durable handle metadata is represented indirectly through `ksmbd_file`; this header only exposes helper functions for response creation and validation.

## Dependencies and Integration Points
The header depends on `smb_common.h` for SMB2 constants and forward declarations from other ksmbd headers included by implementation files. It is part of the contract among `smb2pdu.c`, VFS file objects, connection/session management, and create-context response assembly.

## Risks and Edge Cases
- Many fields are binary buffers and little-endian values; callers must not treat them as native-endian or NUL-terminated strings.
- Public transition helpers assume the supplied opinfo is referenced and in a compatible current state.
- `oplock_info` exposes many mutable fields, so external code must preserve locking discipline defined by `oplock.c`.
- `oplock_break_info::fid` is `int` while public grant APIs and file ids use `u64`; truncation risk depends on actual FID ranges and implementation casts.

## Test Signals
Compile users for type/endianness correctness; run create/open, break, close, lease ack, durable reconnect, and create-context tests described for `oplock.c`; and use lockdep/KCSAN to verify external callers follow expected lock and lifetime rules.
