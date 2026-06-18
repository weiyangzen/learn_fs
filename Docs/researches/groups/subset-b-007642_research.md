# subset-b-007642 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/gnilnd_cb.c -->
# sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/gnilnd_cb.c

## Purpose

`gnilnd_cb.c` is the main callback, send/receive, RDMA, scheduler, and timeout engine for Lustre's Cray Gemini/Aries GNI LNet driver. It bridges LNet messages to GNI short messages (SMSG/FMA), GNI RDMA posts, completion queues, connection scheduling, keepalive/timeout enforcement, and error cleanup.

The file owns most data-plane state transitions for `kgn_tx_t`, `kgn_rx_t`, `kgn_conn_t`, and `kgn_device_t`: creating transmit descriptors, mapping user pages into GNI memory descriptors, queuing work to FMA/RDMA/map queues, polling completion queues, parsing inbound protocol messages, and driving scheduler/reaper kernel threads.

## Important APIs, Types, And Functions

- Scheduling entry points: `kgnilnd_schedule_device()`, `kgnilnd_device_callback()`, `_kgnilnd_schedule_conn()`, `kgnilnd_schedule_process_conn()`, `_kgnilnd_schedule_delay_conn()`, and `kgnilnd_schedule_dgram()` coordinate device wait queues, ready connection lists, and delayed resend lists.
- TX/RX allocation and lifetime: `kgnilnd_alloc_tx()`, `kgnilnd_free_tx()`, `kgnilnd_new_tx_msg()`, `kgnilnd_alloc_rx()`, `kgnilnd_consume_rx()`, `kgnilnd_tx_done()`, and `kgnilnd_txlist_done()` manage slab-backed descriptors and LNet finalization.
- Checksums: `kgnilnd_cksum()`, `kgnilnd_cksum_kiov()`, `kgnilnd_compute_rdma_cksum()`, and `kgnilnd_verify_rdma_cksum()` implement optional header, immediate-payload, and RDMA-payload validation.
- Buffer setup and registration: `kgnilnd_setup_immediate_buffer()`, `kgnilnd_setup_phys_buffer()`, `kgnilnd_setup_rdma_buffer()`, `kgnilnd_map_buffer()`, `kgnilnd_unmap_buffer()`, `kgnilnd_mem_add_map_list()`, and `kgnilnd_mem_del_map_list()` translate LNet bvecs into SMSG payload mappings or GNI physical segment registrations.
- Sending path: `kgnilnd_send()`, `kgnilnd_launch_tx()`, `kgnilnd_queue_tx()`, `kgnilnd_queue_rdma()`, `kgnilnd_sendmsg()`, `kgnilnd_sendmsg_trylock()`, `kgnilnd_sendmsg_nolock()`, `kgnilnd_send_mapped_tx()`, and `kgnilnd_rdma()` choose immediate versus RDMA protocol and push work through FMA, RDMA, and map queues.
- Receive path: `kgnilnd_check_fma_rx()`, `kgnilnd_eager_recv()`, `kgnilnd_recv()`, `kgnilnd_setup_rdma()`, `kgnilnd_release_msg()`, `_kgnilnd_match_reply()`, `kgnilnd_complete_tx()`, and `kgnilnd_finalize_rx_done()` parse inbound SMSG protocol, match replies to outstanding TX cookies, and notify LNet.
- Completion polling: `kgnilnd_check_fma_send_cq()`, `kgnilnd_check_fma_rcv_cq()`, `kgnilnd_check_rdma_cq()`, and `kgnilnd_recv_bte_get()` handle send completions, receive CQ events, RDMA completion status, retries, and reverse-RDMA copy-buffer alignment.
- Progress engines: `kgnilnd_process_fmaq()`, `kgnilnd_process_rdmaq()`, `kgnilnd_process_mapped_tx()`, `kgnilnd_process_conns()`, `kgnilnd_scheduler()`, `kgnilnd_reaper()`, and `kgnilnd_reaper_check()` are the kernel-thread loops and work handlers.
- Close/error helpers: `kgnilnd_nak_rdma()`, `kgnilnd_send_conn_close()`, `kgnilnd_check_conn_timeouts_locked()`, `kgnilnd_check_peer_timeouts_locked()`, `kgnilnd_add_purgatory_tx()`, and `kgnilnd_check_conn_fail_loc()` enforce protocol error signaling and stale-resource handling.

Key types are declared in `gnilnd.h` but heavily manipulated here: `kgn_tx_t`, `kgn_rx_t`, `kgn_conn_t`, `kgn_peer_t`, `kgn_device_t`, `kgn_msg_t`, `kgn_rdma_desc_t`, and `kgn_tx_ev_id_t`.

## Control Flow

Outbound control starts in `kgnilnd_send()`, which receives an LNet message. ACKs, small PUT/REPLY payloads, router-bound GETs, and short GETs become `GNILND_MSG_IMMEDIATE`; larger PUT/REPLY/GET traffic becomes a protocol-specific RDMA request, optionally using reverse-RDMA message variants according to `kgn_reverse_rdma`.

For immediate traffic, `kgnilnd_setup_immediate_buffer()` maps or copies short payload data, computes payload checksums when enabled, and `kgnilnd_launch_tx()` finds or creates a peer/connection. Existing connections call `kgnilnd_queue_tx()` directly. Missing connections place TXs on the peer queue and trigger datagram-based connection setup in `gnilnd_conn.c`.

