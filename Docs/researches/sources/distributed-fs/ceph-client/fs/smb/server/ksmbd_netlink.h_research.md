# sources/distributed-fs/ceph-client/fs/smb/server/ksmbd_netlink.h

Purpose: defines the Generic Netlink userspace ABI between the KSMBD kernel server and the ksmbd userspace IPC daemon. It carries startup/shutdown configuration, heartbeat, login data, share configuration, tree connect authorization, RPC forwarding, Kerberos SPNEGO authentication, and user-extension payloads.

Important APIs/types/functions: ABI identifiers include `KSMBD_GENL_NAME` and `KSMBD_GENL_VERSION`. Packed request/response structs cover `ksmbd_heartbeat`, `ksmbd_startup_request`, `ksmbd_shutdown_request`, login request/response and extension, share config request/response, tree connect request/response/disconnect, logout, `ksmbd_rpc_command`, and SPNEGO auth request/response. `ksmbd_share_config_path()` locates the share path behind an optional veto list in a variable payload. `enum ksmbd_event` defines request/response event numbers. The header also defines global flags, user flags, share flags, tree-connect flags/statuses, RPC method/status flags, and config option values.

Control flow: kernel code sends a request event with a handle, userspace replies with the paired response event, and management/auth code converts the payload into runtime users, shares, sessions, or RPC results. Startup populates global server configuration. Login responses feed `ksmbd_user`. Share responses feed `ksmbd_share_config`. Tree connect responses authorize and flag `ksmbd_tree_connect`. Kerberos requests outsource SPNEGO validation and session key generation to userspace.

State and persistence behavior: this header owns no state, but it defines the ABI for state imported into the kernel. Userspace owns durable account/share configuration; kernel caches selected users, shares, sessions, tree connections, and RPC handles. Packed layouts and reserved fields preserve ABI compatibility.

Dependencies and integration points: depends on Linux integer types and Generic Netlink transport code elsewhere. It integrates with `transport_ipc.c`, `auth.c`, `mgmt/user_config.c`, `mgmt/share_config.c`, `mgmt/tree_connect.c`, `mgmt/user_session.c`, server startup/shutdown, and named-pipe RPC handling.

Risks: this is a stable ABI boundary. Changing struct layout, packing, event numbering, flag values, or payload ordering can break ksmbd-tools. Variable payload fields (`____payload`, veto list, path, group list, SPNEGO blobs) require strict length validation by consumers. User/group IDs and password hashes are trusted from userspace IPC, so daemon authentication and capability checks matter. Reserved fields should remain zero-compatible.

Test signals: netlink compatibility tests with current and older ksmbd-tools, startup config import, heartbeat timeout behavior, login success/failure/extension groups, share path plus veto list parsing, tree connect authorization flags, named-pipe RPC open/read/write/close, Kerberos SPNEGO exchange, and fuzzing of payload sizes and event types.
