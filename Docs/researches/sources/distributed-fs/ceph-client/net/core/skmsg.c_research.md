# sources/distributed-fs/ceph-client/net/core/skmsg.c

Purpose: implements `sk_msg` scatter-gather message storage and `sk_psock` plumbing for BPF sockmap/sockhash stream parser, stream verdict, skb verdict, TLS verdict, redirects, ingress queues, and socket callback interposition. It converts user iterators or incoming skbs into `sk_msg` scatterlists, applies BPF verdict programs, redirects or drops data, and restores socket behavior during teardown.

Important APIs/types/functions:

- `struct sk_msg` scatterlist operations: `sk_msg_alloc`, `sk_msg_clone`, `sk_msg_return_zero`, `sk_msg_return`, `sk_msg_free`, `sk_msg_free_nocharge`, `sk_msg_free_partial`, `sk_msg_free_partial_nocharge`, `sk_msg_trim`, `sk_msg_zerocopy_from_iter`, `sk_msg_memcopy_from_iter`, `sk_msg_recvmsg`, `__sk_msg_recvmsg`, and `sk_msg_is_readable`.
- `struct sk_psock` lifecycle: `sk_psock_init`, `sk_psock_drop`, `sk_psock_stop`, `sk_psock_link_pop`, `sk_psock_destroy`, `__sk_psock_zap_ingress`, and `__sk_psock_purge_ingress_msg`.
- skb ingress and backlog: `sk_psock_skb_ingress`, `sk_psock_skb_ingress_self`, `sk_psock_skb_ingress_enqueue`, `sk_psock_handle_skb`, `sk_psock_backlog`, and `sk_psock_skb_state`.
- BPF verdict/redirect integration: `sk_psock_msg_verdict`, `sk_psock_tls_strp_read`, `sk_psock_verdict_apply`, `sk_psock_skb_redirect`, `sk_psock_start_verdict`, `sk_psock_stop_verdict`, and `sk_psock_verdict_recv`.
- Stream parser integration under `CONFIG_BPF_STREAM_PARSER`: `sk_psock_init_strp`, `sk_psock_start_strp`, `sk_psock_stop_strp`, `sk_psock_strp_data_ready`, `sk_psock_strp_read`, `sk_psock_strp_parse`, and `sk_psock_done_strp`.

Control flow:

- `sk_msg_alloc` grows a message to a requested size using the socket page-frag cache. It refills page fragments, schedules write memory, coalesces with the previous scatterlist entry when contiguous and permitted, otherwise appends a new scatterlist entry, charges socket memory, advances fragment offsets, and trims back to the original size on allocation failure.
- `sk_msg_clone` copies a byte range from one `sk_msg` into another by walking the source ring from `sg.start`, skipping the requested offset, and adding or coalescing destination scatterlist entries. Each cloned byte is charged to the destination socket.
- Free/return/trim paths walk the message scatterlist ring, uncharge socket memory as requested, release page refs when the message does not have an owning skb, zero freed entries, move `sg.start`/`sg.end`/`sg.curr`, and consume `msg->skb` when the skb owns the underlying data.
- Iterator import has two modes. `sk_msg_zerocopy_from_iter` pins pages from an `iov_iter` into scatterlist entries and reverts iterator progress on error, while `sk_msg_memcopy_from_iter` copies bytes into already allocated scatterlist buffers from `sg.curr`/`copybreak` and honors `NETIF_F_NOCACHE_COPY`.
- Receive path peeks messages from `psock->ingress_msg`, copies scatterlist page bytes into the caller's iterator, supports `MSG_PEEK`, updates offsets/lengths and psock total length on consumption, uncharges receive memory for page-owned messages, and dequeues/free messages when all entries are consumed.
- skb ingress allocation checks receive buffer limits, schedules receive memory, maps skb bytes into a scatterlist via `skb_to_sgvec`, falls back to `skb_linearize` and retry if the skb is too fragmented, assigns or preserves skb socket ownership, queues a `sk_msg`, and calls `sk_psock_data_ready`.
- Backlog processing runs from a delayed work item. It protects against stale psocks, takes a psock reference, drains `ingress_skb`, restores any partial offset/length state after `-EAGAIN`, sends data to a socket or enqueues it to ingress depending on the skb's BPF ingress flag, reschedules on temporary backpressure, and disables TX/report errors on hard failures.
- Verdict paths run BPF programs under RCU with skb or sk_msg context, map `SK_PASS`/`SK_DROP` plus redirect metadata into internal verdicts, and then either pass data to local ingress, redirect to another psock's ingress backlog, or drop/eat the skb.
- Stream parser mode replaces `sk_data_ready` with a strparser-aware callback, uses an optional BPF parser to determine message length, and uses a stream verdict program on parsed skbs. Verdict mode without strparser uses socket `read_skb` to pull skbs and apply verdict logic directly.
- Drop/teardown restores the socket protocol and callbacks under `sk_callback_lock`, stops parser or verdict mode, clears TX-enabled state, queues RCU work, cancels backlog work, purges ingress skb/message queues, drops BPF programs and links, releases redirect/pair sockets, and finally drops the held socket reference.