For RDMA traffic, `kgnilnd_setup_phys_buffer()` records physical page segments, `kgnilnd_queue_rdma()` applies RDMA throttle tokens, and `kgnilnd_send_mapped_tx()` registers the memory descriptor before either sending a descriptor-bearing SMSG (`GET_REQ`, `PUT_ACK`, reverse ACK/REQ) or posting an actual RDMA transaction (`PUT_DONE`, `GET_DONE`, reverse DONE). Resource failures move TXs to map or RDMA queues for later retry.

SMSG send completions are consumed by `kgnilnd_check_fma_send_cq()`. If a TX has both its SMSG completion and expected protocol reply, `kgnilnd_tx_done()` finalizes it. If the reply arrived before the send completion and set `GNILND_TX_PENDING_RDMA`, send completion launches the deferred RDMA.

Inbound SMSG receive events are detected by `kgnilnd_check_fma_rcv_cq()` and processed per connection by `kgnilnd_check_fma_rx()`. That function validates timeout, mailbox state, message checksum, magic/version, NID, connection stamp, and sequence number. It dispatches immediate and RDMA request messages into `lnet_parse()`, handles NOOP/CLOSE, matches ACK/DONE/NAK replies to outstanding TXs, launches RDMA after ACKs, and closes the connection on protocol faults.

`kgnilnd_recv()` is the LNet receive callback after `lnet_parse()`. For immediate payloads it verifies/copies payload bytes and finalizes the LNet message. For RDMA request variants it builds ACK or DONE TXs carrying sink buffer descriptors, queues them for mapping, or sends NAKs when LNet rejected/truncated the transfer.

The scheduler thread `kgnilnd_scheduler()` repeatedly checks FMA send CQ, FMA receive CQ, RDMA CQ, RDMA throttling queue, memory-map queue, and ready connections. It spins for bounded busy loops, touches watchdog/heartbeat during long active loops, then sleeps on the device wait queue. The reaper thread scans peer hash buckets, sends NOOP keepalives, times out silent connections, cancels stale peer queued TXs, triggers reconnects, and releases purgatory resources once a new connection proves active or an admin/limit condition forces detach.

## State And Persistence Behavior

This file does not persist state to disk. It maintains in-kernel live state in global `kgnilnd_data` and per-device/peer/connection structures.

TX state is represented by list membership and `tx_list_state`: allocated, peer queue, FMA queue, live FMA, RDMA throttle queue, map queue, live RDMA, dying, and back to allocated before free. `tx_state` overlays protocol waits such as waiting for SMSG completion, waiting for reply, pending RDMA, quiet error, and injected send failures.

Connection scheduling state uses atomic `gnc_scheduled` transitions among idle, wants-schedule, and process. `_kgnilnd_schedule_conn()` uses `xchg()` and a ready list reference so racing wakeups collapse into a single queued connection while preserving a reschedule intent.

Connection liveness state depends on `gnc_state`, `gnc_last_rx`, `gnc_last_rx_cq`, `gnc_last_tx`, sequence counters, NOOP timestamps, close-sent/close-received flags, error codes, and purgatory flags. Connections can continue holding GNI memory descriptors after protocol close so remote hardware cannot corrupt reused memory before deadman/peer-close conditions are satisfied.

Device state tracks scheduler readiness, map queue version, memory descriptor counts, RDMA throttle budget/deadline, completion-queue mutex delay, byte counters, and FMA/RDMA statistics. RDMA throttling is token-bucket-like: interval timers refill `gnd_rdmaq_bytes_ok` after subtracting still-outstanding `gnd_rdmaq_bytes_out`.

## Dependencies And Integration Points

The file integrates with:

- LNet core: `lnet_parse()`, `lnet_finalize()`, `lnet_create_reply_msg()`, `lnet_set_reply_msg_len()`, NID/header conversion helpers, `struct lnet_msg`, and `struct lnet_ni`.
- GNI/KGNI APIs: SMSG send/getnext/release, RDMA post, completion queue polling/get-completed/error decoding, memory registration/deregistration, and memory handles.
- Kernel primitives: spinlocks, rwlocks, mutexes, semaphores, timers, wait queues, atomics, jiffies, kmap/vmap/vunmap, bio_vec/iov_iter, slab caches, `memalloc_noreclaim_save()`, and watchdog/heartbeat hooks.
- Driver-local connection code in `gnilnd_conn.c` for datagram connection establishment, stale connection closure, purgatory release, peer lookup, and endpoint lifetime.
- Tunables from `gnilnd_modparams.c`, especially timeout, checksum mode, max immediate size, RDMA delivery mode, relaxed ordering, retransmit limits, RDMA throttling intervals, scheduler loops, peer health, reverse RDMA, and purgatory limits.
- Debug helpers from `gnilnd_debug.c` through `GNIDBG_*` macros and stringification helpers from the broader gnilnd implementation.

## Risks And Edge Cases

