# sources/distributed-fs/ceph-client/include/net/af_unix.h

Purpose: This header defines core AF_UNIX internal socket structures and helpers shared by Unix-domain socket implementation and in-kernel users.

Important APIs, types, and functions: `unix_get_socket()` returns a `struct unix_sock *` for a file when Unix sockets are enabled, or NULL in disabled builds. `struct unix_address` is a refcounted variable-length sockaddr container. `struct scm_stat` tracks file-descriptor passing counts. `struct unix_sock` embeds `struct sock` as its first member and adds bound address, path, I/O and bind mutexes, peer and listener pointers, graph vertex pointer, state lock, peer waitqueue, peer wake entry, SCM stats, in-queue length, recvmsg inq flag, and optional out-of-band skb. Macros `unix_sk()`, `unix_peer()`, `unix_state_lock()`, and `unix_state_unlock()` provide casts and locking.

Control flow: AF_UNIX implementation allocates sockets as `unix_sock`, binds addresses and paths, connects peers/listeners, transfers data and SCM_RIGHTS, wakes peers through the peer waitqueue, and uses the state spinlock for peer/state transitions. In-kernel users can recover unix socket state from a file via `unix_get_socket()`.

State and persistence behavior: Socket state is runtime-only but may reference filesystem paths and passed file descriptors. Address lifetime is refcounted. Peer/listener links, waitqueue entries, and optional OOB skb require careful teardown during close and garbage collection.

Dependencies and integration points: It depends on atomic/refcounting, mutexes, net core, path handling, spinlocks, waitqueues, sock core, and the Unix socket uAPI. It integrates with SCM_RIGHTS accounting, AF_UNIX garbage collection, filesystem pathname sockets, and optional out-of-band support.

Risks: `struct sock` must remain the first member for casting. Peer pointer and waitqueue lifetime are race-prone during disconnect and close. File descriptor passing can create reference cycles and pressure GC. Disabled `CONFIG_UNIX` builds return NULL, so callers must handle unavailable Unix sockets. Optional OOB state changes struct behavior under config.

Test signals: Stream/datagram/seqpacket bind-connect-close cycles, pathname and anonymous sockets, SCM_RIGHTS accounting and GC, peer wakeups during shutdown, concurrent connect/disconnect, `unix_get_socket()` enabled and disabled builds, recvmsg inq behavior, and OOB support when configured.
