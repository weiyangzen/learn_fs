<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/handshake/netlink.c -->
# sources/distributed-fs/ceph-client/net/handshake/netlink.c

## Purpose
Implements the generic-netlink control plane and per-network-namespace registration for the kernel handshake service.

## APIs, Types, and Functions
Provides `handshake_genl_notify()`, `handshake_genl_put()`, `handshake_nl_accept_doit()`, `handshake_nl_done_doit()`, `handshake_pernet()`, module init/exit, and pernet operations `handshake_net_init()` and `handshake_net_exit()`.

## Control Flow, State, and Persistence
`handshake_genl_notify()` checks protocol notification flag and multicast listeners, then sends `HANDSHAKE_CMD_READY` with handler class. ACCEPT validates handler class, selects the next pending request for that class, prepares an fd for the socket file, calls the protocol `hp_accept()` callback to build a reply, publishes the fd on success, or completes the request with `-EIO` on failure. DONE looks up the socket fd, finds the outstanding request by socket, extracts an optional status, and calls `handshake_complete()`. Per-net init sets a memory-scaled cap for pending handshakes, initializes a spinlock and list, and clears flags. Per-net exit marks draining, splices unaccepted requests, and completes them with timeout. Module init initializes the request hash, registers the netlink family, then registers pernet state last so `handshake_pernet()` stays NULL until safe.

## Dependencies and Integration
Depends on generic-netlink, net namespace generic storage, fd allocation helpers, socket file references, request hash/list APIs, and handshake tracepoints. It registers the generated `handshake_nl_family`.

## Risks and Test Signals
Risks include fd reference handling on ACCEPT error paths, completing accepted requests during namespace teardown only when sockets later close, pending cap sizing, listener absence returning `-ESRCH`, and init ordering around `handshake_net_id`. Test signals include READY multicast with listeners, ACCEPT empty queue returning `-EAGAIN`, ACCEPT fd publication, DONE unknown fd/request, per-net draining, and init failure unwind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/handshake/netlink.c -->
