<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/skmsg.h -->
# sources/distributed-fs/ceph-client/include/linux/skmsg.h

## Purpose
`skmsg.h` defines the kernel socket-message and psock infrastructure used by BPF sockmap/sockhash and stream parser/verdict paths. It represents message payloads as scatterlists, tracks BPF programs attached to sockets, and provides helpers for queuing, receiving, redirecting, and freeing messages.

## Important APIs, Types, and Functions
Core types are `struct sk_msg_sg`, `struct sk_msg`, `struct sk_psock_progs`, `struct sk_psock_link`, `struct sk_psock_work_state`, and `struct sk_psock`. `sk_msg_sg` is a ring of scatterlist elements with `start`, `curr`, `end`, `size`, `copybreak`, and a bitmap marking copied entries. `sk_msg` embeds `sk_msg_sg` first for UAPI assumptions, adds BPF-visible `data`/`data_end`, cork/apply counters, flags, skb pointer, redirect socket, owning socket, and list linkage. `sk_psock` stores the attached socket, redirect socket, BPF programs and links, optional stream parser state, ingress skb/message queues, locks, total queued message length, protocol callback backups, work items, and refcount.

Important functions include `sk_msg_alloc()`, `sk_msg_clone()`, `sk_msg_trim()`, `sk_msg_free*()`, `sk_msg_return*()`, `sk_msg_zerocopy_from_iter()`, `sk_msg_memcopy_from_iter()`, `sk_msg_recvmsg()`, `__sk_msg_recvmsg()`, `sk_msg_is_readable()`, `sk_psock_init()`, `sk_psock_stop()`, `sk_psock_msg_verdict()`, `sk_psock_drop()`, and optional stream-parser functions. Inline helpers initialize ring state, move scatterlist bytes, compute data pointers, add pages, set/clear copy bits, queue/dequeue ingress messages, manage psock refs, restore protocol callbacks, report errors, and handle skb BPF redirection flags.

## Control Flow
Message flow starts by initializing an `sk_msg`, filling its scatterlist from copied or zerocopy iter data, and exposing the current element through `data`/`data_end` unless it is marked copied. Ring iteration wraps at `NR_MSG_FRAG_IDS`, allowing partitioned scatterlists and crypto chaining entries. Verdict flow runs through psock state and BPF programs; messages may be passed, dropped, or redirected.

Ingress queue flow is protected by `psock->ingress_lock`. `sk_psock_queue_msg()` appends to `ingress_msg` only while `SK_PSOCK_TX_ENABLED` is set; otherwise it frees the message. Dequeue/peek helpers update `msg_tot_len` with `WRITE_ONCE` so ioctl-style lockless readers can use `READ_ONCE`. Refcount flow uses `sk_psock_get()` under RCU and `sk_psock_put()` to call `sk_psock_drop()` on the last reference. Program replacement uses `xchg()` or `cmpxchg()` to safely drop old BPF program references.

## State and Persistence Behavior
State is per socket and per message, all in memory. `sk_psock` persists while attached to a socket and holds saved protocol callbacks so teardown can restore socket behavior. Queued ingress messages and skbs persist until received, dropped, or psock teardown. BPF program references and links persist in `sk_psock_progs` until explicitly replaced or dropped. There is no disk persistence.

## Dependencies and Integration Points
The header depends on BPF, filters, scatterlists, skbuffs, socket internals, TCP, and stream parser infrastructure. It integrates with sockmap/sockhash, TLS stream parser support, BPF verdict programs, socket callbacks (`data_ready`, `write_space`, `close`, `destroy`, `unhash`), skb redirection metadata (`_sk_redir`), and memory allocation helpers such as `kzalloc_obj()`.

## Risks and Test Signals
Key risks are scatterlist ring wrap mistakes, incorrect copy-bit handling, message length accounting races, psock refcount misuse, failing to restore socket protocol callbacks, BPF program reference leaks, and stale redirect socket pointers. Useful signals are BPF sockmap selftests, strparser/TLS tests, KASAN/KCSAN reports, refcount warnings, lockdep around `ingress_lock` and callback locks, and tests that exercise corking, redirect, drop, recvmsg, and psock teardown while traffic is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/skmsg.h -->
