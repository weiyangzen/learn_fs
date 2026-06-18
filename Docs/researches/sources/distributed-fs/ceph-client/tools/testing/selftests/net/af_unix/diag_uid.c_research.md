# sources/distributed-fs/ceph-client/tools/testing/selftests/net/af_unix/diag_uid.c

Purpose: Verifies that UNIX socket diagnostic netlink reports the owning UID for a selected AF_UNIX socket, both in the current user namespace and after `CLONE_NEWUSER`.

Important APIs/types/functions: Uses `NETLINK_SOCK_DIAG`, `SOCK_DIAG_BY_FAMILY`, `struct unix_diag_req`, `UNIX_DIAG_UID`, `SO_COOKIE`, `fstat()` inode lookup, and kselftest fixtures. Core helpers are `send_request()`, `receive_response()`, and `render_response()`.

Control flow: Fixture optionally unshares a user namespace, creates a netlink diagnostic socket and an AF_UNIX stream socket, records the socket inode and cookie, sends a targeted UNIX diag request with `UDIAG_SHOW_UID`, then receives one response and validates the UID attribute equals `getuid()`.

State and persistence behavior: State is limited to two file descriptors plus socket inode/cookie identifiers. It does not persist files or namespace state beyond process lifetime.

Dependencies and integration points: Requires `CONFIG_UNIX_DIAG`, AF_UNIX sockets, sock_diag netlink, and permission to unshare a user namespace for the second variant.

Risks: User namespace restrictions can make the unshare variant fail on hardened systems. The response parser assumes the first returned attribute is `UNIX_DIAG_UID` and only one matching message is returned.

Test signals: Passing output confirms UID rendering through UNIX diag and correct UID mapping after user namespace unshare.
