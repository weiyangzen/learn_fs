# Research Group subset-b-004407

This grouped report covers Chelsio inline TLS/kTLS, common Chelsio connection/page-pod helpers, and Cirrus Ethernet build configuration files. Each source file section is delimited for reconciliation into source-tree-aligned per-file research artifacts.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/inline_crypto/ch_ktls/chcr_ktls.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/inline_crypto/ch_ktls/chcr_ktls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/inline_crypto/ch_ktls/chcr_ktls.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/inline_crypto/ch_ktls/chcr_ktls.h

## Purpose

`chcr_ktls.h` declares the private data structures, constants, inline accessors, and CPL handler type used by the Chelsio kTLS TX offload driver. It bridges Linux TLS offload driver-state storage with Chelsio adapter/TCB/L2T resources.

## Important APIs, Types, and Functions

- `struct chcr_ktls_info` is the per-TX-offload connection object. It stores socket, adapter, L2T, netdev, completion, key context, record/IV state, TCB sequence/cache fields, queue/channel/port identity, open state, and pending-close flag.
- `struct chcr_ktls_ctx_tx` is the small object stored in `TLS_DRIVER_STATE_SIZE_TX`; it points to `chcr_ktls_info`.
- `struct chcr_ktls_uld_ctx` stores per-ULD adapter data: list linkage, copied `cxgb4_lld_info`, TID xarray, and detach flag.
- `enum ch_ktls_open_state` defines `CH_KTLS_OPEN_SUCCESS`, `CH_KTLS_OPEN_PENDING`, and `CH_KTLS_OPEN_FAILURE`.
- Inline accessors `__chcr_get_ktls_tx_info()`, `chcr_get_ktls_tx_info()`, and `chcr_set_ktls_tx_info()` safely cast TLS driver state and enforce size with `BUILD_BUG_ON`.
- `chcr_get_first_rx_qid()` fetches the first RX queue ID from the KTLS ULD handle saved on the adapter.
- `chcr_handler_func` is the CPL handler signature used by `chcr_ktls.c`.

## Control Flow

This header does not implement protocol flow directly. It defines how `chcr_ktls.c` stores and retrieves per-connection offload state from `struct tls_context`, how ULD receive handlers reference per-adapter state, and how the first RX queue is selected for control replies.

## State and Persistence Behavior

All state is volatile kernel memory. The design relies on TLS core driver-state memory to hold a pointer, while the actual `chcr_ktls_info` object is allocated/freed by add/delete and detach paths. `chcr_ktls_uld_ctx.detach` is a coarse state bit used to suppress normal deletion during adapter teardown.

## Dependencies and Integration Points

The header includes Chelsio adapter, CPL, TCB, L2T, common crypto, ULD, and CLIP definitions. It also depends on Linux TLS offload context layout via the functions used in inline accessors.

## Risks and Edge Cases

- The TLS driver-state area only stores a pointer; use-after-free prevention depends on the lifecycle in `chcr_ktls.c`.
- `chcr_get_first_rx_qid()` returns `-1` when the ULD handle is absent; callers must treat this as setup failure.
- `chcr_ktls_info` stores both connection state and cached TX state, so partial initialization must be cleaned carefully on errors.

## Test Signals

Compile-time coverage should catch driver-state size regressions through `BUILD_BUG_ON`. Runtime tests should validate that `tls_dev_add` fails cleanly when no KTLS ULD context exists and that detach clears TLS driver state for all TIDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/inline_crypto/ch_ktls/chcr_ktls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/inline_crypto/chtls/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/inline_crypto/chtls/Makefile

## Purpose

This Makefile builds the Chelsio inline TLS TOE driver object `chtls.o` when `CONFIG_CRYPTO_DEV_CHELSIO_TLS` is enabled.

## Important APIs, Types, and Functions

- `ccflags-y` adds include paths for `drivers/net/ethernet/chelsio/cxgb4` and `drivers/crypto/chelsio`.
- `obj-$(CONFIG_CRYPTO_DEV_CHELSIO_TLS) += chtls.o` controls module/object inclusion.
- `chtls-objs := chtls_main.o chtls_cm.o chtls_io.o chtls_hw.o` defines the composite object members.

## Control Flow

Kbuild includes this directory's object only when the Chelsio TLS config option is selected. The resulting `chtls.o` links the main ULD registration code, connection manager, socket I/O paths, and hardware key/TCB helpers.

## State and Persistence Behavior

There is no runtime state in this file. Build state is derived from Kconfig and Kbuild.

## Dependencies and Integration Points

The include paths are required for Chelsio adapter/ULD headers and crypto helper headers used by the four C files. It integrates with the kernel build system and the `CONFIG_CRYPTO_DEV_CHELSIO_TLS` option.

## Risks and Edge Cases

Missing include paths would break access to cxgb4 and Chelsio crypto headers. Adding new source files to the driver requires updating `chtls-objs`; otherwise functions may compile individually but not link into the driver.

## Test Signals

Build tests with `CONFIG_CRYPTO_DEV_CHELSIO_TLS=m` and `=y` should produce `chtls.o` with all four member objects. A config with the option disabled should omit the driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/inline_crypto/chtls/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/inline_crypto/chtls/chtls.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/inline_crypto/chtls/chtls.h

## Purpose

`chtls.h` is the central private header for the Chelsio inline TLS TOE driver. It defines TLS key-context bitfields, device/socket state objects, SKB control-block layouts, helper macros, and cross-file function prototypes used by `chtls_main.c`, `chtls_cm.c`, `chtls_io.c`, and `chtls_hw.c`.

## Important APIs, Types, and Functions