State and persistence behavior:

- `sk_msg` state is an in-memory scatterlist ring with `start`, `end`, `curr`, `copybreak`, total `size`, optional owning `skb`, optional source `sk`, and redirect metadata set by BPF helpers. The ring entries persist until consumed, trimmed, returned, or freed.
- `sk_psock` persists as RCU-protected `sk_user_data` while a socket participates in sockmap/sockhash. It stores saved protocol/callback hooks, BPF program pointers, redirect socket references, ingress message and skb queues, backlog work state, parser state, link list, cork state, and flags such as `SK_PSOCK_TX_ENABLED`.
- Memory accounting is explicit and split by ownership. Page-backed `sk_msg` data charges socket write or receive memory and page refs; skb-backed messages use skb ownership/destructors and avoid double-freeing pages; self-ingress messages mark `msg->sk` so receive code can report bytes copied from the same socket.
- Work and callback state is transient but persistent across backpressure. `psock->work_state.len/off` records partial skb progress when forwarding returns `-EAGAIN`, allowing the delayed work to resume without duplicating already sent bytes.

Dependencies and integration points:

- Depends on `linux/skmsg.h`, `linux/skbuff.h`, scatterlists, socket memory helpers, TCP helpers, TLS RX context checks, strparser, BPF program execution, sockmap/sockhash psock helpers, and skb BPF metadata helpers.
- Integrates tightly with `skbuff.c` via `skb_to_sgvec`, `skb_linearize`, `skb_get`, `consume_skb`, `kfree_skb`, `sock_drop`, `tcp_eat_skb`, skb queue primitives, and `skb_send_sock`.
- Interposes on socket callbacks (`sk_data_ready`, `sk_write_space`) and protocol callbacks saved in `sk_psock_init`; teardown must restore those hooks before freeing psock state.
- BPF integration relies on programs stored in `psock->progs` and helpers that set `msg->sk_redir`, skb redirect target, ingress flags, strparser flags, and apply-byte limits.

Risks:

- Scatterlist ring management is error-prone: incorrect `start`/`end`/`curr`/`copybreak` updates can leak pages, double-uncharge memory, lose data, or make future copies overwrite the wrong region.
- Ownership is split between `sk_msg` pages and skb-owned data. Paths must respect `msg->skb` to avoid freeing pages owned by an skb, and must consume or drop skb refs exactly once.
- Receive/write memory accounting must match every allocation, clone, trim, return, and recv operation. Ingress allocation checks both `sk_rmem_alloc` and `sk_rcvbuf`, but self-ingress intentionally skips some accounting because the skb is already owned by the same socket.
- Backpressure and socket teardown races are sensitive. The backlog worker uses TX-enabled state, psock refcounts, socket dead checks, delayed reschedule, and RCU to avoid using freed sockets; any regression can cause stuck redirects, out-of-order delivery, or use-after-free.
- BPF programs can request redirects without valid targets or redirect to sockets whose psocks are gone or disabled. The code treats these as hard errors and drops/report errors, so test coverage must include invalid and teardown-time redirects.
- `skb_to_sgvec` can fail on highly fragmented skb/frag-list layouts. The fallback linearizes and retries, which can fail under memory pressure; callers intentionally return `-EAGAIN` to retry later rather than dropping in some paths.
- Callback interposition must be balanced. Starting parser/verdict mode saves callbacks only once; stopping must restore them and null BPF program pointers while respecting `sk_callback_lock`, RCU readers, TLS RX special handling, and socket close paths.

Test signals:

- BPF sockmap/sockhash selftests should exercise `SK_PASS`, `SK_DROP`, redirects, ingress redirects, self-ingress, parser and non-parser verdict modes, TLS stream verdict reads, and teardown while work is pending.
- Memory/refcount diagnostics should watch socket `sk_wmem_alloc`, `sk_rmem_alloc`, psock `msg_tot_len`, page refs, skb refs, and leak detectors through allocation failure, trim, partial receive, `MSG_PEEK`, clone, and redirect paths.
- Runtime signals include `trace_sk_data_ready`, psock error reporting, retry/reschedule behavior after `-EAGAIN`, queue lengths for `ingress_msg` and `ingress_skb`, and warnings from skb linearization or fragmented sg mapping failures.
- Regression cases should include max scatterlist exhaustion, mixed zero-copy and memcpy messages, trimming below `copybreak`, copying from self with `copied_from_self`, invalid BPF redirect target, dead destination socket, disabled TX state, strparser parse lengths spanning multiple skbs, and socket removal/re-addition while old psock work is scheduled.
