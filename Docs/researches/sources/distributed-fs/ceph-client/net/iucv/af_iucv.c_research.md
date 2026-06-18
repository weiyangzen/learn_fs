# sources/distributed-fs/ceph-client/net/iucv/af_iucv.c

## Purpose
Implements PF/AF_IUCV sockets for S390. It presents stream and seqpacket sockets over either classic z/VM IUCV paths or HiperSockets frames, including bind/connect/listen/accept, send/receive, shutdown, socket options, callback handling, HiperSockets packet receive, netdevice event handling, and module registration.

## Important APIs, types, and functions
Registers `iucv_proto`, `iucv_sock_family_ops`, `iucv_sock_ops`, `af_iucv_handler`, and `iucv_packet_type`. Core socket functions are `iucv_sock_bind`, `iucv_sock_connect`, `iucv_sock_listen`, `iucv_sock_accept`, `iucv_sock_sendmsg`, `iucv_sock_recvmsg`, `iucv_sock_shutdown`, `iucv_sock_release`, and option handlers for `SO_IPRMDATA_MSG`, `SO_MSGLIMIT`, and `SO_MSGSIZE`. Classic IUCV callbacks include connection request/ack/reject/shutdown, RX, and TX complete. HiperSockets handlers include SYN, SYN|ACK, SYN|FIN, FIN, WIN, data RX, TX notify, and `afiucv_hs_rcv`.

## Control flow
Socket creation allocates `struct iucv_sock`, initializes queues and counters, selects classic IUCV transport if `pr_iucv` is available, links the socket globally, and exposes only stream/seqpacket semantics. Bind either matches the local z/VM user for classic IUCV or locates a HiperSockets netdevice by EBCDIC user id, sets source names, device refs, and message limits. Connect autobinds classic IUCV sockets if needed, stores destination IDs, sends HiperSockets SYN or calls `path_connect`, then waits for connected/disconnected state. Listen/accept use an accept queue guarded by `accept_q_lock`.

Send builds an skb, handles control messages for target class, waits under message limits, then either emits a HiperSockets frame with an AF_IUCV transport header or uses classic IUCV `message_send` with inline IPRM data, direct buffer, or buffer-list DMA descriptors. Receive dequeues skbs, supports stream partial reads and seqpacket truncation/EOR, returns target class as cmsg, manages HiperSockets window updates, drains backlog, and processes saved classic IUCV messages when buffer space returns.

Classic callbacks allocate child sockets on path pending, accept paths, queue incoming messages or descriptors, match TX completions by tag, and move state to disconnect/closed. HiperSockets packet receive decodes the transport header, locates matching sockets, drives the SYN/SYNACK/FIN/WIN/data state machine, and queues payloads.

## State and persistence behavior
Runtime state includes the global AF_IUCV socket list, per-socket names/user IDs, transport selection, IUCV path pointer, HiperSockets device ref, accept queue, send/backlog/message queues, TX tags, message/window counters, shutdown flags, and socket states (`IUCV_OPEN`, `BOUND`, `LISTEN`, `CONNECTED`, `DISCONN`, `CLOSING`, `CLOSED`). No durable persistence exists. Cleanup severs paths, releases device refs, purges queues, zaps sockets, unregisters packet/notifier/family/proto, and unregisters from low-level IUCV if used.

## Dependencies and integration points
Depends on S390 z/VM detection, `iucv_if` from `iucv.c`, EBCDIC conversion, QETH/HiperSockets netdevices, packet type `ETH_P_AF_IUCV`, socket core, skb memory accounting, security socket cloning, filters, netdevice notifier chain, and module registration. It integrates tightly with low-level IUCV path/message callbacks and with netdevice transmit notifications.

## Risks and test signals
Risks include socket-list locking races, path lifetime and `xchg` sever semantics, mismatched ASCII/EBCDIC IDs, HiperSockets flow-control counter imbalance, receive backlog starvation, window-update errors, partial stream-read offset bugs, device-down state transitions, and freeing sockets still on accept or global lists. Test classic z/VM connect/listen/accept, HiperSockets connect refusal and success, stream partial receive, seqpacket EOR/truncation, IPRM short messages, nonlinear large messages, shutdown both directions, message-limit blocking/wakeup, netdevice down/reboot notifier, module unload with active sockets, and cmsg target class behavior.