- The code is highly concurrency-sensitive. Many paths rely on exact lock ordering among `gnd_cq_mutex`, `gnc_smsg_mutex`, `gnc_rdma_mutex`, `gnc_list_lock`, `gnd_lock`, `gnd_map_lock`, `kgn_peer_conn_lock`, and `gnd_conn_sem`. Reordering can deadlock or expose freed TX/connection objects to CQ processing.
- Message integrity depends on correct checksum mode and byte-order handling. Header checksum is computed with `gnm_cksum` cleared, then restored for debugging. Payload and RDMA checksums have fail-injection branches and optional expensive dumps.
- `kgnilnd_cksum_kiov()` uses per-CPU page arrays with `get_cpu()` in the vmap path but does not visibly pair that exact call with `put_cpu()` in this file. Research should verify surrounding kernel/Lustre compatibility wrappers or later patches if CPU-preemption semantics matter.
- `_kgnilnd_match_reply()` contains an assertion expression using assignment in `(tx->tx_id.txe_cookie = cookie)` rather than comparison. If not intentional via macro side effect, this is a latent correctness risk because the assertion mutates the cookie while validating it.
- Reverse RDMA GET alignment uses copy buffers and length rounding. Bugs around `tx_offset`, `desc_nob`, `tx_nob_rdma`, or copy-back can corrupt payload boundaries, especially with unaligned remote addresses or non-multiple-of-four lengths.
- Purgatory handling intentionally holds memory descriptors/mailboxes after close. Leaks or premature release are both dangerous: leaks exhaust MDD/GART resources, while early release can allow stale remote hardware writes into reused memory.
- Scheduler and reaper loops depend on jiffies arithmetic, timeout tunables, and fail-injection paths. Misconfigured zero/very-low tunables can amplify busy looping or false timeout behavior.
- Error paths often close the connection after finalizing or NAKing a TX. Maintaining no-lock-held invariants before `lnet_finalize()` is critical because finalization can re-enter the LND via credit release.

## Test Signals

- Unit or fault-injection coverage should exercise all `CFS_FAIL_GNI_*` branches visible here: allocation failure, checksum corruption, send timeout, RDMA CQ delay/error, map failure/timeout, close send failure, receive timeout, NOOP suppression, purgatory delay, and scheduler deadline stalls.
- Protocol tests should cover immediate PUT/REPLY/ACK, short GET through immediate reply, normal RDMA PUT/GET, reverse RDMA PUT/GET, NAK on no match/truncation, CLOSE handling, duplicate/lost completions, and unmatched replies.
- Stress tests should drive concurrent sends to the same peer until SMSG credits return `GNI_RC_NOT_DONE`, RDMA throttling stalls, map queue retries, and delayed connection rescheduling all occur.
- Fault tests should force bad magic, version, source NID, connstamp, sequence number, header checksum, immediate payload checksum, and RDMA payload checksum; expected signal is connection close and appropriate LNet failure without descriptor leaks.
- Resource tests should track `gnd_n_mdd`, `gnd_n_mdd_held`, `gnd_nbytes_map`, `gnd_map_nphys`, eager allocation counts, and purgatory counts before and after connection churn and stack reset.
- Scheduler tests should monitor `gnd_sched_alive`, `gnd_n_schedule`, `gnd_n_yield`, NOOP timestamps, and reaper reconnect behavior under idle, active, and quiesce states.

<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/gnilnd_cb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/gnilnd_conn.c -->
# sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/gnilnd_conn.c

## Purpose

`gnilnd_conn.c` implements the connection-establishment side of the GNI LNet driver: SMSG mailbox block allocation/registration, connection request datagram packing/unpacking, datagram posting/cancel/probing, active and wildcard connection completion, NAK handling, dgram worker threads, and cleanup of datagrams during network shutdown or stack reset.

It complements `gnilnd_cb.c`: the callback file queues TXs and runs the data path once a `kgn_conn_t` is established; this file creates the underlying GNI endpoint/mailbox pairing that makes SMSG traffic possible.

## Important APIs, Types, And Functions

- SMSG mailbox setup: `kgnilnd_setup_smsg_attr()`, `kgnilnd_map_fmablk()`, `kgnilnd_alloc_fmablk()`, `kgnilnd_unmap_fmablk()`, `kgnilnd_free_fmablk_locked()`, `kgnilnd_find_free_mbox()`, `kgnilnd_setup_mbox()`, and `kgnilnd_release_mbox()`.
- Physical mailbox support: `kgnilnd_count_phys_mbox()`, `kgnilnd_allocate_phys_fmablk()`, `kgnilnd_map_phys_fmablk()`, `kgnilnd_unmap_fma_blocks()`, and `kgnilnd_free_phys_fmablk()`.
- Datagram lookup and lifetime: `kgnilnd_nid2dgramlist()`, `kgnilnd_find_dgram_locked()`, `kgnilnd_find_and_cancel_dgram()`, `kgnilnd_alloc_dgram()`, `kgnilnd_free_dgram()`, `kgnilnd_cleanup_dgram()`, and `kgnilnd_release_dgram()`.
- Connection request protocol: `kgnilnd_pack_connreq()`, `kgnilnd_unpack_connreq()`, `kgnilnd_process_connreq()`, `kgnilnd_send_nak()`, and `kgnilnd_process_nak()`.
- Datagram posting and cancellation: `kgnilnd_post_dgram()`, `kgnilnd_process_dgram()`, `kgnilnd_cancel_dgram_locked()`, `kgnilnd_probe_for_dgram()`, `kgnilnd_setup_wildcard_dgram()`, `kgnilnd_cancel_net_dgrams()`, `kgnilnd_cancel_wc_dgrams()`, `kgnilnd_cancel_dgrams()`, and `kgnilnd_wait_for_canceled_dgrams()`.
- Connection worker paths: `kgnilnd_start_connect()`, `kgnilnd_finish_connect()`, `kgnilnd_probe_and_process_dgram()`, `kgnilnd_reaper_dgram_check()`, `kgnilnd_dgram_waitq()`, `kgnilnd_start_outbound_dgrams()`, `kgnilnd_repost_wc_dgrams()`, and `kgnilnd_dgram_mover()`.

