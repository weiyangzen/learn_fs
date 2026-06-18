# sources/distributed-fs/ceph-client/drivers/scsi/libfc/fc_exch.c

Purpose: implements libfc Fibre Channel exchange and sequence management: XID allocation, frame send/receive routing, response callbacks, abort/REC/RRQ recovery, reset, statistics, and exchange-manager lifecycle.

Important APIs and functions: exported APIs include `fc_seq_send()`, `fc_seq_start_next()`, `fc_seq_set_resp()`, `fc_seq_exch_abort()`, `fc_exch_done()`, `fc_seq_els_rsp_send()`, `fc_seq_assign()`, `fc_seq_release()`, `fc_exch_seq_send()`, `fc_exch_update_stats()`, `fc_exch_mgr_add/del/list_clone/alloc/free/reset()`, `fc_exch_recv()`, `fc_exch_init()`, `fc_setup_exch_mgr()`, and `fc_destroy_exch_mgr()`. Core types are private `fc_exch_mgr`, per-CPU `fc_exch_pool`, `fc_exch_mgr_anchor`, and libfc `fc_exch`/`fc_seq`.

Control flow: send of a new exchange allocates from the first matching exchange-manager anchor, chooses a per-CPU XID slot, initializes exchange/sequence, fills OX_ID/RX_ID/SEQ fields, optionally sets FCP DDP, sends via `frame_send`, and arms a timer. Receive selects an EM by XID, trims fill bytes, then dispatches BLS, originated-sequence responses, recipient responses, or new requests. BLS handles ACK, ABTS, BA_ACC/BA_RJT. Timeouts invoke upper-layer response with `-FC_EX_TIMEOUT`, clear response handlers, and send ABTS. Completed exchanges are removed from pools and released through mempool refs.

State and persistence: exchange state is live in per-CPU XID arrays, `ex_list`, refcounts, sequence counters, `esb_stat`, `state`, OXID/RXID/SID/DID/OID, response callback fields, delayed timeout work, and recovery-qualifier refs. Manager stats are atomics folded into host stats. No disk persistence.

Dependencies and integration: depends on libfc frame/local-port/FCP/rport services, mempool/slab/percpu allocation, ordered workqueue, FC-FS frame semantics, and LLDD `frame_send` callbacks. Offload drivers can add EM anchors with match functions and XID ranges.

Risks and test signals: this is concurrency-heavy. Key risks are refcount imbalance between timers, recovery qualifiers, pool holds, and callback holds; XID reuse while quarantined; response-handler races; reset while callback active; and ABTS/RRQ/REC corner cases. Test high CPU counts/XID ranges, timeout then ABTS response, REC/RRQ accept/reject, lport reset, NPIV destination lookup, DDP setup teardown on send error, invalid EOF drops, and stats increments for not-found/busy/no-free paths.
