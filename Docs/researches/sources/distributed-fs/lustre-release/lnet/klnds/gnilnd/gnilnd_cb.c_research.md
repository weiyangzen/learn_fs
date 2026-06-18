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
- Progress engines: `kgnilnd_process_fmaq()`, `kgnilnd_process_rdmaq()`, `kgnilnd_process_mapped_tx()`, `kgnilnd_process_conns()`, `kgnilnd_scheduler()`, and `kgnilnd_reaper()` are the kernel-thread loops and work handlers.

Key types are declared in `gnilnd.h` but heavily manipulated here: `kgn_tx_t`, `kgn_rx_t`, `kgn_conn_t`, `kgn_peer_t`, `kgn_device_t`, `kgn_msg_t`, `kgn_rdma_desc_t`, and `kgn_tx_ev_id_t`.

## Control Flow

Outbound control starts in `kgnilnd_send()`, which receives an LNet message. ACKs, small PUT/REPLY payloads, router-bound GETs, and short GETs become `GNILND_MSG_IMMEDIATE`; larger PUT/REPLY/GET traffic becomes a protocol-specific RDMA request, optionally using reverse-RDMA message variants according to `kgn_reverse_rdma`.

For immediate traffic, `kgnilnd_setup_immediate_buffer()` maps or copies short payload data, computes payload checksums when enabled, and `kgnilnd_launch_tx()` finds or creates a peer/connection. Existing connections call `kgnilnd_queue_tx()` directly. Missing connections place TXs on the peer queue and trigger datagram-based connection setup in `gnilnd_conn.c`.

For RDMA traffic, `kgnilnd_setup_phys_buffer()` records physical page segments, `kgnilnd_queue_rdma()` applies RDMA throttle tokens, and `kgnilnd_send_mapped_tx()` registers the memory descriptor before either sending a descriptor-bearing SMSG (`GET_REQ`, `PUT_ACK`, reverse ACK/REQ) or posting an actual RDMA transaction (`PUT_DONE`, `GET_DONE`, reverse DONE). Resource failures move TXs to map or RDMA queues for later retry.

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

The file integrates with LNet core (`lnet_parse()`, `lnet_finalize()`, `lnet_create_reply_msg()`, `lnet_set_reply_msg_len()`), GNI/KGNI APIs (SMSG, RDMA, CQ, memory registration), Linux kernel synchronization/memory primitives, connection setup code in `gnilnd_conn.c`, tunables in `gnilnd_modparams.c`, and debug helpers/macros from the rest of gnilnd.

## Risks And Edge Cases

- The code is highly concurrency-sensitive. Many paths rely on exact lock ordering among `gnd_cq_mutex`, `gnc_smsg_mutex`, `gnc_rdma_mutex`, `gnc_list_lock`, `gnd_lock`, `gnd_map_lock`, `kgn_peer_conn_lock`, and `gnd_conn_sem`.
- Message integrity depends on correct checksum mode and byte-order handling. Header checksum is computed with `gnm_cksum` cleared, then restored for debugging.
- `kgnilnd_cksum_kiov()` uses per-CPU page arrays with `get_cpu()` in the vmap path; verify CPU-preemption semantics in surrounding compatibility layers.
- `_kgnilnd_match_reply()` contains an assertion expression using assignment in `(tx->tx_id.txe_cookie = cookie)` rather than comparison, a possible latent correctness risk.
- Reverse RDMA GET alignment uses copy buffers and length rounding, so `tx_offset`, `desc_nob`, and copy-back logic are high-risk boundaries.
- Purgatory handling intentionally holds memory descriptors/mailboxes after close; leaks exhaust resources, early release risks stale remote hardware access.
- `lnet_finalize()` must be called with no relevant locks held because it can re-enter the LND via credit release.

## Test Signals

- Exercise `CFS_FAIL_GNI_*` branches for allocation failure, checksum corruption, send timeout, RDMA CQ delay/error, map failure/timeout, close send failure, receive timeout, NOOP suppression, purgatory delay, and scheduler deadline stalls.
- Cover immediate PUT/REPLY/ACK, short GET, normal RDMA PUT/GET, reverse RDMA PUT/GET, NAK on no match/truncation, CLOSE handling, duplicate/lost completions, and unmatched replies.
- Stress SMSG credit exhaustion, RDMA throttling, map queue retries, delayed connection rescheduling, and connection churn with purgatory resource accounting.
- Inject bad magic, version, source NID, connstamp, sequence number, header checksum, immediate payload checksum, and RDMA payload checksum; expected result is connection close without descriptor leaks.
