# sources/distributed-fs/ceph-client/include/net/af_rxrpc.h

Purpose: This header defines the kernel-service interface for AF_RXRPC users such as kAFS. It provides call creation, data send/receive, peer management, security challenge handling, notifications, and socket option helpers.

Important APIs, types, and functions: `enum rxrpc_interruptibility` controls whether calls can be interrupted or canceled while waiting for slots. `enum rxrpc_oob_type` currently identifies security challenges. `rxrpc_debug_id` supports tracing. `struct rxrpc_kernel_ops` provides callbacks for new calls, discarded calls, user attachment, and out-of-band packets. Notification typedefs report receive and end-of-transmit events. Public APIs set notifications, begin calls, send data, receive data, abort/shutdown/put calls, look up/get/put peers, query remote addresses and RTT, set/get peer app data, pre-charge accept slots, set transmit length, check call life, configure security keyring/min-level/manage-response, dequeue/query/free OOB packets, inspect/respond/reject security challenges, and query call security.

Control flow: A kernel application configures callbacks on an rxrpc socket, looks up a peer or receives a new call notification, begins or accepts calls, sends request data, receives response data, handles end/receive notifications, and finally shuts down and puts the call. Security challenge OOB packets are dequeued, queried, and answered or rejected by rxkad/rxgk helpers.

State and persistence behavior: Runtime state is held in opaque `rxrpc_call` and `rxrpc_peer` objects plus socket state. Peer app data is an unsigned long stored with the peer. Call refs and peer refs must be put explicitly. Security keyrings and minimum levels persist in socket configuration while set.

Dependencies and integration points: It depends on rxrpc uAPI, ktime, keys, sockets, sk_buffs, Kerberos buffers, and abort reasons. It integrates with AF_RXRPC core, kAFS, key management, security protocols rxkad/rxgk, and kernel networking.

Risks: Call and peer lifetime is reference counted and asynchronous notifications can race with shutdown. Interruptibility selection changes blocking semantics and cancellation windows. Security challenge packets must be freed or responded to exactly once. Application callback code must obey socket locking and context rules from the implementation. Tx total length changes must match protocol framing.

Test signals: Client and server call lifecycles, interruptible and uninterruptible waits, send/receive short and full transfers, abort/shutdown behavior, peer lookup/refcount/appdata, RTT query, OOB challenge dequeue/query/reject/respond for rxkad and rxgk, socket security options, and race tests for call life during callback delivery.