- `struct chtls_dev` represents one Chelsio TLS TOE device and stores `tls_toe_device`, LLDI, ports, TID tables, response SKB cache, deferred queue, key map, listen hash, and sizing limits.
- `struct chtls_sock` is per-offloaded socket state: socket pointer, device, L2T/egress device, TX queues, WR credit accounting, TID, qid/channel/port metadata, flags, windows, and embedded `struct chtls_hws`.
- `struct chtls_hws` stores TLS hardware state: receive TLS queue, TX/RX key IDs, record parameters, key length, maximum fragment size, sequence number, and copied TLS crypto info.
- `struct key_map` tracks hardware TLS key-context slots with a bitmap and lock.
- `struct listen_info`, `struct listen_ctx`, and `struct chtls_listen` support passive-open registration.
- SKB control blocks: `wr_skb_cb`, `blog_skb_cb`, and `ulp_skb_cb` attach WR chaining, backlog callbacks, sequence flags, and TLS metadata to `skb->cb`.
- Inline helpers include `to_chtls_dev()`, `csk_set_flag()`, `csk_reset_flag()`, `csk_flag()`, `process_cpl_msg()`, refcount helpers, and `send_or_defer()`.
- Prototypes expose listener, socket, send/receive, TCB, key, and WR functions across implementation files.

## Control Flow

The header establishes shared conventions for CPL processing. `process_cpl_msg()` resets SKB headers, locks the socket with bottom halves, and either invokes a handler immediately or queues the SKB to the socket backlog when user context owns the socket. TX-side files use `ULP_SKB_CB()` and `WR_SKB_CB()` to track queued WRs and application data. Connection-manager files use `BLOG_SKB_CB()` to reroute deferred processing through a listener or child socket backlog.

## State and Persistence Behavior

All state is in-memory and socket/device scoped. `chtls_sock` lifetime is tied to socket user-data and a `kref`; `chtls_dev` lifetime is tied to `tls_toe_device.kref`. WR credits, TID IDs, TLS key IDs, receive queues, and listen hashes are maintained in these structures and are reset on close/detach.

## Dependencies and Integration Points

The header depends on Linux crypto, TLS, TCP, `tls_toe`, Chelsio CPL/FW APIs, L2T, ULD, and Chelsio crypto core headers. It integrates with Linux socket protocol replacement, TLS setsockopt/getsockopt, and `cxgb4` offload send helpers.

## Risks and Edge Cases

- `skb->cb` is shared storage; every path must agree on which control block layout is active.
- `csk_flag()` checks `CSK_CONN_INLINE` before reading flags; callers that already know inline state use `csk_flag_nochk()`.
- The header contains bitfield macros for hardware layouts; incorrect shifts/masks would be hard to detect without hardware tests.
- Device/socket object lifetimes depend on RCU socket user-data and refcount discipline across multiple files.

## Test Signals

Build tests should cover IPv4-only and IPv6-enabled configurations. Runtime signals include clean protocol replacement/restoration, correct socket backlog handling under owned sockets, WR credit accounting consistency, and TLS key allocation/free balance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/inline_crypto/chtls/chtls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/inline_crypto/chtls/chtls_cm.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/inline_crypto/chtls/chtls_cm.c

## Purpose

`chtls_cm.c` implements Chelsio TLS TOE connection management. It owns passive-open listener setup, child socket creation, accept queue movement, CPL dispatch for connection/data/close/abort messages, receive queue demultiplexing, close/disconnect/shutdown/destroy protocol operations, and WR acknowledgement handling.

## Important APIs, Types, and Functions

- Socket allocation/lifetime: `chtls_sock_create()`, `chtls_sock_release()`, `chtls_release_resources()`, and `chtls_destroy_sock()`.
- Listener management: `chtls_listen_start()`, `chtls_listen_stop()`, listen hash helpers, `chtls_reset_synq()`, and PASS_OPEN/CLOSE_LISTSRV reply handlers.
- Passive accept: `chtls_pass_accept_req()`, `chtls_pass_accept_request()`, `chtls_recv_sock()`, `chtls_pass_accept_rpl()`, `chtls_pass_establish()`, and accept queue helpers.
- Close/abort: `chtls_close()`, `chtls_disconnect()`, `chtls_shutdown()`, `chtls_close_conn()`, `chtls_send_reset()`, `chtls_send_abort()`, `chtls_peer_close()`, `chtls_close_con_rpl()`, `chtls_abort_req_rss()`, and `chtls_abort_rpl_rss()`.
- RX data/TLS: `chtls_rx_data()`, `chtls_recv_data()`, `chtls_rx_pdu()`, `chtls_recv_pdu()`, `chtls_rx_cmp()`, and `chtls_rx_hdr()`.
- ACK/TCB replies: `chtls_wr_ack()`/`chtls_rx_ack()` and `chtls_set_tcb_rpl()`.
- Exported dispatch table: `chtls_handlers[NUM_CPL_CMDS]`.

## Control Flow

Listener start resolves a Chelsio-owned netdev for the listening address, checks adapter initialization, allocates a `listen_ctx`, allocates an STID, records it in the listen hash, optionally installs an IPv6 CLIP entry, and calls `cxgb4_create_server()` or `cxgb4_create_server6()`. Listener stop removes the hash entry, resets SYN-received children, requests server removal, releases CLIP entries, and disconnects offloaded accept-queue children.

On `CPL_PASS_ACCEPT_REQ`, the handler validates the STID/TID, then processes the request under the listener lock or backlog. It allocates a Linux request socket, parses Ethernet/IP/TCP headers, records peer/local tuple and TCP options, creates a child socket with `tcp_create_openreq_child()`, resolves route/neighbour/L2T, fills `chtls_sock` fields, installs `chtls_backlog_rcv`, chooses RSS/TX queues, inserts the TID, and sends a PASS_ACCEPT_RPL through L2T. When `CPL_PASS_ESTABLISH` arrives, the child moves to `TCP_ESTABLISHED`, receives WR credits, and is either added to the parent accept queue or scheduled for reaping if the queue is full.

RX data CPLs are demultiplexed by TID. Plain `CPL_RX_DATA` strips CPL/RSS headers, updates TCP receive state, handles urgent pointers, queues the SKB on `sk_receive_queue`, and wakes readers. TLS payload CPLs are queued on `tlshws.sk_recv_queue`; TLS completion/header CPLs synthesize a TLS header SKB, mark errors as `CONTENT_TYPE_ERROR`, pair the header with queued payload, advance `rcv_nxt`, and wake readers.

