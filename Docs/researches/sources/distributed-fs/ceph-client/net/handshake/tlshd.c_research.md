<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/handshake/tlshd.c -->
# sources/distributed-fs/ceph-client/net/handshake/tlshd.c

## Purpose
Adapts the generic handshake framework to TLS sessions handled by the userspace `tlshd` agent for kernel socket consumers.

## APIs, Types, and Functions
Defines private `struct tls_handshake_req`, `tls_handshake_proto`, and exported public APIs `tls_client_hello_anon()`, `tls_client_hello_x509()`, `tls_client_hello_psk()`, `tls_server_hello_x509()`, `tls_server_hello_psk()`, `tls_handshake_cancel()`, and `tls_handshake_close()`. Helpers include `tls_handshake_req_init()`, `tls_handshake_remote_peerids()`, `tls_handshake_done()`, `tls_handshake_private_keyring()`, `tls_handshake_put_peer_identity()`, `tls_handshake_put_certificate()`, and `tls_handshake_accept()`.

## Control Flow, State, and Persistence
Each public client/server helper allocates a generic request, initializes common fields from `struct tls_handshake_args`, sets message type and auth mode, copies certificates, private keys, or peer IDs, and submits the request. ACCEPT optionally links a configured keyring into the process keyring, builds a netlink reply containing socket fd, message type, peername, timeout, keyring, auth mode, peer identities or certificate tuple, and replies to the accepting agent. DONE extracts up to five remote peer identity attributes, sets the session flag when status is zero, and calls the kernel consumer callback with `-status` and the first peer ID. `tls_handshake_close()` finds the request for a socket, clears the active session bit, and sends TLS close_notify. Persistent state is held in the outstanding request until socket destruction.

## Dependencies and Integration
Depends on the generic handshake framework, kTLS alert helper, generic-netlink attributes from the handshake UAPI, keyrings when `CONFIG_KEYS` is enabled, and public TLS handshake argument definitions.

## Risks and Test Signals
Risks include PSK peer ID array bounds, server PSK assuming at least one peer ID, keyring link side effects in the userspace agent process, status sign conversion, missing remote peer IDs, and close_notify only if the request still maps to the socket. Test signals include all five public handshake modes, ACCEPT payload per auth mode, keyring linking failures, DONE with multiple remote auth attributes, consumer callback status mapping, cancel, and close_notify after successful session.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/handshake/tlshd.c -->
