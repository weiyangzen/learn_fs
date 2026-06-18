# sources/distributed-fs/ceph-client/net/tipc/socket.h

## Purpose
Declares the public interface and shared flow-control constants for the TIPC socket implementation. It is the boundary used by TIPC core, netlink, diagnostics, topology server, trace code, and bearer receive paths to interact with sockets without exposing the private `struct tipc_sock` layout.

## Important APIs, Types, And Constants
The header defines legacy message-based flow-control values (`FLOWCTL_MSG_WIN`, `FLOWCTL_MSG_LIM`), block flow-control size (`FLOWCTL_BLK_SZ`), and receive buffer min/default/max constants. It forward-declares `struct tipc_sock` and exports lifecycle APIs (`tipc_socket_init`, `tipc_socket_stop`), receive dispatch (`tipc_sk_rcv`, `tipc_sk_mcast_rcv`), address reinitialization (`tipc_sk_reinit`), hash table setup/teardown, socket and publication netlink dump functions, socket-diagnostic fill/walk helpers, dump iterator start/done helpers, socket port lookup, overload predicates, bind, and importance setter.

## Control Flow And State
The header itself has no runtime state, but the constants directly shape socket receive-buffer sizing and the fallback path when peers do not advertise block flow control. The declared rhashtable and dump APIs imply per-network-namespace socket indexing, and `tipc_sk_rcv`/`tipc_sk_mcast_rcv` are the ingress bridge from lower TIPC routing into Linux socket queues.

## Dependencies And Integration Points
Includes `net/sock.h` and `net/genetlink.h`, so consumers can pass `struct sock`, `struct socket`, `struct sk_buff`, and netlink callback objects. `trace.h` calls `tipc_sk_dump`, `tipc_sock_get_portid`, and overload checks; `topsrv.c` uses `tipc_sk_bind` and `tsk_set_importance`; TIPC network namespace setup uses hash init/destroy.

## Risks And Test Signals
The main risk is contract drift: changing constants or prototypes can silently alter queue limits, diagnostics, or module init ordering across TIPC. Compile coverage with TIPC enabled, socket diagnostics, tracepoints, and topology server enabled is the primary signal. Runtime tests should exercise block-flow and legacy-flow peers because the constants here define both behavior families.