Key state types are `kgn_fma_memblock_t`, `kgn_mbox_info_t`, `kgn_dgram_t`, `kgn_connreq_t`, `kgn_conn_t`, `kgn_peer_t`, `kgn_device_t`, and GNI `gni_smsg_attr_t`.

## Control Flow

Connection setup starts when a peer has queued TXs but no established connection. The reaper in `gnilnd_cb.c` marks the peer as connecting and places it on `gnd_connd_peers`; `kgnilnd_dgram_mover()` calls `kgnilnd_start_outbound_dgrams()`, which removes peers from that list and calls `kgnilnd_start_connect()`.

`kgnilnd_start_connect()` validates that the peer is still active, transitions `gnp_connecting` through `CONNECT` to `POSTING`, and calls `kgnilnd_post_dgram()` for an active `GNILND_CONNREQ_REQ`. Posting creates a temporary connection, binds the endpoint for active connects, sets up an SMSG mailbox for request datagrams, packs source/destination NIDs, stamps, timeout, host ID, CQ ID, and SMSG attributes into `kgn_connreq_t`, then posts the datagram with a GNI ID equal to the dgram pointer.

Wildcard receive datagrams are posted by `kgnilnd_setup_wildcard_dgram()` and reposted by `kgnilnd_release_dgram()`/`kgnilnd_repost_wc_dgrams()`. They listen with `LNET_NID_ANY`, use net 0 for the local NID field, and become inbound connection requests once GNI matches them.

`kgnilnd_dgram_waitq()` waits in a blocking GNI probe path and wakes `kgnilnd_dgram_mover()`. The mover uses `kgnilnd_probe_and_process_dgram()`, which calls `kgnilnd_probe_for_dgram()` to remove a ready dgram from the hash list, test post state, and classify it as complete, pending, timeout, or terminated. Complete request datagrams go through `kgnilnd_process_connreq()`.

`kgnilnd_unpack_connreq()` validates magic, handles byte-swapping, normalizes the source NID for active matches, verifies wildcard destination network, checks protocol version, stamps, timeout, and request type, and for request packets calls `kgnilnd_set_conn_params()` to wire remote SMSG parameters into the endpoint. `kgnilnd_finish_connect()` then creates or finds the peer, rejects duplicates/stale attempts, closes older stale connections, initializes timestamps, marks the connection established, inserts it into peer and CQID hash lists, sends an initial NOOP, moves queued peer TXs to the new connection, notifies LNet, and clears reconnect backoff.

NAK datagrams use the same GNI datagram mechanism but carry an errno. `kgnilnd_process_nak()` either closes stale connections that match the NAK stamps or cancels an in-flight active dgram and adjusts reconnect state.

Mailbox allocation control starts with `kgnilnd_setup_mbox()`, which searches existing FMA blocks via `kgnilnd_find_free_mbox()` and allocates a new virtual FMA block if none are available. FMA blocks are registered with GNI and tracked with bitmaps, available/held counts, debug metadata, version counters, and device MDD/byte counters. Release can free immediately, hold for purgatory, or release a previously held mailbox; once all mailboxes in a virtual block are available it deregisters and frees the block.

## State And Persistence Behavior

No disk persistence is present. State is live kernel state in devices, peers, dgrams, conns, and FMA blocks.

FMA block state transitions include physical or virtual allocation, mapped/live, idle/unmapped, and freed. Physical blocks are preallocated and preserved across normal connection churn; virtual blocks are allocated on demand and freed when all mailboxes are available and no purgatory holds remain. `gnd_fmablk_vers` lets waiters detect that the block list changed while they were sleeping.

Mailbox state is represented by a bit array and counters: total, available, held, next available, maximum timeout, and per-mailbox debug timestamps/counters. `kgnilnd_release_mbox()` requires the endpoint to be destroyed before clearing a mailbox bit, because KGNI may still inspect SMSG blocks until EP teardown.

Dgram state transitions include `USED`, `POSTED`, `PROCESSING`, `CANCELED`, and `DONE`. Dgrams remain on NID hash lists while posted or canceled, and canceled wildcard datagrams may require a full GNI state-machine cycle before safe release. `gnd_canceled_dgrams` tracks outstanding cancellation completions.

Peer connection attempt state uses `GNILND_PEER_IDLE`, `CONNECT`, `POSTING`, `POSTED`, `NEEDS_DEATH`, and `KILL`. These states are protected by `kgn_peer_conn_lock` for peer visibility and `gnd_connd_lock` for the outbound worker queue.

Established connections inserted by `kgnilnd_finish_connect()` hold references for the peer list and CQID hash list. The dgram itself does not transfer its temporary connection reference to those tables; the function explicitly increments connection and peer refs before insertion.

## Dependencies And Integration Points

The file integrates with:

