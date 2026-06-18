## sources/distributed-fs/ceph-client/fs/smb/server/vfs_cache.h

Purpose: defines ksmbd's core open-file and inode cache data structures and declares file-table, durable-handle, lookup, close, delete-on-close, and cache lifecycle APIs.

Important APIs and types: defines Windows generic access constants, FID sentinel values, `struct ksmbd_lock`, `struct stream`, `struct ksmbd_inode`, fp states (`FP_NEW`, `FP_INITED`, `FP_CLOSED`), `struct durable_owner`, `struct ksmbd_file`, `struct ksmbd_file_table`, `has_file_id`, `ksmbd_stream_fd`, and all open/close/lookup/durable/scavenger/file-cache/inode-status declarations. `struct ksmbd_file` carries filp, volatile/persistent ids, access/share/create options, timestamps, stream state, lock/oplock linkage, durable flags, owner identity, connection/tcon pointers, and readdir state.

Control flow: SMB command handlers use lookup helpers to pin an fp, operate through VFS/oplock/lock paths, and release with `ksmbd_fd_put`. Create paths allocate with `ksmbd_open_fd`, populate metadata, and publish via `ksmbd_update_fstate`. Close, tree/session teardown, and durable reconnect use the declared close and reopen helpers.

State and persistence behavior: structures are runtime state, but `ksmbd_inode` flags drive persistent delete-on-close effects in the implementation. `stream.name` maps an open to xattr-backed alternate data streams. Durable owner fields persist identity across a disconnected handle's in-memory lifetime only.

Dependencies and integration points: includes Linux file/fs/rwsem/spinlock/idr/workqueue plus ksmbd VFS and share config headers. It is shared by SMB2 create/close/read/write/ioctl/query-directory, oplock/lease code, byte-range lock handling, tree/session management, and VFS helpers.

Risks: consumers must respect fp state and reference rules. `has_file_id` treats ids below `INT_MAX` as valid; SMB2 all-ones ids are invalid. `ksmbd_stream_fd` is a simple name check, so stream metadata must be initialized atomically with open setup. `ksmbd_file` mixes RCU, spinlock, rwsem, list, and atomic fields, making lock ordering important.

Test signals: compile across all users, open/close reference pairing, stream fd detection, compound fid fallback, delete-on-close flags, durable owner compare, id sentinel handling, and lockdep coverage for inode/file-table locks.
