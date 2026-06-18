# sources/distributed-fs/ceph-client/fs/smb/server/oplock.c

## Purpose
Implements ksmbd SMB2 oplock and lease management. It grants requested oplocks/leases during create/open, tracks per-inode and per-client lease state, sends server-initiated oplock/lease break notifications, waits for acknowledgements, handles parent directory lease breaks, emits create-context response buffers, and validates durable handle reconnect oplock/lease requirements.

## Important APIs, Types, and Functions
- Global state: `lease_table_list` groups active leases by client GUID; `lease_list_lock` protects that list. Per-inode lists live in `ksmbd_inode::m_op_list` and are protected by `m_lock`.
- Allocation/lifetime helpers: `alloc_opinfo()`, `alloc_lease()`, `alloc_lease_table()`, `opinfo_get()`, `opinfo_get_list()`, `opinfo_put()`, `opinfo_add()`, `opinfo_del()`, `free_opinfo()` and RCU callback cleanup manage `struct oplock_info` references and publication through `fp->f_opinfo`.
- State transition APIs exported through the header: `opinfo_write_to_read()`, `opinfo_read_handle_to_read()`, `opinfo_write_to_none()`, `opinfo_read_to_none()`, and `lease_read_to_write()`.
- Grant helpers `grant_write_oplock()`, `grant_read_oplock()`, `grant_none_oplock()`, `set_oplock_level()`, and the public `smb_grant_oplock()` implement open-time policy.
- Break helpers `oplock_break_pending()`, `oplock_break()`, `smb2_oplock_break_noti()`, `smb2_lease_break_noti()`, `smb_break_all_write_oplock()`, `smb_break_all_levII_oplock()`, and `smb_break_all_oplock()` coordinate notifications and wait states.
- Lease table helpers `same_client_has_lease()`, `find_same_lease_key()`, `lookup_lease_in_table()`, `destroy_lease_table()`, `copy_lease()`, and `add_lease_global_list()` handle lease identity and global lookup by client GUID/lease key.
- Parent lease helpers `smb_send_parent_lease_break_noti()` and `smb_lazy_parent_lease_break_close()` implement SMB2.1/3 directory lease invalidation.
- Create-context helpers `create_lease_buf()`, `parse_lease_state()`, `smb2_find_context_vals()`, `create_durable_rsp_buf()`, `create_durable_v2_rsp_buf()`, `create_mxac_rsp_buf()`, `create_disk_id_rsp_buf()`, and `create_posix_rsp_buf()` parse request contexts and build response contexts.
- `smb2_map_lease_to_oplock()` maps SMB2 lease state bits to legacy oplock levels.
- `smb2_check_durable_oplock()` validates durable reconnect owner, GUID, lease key, handle caching state, lease version, and reconnect name.

## Control Flow
During open, SMB2 create handling parses lease context with `parse_lease_state()`, checks lease-key reuse with `find_same_lease_key()`, then calls `smb_grant_oplock()`. `smb_grant_oplock()` rejects unsupported directory lease cases, allocates an `oplock_info`, optionally attaches a `lease`, handles same-client lease upgrade/copy, finds existing inode oplocks, breaks conflicting batch/exclusive holders to level II when needed, downgrades the new request for stacked lease/oplock cases, sets final level, preallocates a lease table if required, publishes `o_fp`, increments inode oplock count, links the opinfo to inode and global lease lists, and RCU-publishes it in the file.

Break flow uses `pending_break` as a bit lock, sets `op_state` to `OPLOCK_ACK_WAIT` for ack-required transitions, sends an async SMB2 OPLOCK_BREAK response through a temporary `ksmbd_work`, optionally sends interim `STATUS_PENDING` on the triggering request, waits up to `OPLOCK_WAIT_TIME`, and force-downgrades to none on timeout. Lease break state chooses new state based on write/handle/read bits and truncation. Close flow calls `close_id_del_oplock()`, unlinks lease/inode list entries, clears `fp->f_opinfo`, wakes waiters if an ack was pending, decrements counts, and drops references.

Create-context parsing walks the SMB2 create context chain validated earlier by `ksmbd_smb2_check_message()`, enforcing alignment, name offset, data offset, and bounds. Response helpers fill SMB2 create context structures with offsets, lengths, names, and data for leases, durable handles, maximal access, disk id, and POSIX metadata.

## State and Persistence
Oplock and lease state is in memory, tied to open files, inodes, connections, sessions, and client GUIDs. `struct lease` persists requested/current/new lease states, flags, duration, parent key, version, and epoch while the file is open. Durable handles can outlive a transient connection elsewhere, but this file only validates reconnect state and emits durable response contexts; it does not persist handles itself. Synchronization uses inode rwsems, global rwlock, per-table spinlocks, RCU, wait queues, atomics, and bit waits.

## Dependencies and Integration Points
The file depends on SMB2 PDU structures/status constants, connection/session/share/tree management, global file lookup, VFS durable owner/name checks, inode cache objects, workqueue response writing, and SID/id conversion for POSIX create contexts. It is called heavily from `smb2pdu.c` create/open, write/truncate, close, lease break ack, and durable reconnect paths. Share flag `KSMBD_SHARE_FLAG_OPLOCKS` controls whether breaks are sent.

## Risks and Edge Cases
- This is concurrency-sensitive code: RCU publication, list traversal, atomic refcounts, wait queues, and lock nesting must remain consistent to avoid use-after-free, missed wakeups, or deadlocks.
- `oplock_break()` increments `breaking_cnt` before `oplock_break_pending()`; early error paths must ensure the counter is decremented or waiters can stall.
- Break notification work uses `work->request_buf` to carry allocated break info; cleanup depends on `ksmbd_free_work_struct()` freeing request buffers correctly.
- `smb2_find_context_vals()` assumes `CreateContextsOffset/Length` were validated by `ksmbd_smb2_check_message()`; direct callers on unchecked buffers would be unsafe.
- `create_durable_v2_rsp_buf()` casts to `create_durable_rsp_v2` but zeros only `sizeof(struct create_durable_rsp)`, which may leave v2 fields uninitialized if the v2 structure is larger.
- Lease/oplock level comparisons mix SMB2 lease bitfields and oplock constants in some conditions; tests must catch incorrect downgrade decisions.
- Timeout-driven forced downgrade can preserve server progress but risks client cache incoherency if a client later sends a stale ack.

## Test Signals
Exercise single open grants for none/II/exclusive/batch and lease R/RH/RWH; conflicting opens requiring batch/exclusive break to II; write/truncate break to none; same-client lease upgrades and break-in-progress flags; duplicate lease key on different files; parent directory lease breaks; close during pending break; break timeout; durable reconnect success/failure for owner, GUID, lease key, handle caching, version, and renamed/deleted files; malformed create contexts with bad alignment/offset/length; and KASAN/KCSAN stress with concurrent open/close/break/disconnect.