- GNI datagram and endpoint APIs: endpoint bind, postdata with ID, postdata probe/test/cancel, blocking probe wait, SMSG buffer size calculation, memory registration/deregistration, and MDD release.
- Driver-local peer/connection helpers from other gnilnd files: `kgnilnd_create_conn()`, `kgnilnd_create_peer_safe()`, `kgnilnd_add_peer_locked()`, `kgnilnd_find_peer_locked()`, `kgnilnd_find_conn_locked()`, `kgnilnd_conn_isdup_locked()`, `kgnilnd_close_stale_conns_locked()`, `kgnilnd_set_conn_params()`, `kgnilnd_peer_alive()`, `kgnilnd_peer_notify()`, `kgnilnd_peer_increase_reconnect_locked()`, `kgnilnd_add_purgatory_locked()`, and reference helpers.
- LNet NID and notification APIs: NID packing/unpacking, network number checks, `lnet_notify()`, and `struct lnet_ni`.
- Hardware service helpers from `gnilnd_hss_ops.h` for NID-to-NIC address translation.
- Tunables from `gnilnd_modparams.c`: mailbox credits, mailboxes per block, number of physical mailboxes, hash sizes, timeout, wildcard dgram count, reconnect behavior, reg-failure timeout, and purgatory limits.
- Kernel memory and sync primitives: slab caches, vmalloc/vfree wrappers, bitmaps, spinlocks, mutexes, rwlocks, wait queues, timers, atomics, jiffies, and free-page checks on Cray XT service configurations.

## Risks And Edge Cases

- Connection setup races are central. Active and wildcard dgrams can complete while peers are being deleted, NAKed, or reconnected. The code depends on precise coordination of peer refs, `gnp_connecting`, connd list membership, dgram list membership, and duplicate-connection checks.
- `kgnilnd_release_mbox()` intentionally delays reuse through purgatory. Prematurely clearing `gnm_bit_array` or freeing an FMA block while KGNI can still inspect an endpoint/mailbox risks stale hardware access.
- Datagram cancellation is asynchronous. Some canceled wildcard dgrams are immediately gone, while others return pending and need a later terminated event. Cleanup code must not free a dgram that KGNI can still return by ID.
- `kgnilnd_cancel_dgrams()` iterates only to `peer_hash_size - 1`, matching the same pattern used elsewhere. If hash bucket coverage is intended to include all buckets, this boundary deserves verification against hash allocation and wildcard bucket conventions.
- `kgnilnd_map_fmablk()` has a static registration-failure timeout shared across devices/blocks. In concurrent multi-device failure scenarios, one device's registration failures can affect assertion timing for another.
- `kgnilnd_unpack_connreq()` must return only `-EBADF` before source NID normalization when it cannot safely NAK. Changes to error ordering can cause NAKs to untrusted or wrong NIDs.
- Physical FMA blocks are special during stack reset: their memory can stay allocated while handles are cleared/remapped. Any path that treats physical and virtual blocks identically can leak or double-deregister MDDs.
- The code uses many assertions (`LASSERTF`) in paths that can be triggered by hardware or peer behavior. Production robustness depends on whether those conditions truly indicate local corruption versus recoverable remote/network faults.

## Test Signals

- Mailbox tests should allocate/release virtual and physical FMA blocks, hold and release purgatory mailboxes, exhaust mailbox blocks, and verify MDD/byte/fmablk counters return to expected values.
- Connection-race tests should force simultaneous active connects, active connect versus wildcard receive, duplicate connection request completion, peer deletion during `POSTING`, NAK arriving while connecting, and TX queue migration after establishment.
- Datagram tests should cover successful active request, successful wildcard request, NAK posting, timeout, terminated, canceled wildcard immediate `NO_MATCH`, canceled wildcard `POST_PENDING`, and shutdown wait for `gnd_canceled_dgrams`.
- Protocol validation should inject bad magic, byte-swapped requests, wrong source/destination NID, unsupported version/type, zero stamps, too-small timeout, unknown network, and malformed SMSG attributes.
- Stack reset/shutdown tests should cancel net-specific dgrams, cancel wildcard dgrams, cancel all non-wildcard dgrams, wait for cancellation completions, preserve/remap physical FMA blocks, and avoid reposting wildcards while reset/kill flags are active.
- Runtime counters and traces to watch include `gnd_ndgrams`, `gnd_nwcdgrams`, `gnd_canceled_dgrams`, `gnd_nfmablk`, `gnd_n_mdd`, `gnd_n_mdd_held`, `gnm_avail_mboxs`, `gnm_held_mboxs`, peer reconnect intervals, and LNet notify events.

<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/gnilnd_conn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/gnilnd_debug.c -->
# sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/gnilnd_debug.c

## Purpose

`gnilnd_debug.c` centralizes verbose debug formatting for GNI LNet driver messages, connections, transmit descriptors, and unexpected GNI API return codes. It exists so macros in the rest of gnilnd can emit consistent, high-context diagnostic records without duplicating formatting logic.

## Important APIs, Types, And Functions

- `_kgnilnd_debug_msg(kgn_msg_t *msg, struct libcfs_debug_msg_data *msgdata, const char *fmt, ...)` logs a caller-supplied prefix plus message pointer, magic, version, type, checksums, payload length, sequence number, and type string.
- `_kgnilnd_debug_conn(kgn_conn_t *conn, struct libcfs_debug_msg_data *msgdata, const char *fmt, ...)` logs a connection pointer, peer NID, connection state, CQID, timeout, RX/TX sequence/timing data, NOOP timing data, scheduler timing data, and device scheduler liveness.
- `_kgnilnd_debug_tx(kgn_tx_t *tx, struct libcfs_debug_msg_data *msgdata, const char *fmt, ...)` logs a TX pointer, peer NID, event/cookie IDs, message type, buffer type, message sequence, list state, queue age, flags, and retransmit count.
- `_kgnilnd_api_rc_lbug(const char *rcstr, int rc, struct libcfs_debug_msg_data *msgdata, const char *fmt, ...)` logs an unexpected GNI API return code and then calls `LBUG()`.

