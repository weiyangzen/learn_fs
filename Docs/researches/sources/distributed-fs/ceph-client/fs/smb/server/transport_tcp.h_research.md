## sources/distributed-fs/ceph-client/fs/smb/server/transport_tcp.h

Purpose: declares the public TCP transport setup and interface-management API for ksmbd.

Important APIs and types: declares `ksmbd_tcp_set_interfaces`, `ksmbd_find_netdev_name_iface_list`, `ksmbd_free_transport`, `ksmbd_tcp_init`, and `ksmbd_tcp_destroy`. `struct interface` is intentionally opaque to most users and defined in the implementation.

Control flow: server startup initializes TCP notifier state, daemon startup config passes the interface list through `ksmbd_tcp_set_interfaces`, netdevice events create/destroy sockets, and server teardown calls `ksmbd_tcp_destroy`.

State and persistence behavior: no state is stored in the header. Implementation state lives in the interface list and per-transport objects.

Dependencies and integration points: included by IPC startup config and server lifecycle code that needs TCP initialization and interface binding. The declared `ksmbd_free_transport` is part of the broader transport abstraction even though TCP frees through its ops table in this file set.

Risks: consumers should not depend on `struct interface` layout. Interface-list strings are NUL-separated and size-bounded by the caller; malformed lists can produce partial configuration.

Test signals: compile users of the header, interface-list parsing through the public function, lookup by netdev name after startup config, and init/destroy ordering relative to server start/stop.
