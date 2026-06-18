# sources/distributed-fs/ceph-client/drivers/scsi/cxgbi/libcxgbi.h

## Purpose

`libcxgbi.h` defines the shared contract between Chelsio iSCSI adapter drivers and the common `libcxgbi` implementation. It contains debug infrastructure, protocol sizing constants, skb control-block layout, socket/device/HBA/endpoint/task/ISO data structures, state and flag enums, inline helpers for reference/queue/state handling, adapter callback slots, and exported function prototypes.

## Important APIs, Types, And Functions

Important constants describe iSCSI offload sizing: `SKB_TX_ISCSI_PDU_HEADER_MAX`, `ISCSI_PDU_NONPAYLOAD_LEN`, `ULP2_MAX_PKT_SIZE`, `ULP2_MAX_PDU_PAYLOAD`, `CXGBI_ULP2_MAX_ISO_PAYLOAD`, `CXGBI_MAX_ISO_DATA_IN_SKB`, and `cxgbi_align_pdu_size()`. `cxgbi_ulp_extra_len()` reports TCP sequence-space bytes consumed by hardware-inserted header/data digests.

`struct cxgbi_sock` is the central per-offloaded-connection object. It stores adapter identity, TID/ATID, flags, MTU/MSS/RSS/queue/channel state, WR credits, digest lengths, L2T pointer, preallocated CPL skbs, pending ULP header skb, queues, timer, completion, callback data, address unions, route, TCP sequence/window values, and ISO throttling state. `enum cxgbi_sock_states` and `enum cxgbi_sock_flags` define the connection state machine and close/abort/resource flags.

`struct cxgbi_skb_cb` overlays `sk_buff.cb` and is split into RX metadata (`ddigest`, `pdulen`) and TX metadata (`handle`, `arp_err_handler`, `wr_next`, `iscsi_hdr_len`, `ulp_mode`) plus shared flags and TCP sequence. `enum cxgbi_skcb_flags` marks TX header need, memory-write WRs, completion requests, RX header/data/status/DDP/digest/padding conditions, and ISO TX. Inline helpers set/clear/test skb flags and expose control fields.

Other key structs are `cxgbi_hba`, `cxgbi_ports_map`, `cxgbi_device`, `cxgbi_conn`, `cxgbi_endpoint`, `cxgbi_task_data`, and `cxgbi_iso_info`. `cxgbi_device` is the adapter-neutral object with port/HBA arrays and callback slots that adapter drivers populate. `cxgbi_task_data` extends libiscsi TCP tasks with SGL fragment state, skb ownership, transfer offsets, and DDP tag info. `cxgbi_iso_info` is written into reserved skb headroom for adapter ISO work requests.

## Control Flow

The header itself has no standalone runtime flow, but its inline helpers are on hot paths. Socket state is changed by `cxgbi_sock_set_state()`. References are managed through `cxgbi_sock_get()` and `cxgbi_sock_put()`, which wrap `kref` and free with `cxgbi_sock_free()`. Write-request bookkeeping uses `cxgbi_sock_reset_wr_list()`, `cxgbi_sock_enqueue_wr()`, `cxgbi_sock_count_pending_wrs()`, `cxgbi_sock_peek_wr()`, and `cxgbi_sock_dequeue_wr()`. Adapter and common code cooperate through function pointers inside `struct cxgbi_device`: common code calls adapter-specific open/close/abort/TX/RX-credit/DDP operations, while adapter code calls exported common functions for state transitions and PDU delivery.

## State And Persistence Behavior

The header defines in-memory state layouts only. No persistent storage is involved. It does, however, define ownership-relevant fields: socket krefs, queue heads, skbs that must be freed or handed off exactly once, TID/ATID flags that imply hardware table ownership, source-port-map entries, DMA/DDP tag information, and callback pointers into libiscsi. Because these structures are shared across interrupt/softirq, worker, and libiscsi contexts, their lock fields (`spinlock_t`, `rwlock_t`, completion, timer) are part of the state contract.

## Dependencies And Integration Points

The header includes Linux kernel, debugfs, list, netdevice, VLAN, scatterlist, skbuff, vmalloc, SCSI, libiscsi_tcp, and `libcxgb_ppm` definitions. It is included by both common and adapter-specific Chelsio iSCSI code. It also depends on `sk_buff.cb` being large enough for `struct cxgbi_skb_cb`, which `libcxgbi.c` checks at module init. The public prototypes are the API surface used by `cxgb4i.c` and potentially other Chelsio iSCSI adapter drivers.

## Risks

The largest risk is ABI-like coupling through shared structs and skb control blocks. Any field layout or flag semantic change must be coordinated across common and adapter code. The write-pending list stores WR credit counts in `skb->csum`, so helpers assume all enqueued WR skbs follow that convention. `cxgbi_sock_free()` only frees the socket memory; callers must release CPL skbs, route, L2T, TID/ATID, port-map, queues, DMA, and DDP resources before the final put. Inline state setters do not enforce legal transitions, so implementation code must maintain the state machine.

## Test Signals

Compile-time coverage should catch missing dependencies and struct/control-block sizing. Runtime signals include stable socket reference counts across connect/close/abort, WR queue invariant checks, correct skb flag interpretation by receive and transmit paths, successful DDP tag lifecycle, and no crashes under adapter detach or iSCSI session teardown. Because this header defines the shared contract, cross-driver build and load tests are especially valuable.