All functions use kernel `va_list` plus `struct va_format` and pass formatting through `libcfs_debug_msg()`.

## Control Flow

Callers pass an already populated `libcfs_debug_msg_data` and an optional formatted prefix. Each helper starts a variadic argument list, wraps it in `va_format`, emits one `libcfs_debug_msg()` record with driver-specific fields, and then ends the argument list. `_kgnilnd_api_rc_lbug()` additionally crashes through `LBUG()` after logging.

## State And Persistence Behavior

The file does not mutate protocol state except for reading live fields from `kgn_msg_t`, `kgn_conn_t`, and `kgn_tx_t`. It does not persist data; output goes to Lustre/libcfs debug logging. Values such as `jiffies` deltas and atomics are snapshots and may race benignly with live driver activity.

## Dependencies And Integration Points

This file depends on `gnilnd.h` for driver structures and stringification helpers such as `kgnilnd_msgtype2str()`, `kgnilnd_conn_state2str()`, and `kgnilnd_tx_state2str()`. It depends on libcfs debug infrastructure, Linux variadic formatting, atomics, `jiffies`, and `cfs_duration_sec()`.

The functions are normally reached through local debug macros (`GNIDBG_MSG`, `GNIDBG_CONN`, `GNIDBG_TX`, and API return-check wrappers) used throughout `gnilnd_cb.c`, `gnilnd_conn.c`, and related files.

## Risks And Edge Cases

- Debug helpers assume non-NULL `msg`/`tx`/`conn` for most field accesses. `_kgnilnd_debug_conn()` tolerates a NULL peer pointer, and `_kgnilnd_debug_tx()` tolerates missing connection/peer for the NID string, but not a NULL TX itself.
- Because the code reads live connection/TX fields without taking their locks, output can be internally inconsistent during heavy races. It is diagnostic, not an invariant snapshot.
- `_kgnilnd_api_rc_lbug()` is intentionally fatal. It should only wrap API return codes that the driver genuinely cannot recover from.
- The message debug helper has a TODO for union-specific payload detail; current output identifies type and common header only.

## Test Signals

- Build tests should verify format strings match argument types across supported kernels, especially `%pV`, `%px`/`%p`, `%llu`, and atomic/jiffies-derived fields.
- Runtime debug tests can force representative TX, RX, connection timeout, and API error paths and confirm logs include NID, state, sequence, age, and cookie fields needed to trace a failed transaction.
- Fatal-path testing should only use controlled fail injection to ensure `_kgnilnd_api_rc_lbug()` is not reachable from recoverable GNI return codes.

<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/gnilnd_debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/gnilnd_gemini.h -->
# sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/gnilnd_gemini.h

## Purpose

`gnilnd_gemini.h` provides Gemini-platform defaults and small platform hooks for the gnilnd driver. It is a hardware-profile header selected by the broader driver build to define timeout, checksum, RDMA delivery, scheduler thread, and thread-safe KGNI defaults for Gemini systems.

## Important APIs, Types, And Functions

- Constants:
  - `GNILND_BASE_TIMEOUT` is 60 seconds.
  - `GNILND_CHECKSUM_DEFAULT` is 3, enabling SMSG plus BTE/RDMA checksumming by default.
  - `GNILND_REVERSE_RDMA` is `GNILND_REVERSE_NONE`.
  - `GNILND_RDMA_DLVR_OPTION` is `GNI_DLVMODE_PERFORMANCE`.
  - `GNILND_SCHED_THREADS` is 3 when not building for `CONFIG_CRAY_COMPUTE`.
  - `GNILND_KGNI_TS_MINOR_VER` is `0x44`, documenting the KGNI minor version where thread-safe support appeared.
  - `GNILND_TS_ENABLE` is 0, disabling thread-safe KGNI use by default.
- Inline hooks:
  - `kgnilnd_register_smdd_buf(kgn_device_t *dev)` returns `GNI_RC_SUCCESS`.
  - `kgnilnd_deregister_smdd_buf(kgn_device_t *dev)` returns `GNI_RC_SUCCESS`.

## Control Flow

The header has no runtime control flow beyond two no-op inline functions. Compile-time flow enforces that `gnilnd_hss_ops.h` must be included first and conditionally defines scheduler thread count for non-compute builds.

## State And Persistence Behavior

No mutable state or persistence exists. The macros seed module parameter defaults in `gnilnd_modparams.c` and platform behavior in the rest of the driver.

## Dependencies And Integration Points

The header depends on `gnilnd_hss_ops.h` being included first, likely so hardware service and NIC/NID translation hooks are available before platform defaults are processed. It uses GNI return constants and `kgn_device_t` from the surrounding gnilnd include context.

The defaults feed directly into module parameters such as `timeout`, `checksum`, `bte_put_dlvr_mode`, `bte_get_dlvr_mode`, `sched_threads`, `reverse_rdma`, and `thread_safe`.

## Risks And Edge Cases

- The enforced include order can break refactors that include this header directly. The preprocessor error is intentional and should be preserved unless the include hierarchy changes.
- Gemini defaults favor full checksumming and performance delivery mode. Changing them affects wire validation cost, RDMA routing behavior, and compatibility expectations.
- The SMDD registration hooks are no-ops here. Code shared with other GNI platforms must not assume these functions actually register resources on Gemini.
- `GNILND_TS_ENABLE` remains disabled even though the header documents KGNI thread-safe support. Enabling thread-safe mode should be validated against the runtime KGNI minor version and lock assumptions in the driver.

