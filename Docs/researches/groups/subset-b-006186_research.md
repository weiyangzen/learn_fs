# subset-b-006186 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/skbuff.c -->
# sources/distributed-fs/ceph-client/net/core/skbuff.c

Purpose: implements the Linux networking core's `struct sk_buff` allocation, ownership, data mutation, scatter-gather, checksum, segmentation, queue, protocol-header manipulation, timestamp/error-queue, extension, page-pool, and deferred-free helpers. This file is the shared data-plane substrate used by device RX/TX, TCP/UDP, GRO/GSO, BPF sockmap paths, splice/sendfile-style flows, zero-copy sends, VLAN/MPLS transforms, and error reporting. In the Ceph-client source snapshot it is not Ceph-specific; Ceph networking reaches these routines through ordinary kernel socket and network-stack integration.

Important APIs/types/functions:

- Core allocation/building: `__alloc_skb`, `__netdev_alloc_skb`, `napi_alloc_skb`, `__build_skb`, `build_skb`, `build_skb_around`, `napi_build_skb`, `slab_build_skb`, `alloc_skb_with_frags`, and `skb_init` create skb shells, head buffers, NAPI caches, fclone objects, and small-head slab caches.
- Lifetime and accounting: `__kfree_skb`, `consume_skb`, `napi_consume_skb`, `kfree_skb_list_reason`, `sk_skb_reason_drop`, `skb_release_head_state`, `skb_release_data`, `kfree_skb_partial`, `skb_attempt_defer_free`, and page-pool helpers handle refcounts, destructors, drop reasons, socket accounting callbacks, page references, skb extensions, and remote CPU freeing.
- Copy/clone/COW: `skb_clone`, `skb_morph`, `skb_copy`, `__pskb_copy_fclone`, `pskb_expand_head`, `skb_expand_head`, `skb_copy_expand`, `skb_realloc_headroom`, `skb_ensure_writable`, `skb_ensure_writable_head_tail`, `skb_cow_data`, `skb_condense`, and `pskb_extract` maintain private-vs-shared head and fragment ownership.
- Data movement and layout: `skb_put`, `pskb_put`, `skb_push`, `skb_pull`, `skb_pull_data`, `skb_trim`, `___pskb_trim`, `__pskb_pull_tail`, `skb_copy_bits`, `skb_store_bits`, `skb_splice_bits`, `skb_send_sock`, `skb_send_sock_locked`, `skb_splice_from_iter`, and `skb_to_sgvec` operate over linear data, page fragments, and frag lists.
- Checksums and validation: `skb_checksum`, `skb_copy_and_csum_bits`, `skb_crc32c`, `__skb_checksum_complete_head`, `__skb_checksum_complete`, `skb_copy_and_csum_dev`, `skb_partial_csum_set`, `skb_checksum_setup`, and `skb_checksum_trimmed` recompute or validate checksum state after data/header changes.
- Segmentation/coalescing: `skb_segment_list`, `skb_segment`, `skb_split`, `skb_shift`, `skb_try_coalesce`, and `skb_append_pagefrags` implement GSO/GRO-oriented packet splitting, merging, and fragment transfer.
- Queues and diagnostics: `skb_dequeue`, `skb_dequeue_tail`, `skb_queue_head`, `skb_queue_tail`, `skb_unlink`, `skb_append`, `skb_queue_purge_reason`, `skb_rbtree_purge`, `skb_errqueue_purge`, `skb_dump`, `drop_reasons_register_subsys`, and `drop_reasons_unregister_subsys`.
- Protocol-tag transforms: `skb_vlan_untag`, `__skb_vlan_pop`, `skb_vlan_pop`, `skb_vlan_push`, `skb_eth_pop`, `skb_eth_push`, `skb_mpls_push`, `skb_mpls_pop`, `skb_mpls_update_lse`, `skb_mpls_dec_ttl`, and `__vlan_get_protocol_offset`.
- Ancillary state: `sock_queue_err_skb`, `sock_dequeue_err_skb`, `skb_clone_sk`, `skb_complete_tx_timestamp`, `__skb_tstamp_tx`, `skb_tstamp_tx`, `skb_complete_wifi_ack`, `skb_ext_add`, `__skb_ext_set`, `__skb_ext_del`, `__skb_ext_put`, `mm_account_pinned_pages`, `msg_zerocopy_realloc`, `skb_zerocopy_iter_stream`, `skb_copy_ubufs`, and `skb_zerocopy`.

