<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/unix/af_unix.c -->
# sources/distributed-fs/ceph-client/net/unix/af_unix.c

## Purpose
`af_unix.c` is the main Linux Unix domain socket implementation. It implements socket creation, binding, lookup, stream/seqpacket/datagram connect and accept, sendmsg/recvmsg/splice/read_skb, credentials and SCM_RIGHTS handling, poll/ioctl/shutdown behavior, procfs enumeration, BPF iterator support, and per-network-namespace AF_UNIX hash tables.

## Important APIs, Types, and Functions
- Global and per-net hash tables track unbound/abstract sockets, while separate BSD bind buckets map pathname socket inodes.
- Address helpers include `unix_validate_addr()`, `unix_mkname_bsd()`, `unix_bind_bsd()`, `unix_bind_abstract()`, and `unix_autobind()`.
- Lifecycle functions include `unix_create1()`, `unix_create()`, `unix_release()`, `unix_release_sock()`, `unix_sock_destructor()`, and `af_unix_init()`.
- Connection functions include `unix_dgram_connect()`, `unix_stream_connect()`, `unix_socketpair()`, `unix_accept()`, and `unix_getname()`.
- Datapath functions include `unix_dgram_sendmsg()`, `unix_stream_sendmsg()`, `unix_seqpacket_sendmsg()`, `__unix_dgram_recvmsg()`, `__unix_stream_recvmsg()`, `unix_stream_read_generic()`, `unix_stream_splice_read()`, and `unix_read_skb()`/`unix_stream_read_skb()`.
- SCM helpers include `unix_scm_to_skb()`, `unix_skb_to_scm()`, `unix_maybe_add_creds()`, `unix_attach_fds()`, `unix_detach_fds()`, `scm_stat_add()`, `scm_stat_del()`, and `unix_orphan_scm()`.
- Readiness and controls include `unix_poll()`, `unix_dgram_poll()`, `unix_ioctl()`, `unix_inq_len()`, `unix_outq_len()`, `unix_shutdown()`, and `unix_setsockopt(SO_INQ)`.
- Proc/BPF iterator support includes seq operations for `/proc/net/unix` and the `unix` BPF iterator target.

## Control Flow
Kernel init registers datagram and stream protos, registers the `PF_UNIX` family, registers per-net namespace state, builds BPF proto wrappers, and optionally registers a BPF iterator. Socket creation selects stream, datagram, raw-as-datagram, or seqpacket ops and inserts a new unbound socket into the per-net hash. Bind either creates a pathname socket inode and adds a BSD inode bucket entry or creates an abstract address and moves the socket to the abstract hash. Datagram connect finds a peer and updates `unix_peer()` with permission and flow-control checks. Stream connect creates an embryo socket, waits for listener backlog room, copies listener address/credentials, links peers, and queues the embryo skb on the listener. Accept dequeues that skb and grafts the embryo socket into the accepted socket.

Datagram send builds one skb, attaches credentials and optional file descriptors, resolves destination by name or connected peer, applies filters/security, waits on peer receive queue flow control, updates SCM accounting, queues to the peer, and wakes readers. Stream send chunks data into paged skbs, attaches SCM only to the first buffer, maintains `inq_len`, supports splice pages, and optionally queues a one-byte OOB skb. Receive paths serialize with `u->iolock`, honor peek offsets, copy credentials/file descriptors, update SCM graph accounting, manage OOB and `SCM_INQ`, and free or retain skbs depending on consumption and `MSG_PEEK`.

## State and Persistence
Per socket state lives in `struct unix_sock`: address/path, peer pointer, listener pointer for embryos, state lock, I/O and bind mutexes, peer wait/wake entries, SCM fd accounting, optional OOB skb, receive queue byte count, and `SO_INQ` setting. Per-net state includes `net->unx.table` buckets/locks and `sysctl_max_dgram_qlen`. Global state includes BSD inode buckets, lockdep comparison functions, and `unix_nr_socks`. Pathname bindings persist as filesystem socket nodes until unlinked by userspace; abstract bindings and queues are in-memory.

## Dependencies and Integration Points
The file depends on VFS path creation/lookup, LSM hooks, pidfs registration for peer credentials, SCM_RIGHTS helpers, `garbage.c` for inflight Unix fd graph management, sysctl registration, BPF cgroup hooks, sockmap/BPF proto replacement, procfs/seq_file, BPF iterators, and core socket/TCP-state conventions. It exports `unix_peer_get()`, `unix_inq_len()`, and `unix_outq_len()` for diagnostics and other kernel users.

## Risks and Edge Cases
This file is concurrency-sensitive. Correctness depends on hash bucket locks, `unix_state_lock()`, double-lock ordering, receive queue locks, `u->iolock`, and bind mutexes. Stream connect has subtle backlog waiting and embryo cleanup paths. SCM_RIGHTS must update the GC graph exactly when skb ownership changes, including peek, partial stream consumption, accept, and orphaning for BPF read_skb. Datagram asymmetric flow control uses peer wait relays to avoid stuck writers. OOB support must coordinate `oob_skb`, consumed lengths, `SIOCATMARK`, and inline vs non-inline reads. Pathname binds must unlink created filesystem nodes on late failure.

## Test Signals
Run AF_UNIX selftests for stream/datagram/seqpacket bind/connect/listen/accept/socketpair, abstract and pathname sockets, autobind, reconnect/disconnect, backlog blocking, poll readiness, shutdown propagation, `SIOCINQ`/`SIOCOUTQ`/`SIOCUNIXFILE`, `SO_INQ`/`SCM_INQ`, `SCM_CREDENTIALS`, pidfd credentials, SCM_RIGHTS pass/peek/partial receive, OOB send/recv/atmark, splice send/read, BPF cgroup hooks, sockmap insertion, `/proc/net/unix`, BPF iterator output, namespace teardown, and stress tests with concurrent close/send/recv.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/unix/af_unix.c -->
