# sources/distributed-fs/ceph-client/include/uapi/linux/tipc_sockets_diag.h

Purpose: Defines the AF_TIPC socket diagnostic request structure used with Linux sock_diag to query open TIPC sockets.

Important APIs/types/functions: `struct tipc_sock_diag_req` contains `sdiag_family` (must be `AF_TIPC`), `sdiag_protocol` (must be zero), zero padding, and `tidiag_states` to filter queried socket states.

Control flow: Userspace submits this request to the sock_diag netlink interface. The kernel filters TIPC sockets by requested states and emits diagnostic socket records through the common sock_diag path.

State and persistence behavior: The structure observes transient kernel socket state only. It does not configure or persist anything.

Dependencies and integration points: Includes `linux/types.h` and `linux/sock_diag.h`; integrates with AF_TIPC, netlink sock_diag, and diagnostic tools such as `ss`.

Risks: The ABI depends on strict zeroing of protocol and padding. Mismatched family or stale state masks should fail or return no results predictably.

Test signals: Exercise sock_diag TIPC dumps for empty and active sockets, all state masks, nonzero padding/protocol rejection, and 32/64-bit userspace compatibility.