Close and abort handling mirrors TCP state transitions with Chelsio CPLs. Local close may send `CPL_CLOSE_CON_REQ` or abort depending on data loss, SYN state, and linger. Peer close and close replies move sockets through CLOSE_WAIT, CLOSING, FIN_WAIT2, LAST_ACK, TIME_WAIT, or TCP_CLOSE and release hardware resources. Abort requests send abort replies, tear down TIDs/L2T/queues, and complete sockets; SYN_RECV aborts are coordinated through the listener backlog.

WR acknowledgements return credits, retire WR SKBs from the outstanding list by credit count stored in `skb->csum`, update `snd_una`, clear wait/failover flags, and push more queued frames if possible.

## State and Persistence Behavior

State is volatile and divided among listener hash entries, `listen_ctx` SYN queues, `request_sock` objects, child sockets, and `chtls_sock`. Hardware identity is tracked by STID/TID tables in `cdev->tids`. WR credits are maintained in `csk->wr_credits`, `wr_unacked`, `wr_max_credits`, `wr_nondata`, and the WR list. Passive children use `csk->passive_reap_next` both for request-socket linkage and reap-list linkage depending on state.

Synchronization uses socket locks, BH disabling, listener/device spinlocks, a global reap-list spinlock, and backlog callbacks when sockets are owned by user context.

## Dependencies and Integration Points

The file integrates with Linux TCP internals (`tcp_create_openreq_child`, request queues, timewait, port inheritance), TLS context destructors, IPv4/IPv6 routing and neighbour APIs, VLAN real devices, Chelsio L2T/TID/STID APIs, Chelsio CPL/FW formats, and `chtls_io.c`/`chtls_hw.c` for TX flow-control, push, key freeing, and TCB quiesce.

## Risks and Edge Cases

- Passive-open handling has many lifetime edges: request socket, child socket, listener, STID/TID, L2T, module ref, and accept queue state must unwind in the right order.
- `passive_reap_next` is reused for multiple logical links, increasing the risk of stale linkage if a path skips cleanup.
- RX TLS header/payload pairing assumes completion and payload queues remain ordered; missing payloads queue the header alone.
- `alloc_ctrl_skb()` can reuse cached SKBs by incrementing refcount; misuse could corrupt abort messages.
- Some allocations use `__GFP_NOFAIL`, which avoids failed control sends but can block under memory pressure.

## Test Signals

Exercise listen start/stop for IPv4/IPv6, duplicate listen attempts, CLIP failure, accept queue full, SYN queue reset, passive-open ARP failure, child establishment, TLS RX header/payload/error records, local close with data pending, peer close across FIN states, abort request/reply races, WR credit retirement, and detach while listeners/children exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/inline_crypto/chtls/chtls_cm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/inline_crypto/chtls/chtls_cm.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/inline_crypto/chtls/chtls_cm.h

## Purpose

`chtls_cm.h` defines connection-manager constants, TCB bitfield helpers, TX header sizing, TLS content type values, deferred SKB metadata, request-socket helpers, accept queue macros, and WR queue primitives used by the Chelsio inline TLS connection manager and I/O code.

## Important APIs, Types, and Functions

- TCB/TLS field macros include `TCB_ULP_TYPE_*`, `TCB_ULP_RAW_*`, `TF_TLS_*`, and `TF_RX_QUIESCE_*`.
- Window and payload constants include `MAX_RCV_WND`, `MIN_RCV_WND`, `MAX_MSS`, `TX_HEADER_LEN`, `TX_TLSHDR_LEN`, and `TXDATA_SKB_LEN`.
- TLS record content enums map TLS header types to Chelsio SFO types.
- `struct deferred_skb_cb` and `DEFERRED_SKB_CB()` carry deferred handler state in `skb->cb`.
- `chtls_defer_reply()` is declared for deferred processing.
- `chtls_init_rsk_ops()` initializes request-socket ops for IPv4/IPv6 protocol replacements.
- Queue helpers include `chtls_free_skb()`, `chtls_kfree_skb()`, `chtls_reset_wr_list()`, `enqueue_wr()`, and `dequeue_wr()`.

## Control Flow

The header provides small inline pieces used in larger flows. `chtls_init_rsk_ops()` wires new protocol structures to existing TCP request socket slabs. `enqueue_wr()` and `dequeue_wr()` maintain the linked list of outstanding work requests, taking an SKB reference when enqueued and clearing `next_wr` on dequeue. Wakeup and request-address helpers are used during passive accept and receive processing.

## State and Persistence Behavior

No persistent state is stored here. The macros operate on socket queues, SKB control blocks, request sockets, and `chtls_sock` WR list pointers. State is in memory and tied to sockets/SKBs.

## Dependencies and Integration Points

This header depends on `chtls.h` structures and Linux TCP request-socket internals. It provides glue between Chelsio CPL/TLS hardware fields and the TCP socket/request APIs used by `chtls_cm.c`, `chtls_io.c`, and `chtls_hw.c`.

## Risks and Edge Cases

- The TLS error macros contain typo-prone shift references; hardware error reporting should be tested carefully.
- `enqueue_wr()` increments SKB references, so every successful dequeue path must free or put exactly once.
- `ACCEPT_QUEUE(sk)` reaches into request queue internals; kernel API changes can break assumptions.
- Inline free helpers steal dst refs before unlinking; callers must pass SKBs that really are on the expected queue.

## Test Signals

Tests should cover WR list enqueue/dequeue under credit ACKs, request-socket allocation/destruction, accept queue unlinking, RX queue free paths, and TCB quiesce/key field programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/inline_crypto/chtls/chtls_cm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/inline_crypto/chtls/chtls_hw.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/inline_crypto/chtls/chtls_hw.c

## Purpose

`chtls_hw.c` implements Chelsio TLS hardware programming helpers: TCB field updates, receive quiesce control, key-context slot bitmap management, TLS key-context construction, and memory-write work requests that install RX/TX TLS keys into adapter key memory.

