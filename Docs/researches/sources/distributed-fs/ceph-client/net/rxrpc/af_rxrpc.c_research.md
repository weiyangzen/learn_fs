# sources/distributed-fs/ceph-client/net/rxrpc/af_rxrpc.c

## Purpose
Implements the AF_RXRPC socket family front end: socket creation, bind/listen/connect/send/poll/shutdown/release operations, kernel-service helper APIs, socket options, protocol registration, module initialization, and module teardown.

## Important APIs, Types, and Functions
Defines module parameter `debug`, exported `rxrpc_debug_id`, global `rxrpc_n_rx_skbs`, and `rxrpc_workqueue`. Public kernel helpers include `rxrpc_kernel_lookup_peer()`, `rxrpc_kernel_get_peer()`, `rxrpc_kernel_put_peer()`, `rxrpc_kernel_begin_call()`, `rxrpc_kernel_shutdown_call()`, `rxrpc_kernel_put_call()`, `rxrpc_kernel_check_life()`, `rxrpc_kernel_set_notifications()`, and `rxrpc_sock_set_min_security_level()`. Socket ops include `rxrpc_bind()`, `rxrpc_listen()`, `rxrpc_connect()`, `rxrpc_sendmsg()`, `rxrpc_setsockopt()`, `rxrpc_getsockopt()`, `rxrpc_poll()`, `rxrpc_shutdown()`, and `rxrpc_release()`.

## Control Flow
`rxrpc_create()` validates datagram socket type and protocol family, allocates `struct rxrpc_sock`, initializes queues, locks, call trees, state, write-space callback, and schedules peer keepalive soon. `rxrpc_bind()` validates `sockaddr_rxrpc`, obtains or creates a local UDP endpoint, and transitions to client-bound or server-bound state, allowing a second service ID for upgradeable services. `rxrpc_listen()` sizes the service backlog and preallocates service calls, with backlog zero disabling listen. `rxrpc_connect()` stores a default destination without network negotiation. `rxrpc_sendmsg()` auto-binds client sockets when needed, uses connected destination when no msg_name is supplied, and delegates data/OOB transmission to lower send helpers. Release orphan-closes the socket, marks services closed, detaches local service pointers, discards preallocations, releases calls, flushes the ordered workqueue, purges OOB and receive queues, drops local and key references, and finally `sock_put()`s.

## State and Persistence
Socket state is in `sk_state` values such as `RXRPC_UNBOUND`, client/server bound states, listening, listen-disabled, and close. `struct rxrpc_sock` stores family, local endpoint, service IDs, connection flags, security keys/keyrings, min security level, call RB tree, accept and receive queues, OOB queues, locks, and app callbacks. Module state includes the call slab, ordered high-priority reclaim workqueue, registered key types, pernet state, proto registration, socket family registration, security subsystem, and sysctls. All state is runtime-only.

## Dependencies and Integration
Depends on the Linux socket/proto APIs, net namespaces, UDP transport endpoints, RxRPC internal call/connection/peer/local/security/key/send/recv modules, key retention service, crypto-backed security classes, sysctl, RCU teardown, skb queues, and AFS or kernel consumers using exported helper APIs.

## Risks and Test Signals
Risks include state-machine violations for bind/listen/connect/options, reference leaks on local endpoints, peers, calls, keys, and sockets, release-time workqueue flushing latency, OOB queue leaks, service close races, and incorrect address validation tail clearing. Test signals are userspace socket lifecycle tests for client and server modes, second-service binding and upgrade option validation, auto-bind sendmsg, connected sendmsg, poll readability/writability, shutdown idempotence, kernel API begin/shutdown/put call flows, module init failure unwinding at each registration step, and module exit with `rxrpc_n_rx_skbs == 0`.
