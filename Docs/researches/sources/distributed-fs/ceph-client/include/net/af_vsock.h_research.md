# sources/distributed-fs/ceph-client/include/net/af_vsock.h

## Purpose

`af_vsock.h` defines the in-kernel AF_VSOCK socket object, transport interface, global lookup tables, tap hooks, receive helpers, BPF integration hooks, and network-namespace mode helpers used by `net/vmw_vsock/af_vsock.c` and transport drivers. It is the contract between the common vsock socket layer and transports such as virtio, VMCI, Hyper-V, and loopback.

## Important APIs, Types, and Functions

`struct vsock_sock` embeds `struct sock` first and adds local/remote `sockaddr_vm`, table links, trust/owner metadata, stream/listener state, delayed works for connect/pending/close paths, peer shutdown flags, buffer sizing, and transport-private `trans`. `struct vsock_transport` is the central vtable: lifecycle, connection, datagram, stream, seqpacket, notification, shutdown, CID lookup, `read_skb`, and zero-copy capability callbacks. `vsock_core_register()` and `vsock_core_unregister()` publish a transport with feature flags for host-to-guest, guest-to-host, datagram, and local service. Table helpers cover bound/connected insertion, removal, lookup, pending/accept queues, transport assignment, CID lookup, and linger.

The tap API uses `struct vsock_tap`, `vsock_add_tap()`, `vsock_remove_tap()`, and `vsock_deliver_tap()` to mirror vsock traffic to monitor devices. Receive helpers cover connectible and datagram sockets. Namespace helpers expose global/current mode reads, child mode locking, and cross-namespace reachability checks.

## Control Flow

Common socket operations allocate a `vsock_sock`, assign a transport, add it to bound or connected hash tables under `vsock_table_lock`, and then call the selected `vsock_transport` callbacks for transport-specific packet movement. Listener flow is modeled through pending and accept queues: children remain pending until the handshake completes, then move to the accept queue. Stream and seqpacket I/O routes through the vtable while notification callbacks let transports adjust poll and blocking behavior around enqueue/dequeue. Namespace reachability is evaluated by comparing `struct net` vsock modes before allowing cross-namespace communication.

## State and Persistence Behavior

There is no filesystem persistence. State lives in socket objects, global bound/connected tables, delayed work items, tap registrations, and per-net vsock mode fields. `owner`, `trusted`, and cached peer datagram fields are deliberately immutable after create/destruct because they are read without the socket lock. Buffer sizes are protected by `lock_sock(sk)`.

## Dependencies and Integration Points

The header depends on Linux sockets, workqueues, credentials, sk_buffs, BPF psock support when enabled, `netns/vsock.h`, UAPI `vm_sockets.h`, and `vsock_addr.h`. Transport drivers implement `struct vsock_transport`; userspace observes the ABI through AF_VSOCK sockets; optional taps integrate with net devices and monitor paths.

## Risks and Edge Cases

The global tables require correct `vsock_table_lock` discipline; stale table links can expose sockets after teardown. Transport callbacks must honor lock context, especially notification callbacks where comments document `sk_lock` ownership. Namespace helpers treat `NULL` as global mode, which is convenient but easy to misuse in new code. Cross-namespace policy depends on the child mode lock being set consistently. Zero-copy and BPF hooks are conditional and must degrade cleanly when unsupported.

## Test Signals

Exercise bind/connect/accept teardown races, pending-to-accept transitions, stream/dgram/seqpacket routing per transport, transport unregister with connected sockets, tap add/remove and delivery, BPF proto update/restore when enabled, namespace mode combinations, CID routing/fallback, linger/close delayed work, and MSG_ZEROCOPY allow/deny behavior.
