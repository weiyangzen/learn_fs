## sources/distributed-fs/ceph-client/fs/smb/server/transport_tcp.c

Purpose: implements ksmbd's TCP transport: interface-bound listener management, accept loops, per-client connection creation, socket read/write helpers, connection limits, and netdevice up/down reaction.

Important APIs and functions: exported functions include `ksmbd_tcp_init`, `ksmbd_tcp_destroy`, `ksmbd_tcp_set_interfaces`, and `ksmbd_find_netdev_name_iface_list`. Internal helpers allocate/free `tcp_transport`, create listener sockets, start/stop listener kthreads, accept clients, read exact byte ranges with retry behavior, send kvec responses, and disconnect transports. `struct interface` tracks a netdev name, listener socket/thread, list membership, and state.

Control flow: initialization registers a netdevice notifier. Startup configuration populates `iface_list`; if the daemon provided no list, future NETDEV_UP events bind additional interfaces. On NETDEV_UP, `create_socket` creates an IPv6 socket with IPv4 fallback, disables IPv6-only mode, enables nodelay/reuseaddr, tries `SO_BINDTODEVICE`, binds to `server_conf.tcp_port`, listens, and starts an accept thread. The accept loop enforces optional per-IP and global connection limits, sets socket timeouts, wraps accepted sockets in ksmbd transports, and starts a per-connection handler thread. Reads loop until the requested byte count is satisfied or connection/reconnect/retry limits terminate.

State and persistence behavior: runtime state includes `iface_list`, `bind_additional_ifaces`, listener socket/thread pointers, `active_num_conn`, per-transport cached iov arrays, and each connection's IPv4/IPv6 address hash in the global connection table. There is no persistent storage.

Dependencies and integration points: uses Linux kernel sockets, netdevice notifier API, freezer support, ksmbd connection allocation/handler loop, global connection list, server configuration from IPC startup, transport ops consumed by generic ksmbd I/O, and TCP timeout constants from connection/server headers.

Risks: netdevice event handling must avoid leaking sockets or stale interface entries on bind/listen/thread failures. Per-IP limiting scans the global connection hash and must release the just-accepted socket on rejection. `active_num_conn` is decremented only when max-connections accounting is enabled, so all failure/close paths must match that condition. `kvec_array_init` and cached iov resizing are sensitive to partial reads. `SO_BINDTODEVICE` tolerates `-ENODEV`, so unexpected interface names can still bind broadly depending on kernel behavior.

Test signals: IPv6 listener with IPv4 fallback, interface list and bind-additional modes, NETDEV_UP/DOWN cycles, port bind failures, global and per-IP connection limits, accepted connection thread failure unwind, socket read retry on `-EAGAIN/-ERESTARTSYS`, reconnect shutdown path, writev with `MSG_NOSIGNAL`, and destroy cleanup after active listeners.