## Important APIs, Types, and Functions

- TCB helpers: `chtls_set_tcb_field()`, `chtls_set_tcb_field_rpl_skb()`, `chtls_set_tcb_keyid()`, `chtls_set_tcb_seqno()`, `chtls_set_tcb_quiesce()`, and `chtls_set_quiesce_ctrl()`.
- Key map: `chtls_init_kmap()` initializes `cdev->kmap`; `get_new_keyid()` allocates a bitmap slot; `free_tls_keyid()` releases RX/TX slots; `keyid_to_addr()` converts a key ID to hardware memory address units.
- Key context: `chtls_key_info()` supports TLS 1.2 AES-GCM-128 and AES-GCM-256, computes GHASH H, fills Chelsio key context headers, copies salt/key/H, and clears the copied key.
- TX SCMD setup: `chtls_set_scmd()` sets TLS AES-GCM command fields.
- Public key install: `chtls_setkey()` flushes pending TX data for TX keys, allocates a key slot, builds `FW_ULPTX_WR`/`ULP_TX_MEM_WRITE`, enqueues/sends it, then programs TCB fields for RX keys or sets TX sequence state for TX keys.

## Control Flow

For `setsockopt(SOL_TLS, TLS_TX/TLS_RX)`, `chtls_main.c` copies crypto info into `csk->tlshws.crypto_info` and calls `chtls_setkey()`. The key path reserves a hardware key slot, builds a memory-write request containing a key context, and sends it through the offload queue while charging WR credits. For RX keys, it also writes the key ID into TCB word 31, enables TLS ULP raw bits, resets sequence number, and clears RX quiesce. For TX keys, it initializes `tx_seq_no` and records the key ID for later TX WRs.

## State and Persistence Behavior

Key-slot state is volatile in `cdev->kmap.addr` under `kmap.lock`. Socket TLS hardware state is in `csk->tlshws.rxkey`, `txkey`, `keylen`, `scmd`, `crypto_info`, and `tx_seq_no`. WR credit state is updated when key memory-write and TCB WRs are enqueued. Key material copied from userspace is zeroed from the stored crypto-info key area after constructing the key context.

## Dependencies and Integration Points

The file depends on Chelsio CPL/ULPTX/FW layouts, TCB field definitions, Linux TLS crypto-info structs, AES helpers, and `chtls_io.c` WR queue functions. It integrates with `chtls_destroy_sock()` via `free_tls_keyid()` and with `chtls_sendmsg()` through the `txkey` state that enables TLS TX WR generation.

## Risks and Edge Cases

- `cdev->kmap.available` is initialized to the number of longs, not decremented on allocation; capacity enforcement is actually via `find_first_zero_bit()`.
- Partial failure in `chtls_setkey()` after key allocation calls `free_tls_keyid()`, which frees both RX and TX keys, not only the just-failed direction.
- Key install consumes WR credits; callers depend on enough credits being present before key programming.
- RX TCB setup requires several sequential writes; failure after some writes can leave hardware partially configured.

## Test Signals

Test AES-GCM-128 and AES-GCM-256 for TX and RX, key memory exhaustion, setsockopt after abort shutdown, pending TX flush before TX key replacement, RX quiesce clearing, key ID reuse after socket destroy, and malformed TLS version/cipher rejection through the caller.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/inline_crypto/chtls/chtls_hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/inline_crypto/chtls/chtls_io.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/inline_crypto/chtls/chtls_io.c

## Purpose

`chtls_io.c` implements the socket send and receive paths for Chelsio inline TLS TOE sockets. It builds flow-control, plain offload TX, and TLS TX work requests; manages SKB TX queues and WR credits; copies user data into SKBs/pages; handles TLS record-type control messages; returns RX credits; and implements TLS/plain receive behavior.

## Important APIs, Types, and Functions

- TX setup: `send_tx_flowc_wr()`, `flowc_wr_credits()`, `send_flowc_wr()`, and `tcp_state_to_flowc_state()`.
- TLS TX WR helpers: `tls_copy_ivs()`, `tls_copy_tx_key()`, `tls_tx_data_wr()`, `chtls_expansion_size()`, `make_tlstx_data_wr()`, and `chtls_wr_size()`.
- Plain TX WR helpers: `make_tx_data_wr()`, `is_ofld_imm()`, `calc_tx_flits()`, and `chtls_push_frames()`.
- Queue/application send: `chtls_sendmsg()`, `chtls_tcp_push()`, `skb_entail()`, `get_tx_skb()`, `get_record_skb()`, `tx_skb_finalize()`, and `chtls_splice_eof()`.
- Memory waits: `csk_mem_free()` and `csk_wait_memory()`.
- RX credit/read: `chtls_cleanup_rbuf()`, `send_rx_credits()`, `chtls_recvmsg()`, `chtls_pt_recvmsg()`, and `peekmsg()`.
- TLS control message parsing: `chtls_proccess_cmsg()` handles `TLS_SET_RECORD_TYPE`.

## Control Flow

`chtls_sendmsg()` locks the socket, waits for connection establishment if needed, checks errors/shutdown, then loops over the user iterator. When TLS TX is enabled and no record is active, it parses optional TLS control messages, sets record type, and starts a record with `tlshws.txleft`. It appends data to an existing tail SKB when possible or allocates a plain/TLS SKB with enough reserved headroom for WR headers, key memory reference, and IVs. Data is copied into linear tailroom, page fragments, or spliced from pages. Full/MSS-limited SKBs are finalized, `write_seq` advances, TLS `txleft` decreases, and push decisions honor corking, `MSG_MORE`, Nagle, and send buffer pressure.

`chtls_push_frames()` is the central TX drain. It ensures a FLOWC WR is sent before first data, computes immediate vs scatter-gather format, accounts WR credits, enqueues SKBs on the outstanding WR list, builds TLS or plain TX WR headers when needed, advances `snd_nxt`, sets completion requests, and sends through L2T. It stops when credits are insufficient or the head SKB is held.