## Test Signals

- Compile tests should include Gemini builds with and without `CONFIG_CRAY_COMPUTE` to verify scheduler-thread defaults and include ordering.
- Module-parameter tests should confirm Gemini defaults surface through `gnilnd_modparams.c`.
- Runtime smoke tests should verify no SMDD register/deregister side effects are expected on Gemini.

<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/gnilnd_gemini.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/gnilnd_hss_ops.h -->
# sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/gnilnd_hss_ops.h

## Purpose

`gnilnd_hss_ops.h` defines optional hardware supervisory-system/RCA integration helpers for gnilnd. When `GNILND_USE_RCA` is enabled, it exposes heartbeat and NID/NIC translation wrappers around Cray RCA APIs while preserving type checks against gnilnd/LNet expectations.

## Important APIs, Types, And Functions

Under `GNILND_USE_RCA`:

- Includes `<krca_lib.h>` for RCA types and translation functions.
- Declares external `send_hb_2_l0()` because it is not exported through a normal header.
- `kgnilnd_hw_hb()` sends a hardware heartbeat to L0 via `send_hb_2_l0()`.
- `kgnilnd_nid_to_nicaddrs(rca_nid_t nid, int numnic, nic_addr_t *nicaddrs)` type-checks RCA NID/NIC types against `__u32`, calls `krca_nid_to_nicaddrs()`, logs the translation, and returns the RCA result.
- `kgnilnd_nicaddr_to_nid(nic_addr_t nicaddr, rca_nid_t *nid)` type-checks and calls `krca_nicaddr_to_nid()`.
- `kgnilnd_setup_nic_translation(__u32 device_id)` currently returns 0.

When `GNILND_USE_RCA` is not defined, this header contributes only include guards; fallback implementations must come from other platform headers or conditional build paths.

## Control Flow

The wrappers are simple inline calls. The only branching is compile-time: RCA support either exposes heartbeat/translation functions or omits them. `kgnilnd_nid_to_nicaddrs()` logs every translation at `D_NETTRACE` level.

## State And Persistence Behavior

No local state is stored. RCA translation and heartbeat side effects occur in external HSS/RCA subsystems. The setup hook is currently a no-op, so no translation cache or persistent mapping is initialized here.

## Dependencies And Integration Points

This header depends on Linux `typecheck`, RCA headers/types/functions when enabled, libcfs/Lustre debug macros, and `__u32`. `gnilnd_conn.c` uses `kgnilnd_nid_to_nicaddrs()` before binding active datagram endpoints; `gnilnd_cb.c` uses `kgnilnd_hw_hb()` in long scheduler busy loops to avoid heartbeat failure while the thread is doing continuous work.

## Risks And Edge Cases

- The direct `extern void send_hb_2_l0(void)` binds to a symbol described as not exported in a normal way. Kernel API drift or symbol visibility changes can break builds.
- Type checks ensure compile-time compatibility with `__u32`, but runtime translation can still fail or return zero/negative values; active connection setup treats that as `-ESRCH`.
- Non-RCA builds need alternate definitions for the heartbeat and translation functions. Missing fallback coverage would appear as link or compile failures in platform combinations.
- The setup hook returning success without work can hide platforms that need real NIC translation initialization.

## Test Signals

- Compile both RCA and non-RCA configurations to ensure the expected functions are available through the platform include chain.
- Mock or fail RCA translation to verify active dgram posting handles no NIC address cleanly.
- Scheduler stress tests on RCA-enabled systems should verify repeated `kgnilnd_hw_hb()` calls do not regress heartbeat behavior.
- NID/NIC translation tests should compare RCA results with expected LNet NID address mapping for local and remote Gemini/Cray nodes.

<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/gnilnd_hss_ops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/gnilnd_modparams.c -->
# sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/gnilnd_modparams.c

## Purpose

`gnilnd_modparams.c` declares and validates module parameters for the gnilnd driver and exposes them through the global `kgnilnd_tunables` pointer table. These tunables control send credits, mailbox sizing, timeout/reconnect behavior, checksum policy, RDMA options, scheduler behavior, peer health handling, purgatory limits, and platform-specific defaults.

## Important APIs, Types, And Functions

- Module parameters include:
  - Flow control and credits: `credits`, `peer_credits`, `concurrent_sends`, `fma_cq_size`, `eager_credits`, `mbox_credits`.
  - Timeouts/reconnects: `timeout`, `min_reconnect_interval`, `max_reconnect_interval`, `hardware_timeout`, `mdd_timeout`, `sched_timeout`, `dgram_timeout`, `fast_reconn`, `to_reconn_disable`.
  - Message/RDMA sizing and checksums: `max_immediate`, `checksum`, `checksum_dump`, `vmap_cksum`, `reverse_rdma`.
  - GNI/RDMA behavior: `bte_put_dlvr_mode`, `bte_get_dlvr_mode`, `bte_relaxed_ordering`, `ptag`, `pkey`, `thread_safe`.
  - Retry/resource limits: `max_retransmits`, `rdmaq_intervals`, `max_conn_purg`, `reg_fail_timeout`, `vzalloc_no_retry`.
  - Threading/scheduling: `nice`, `sched_nice`, `sched_threads`, `loops`, `thread_affinity`.
  - Hash/list sizing and datagrams: `hash_size`, `net_hash_size`, `nwildcard`, `mbox_per_block`, `nphys_mbox`.
  - Peer-health behavior: `peer_health`, `peer_timeout`.
  - Fault behavior: `efault_lbug`.
