# sources/distributed-fs/ceph-client/include/net/handshake.h

Purpose: declares the kernel TLS handshake service interface, backed by generic netlink, for offloading handshake negotiation to a userspace agent while kernel sockets wait for completion.

Important APIs/types: `tls_done_func_t` is the async completion callback returning status and peer key serial. `struct tls_handshake_args` carries socket, callback, caller data, peer name, timeout, keyring, certificate/private-key serials, and up to five peer ids. Client and server entry points cover anonymous, X.509, and PSK modes: `tls_client_hello_*()` and `tls_server_hello_*()`. Lifecycle helpers include `tls_handshake_cancel()`, `tls_handshake_close()`, `tls_get_record_type()`, and `tls_alert_recv()`.

Control flow and state: a caller fills args, starts a handshake with allocation flags, and receives completion asynchronously. Cancellation is keyed by `struct sock`; close is keyed by `struct socket`. Record-type and alert helpers inspect ancillary data/messages after TLS is active.

Dependencies and integration: uses sockets, sock, msghdr/cmsghdr, key serials, GFP flags, and generic netlink service implementation. It is relevant to in-kernel consumers such as NFS/RPC-over-TLS and any distributed filesystem transport adopting kernel TLS.

Risks: async lifetime of socket and caller data must outlive completion or cancellation. Key serial zero has sentinel meanings. Tests should cover timeout, cancel vs completion races, missing keyring/certs, PSK and X.509 modes, close during pending handshake, alert parsing, and userspace agent failure.
