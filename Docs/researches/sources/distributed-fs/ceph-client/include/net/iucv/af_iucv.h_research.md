# sources/distributed-fs/ceph-client/include/net/iucv/af_iucv.h

Purpose: Defines the AF_IUCV socket layer data structures for IBM s390 IUCV and HiperSockets transport, including socket states, wire transport header, send/receive queues, socket options, and skb control metadata.

Important APIs/types/functions: `sockaddr_iucv` names a VM guest user/application endpoint. `sock_msg_q` associates an `iucv_path`, message, list node, and lock. `af_iucv_trans_hdr` is the packed HiperSockets transport header with SYN/ACK/FIN/WIN/SHT flags, node/user/app identifiers, and embedded IUCV message metadata. `iucv_sock` embeds `struct sock` and stores endpoint names, accept queue, parent, path, HiperSockets device, send/backlog queues, message queue, tags, msg limits, counters, transport type, and tx notification callback. `iucv_skb_cb` stores class, tag, and receive offset.

Control flow: Socket code moves through open/bound/listen/connected/disconnect/closing/closed states. Data uses send and backlog skb queues plus message queue entries tied to IUCV path messages. HiperSockets packets use `iucv_trans_hdr()` over the skb network header.

State and persistence: Per-socket state includes path ownership, queue contents, message limits, counters, pending sends, and transport selection. `iucv_sock_list` holds bound sockets under rwlock with an autobind counter. State is volatile socket lifetime state.

Dependencies/integration: Depends on s390 IUCV base API, Linux sockets, sk_buffs, netdevice for HiperSockets, and poll/list/spinlock primitives.

Risks: Packed header layout is ABI-like for HiperSockets transport; queue and counter updates need lock/atomic correctness; message limit defaults are large and flow-control bugs can exhaust memory. Test signals include bind/listen/connect/disconnect, tx notification variants, IPRMDATA socket option, message limit enforcement, HiperSockets header parsing, and skb control block use.
