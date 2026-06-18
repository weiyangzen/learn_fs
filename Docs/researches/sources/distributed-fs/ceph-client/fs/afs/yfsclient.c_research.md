# sources/distributed-fs/ceph-client/fs/afs/yfsclient.c

Purpose: Implements YFS fileserver RPC client stubs for data I/O, namespace changes, status, volume status, locks, bulk status, and opaque ACL operations.

Important APIs and functions: XDR helpers encode/decode YFS FIDs, strings, 64-bit values, times, store-status records, fetch-status records, callbacks, and volsync. Operation entry points include `yfs_fs_fetch_data()`, create/mkdir/remove/link/symlink/rename variants, `yfs_fs_store_data()`, `yfs_fs_setattr()`, `yfs_fs_get_volume_status()`, lock operations, `yfs_fs_fetch_status()`, `yfs_fs_inline_bulk_status()`, `yfs_fs_fetch_opaque_acl()`, and `yfs_fs_store_opaque_acl2()`.

Control flow: Each exported operation computes request/reply sizes, allocates a flat call, encodes opcode/RPC flags/FIDs/names/status payloads, checks request size with `yfs_check_req()`, tags `call->fid`, traces, and submits through `afs_make_op_call()`. Delivery functions either transfer a fixed reply or run `call->unmarshall` state machines for streamed data, volume strings, inline bulk arrays, and opaque ACLs.

State and persistence: Replies update `afs_operation` file slots with decoded status/callback data and `op->volsync`. Store and setattr calls persist server-side file data, length, mode, owner, group, and mtime. Rename/remove fallback bits (`AFS_SERVER_FL_NO_RM2`, `AFS_SERVER_FL_NO_RENAME2`) persist per server after opcode rejection.

Dependencies and integration points: Depends on YFS protocol definitions, AFS operation lifecycle, RxRPC flat calls, netfs subrequests for fetch data, vnode status commit by higher layers, lock completion callbacks, and xattr opaque ACL callers.

Risks: The file has many near-duplicate request-size calculations, making off-by-one padding and request overflow bugs high impact. Variable-length replies must cap counts and handle protocol errors. Fallback/downgrade flags affect later operations on the same server.

Test signals: Fetch short and overlong data, EOF flagging, create/remove status updates, RemoveFile2 and Rename2 downgrade on invalid opcode, setattr with and without size, lock completion, bulk-status count mismatch, opaque ACL partial requests, and negative YFS time conversion.
