# sources/distributed-fs/lustre-release/lnet/klnds/socklnd/socklnd.c

## Purpose
Implements the main socklnd LNet driver lifecycle: module registration, NI startup and shutdown, interface binding, peer and connection-control-block management, active/passive connection creation, close paths, LNet control operations, and netdevice/address notifier handling.

## Important APIs and functions
Exports the `struct lnet_lnd` callbacks through `the_ksocklnd`: `ksocknal_startup`, `ksocknal_shutdown`, `ksocknal_ctl`, `ksocknal_send`, `ksocknal_recv`, `ksocknal_accept`, and tunable/netlink helpers. Peer APIs include `ksocknal_add_peer`, `ksocknal_find_peer_locked`, `ksocknal_close_matching_conns`, and `ksocknal_peer_failed`. Connection lifecycle APIs include `ksocknal_create_conn`, `ksocknal_close_conn_locked`, `ksocknal_terminate_conn`, `ksocknal_queue_zombie_conn`, and `ksocknal_destroy_conn`.

## Control flow
`ksocklnd_init` initializes tunables, libcfs, and registers the LND. `ksocknal_startup` performs global base startup if needed, allocates `ksock_net`, selects an IP interface from `lnet_inet_enumerate`, initializes NI NID/interface state, starts scheduler threads for configured CPTs, checks link state, and registers acceptor sockets. `ksocknal_add_peer` creates or finds a peer and attaches a single route/control block. `ksocknal_create_conn` is the central handshake path: allocate `ksock_conn`, save socket callbacks, exchange hello messages, resolve protocol version and identity, create or find the peer for passive accepts, reject duplicate or racing connections, bind a scheduler, queue pending TXs, set socket options, install callbacks, and kick RX/TX readiness. Close paths remove connections from peers, move blocked TXs for completion or drain, enqueue deathrow/zombie work to the reaper, and notify LNet when kernel peers appear down.

## State and persistence
Global state lives in `ksocknal_data`: peer hash, net list, scheduler array, connd/reaper lists, TX freelist, and shutdown flags. Per-NI state is `struct ksock_net`, including incarnation, selected interface, and peer count. Peer state records NID/PID, protocol, incarnation, connection list, pending TX queue, zero-copy requests, and keepalive timestamps. All state is volatile kernel memory. Shutdown applies `SOCKNAL_SHUTDOWN_BIAS` to prevent new peers, deletes peers, removes acceptor sockets, waits for refs to drain, then tears down global threads when the last net exits.

## Dependencies and integration points
Integrates with LNet NI registration, acceptor socket management, libcfs allocation/CPT APIs, Linux netdevice and inet address notifiers, kernel sockets, SunRPC sockaddr helpers, netlink tunable export/import, and socklnd protocol/lib/callback helpers.

## Risks and test signals
High-risk areas are lock ordering around `ksnd_global_lock`, scheduler locks, and reaper/connd locks; passive/active race resolution; duplicate connection limits; peer reboot incarnation handling; IPv6/large-NID protocol selection; and shutdown refcount drainage. Test signals include multi-peer startup/shutdown, interface down/up and address removal events, mixed v3/v4 peers, connection-race tests, duplicate `conns_per_peer` scenarios, ioctl/netlink tunable checks, and leak/refcount assertions during module unload.