- `kgn_tunables_t kgnilnd_tunables` stores pointers to all parameter variables so other files read current values through a uniform global structure.
- `kgnilnd_tunables_init()` validates checksum mode, bounds `max_immediate`, normalizes `mbox_per_block`, and derives or validates `concurrent_sends`.
- `kgnilnd_tunables_setup(struct lnet_ni *ni)` applies credit defaults to the LNet network when net tunables were not explicitly set, fills gnilnd-specific ioctl tunables, records `CURRENT_LND_VERSION`, and exports the effective timeout.

## Control Flow

At module load, Linux module parameter declarations make values available through module arguments/sysfs permissions. `kgnilnd_tunables_init()` is the validation gate before the driver uses them. It switches over checksum mode and emits console messages for valid enabled modes; invalid checksum modes return `-EINVAL`. It rejects `max_immediate` above `GNILND_MAX_IMMEDIATE`, clamps `mbox_per_block` to at least 1, and if `concurrent_sends` is zero sets it to `peer_credits`; otherwise it rejects values larger than `peer_credits`.

When an LNet NI is configured, `kgnilnd_tunables_setup()` copies driver credit defaults into `ni->ni_net->net_tunables` only if the LNet network tunables were not already set. It then writes gnilnd-specific tunables under `ni->ni_lnd_tunables.lnd_tun_u.lnd_gni`.

## State And Persistence Behavior

The module parameter variables are static file-scope kernel state. Many are read-only after module load due to mode `0444`; others are runtime-writable with `0644`, including reconnect intervals, checksum mode/dump level, BTE delivery modes, relaxed ordering, RDMA throttle intervals, loop count, vmap checksum, mailbox block size/credits, MDD/scheduler/dgram timeouts, reverse RDMA, fault LBUG behavior, fast reconnect, purgatory limit, reg-failure timeout, timed-out reconnect disable, and vmalloc retry behavior.

`kgnilnd_tunables` stores pointers, not copies, so runtime-writable parameters affect code paths that read through the pointer table after the write. No disk persistence is implemented; sysfs/module parameter persistence depends on normal kernel/module configuration outside this file.

## Dependencies And Integration Points

The file depends on `gnilnd.h` for `kgn_tunables_t`, constants, `kgnilnd_timeout()`, and gnilnd/LNet tunable structures. Platform defaults from headers such as `gnilnd_gemini.h` feed initial values for timeout, checksum, RDMA delivery mode, scheduler threads, reverse RDMA, and thread-safe KGNI.

Other gnilnd files consume these parameters heavily:

- `gnilnd_cb.c` reads timeout, checksum, max immediate, RDMA delivery/ordering, retry limits, RDMA throttling, scheduler loops/timeouts/nice, reverse RDMA, eager credits, purgatory, and failure behavior.
- `gnilnd_conn.c` reads mailbox sizing/credits, physical mailbox count, wildcard datagram count, hash size, timeout, register-failure timeout, and nice values.
- Driver startup and LNet integration use `ptag`, `pkey`, `thread_safe`, hash sizes, thread counts, affinity, and peer-health settings.

## Risks And Edge Cases

- Runtime-writable tunables can change while data-plane code is executing. Many paths intentionally reread checksum and RDMA options at send time, but changes to sizing/timeouts can create mixed behavior across existing connections.
- `eager_credits` is described as "# eager buffers" but defaults to `256 * 1024`, a large count-like limit. Misconfiguration can cause high memory pressure for eager copies.
- `max_immediate` is rejected above `GNILND_MAX_IMMEDIATE`, but very small values can force more RDMA and memory registration pressure.
- `concurrent_sends` is only validated against `peer_credits`; comments say it sizes mailbox buffers rather than enforcing a hard send cap, so operators may assume stronger limiting than the code provides.
- `checksum` can be changed at runtime. Mixed enabled/disabled endpoints are tolerated by warnings around missing checksums, but fault isolation may be harder during live changes.
- Parameters with `0644` permissions that influence resource release or fatal behavior (`efault_lbug`, `reg_fail_timeout`, `to_reconn_disable`, `max_conn_purg`) can materially change recovery characteristics on a live system.
- Hash-size parameters are expected to be prime by description but not validated as prime here.

## Test Signals

- Module-load tests should validate invalid checksum values, excessive `max_immediate`, `mbox_per_block < 1`, `concurrent_sends == 0`, and `concurrent_sends > peer_credits`.
- LNet setup tests should verify NI credit defaults are applied only when net tunables were not user-set and that gnilnd ioctl tunables report version and timeout.
- Runtime sysfs tests should flip writable parameters such as checksum mode, checksum dump, RDMA delivery mode, rdmaq intervals, reverse RDMA, fast reconnect, and purgatory limit while traffic is active, then verify no crashes or counter leaks.
- Configuration tests should cover platform defaults from Gemini/compute versus service builds and KNC-specific `ptag` selection under `CONFIG_MK1OM`.
- Stress tests should combine low credits, small `max_immediate`, low retransmit limits, low mailbox counts, and small purgatory limits to expose resource exhaustion paths in `gnilnd_cb.c` and `gnilnd_conn.c`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/gnilnd_modparams.c -->