Control flow:

- Allocation starts with an skb shell from the main, fclone, or per-CPU NAPI cache, then obtains head storage via small-head slab, kmalloc, page-frag, caller-provided page memory, or slab wrapping. `__finalize_skb_around` initializes `head`, `data`, `tail`, `end`, shared info, reference counts, header sentinels, allocation CPU, and kcov handle. RX helpers reserve `NET_SKB_PAD` and optional `NET_IP_ALIGN`, propagate `pfmemalloc`, and attach the receiving device.
- Freeing first drops head-side state (`dst`, destructor/socket owner, conntrack, extensions), then releases data only after shared data refs reach zero. It clears zero-copy state, unrefs page frags or page-pool netmems, frees frag lists recursively, and releases the head buffer through page-pool recycling, page-frag free, or kmalloc free. Finally it frees the skb shell either directly, through fclone refcount rules, bulk slab free, NAPI cache return, or deferred remote-CPU release.
- Clone/copy paths separate skb metadata from packet storage. `skb_clone` shares packet data and increments shared info `dataref`; `skb_copy` linearizes into a fully private buffer; `__pskb_copy_fclone` copies only the head while sharing frags; expansion paths reallocate the head and then update all relative header/checksum offsets. Any caller that mutates shared data must unclone or COW before writing.
- Linear/nonlinear mutation routines walk the linear head, page frags, and nested frag lists in order. Pull/trim operations reduce length and may free or shrink trailing frags; `__pskb_pull_tail` copies nonlinear bytes into the head and then removes the corresponding fragment references; store/copy/checksum routines recurse through frag lists while preserving offsets.
- Segmentation starts by deriving protocol and checksum capability from the network header and device features, then emits a list of new skbs whose headers are copied and whose payload either uses SG references or copied data. Frag-list GSO has special fast paths, but falls back when untrusted `SKB_GSO_DODGY` layout cannot be safely represented by page sharing.
- Queue APIs wrap the lockless list primitives in spin locks for common producers/consumers. Purge paths detach queues under lock, then free outside the lock with explicit drop reasons.
- Protocol transforms make the relevant bytes writable, move MAC metadata and payload bytes, update skb protocol/header offsets, and adjust `CHECKSUM_COMPLETE` using postpull/postpush or explicit checksum deltas.
- Error/timestamp flows clone or allocate notification skbs, fill `sock_exterr_skb`, queue to `sk_error_queue` with receive-memory accounting, and notify the socket unless it is dead.

State and persistence behavior:

- Persistent state is in memory only: skb shell fields, head buffer content, `skb_shared_info`, per-fragment page/netmem references, socket memory counters, error queues, per-CPU NAPI/free caches, and globally initialized kmem caches. There is no durable storage.
- Reference-counted state is central. `skb->users` protects the skb shell, `skb_shinfo(skb)->dataref` protects shared packet data, fclone refcounts protect paired clone slabs, page/netmem refs protect fragments, `ubuf_info` refs protect MSG_ZEROCOPY completion records, and `skb_ext` refs protect optional extension storage.
- Socket accounting is split by path: write-memory destructors such as `sock_wfree` and receive-memory destructors such as `sock_rmem_free` adjust socket counters; zero-copy pin accounting charges `user->locked_vm`; error-queue entries charge receive memory but do not use forward allocation.
- Per-CPU caches (`napi_alloc_cache`, `netdev_alloc_cache`, defer lists) intentionally persist across packet lifetimes for performance. They rely on local BH locks, CPU identity, and softirq or IPI cleanup to avoid cacheline churn.

Dependencies and integration points:

- Depends on kernel memory management, slab caches, page fragments, page pool/netmem, scatterlist, splice pipes, iov iterators, checksum helpers, textsearch, CRC32C, netdevice features, GRO/GSO, XFRM, netfilter, BPF timestamping, TLS-related socket callbacks indirectly through callers, MPTCP/MCTP/CAN/PSP skb extensions, VLAN/MPLS headers, and tracepoints.
- Provides exported symbols consumed by drivers, protocols, tunnel implementations, BPF/sockmap code, TCP/UDP paths, netfilter, qdisc/actions, error-queue/timestamping users, and zero-copy send implementations.
- Integrates with `net_hotdata` for core slab caches and sysctls such as maximum skb frags and deferred-free limits. `skb_init` must run before consumers allocate skb heads.
- `skmsg.c` directly uses `skb_to_sgvec`, `consume_skb`, `skb_queue_tail`, `skb_dequeue`, `skb_send_sock`, `skb_bpf_*` metadata, and drop helpers to bridge skb payloads into `sk_msg` and sockmap ingress queues.

