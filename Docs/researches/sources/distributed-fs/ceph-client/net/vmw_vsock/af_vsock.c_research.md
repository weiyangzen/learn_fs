# sources/distributed-fs/ceph-client/net/vmw_vsock/af_vsock.c

## Purpose
`af_vsock.c` is the core `AF_VSOCK` socket-family implementation. It registers the protocol family and `/dev/vsock`, owns generic socket lifecycle and operations for datagram, stream, and seqpacket sockets, maintains bound and connected socket lookup tables, selects a registered transport for each socket, implements accept/connect/shutdown/poll/send/receive/ioctl/socket-option behavior, and exposes per-network-namespace vsock mode sysctls.

## Important APIs, Types, And Functions
Persistent objects include `struct proto vsock_proto`, `vsock_bind_table`, `vsock_connected_table`, and the registered transport pointers `transport_h2g`, `transport_g2h`, `transport_dgram`, and `transport_local`. Exported helpers include `vsock_assign_transport()`, `vsock_find_bound_socket_net()`, `vsock_find_connected_socket_net()`, `vsock_create_connected()`, `vsock_insert_connected()`, `vsock_remove_sock()`, `vsock_stream_has_data()`, `vsock_stream_has_space()`, `vsock_linger()`, `vsock_core_register()`, and `vsock_core_unregister()`.

## Control Flow
Module init initializes lookup tables, registers `/dev/vsock`, registers the socket protocol and family, installs pernet sysctls, and prepares optional BPF protocol hooks. Socket creation chooses proto ops by type, allocates `struct vsock_sock`, initializes addresses, delayed work, credentials, buffer sizes, and inserts the socket into the unbound list; datagram sockets immediately receive a datagram transport.

`connect()` validates state, stores the remote address, assigns a transport based on CID and flags, autobinds a local port, sends the transport request, and either waits for `TCP_ESTABLISHED` or returns `-EINPROGRESS` with timeout work scheduled. Listen sockets accept transport-created child sockets from the accept queue. Send and receive paths are generic loops around transport callbacks for enqueue/dequeue, notification hooks, rcvlowat handling, zero-copy checks, and stream versus seqpacket semantics.

## State And Persistence
Core state is in `struct vsock_sock`: local/remote addresses, selected transport, pending/accept lists, shutdown flags, connect and cleanup delayed works, owner credentials, trust/cache state, buffer bounds, and transport-private `trans`. The global tables persist bound and connected sockets with reference counts taken for each list entry. Network namespaces persist `mode`, `child_ns_mode`, write-once child mode lock state, and `g2h_fallback` through `net->vsock`.

## Dependencies And Integration Points
The core depends on the Linux socket layer, skbuff queues, workqueues, credentials/capabilities, sysctl, misc devices, network namespaces, BPF sockmap hooks, and `uapi/linux/vm_sockets.h`. It is the integration point for VMCI, virtio, Hyper-V, loopback, vhost, sock_diag, BPF, and vsockmon taps via exported helpers and transport callbacks.

## Risks And Edge Cases
Critical risks are socket lifetime and lock ordering across listener/pending/accepted sockets, global table references, delayed connect and pending cleanup work, and transport module references. Transport reassignment during connect must release/destruct the previous transport while preserving bindings. Namespace mode checks protect local-mode containment; missing namespace-aware lookup in a transport forces global semantics. Send/receive loops must handle shutdown races, signal/timeout interruption, partial seqpacket sends, and zero-copy support negotiation.

## Test Signals
Useful coverage includes stream, seqpacket, and dgram socket creation; bind to explicit and auto ports; reserved-port permission checks; blocking and nonblocking connect timeout/cancel; listen/accept backlog and pending cleanup; poll readiness; `SO_VM_SOCKETS_*` and `SO_ZEROCOPY`; `SIOCINQ/SIOCOUTQ`; namespace `ns_mode` and `child_ns_mode`; transport register/unregister conflicts; module unload with open sockets; BPF sockmap redirection; and lockdep/KASAN/KCSAN around close and workqueue paths.