For receives, `chtls_recvmsg()` delegates OOB to TCP, PEEK to `peekmsg()`, busy-polls when possible, and selects `chtls_pt_recvmsg()` when RX TLS offload is active. Plain receive copies queued SKB payloads from `sk_receive_queue`, handles urgent data, frees consumed SKBs, and returns RX credits. TLS receive treats TLS header SKBs specially: it emits `TLS_GET_RECORD_TYPE` cmsgs, suppresses copying the synthetic TLS header to user data, tracks payload length through `hws->rcvpld`, and increments TLS RX stats for payload consumption.

## State and Persistence Behavior

TX state is in `csk->txq`, WR list pointers, `wr_credits`, `wr_unacked`, `wr_nondata`, `CSK_TX_*` flags, `tp->write_seq`, `tp->snd_nxt`, and `tlshws.txleft/type/tx_seq_no`. RX state is in `tp->copied_seq`, `tp->rcv_wup`, `tp->rcv_wnd`, `hws->copied_seq`, `hws->rcvpld`, and receive queues. There is no persistent storage.

## Dependencies and Integration Points

This file depends on Linux socket send/receive APIs, iterator copying/splicing, TCP cork/Nagle/urgent handling, busy-poll support, Chelsio WR/CPL definitions, L2T send, and key state populated by `chtls_hw.c`. It is installed as socket operations by `chtls_main.c`.

## Risks and Edge Cases

- `chtls_push_frames()` temporarily increments `nr_frags` for IV DSGL accounting and must undo it when credits are insufficient.
- TLS IV allocation can fail after SKB state has been prepared; callers largely rely on later behavior rather than explicit propagation from `make_tlstx_data_wr()`.
- Send memory accounting spans `sk_wmem_queued`, `skb->truesize`, page caching in `TCP_PAGE`, and Chelsio WR credits.
- `chtls_pt_recvmsg()` peeks at the next SKB after freeing one and checks its flags; empty queue handling around `next_skb` is a sensitive edge.
- `chtls_proccess_cmsg` spelling is nonstandard but local; behavior rejects `MSG_MORE` with record-type cmsg.

## Test Signals

Exercise plain and TLS send with immediate and SG WRs, large records split by MFS, `MSG_MORE`, cork, OOB, splice pages, page-frag coalescing, no WR credits, send buffer exhaustion, TLS record type cmsgs, RX TLS header/payload pairing, `MSG_PEEK`, busy-poll receive, urgent data, RX credit thresholds, and socket error/shutdown handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/inline_crypto/chtls/chtls_io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/inline_crypto/chtls/chtls_main.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/inline_crypto/chtls/chtls_main.c

## Purpose

`chtls_main.c` is the module and ULD integration layer for the Chelsio inline TLS TOE driver. It registers with `cxgb4`, registers a `tls_toe_device`, manages device lifetimes, dispatches RX CPLs to `chtls_handlers`, installs TLS-aware socket protocol operations, and handles SOL_TLS setsockopt/getsockopt for hardware keys.

## Important APIs, Types, and Functions

- Module lifecycle: `chtls_register()` and `chtls_unregister()`.
- ULD hooks: `chtls_uld_add()`, `chtls_uld_state_change()`, `chtls_uld_rx_handler()`, and `chtls_uld_info`.
- TLS TOE registration: `chtls_register_dev()`, `chtls_free_uld()`, `chtls_dev_release()`, and `chtls_free_all_uld()`.
- Listen integration: notifier registration, `listen_notify_handler()`, `chtls_start_listen()`, `chtls_stop_listen()`, and `listen_backlog_rcv()`.
- RX dispatch: `copy_gl_to_skb_pkt()`, `chtls_recv_packet()`, `chtls_recv_rsp()`, and `chtls_recv()`.
- Socket operations: `chtls_install_cpl_ops()` and `chtls_init_ulp_ops()`.
- TLS options: `chtls_setsockopt()`, `do_chtls_setsockopt()`, `chtls_getsockopt()`, and `do_chtls_getsockopt()`.

## Control Flow

On module init, the driver copies base TCP protocol structures, overrides close/disconnect/destroy/shutdown/send/receive/TLS option methods, initializes request-socket ops, registers a listen notifier, and registers `CXGB4_ULD_TLS`. When a Chelsio adapter adds the ULD, `chtls_uld_add()` allocates `chtls_dev`, copies LLDI, caches response SKBs, initializes IDR/listen/deferred-queue/key state, optionally initializes the key map, and adds it to the global list. On `CXGB4_STATE_UP`, the TLS TOE device is registered with the TLS core; on detach, it is removed and released through `kref`.

Listening sockets call the TLS TOE hash/unhash hooks. The main file validates TCP/non-loopback constraints, sets a backlog handler, and uses a raw notifier to call the connection-manager listener functions. Incoming adapter responses are converted to SKBs and dispatched to `chtls_handlers` by opcode. `CPL_RX_PKT` is specially synthesized into a PASS_ACCEPT-like SKB path; response-only CPLs use cached or newly allocated SKBs; packet-gl data uses `cxgb4_pktgl_to_skb()`.

For `SOL_TLS` setsockopt, the code validates TLS 1.2, accepts AES-GCM-128/256 crypto-info layouts, copies full crypto info from userspace into `csk->tlshws.crypto_info`, and calls `chtls_setkey()`. Getsockopt returns a minimal `tls_crypto_info` with TLS 1.2 version.

## State and Persistence Behavior

Global state includes `cdev_list`, `cdev_mutex`, `notify_mutex`, `listen_notify_list`, protocol templates, request-socket ops, and module parameter-like `send_page_order`. Per-device state includes cached SKBs, key map, deferred queue, LLDI copy, and TLS TOE refcount. All state is volatile kernel memory and released on detach/module unload.

## Dependencies and Integration Points

The file integrates with `cxgb4_register_uld()`, Linux TLS TOE registration, TCP protocol structs, raw notifier chains, Chelsio packet-gl conversion, Chelsio TID/CPL handlers, and userspace SOL_TLS APIs. It calls into `chtls_cm.c`, `chtls_io.c`, and `chtls_hw.c`.

