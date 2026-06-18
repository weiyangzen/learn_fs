# sources/distributed-fs/ceph-client/fs/smb/server/mgmt/tree_connect.h

Purpose: declares KSMBD tree-connection state, flags, status wrapper, and management APIs.

Important APIs/types/functions: enum values `TREE_NEW`, `TREE_CONNECTED`, and `TREE_DISCONNECTED` track tree lifecycle. `struct ksmbd_tree_connect` stores TID, flags, referenced share config, user pointer, list node, maximal access, POSIX extension state, refcount, and state. `struct ksmbd_tree_conn_status` returns both a status code and optional tree pointer from connect. `test_tree_conn_flag()` checks KSMBD tree flags. APIs cover connect, put, disconnect, lookup, and session logoff.

Control flow: SMB2 tree-connect code calls connect and later moves state to connected when the protocol response succeeds. Request handlers look up trees by TID, use share config and flags, then put references. Tree disconnect/logoff code removes objects.

State and persistence behavior: declared objects are runtime per-session state only. Share configuration is separately refcounted.

Dependencies and integration points: includes KSMBD netlink flag/status definitions and integrates with user session, share config, and protocol command handlers.

Risks: `user` is a raw pointer to the session user; tree lifetime must not outlive session destruction. `maximal_access` and `posix_extensions` must be initialized by protocol paths before use.

Test signals: state transitions, flag checks for guest/read-only/writeable/admin/update, POSIX extension behavior, maximal-access reporting, and refcounted lookup/put under disconnect.
