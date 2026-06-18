# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/inline_crypto/ch_ktls/chcr_ktls.c

## Purpose

`chcr_ktls.c` implements the Chelsio T6 kernel TLS transmit offload ULD named `ch_ktls`. It plugs into `cxgb4` as `CXGB4_ULD_KTLS`, exposes `tlsdev_ops` for `tls_dev_add`/`tls_dev_del`, creates a lightweight TCB/L2T context per offloaded socket, and converts outgoing kTLS SKBs into Chelsio ULP/TLS work requests. It is TX-only in this file; RX offload is explicitly rejected.

## Important APIs, Types, and Functions

- Module and ULD entry points: `chcr_ktls_init()`, `chcr_ktls_exit()`, `chcr_ktls_uld_add()`, `chcr_ktls_uld_state_change()`, `chcr_ktls_uld_rx_handler()`, and `chcr_ktls_uld_info`.
- TLS device callbacks: `chcr_ktls_dev_add()` allocates and initializes `struct chcr_ktls_info`; `chcr_ktls_dev_del()` tears it down and clears the TLS driver state.
- Connection setup: `chcr_setup_connection()`, `chcr_ktls_act_open_req()`, `chcr_ktls_act_open_req6()`, `chcr_init_tcb_fields()`, and `chcr_set_tcb_field()`.
- CPL replies: `chcr_ktls_cpl_act_open_rpl()` handles active-open replies and inserts the final TID; `chcr_ktls_cpl_set_tcb_rpl()` completes TCB initialization.
- Transmit fast path: `chcr_ktls_xmit()` is the `cxgb4` TX handler and dispatches to full-record, short-record, plaintext, fallback, TCB-update, and TCP-option helpers.
- Work request builders: `chcr_ktls_xmit_tcb_cpls()`, `chcr_ktls_xmit_wr_complete()`, `chcr_ktls_xmit_wr_short()`, `chcr_ktls_tx_plaintxt()`, `chcr_ktls_write_tcp_options()`, and `chcr_ktls_tunnel_pkt()`.
- Crypto setup: `chcr_ktls_save_keys()` supports `TLS_CIPHER_AES_GCM_128`, computes GHASH H using `aes_prepareenckey()`/`aes_encrypt()`, and fills `struct ktls_key_ctx`.

## Control Flow

On `tls_dev_add`, the driver rejects RX direction, allocates `chcr_ktls_info`, stores port/queue/SMT metadata from `netdev_priv()`, saves AES-GCM key material, resolves the peer route and neighbor, obtains an L2T entry, takes a module reference, and sends an active-open request to create a TCB. It waits for `CPL_ACT_OPEN_RPL`, then sends TCB field updates to put the connection in core-bypass/non-offload mode, reset sequence fields, and set the L2T index. A second completion waits for `CPL_SET_TCB_RPL`; on success the pointer is stored in the TLS TX driver state.

On TX, `chcr_ktls_xmit()` validates the TLS netdev, obtains `tls_offload_context_tx`, selects the Ethernet TX queue from `queue_mapping + first_qset`, emits standalone TCP options when the hardware cannot synthesize them, then locks `tx_ctx->lock` and walks TLS records using `tls_get_record()`. It first updates TCB fields for sequence, ack, and window. Start markers are sent as plaintext. Records ending inside the SKB are either sent as complete AES-GCM records, or if only the tail is visible, the complete record is copied into a temporary SKB so the adapter can generate the tag. Middle and start fragments use AES-CTR-like short-record WRs, with prior bytes copied to align the cipher stream on a 16-byte boundary. Header-only fragments use plaintext TX_DATA WRs. If a fragment would cut into the GCM tag in an unsupported way, the path falls back to `tls_encrypt_skb()` and tunnels the software-encrypted packet with a normal Ethernet TX packet WR.

Device state changes add/remove ULD contexts from a global list under `dev_mutex`. On down, recovery, or detach, `ch_ktls_reset_all_conn()` iterates the xarray of TIDs, clears hardware resources, frees `chcr_ktls_info`, clears TLS driver state, and drops module references.

## State and Persistence Behavior

Per-connection state lives in `struct chcr_ktls_info`: socket pointer, adapter/netdev/L2T/TID/ATID, queue/channel identity, TCB tracking (`prev_seq`, `prev_ack`, `prev_win`), crypto context, IV/record number, open-state completion, and `pending_close`. This state is in-memory only and bound to the TLS context driver-state storage. Per-adapter ULD state lives in `struct chcr_ktls_uld_ctx`, with an xarray `tid_list` mapping TIDs to TLS TX contexts for cleanup. No persistent storage exists.

Synchronization is split between `tx_ctx->lock` for TLS record lookup and per-connection `tx_info->lock` for open-state/pending-close races. The global ULD list is protected by `dev_mutex`; the xarray uses `XA_FLAGS_LOCK_BH`.

## Dependencies and Integration Points

The file depends on `cxgb4` ULD infrastructure, TCB/CPL definitions, Chelsio TX descriptor helpers from the crypto/common driver, Linux kTLS (`tls_get_ctx`, `tls_get_record`, `tls_encrypt_skb`), neighbor/route/L2T APIs, IPv6 CLIP management, and adapter statistics. It integrates with the networking stack through `struct tlsdev_ops` and through `cxgb4_uld_info.tx_handler`.

## Risks and Edge Cases

- Error-path locking around `pending_close` is subtle: `chcr_ktls_dev_add()` can leave hardware replies racing with local teardown and intentionally defers freeing when a reply is pending.
- `chcr_get_nfrags_to_send()` walks fragments based on caller-supplied offsets; malformed offsets would risk out-of-range fragment access, so callers must keep record/SKB offsets consistent.
- Partial TLS record handling is complex and sensitive to GCM tag boundaries, AES block alignment, and SKB refcount ownership.
- Fallback returns `NETDEV_TX_OK` even when software encryption produces no SKB, so tests should watch packet loss counters rather than only return codes.
- Detach cleanup assumes `u_ctx` remains valid while walking `tid_list`; ordering with TLS core callbacks is an important concurrency surface.

## Test Signals

Useful coverage includes TLS TX offload setup for IPv4 and IPv6, active-open failure paths, adapter detach while `tls_dev_add` is waiting, full-record and partial-record sends, SKBs with TCP options and FIN, GSO and non-GSO traffic, fallback around tag-boundary fragments, L2T invalidation, and stats counter changes such as `ktls_tx_ctx`, `ktls_tx_fallback`, `ktls_tx_ooo`, and close/fail counters.
