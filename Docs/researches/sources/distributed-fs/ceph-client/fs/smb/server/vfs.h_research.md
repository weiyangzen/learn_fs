## sources/distributed-fs/ceph-client/fs/smb/server/vfs.h

Purpose: declares the ksmbd VFS abstraction used by SMB command handlers and defines helper structures for directory enumeration, stat conversion, and stream typing.

Important APIs and types: defines stream type constants `DATA_STREAM` and `DIR_STREAM`, create-option helper flags, `struct ksmbd_dir_info`, `struct ksmbd_readdir_data`, and `struct ksmbd_kstat`. It declares VFS helpers for create/mkdir/read/write/fsync/remove/link/getattr/rename/truncate/copychunk, xattr and stream names, path lookup/create/remove, fadvise, zero data, allocated ranges, unlink, stat formatting, lock wait/unblock, ACL/SD/DOS xattrs, and POSIX ACL initialization/inheritance.

Control flow: SMB2 command handlers populate work/file/path structures, call these helpers for filesystem operations, and translate returned Linux errors to SMB status. Directory query code uses `ksmbd_dir_info` and `ksmbd_readdir_data` to track output cursor state and fill callbacks.

State and persistence behavior: structures hold per-request and per-open enumeration state. Persistent filesystem changes are performed by implementation functions in `vfs.c`.

Dependencies and integration points: includes Linux file/fs/namei/xattr/POSIX ACL/unicode headers plus ksmbd ACL and xattr definitions. It is the main contract between SMB PDU handlers, ACL handling, file-cache lifetime, and VFS persistence.

Risks: many APIs require paired cleanup (`ksmbd_vfs_kern_path_start_removing` with `ksmbd_vfs_kern_path_end_removing`, xattr buffers freed by callers, file references put elsewhere). Misusing idmapped mount arguments can apply permissions or ACLs under the wrong id view. Directory info buffer fields are mutable cursors and must be initialized per query.

Test signals: compile coverage for all SMB2 handlers, path-start/end pairing, xattr buffer ownership, directory enumeration cursor behavior, idmapped mount operations, and error translation for every declared VFS helper.
