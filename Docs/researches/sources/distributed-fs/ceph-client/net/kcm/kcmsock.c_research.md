# sources/distributed-fs/ceph-client/net/kcm/kcmsock.c

## Purpose
Implements PF_KCM sockets, which multiplex framed application messages over attached TCP sockets. It owns mux creation/destruction, KCM socket send/receive semantics, psock attachment to TCP sockets, BPF/stream-parser receive framing, transmit psock reservation, clone/ioctl control, receive-disable options, proc initialization, per-net state, and module lifecycle.

## Important APIs, types, and functions
Registers `kcm_proto`, `kcm_family_ops`, datagram and seqpacket `proto_ops`, pernet `kcm_net_ops`, slab caches, and a single-thread workqueue. Key user operations are `kcm_create`, `kcm_sendmsg`, `kcm_recvmsg`, `kcm_splice_read`, `kcm_setsockopt`, `kcm_getsockopt`, `kcm_ioctl`, `kcm_release`, and `kcm_clone`. Attach control is through `SIOCKCMATTACH`, `SIOCKCMUNATTACH`, and `SIOCKCMCLONE`, using `struct kcm_attach`, `kcm_unattach`, and `kcm_attach`. Receive parsing uses strparser callbacks `kcm_rcv_strparser`, `kcm_parse_func_strparser`, and `kcm_read_sock_done`.

## Control flow
Creating a KCM socket allocates a mux, initializes mux lists/locks/hold queue, links it into per-net state, initializes the first KCM socket, and places that socket on the receive-waiter list. Clone creates another socket sharing the same mux. Attach looks up a TCP socket and BPF socket-filter program, rejects unsupported or already-attached sockets, initializes `strparser`, swaps TCP callbacks to KCM wrappers, holds the socket/file, links a psock into the mux, makes it available for transmit, and kicks receive parsing.

Receive flow starts from TCP `sk_data_ready`, enters strparser, runs the BPF parser to determine message length, reserves a KCM receiver if one is waiting, queues the message to that KCM receive queue, or pauses the psock with a ready message if no KCM can receive. `kcm_rfree`, `kcm_rcv_ready`, `requeue_rx_msgs`, receive-disable, and unreserve logic move queued messages among KCM sockets while honoring receive buffer limits.

Send flow builds an skb-backed message from copied or spliced pages. Datagram sockets complete on lack of `MSG_MORE`; seqpacket sockets require `MSG_EOR`. Completed messages are queued on `sk_write_queue`, then `kcm_write_msgs` reserves an available psock, sends page fragments through the lower TCP socket, handles `-EAGAIN` by saving fragment progress, aborts and retries on hard psock errors, and unreserves psocks when queues drain. `psock_write_space` and workqueue processing resume blocked writers.

Release cancels pending TX work, purges queues, aborts reserved psocks, requeues receive messages, removes the KCM socket from the mux, and releases the mux when the last KCM socket closes. Unattach restores TCP callbacks, stops/destroys strparser, drops ready messages, aggregates stats, and either frees the psock immediately or defers until a reserved transmit path unreserves it.

## State and persistence behavior
Runtime state includes per-net mux lists and aggregate stats, each mux's KCM socket list, psock list, waiters, available psocks, ready psocks, receive hold queue, locks, and counters. KCM sockets track TX partial message state, reserved TX psock, RX wait/reservation/disable flags, work item, and stats. Psocks track attached TCP socket callbacks, BPF program, strparser, reserved KCM, ready RX message, availability, done/unattaching/tx_stopped flags, stats, and held file/socket refs. No durable persistence exists.

## Dependencies and integration points
Depends on INET/TCP sockets, BPF socket-filter programs, stream parser, socket memory accounting, splice/page-frag helpers, net namespace generic IDs, proc support from `kcmproc.c`, RCU, workqueues, and ioctl UAPI from `linux/kcm.h`.

## Risks and test signals
Risks include callback restoration races on attached TCP sockets, psock reserved/free lifetime bugs, TX retry causing duplicate or corrupted message framing, receive requeue ordering, buffer accounting mismatches, BPF parser invalid lengths, deadlocks between mux locks and socket locks, clone/mux teardown races, and splice/EOR edge cases. Test attach/unattach under traffic, clone fanout, receive-disable/re-enable, datagram `MSG_MORE`, seqpacket `MSG_EOR`, splice send/read, BPF parser failures and oversized messages, TCP close/error propagation, socket release with reserved TX/RX psocks, proc stats under churn, and netns teardown.