## Risks and Edge Cases

- Device release resets adapter TLS stats and frees cached SKBs; detach ordering must avoid RX handlers accessing freed `cdev`.
- `chtls_uld_add()` has multi-stage allocation with partial cleanup; response SKB cache count must match the loop index on failure.
- `copy_gl_to_skb_pkt()` synthesizes PASS_ACCEPT request space around packet data, so header offsets must match hardware packet shift.
- `do_chtls_getsockopt()` ignores opt length validation and returns only base crypto info.
- Listen notification allocates `chtls_listen` and expects notifier handlers to free it.

## Test Signals

Validate module load/unload, ULD add/detach, TLS TOE device registration, listener hash/unhash, RX dispatch for response-only and packet-gl CPLs, SOL_TLS option validation for version/cipher/short buffers, IPv6 protocol replacement, and failure cleanup when key map or SKB cache allocation fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/inline_crypto/chtls/chtls_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/libcxgb/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/libcxgb/Makefile

## Purpose

This Makefile builds the shared Chelsio library object `libcxgb.o` when `CONFIG_CHELSIO_LIB` is enabled.

## Important APIs, Types, and Functions

- `ccflags-y := -I $(src)/../cxgb4` adds the sibling cxgb4 include directory.
- `obj-$(CONFIG_CHELSIO_LIB) += libcxgb.o` controls inclusion.
- `libcxgb-y := libcxgb_ppm.o libcxgb_cm.o` links page-pod manager and connection-management helpers into the composite object.

## Control Flow

Kbuild conditionally builds `libcxgb.o` and links the two helper implementation files into it. Other Chelsio upper-layer drivers can depend on this library.

## State and Persistence Behavior

No runtime state exists in this build file.

## Dependencies and Integration Points

The file integrates with kernel Kbuild and `CONFIG_CHELSIO_LIB`. The include path supports direct inclusion of cxgb4 headers by library sources.

## Risks and Edge Cases

If `CONFIG_CHELSIO_LIB` is disabled while consumers expect exported symbols from `libcxgb_cm.c` or `libcxgb_ppm.c`, link failures occur. New library sources must be added to `libcxgb-y`.

## Test Signals

Build with `CONFIG_CHELSIO_LIB=m`/`=y` and with dependent Chelsio iSCSI/RDMA consumers enabled to verify exported symbol resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/libcxgb/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/libcxgb/libcxgb_cm.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/libcxgb/libcxgb_cm.c

## Purpose

`libcxgb_cm.c` provides common Chelsio connection-management helpers for parsing passive-open tuples and finding routes that egress through a Chelsio-owned interface. The functions are exported for other Chelsio upper-layer drivers.

## Important APIs, Types, and Functions

- `cxgb_get_4tuple()` parses `struct cpl_pass_accept_req` to extract IPv4/IPv6 local and peer addresses and TCP ports. It accounts for T5-and-earlier versus T6 header length field layouts.
- `cxgb_find_route()` builds an IPv4 route with `ip_route_output_ports()`, looks up the neighbour, and accepts the route only if the real egress device belongs to the Chelsio LLDI ports or is loopback.
- `cxgb_find_route6()` builds an IPv6 route with `ip6_route_output()`, handles link-local scope ID, and applies the same Chelsio-interface/loopback filter.
- `cxgb_our_interface()` is a local helper that normalizes real devices through a callback and compares against `lldi->ports[]`.

## Control Flow

Consumers pass a hardware PASS_ACCEPT request to `cxgb_get_4tuple()` to decode peer/local tuple data. For active route validation, consumers call the IPv4 or IPv6 finder with local/peer tuple and a callback that maps VLAN/bond devices to real devices. The function releases routes/neighbours and returns `NULL` if routing fails, neighbour lookup fails, or egress is not associated with the Chelsio adapter.

## State and Persistence Behavior

The file stores no long-lived state. Returned `dst_entry` references must be released by callers. Neighbour references are short-lived and released before return.

## Dependencies and Integration Points

It depends on Linux IPv4/IPv6 route APIs, neighbour lookup, ECN/TOS helpers, Chelsio CPL layout macros, and `cxgb4_lld_info`. Symbols are exported with `EXPORT_SYMBOL`.

## Risks and Edge Cases

- In `cxgb_find_route()`, if `dst_neigh_lookup()` fails, the route is returned neither released nor passed back; this is a potential leak pattern unless route internals handle it elsewhere.
- IPv6 support is wrapped in `IS_ENABLED(CONFIG_IPV6)`; when disabled, `cxgb_find_route6()` returns `NULL`.
- Interface filtering depends on the caller's `get_real_dev` callback handling VLAN or stacked devices correctly.

## Test Signals

Test tuple parsing for T5/T6 header length encodings, IPv4 and IPv6 PASS_ACCEPT requests, VLAN real-device mapping, non-Chelsio route rejection, loopback acceptance, IPv6 link-local scope, and route/neighbour failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/libcxgb/libcxgb_cm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/libcxgb/libcxgb_cm.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/libcxgb/libcxgb_cm.h

## Purpose

`libcxgb_cm.h` declares common Chelsio connection-management helper APIs and provides inline builders for frequently used CPL control messages.

## Important APIs, Types, and Functions

- Declared exported APIs: `cxgb_get_4tuple()`, `cxgb_find_route()`, and `cxgb_find_route6()`.
- `cxgb_is_neg_adv()` identifies negative-advice CPL statuses.
- `cxgb_best_mtu()` chooses an aligned MTU index from adapter MTU tables while accounting for IPv4/IPv6, TCP, and timestamp option header sizes.
- CPL builders: `cxgb_mk_tid_release()`, `cxgb_mk_close_con_req()`, `cxgb_mk_abort_req()`, `cxgb_mk_abort_rpl()`, and `cxgb_mk_rx_data_ack()`.
- `cxgb_compute_wscale()` computes a TCP window scale for a desired receive window.