Risks:

- Pointer geometry is fragile: callers must reload skb data/header pointers after `pskb_expand_head`, `__pskb_pull_tail`, `skb_cow_head`, segmentation, or carve/extract operations.
- Shared storage mistakes can corrupt packets or cause use-after-free. Mutation paths must respect `skb_shared`, `skb_cloned`, shared frags, zero-copy user buffers, managed frag refs, and page-pool recycling differences.
- Accounting errors can leak socket memory, locked user pages, page refs, extension refs, or skb shells. Particularly sensitive paths include MSG_ZEROCOPY completion, `skb_set_owner_*` interactions, error queues, deferred freeing, page-pool recycling, and fclone fast paths.
- Nonlinear packets require exhaustive offset handling across head, frags, and frag lists. Deep or malformed frag-list recursion can hit `-EMSGSIZE`, `-EFAULT`, `-ENOMEM`, or fallback linearization.
- Checksum state must track every header/data movement. VLAN/MPLS/Ethernet manipulation and trim/pull paths have explicit checksum deltas because stale `CHECKSUM_COMPLETE` or invalid `CHECKSUM_PARTIAL` offsets can produce bad packets or kernel warnings.
- GSO/GRO segmentation depends on device feature flags and packet layout. Incorrect feature decisions can create too many frags, bad checksum offload assumptions, invalid partial GSO metadata, or unsafe sharing of dodgy frag lists.
- Context constraints matter: many paths require `GFP_ATOMIC`, softirq/BH context, no hardirq destructor execution, socket lock ownership, or caller-provided synchronization for rbtrees and lockless queue primitives.

Test signals:

- Kernel selftests and runtime coverage should include skb allocation/free under KASAN/KMSAN/KCSAN, page-pool recycling, NAPI cache use, fclone clone/free order, zerocopy send completion, splice/sendmsg paths, checksum validation for IPv4/IPv6/TCP/UDP, VLAN/MPLS push/pop, GSO/GRO segmentation with and without SG/checksum offload, and BPF sockmap redirects.
- Tracepoints `trace_kfree_skb`, `trace_consume_skb`, `trace_sk_data_ready`, timestamp/error-queue observations, drop reason strings, `skb_dump`, `net_warn_ratelimited` checksum/GSO warnings, refcount warnings, and leak detectors are useful integration signals.
- Focused regression cases should include cloned skb mutation, non-readable/devmem frags, nested frag lists near recursion limits, `MAX_SKB_FRAGS` exhaustion, `pfmemalloc` RX allocation, zero-length or oversized allocations, `MSG_ZEROCOPY` abort/extend notifications, and socket teardown while notifications or deferred frees are pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/skbuff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/skmsg.c -->
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
- `skb_to_sgvec` can fail on highly fragmented skb/frag_list layouts. The fallback linearizes and retries, which can fail under memory pressure; callers intentionally return `-EAGAIN` to retry later rather than dropping in some paths.
- Callback interposition must be balanced. Starting parser/verdict mode saves callbacks only once; stopping must restore them and null BPF program pointers while respecting `sk_callback_lock`, RCU readers, TLS RX special handling, and socket close paths.

Test signals:

- BPF sockmap/sockhash selftests should exercise `SK_PASS`, `SK_DROP`, redirects, ingress redirects, self-ingress, parser and non-parser verdict modes, TLS stream verdict reads, and teardown while work is pending.
- Memory/refcount diagnostics should watch socket `sk_wmem_alloc`, `sk_rmem_alloc`, psock `msg_tot_len`, page refs, skb refs, and leak detectors through allocation failure, trim, partial receive, `MSG_PEEK`, clone, and redirect paths.
- Runtime signals include `trace_sk_data_ready`, psock error reporting, retry/reschedule behavior after `-EAGAIN`, queue lengths for `ingress_msg` and `ingress_skb`, and warnings from skb linearization or fragmented sg mapping failures.
- Regression cases should include max scatterlist exhaustion, mixed zero-copy and memcpy messages, trimming below `copybreak`, copying from self with `copied_from_self`, invalid BPF redirect target, dead destination socket, disabled TX state, strparser parse lengths spanning multiple skbs, and socket removal/re-addition while old psock work is scheduled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/skmsg.c -->
