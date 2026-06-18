# sources/distributed-fs/lustre-release/lnet/lnet/acceptor.c

## Purpose
Implements LNet's TCP acceptor and outbound connect helper used by IP-based LNDs such as socklnd. It manages listen sockets per interface/port, accepts inbound socket requests, validates acceptor protocol headers, maps requested NIDs to local NIs, delegates accepted sockets to the selected LND, and creates outbound sockets from reserved ports.

## Important APIs and functions
Exports `lnet_acceptor_port`, `lnet_acceptor_port_bulk`, `lnet_acceptor_timeout`, `lnet_connect_console_error`, `lnet_acceptor_add_sockets`, `lnet_acceptor_remove_sockets`, `lnet_connect`, `lnet_acceptor_start`, and `lnet_acceptor_stop`. Internal objects include `struct listening_socket`, global `socket_list`, and `lnet_acceptor_state` with readiness, shutdown, completion, and original socket callback state.

## Control flow
`lnet_acceptor_add_sockets` binds listen sockets for control and optionally bulk ports and installs a data-ready callback that wakes the acceptor thread. `lnet_connect` chooses the correct destination port, iterates privileged local ports, connects, writes an acceptor request containing either NID4 or large-NID form, and returns the connected socket. The acceptor thread waits for readiness, snapshots active listen sockets, accepts nonblocking sockets, optionally enforces secure reserved-port sources, reads magic/version/NID, calls `lnet_accept`, and delegates to `ni->ni_net->net_lnd->lnd_accept`.

## State and persistence
Runtime state includes the listen socket list, per-listen refcounts, active socket count, original data-ready callback, acceptor shutdown flag, waitqueue, and completion. No disk persistence. Socket refs are deliberately dropped outside spinlocks.

## Dependencies and integration points
Depends on Linux sockets, network namespaces, LNet protocol structs/constants, NI lookup/refcounting, module parameters, and LND `lnd_accept` callbacks. Socklnd calls the exported add/remove/connect/timeout/port helpers.

## Risks and test signals
Risks include listen-socket callback restoration races, leaks on `lnet_acceptor_add_socket` error paths, secure-port policy surprises, acceptor protocol compatibility, NID4 vs NID16 parsing, and start/stop decisions tied to `lnet_count_acceptor_nets`. Tests should cover secure/all/none modes, multiple interfaces, bulk port distinct from control port, IPv4 and IPv6/large-NID connect requests, malformed magic/version, no matching NI, concurrent socket removal during accept, and stop while refs are active.