## Control Flow

Callers allocate an SKB of suitable size and use the inline builders to append zeroed CPL structures, initialize TP WR fields, set opcode/TID, choose TX priority/queue, and optionally attach ARP error handlers. Route and tuple functions are implemented in `libcxgb_cm.c`.

## State and Persistence Behavior

No state is owned here. Inline builders mutate caller-provided SKBs and rely on caller-owned TID/channel/handler values.

## Dependencies and Integration Points

The header depends on Linux TCP headers and Chelsio `cxgb4`, CPL, and L2T APIs. It is intended as shared glue for Chelsio offload consumers that need consistent CPL construction.

## Risks and Edge Cases

- Inline builders assume the caller sized the SKB correctly and that `__skb_put_zero()` has enough tailroom.
- `cxgb_best_mtu()` subtracts header size from MTU; callers must avoid invalid MTU/header combinations.
- `cxgb_compute_wscale()` caps at 13/14 loop behavior consistent with TCP scaling but should be validated against max window expectations.

## Test Signals

Compile consumers with this header, inspect generated CPLs for opcode/TID/queue/handler fields, test MTU selection with timestamp and IPv6 combinations, and validate negative-advice recognition against firmware statuses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/libcxgb/libcxgb_cm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/libcxgb/libcxgb_ppm.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/libcxgb/libcxgb_ppm.c

## Purpose

`libcxgb_ppm.c` implements the Chelsio iSCSI Direct Data Placement PagePod Manager. It allocates and frees page-pod index ranges, builds DDP tags and page-pod headers, initializes shared/per-CPU page-pod pools, and manages the lifetime of a `struct cxgbi_ppm` instance.

## Important APIs, Types, and Functions

- `cxgbi_ppm_find_page_index()` maps a page size to one of the configured DDP page-size indices.
- Allocation helpers: `ppm_find_unused_entries()`, `ppm_get_cpu_entries()`, `ppm_get_entries()`, and `ppm_mark_entries()`.
- Release helpers: `ppm_unmark_entries()` and exported `cxgbi_ppm_ppod_release()`.
- Exported reservation: `cxgbi_ppm_ppods_reserve()` reserves enough page pods for a number of pages and returns both software index and wire DDP tag.
- Exported header builder: `cxgbi_ppm_make_ppod_hdr()` fills `cxgbi_pagepod_hdr` with valid flag, TID, tag bits, max offset, and page offset.
- Lifetime: `cxgbi_ppm_init()`, `cxgbi_ppm_release()`, `ppm_destroy()`, and `ppm_free()`.
- Tag mask sizing: `cxgbi_tagmask_set()`.

## Control Flow

Initialization computes total page pods from iSCSI DDR/EDRAM sizes, optionally reserves per-CPU pools based on `reserve_factor`, allocates one `vzalloc()` block containing `struct cxgbi_ppm`, per-pod data, and the shared bitmap, handles EDRAM/DDR boundary reservation, initializes locks/refcount, copies the tag format, sets base indices, and stores the pointer in the caller's `ppm_pp`. If another initializer wins the race, it frees the new object and increments the existing refcount.

Reservation converts page count to page-pod count, tries the current CPU pool first, then the shared pool, marks caller data and advances color, computes hardware index as `base_idx + idx`, builds a DDP tag with color and optional page selector bits, and returns count/index/tag. Release validates index and `npods`, then clears either the per-CPU bitmap or shared bitmap and rewinds the next search pointer if possible. Header creation masks off wire-only page selector bits and fills a hardware page-pod header.

## State and Persistence Behavior

State is volatile in `struct cxgbi_ppm`: refcount, device pointers, tag format, total/low-limit/base indices, per-CPU pool reservation, shared bitmap, per-pod metadata (`color`, `npods`, `caller_data`), and next-search cursors. Per-CPU pools use their own spinlocks; shared allocation uses `map_lock`. Refcount release clears the caller's ppm pointer and frees pools/object.

## Dependencies and Integration Points

The file depends on Linux bitmap, per-CPU allocation, scatterlist/SKB/PIC headers, Chelsio iSCSI page-pod types from `libcxgb_ppm.h`, and exports symbols for Chelsio iSCSI consumers.

## Risks and Edge Cases

- The extra-bit mask calculation compares `ppod_bmap_size >> 3` to pod count; bitmap sizing logic should be verified for non-multiple-of-word pod counts.
- `cxgbi_ppm_ppod_release()` does not clear `pdata->npods` after unmarking, so double release is only guarded if bitmap state or caller discipline prevents it.
- Per-CPU allocation uses `get_cpu()`/`put_cpu()` before locking the pool pointer; migration is disabled only during pointer acquisition.
- EDRAM/DDR contiguity assumptions reject noncontiguous regions and reserve one boundary pod.

## Test Signals

Test initialization with DDR-only, EDRAM+DDR contiguous, noncontiguous EDRAM rejection, reserve factor on/off, page size mapping, reserve/release wraparound, per-CPU and shared fallback allocation, DDP tag color rollover, tag page selector bits, concurrent reserve/release, and refcounted double initialization/release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/libcxgb/libcxgb_ppm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/libcxgb/libcxgb_ppm.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/libcxgb/libcxgb_ppm.h

## Purpose

`libcxgb_ppm.h` defines the data structures, tag format, constants, inline tag helpers, and exported function prototypes for Chelsio iSCSI Direct Data Placement page-pod management.

## Important APIs, Types, and Functions

- Hardware structures: `struct cxgbi_pagepod_hdr` and `struct cxgbi_pagepod`.
- Task mapping: `struct cxgbi_task_tag_info` records per-task DDP mapping flags, page size, pod count, index/tag, header, and scatterlist metadata.
- Tag layout: `struct cxgbi_tag_format` stores page-size order, default index, free/color/index/reserved bit counts, and masks.
- Pool state: `struct cxgbi_ppm_pool` and `struct cxgbi_ppm`.
- Inline helpers include DDP/non-DDP tag checks and conversion, `cxgbi_ppm_make_non_ddp_tag()`, `cxgbi_ppm_decode_non_ddp_tag()`, `cxgbi_ppm_ddp_tag_get_idx()`, `cxgbi_ppm_make_ddp_tag()`, `cxgbi_ppm_get_tag_caller_data()`, `cxgbi_ppm_ddp_tag_update_sw_bits()`, `cxgbi_ppm_ppod_clear()`, and `cxgbi_tagmask_check()`.
- Exported prototypes include page index lookup, page-pod header creation, reserve/release/init/release, tagmask check/set.

