# sources/distributed-fs/ceph-client/fs/smb/server/mgmt/tree_connect.c

Purpose: manages SMB tree connections that bind an authenticated session to a configured share, including userspace authorization, per-session xarray registration, lookup, disconnect, and session logoff cleanup.

Important APIs/types/functions: `ksmbd_tree_conn_connect()` creates a tree connection. `ksmbd_tree_conn_lookup()` returns a referenced connected tree by ID. `ksmbd_tree_conn_disconnect()` removes one tree connection. `ksmbd_tree_conn_session_logoff()` disconnects all trees for a session. `ksmbd_tree_connect_put()` drops a reference. Internal `__ksmbd_tree_conn_disconnect()` sends the IPC disconnect and releases IDs/counters.

Control flow: connect obtains the share config, allocates a tree object, allocates a TID from the session, sends a userspace tree-connect request with session/share/peer data, checks the returned status, optionally refreshes stale share config when the update flag is set, initializes flags/user/share/state/refcount, stores the object in `sess->tree_conns`, and increments the tree counter. Disconnect erases the tree from the session xarray, sends userspace disconnect, releases the TID, decrements counters, drops share refs, and frees on final ref. Lookup only returns trees in `TREE_CONNECTED` state and increments the refcount.

State and persistence behavior: tree connections are per-session runtime objects stored in `sess->tree_conns` under `tree_conns_lock`. They hold a referenced share config and user pointer. Userspace receives connect/disconnect notifications but durable state remains outside this file.

Dependencies and integration points: depends on IPC transport, connection peer address, user session state, share config cache, IDA helpers, xarray, and KSMBD stats counters. Protocol handlers use tree lookup for TID validation before VFS operations.

Risks: tree state transitions must align with SMB2 TREE_CONNECT/TREE_DISCONNECT and session logoff; lookups deliberately reject non-connected states. Error paths must release TIDs and share refs. Share update handling deletes stale cache entries while active references may exist, so refcounts must be correct. Session logoff iterates while erasing xarray entries and must avoid double-disconnect.

Test signals: successful and failed tree connects, host denied/no share/no user statuses, stale share update flag, lookup before and after marking connected/disconnected, disconnect notification to userspace, logoff with multiple shares, concurrent file operations holding tree refs, and stats counter balance.