## Control Flow

Consumers use `cxgbi_tagmask_check()` to derive tag bit layout from a hardware tag mask, initialize a PPM with `cxgbi_ppm_init()`, reserve page-pod ranges with `cxgbi_ppm_ppods_reserve()`, build page-pod headers with `cxgbi_ppm_make_ppod_hdr()`, and release ranges with `cxgbi_ppm_ppod_release()`. Inline tag helpers encode/decode DDP tags and preserve non-DDP software tags by inserting/removing the no-DDP marker bit.

## State and Persistence Behavior

The header defines the in-memory PPM state. Per-pod `cxgbi_ppod_data` tracks color, channel, pod count, and caller data. The tag format determines how 32-bit tags are interpreted and is copied into the PPM at initialization. No persistent storage is involved.

## Dependencies and Integration Points

It depends on Linux kernel, debugfs, list, netdevice, scatterlist, SKB, vmalloc, and bitmap APIs. It integrates with Chelsio iSCSI drivers that need DDP page-pod tags.

## Risks and Edge Cases

- Tag helper arithmetic is mask/shift sensitive; invalid tagmask values could produce negative or nonsensical bit allocations.
- `cxgbi_ppm_make_non_ddp_tag()` rejects software tags using bit 31 and treats zero specially as exactly `no_ddp_mask`.
- `cxgbi_ppm_ddp_tag_update_sw_bits()` validates free-bit capacity but depends on the original tag being a DDP tag.
- `PPOD_PI_EXTRACT_CTL_FLAG` references a `V_` macro name that is not defined in this header, so consumers should verify compile coverage for that macro path.

## Test Signals

Unit-style tests can validate tagmask-derived masks, DDP tag index/color extraction, non-DDP tag round trips, SW-bit update bounds, default page-size index, page-pod header clearing, and compile coverage of all macros used by consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/libcxgb/libcxgb_ppm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cirrus/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cirrus/Kconfig

## Purpose

This Kconfig file defines the Cirrus Ethernet vendor menu and driver options for CS89x0 ISA/platform Ethernet, EP93xx Ethernet, and Macintosh CS89x0 cards.

## Important APIs, Types, and Functions

- `NET_VENDOR_CIRRUS` is a vendor-level boolean, defaulting to `y` when platform dependencies match.
- `CS89x0` is a hidden tristate selected by the ISA and platform variants.
- `CS89x0_ISA` enables ISA CS89x0 support and selects `NETDEV_LEGACY_INIT` and `CS89x0`.
- `CS89x0_PLATFORM` enables platform-driver CS89x0 support for ARM or compile-test builds and selects `CS89x0`.
- `EP93XX_ETH` enables EP93xx SoC Ethernet and selects `MII`.
- `MAC89x0` enables Macintosh Nubus/LC-PDS CS89x0 support.

## Control Flow

When `NET_VENDOR_CIRRUS` is disabled, the nested Cirrus driver prompts are skipped. Enabling specific drivers controls which objects the directory Makefile includes. Hidden `CS89x0` is selected by concrete ISA/platform variants so shared CS89x0 code builds when either frontend is enabled.

## State and Persistence Behavior

Kconfig selections are build-time configuration state. There is no runtime state in this file.

## Dependencies and Integration Points

The file integrates with architecture symbols (`ISA`, `EISA`, `ARM`, `MAC`, `ARCH_EP93XX`, `COMPILE_TEST`), I/O port support (`HAS_IOPORT_MAP`), legacy netdev init, and MII support. Help text points users to the CS89x0 documentation.

## Risks and Edge Cases

- `CS89x0_ISA` depends on `CS89x0_PLATFORM=n`, making the ISA and platform variants mutually exclusive in that direction.
- Architecture dependencies intentionally exclude PPC32 for ISA and PPC for ARM compile-test platform support.
- Hidden `CS89x0` has no prompt; it must only be selected by valid frontends.

## Test Signals

Run Kconfig matrix checks for ISA, ARM, MAC, EP93XX, and COMPILE_TEST builds. Verify the expected object files appear for each selected option and that mutual exclusion between ISA and platform CS89x0 behaves as intended.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cirrus/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cirrus/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cirrus/Makefile

## Purpose

This Makefile maps Cirrus Ethernet Kconfig symbols to driver objects.

## Important APIs, Types, and Functions

- `obj-$(CONFIG_CS89x0) += cs89x0.o` builds the shared CS89x0 driver object.
- `obj-$(CONFIG_EP93XX_ETH) += ep93xx_eth.o` builds the EP93xx Ethernet driver.
- `obj-$(CONFIG_MAC89x0) += mac89x0.o` builds the Macintosh CS89x0 driver.

## Control Flow

Kbuild includes each object when the corresponding Kconfig symbol is `y` or `m`. The hidden `CONFIG_CS89x0` symbol is selected by ISA/platform CS89x0 options in `Kconfig`.

## State and Persistence Behavior

No runtime state exists. Build inclusion follows configuration state.

## Dependencies and Integration Points

This file integrates with the kernel networking driver build under `drivers/net/ethernet/cirrus` and consumes symbols defined in the adjacent Kconfig.

## Risks and Edge Cases

If a frontend selects `CONFIG_CS89x0`, only `cs89x0.o` is built here; platform-specific behavior must be contained in that source or elsewhere in the directory. New driver symbols require matching object entries.

## Test Signals

Build with each Cirrus option as module and built-in, then verify the expected object is compiled and no disabled driver object appears.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cirrus/Makefile -->
