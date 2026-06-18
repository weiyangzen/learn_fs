# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_iwarp.h

## Purpose

`qed_iwarp.h` is the internal iWARP contract for the QED driver. It defines the in-memory iWARP state machine, endpoint/listener structures, LL2 buffer tracking structures, partial FPDU alignment state, and the function prototypes consumed by the RDMA setup and connection-management code.

The header is not a userspace ABI. It binds `qed_iwarp.c` to the rest of the QED RDMA stack through `struct qed_hwfn`, `struct qed_rdma_qp`, `struct qed_rdma_start_in_params`, firmware HSI structures, and callback types from the RDMA interface.

## Important APIs, types, and constants

- `enum qed_iwarp_qp_state` defines the QED iWARP QP states: `IDLE`, `RTS`, `TERMINATE`, `CLOSING`, and `ERROR`.
- `qed_roce2iwarp_state()` maps the common RDMA/RoCE state vocabulary into iWARP state for shared QP handling.
- `QED_IWARP_PREALLOC_CNT` is 256, matching the passive endpoint/TCP CID reserve used by SYN processing.
- LL2 sizing constants define SYN TX/RX depth, OOO defaults, OOO maximum RX size, and invalid LL2 handle value.
- `struct qed_iwarp_ll2_buff` wraps a DMA buffer posted to LL2 and optionally chains a `piggy_buf` that should be reposted or freed with it.
- `struct qed_iwarp_ll2_mpa_buf` tracks firmware opaque unaligned-packet metadata, the LL2 buffer, TCP payload length, and placement offset while the MPA alignment path processes pending packets.
- `struct qed_iwarp_fpdu` records a partial or current FPDU's header DMA address, MPA fragment virtual/physical address, fragment length, total FPDU length, remaining incomplete bytes, and header size.
- `struct qed_iwarp_info` is the per-hwfn iWARP runtime state: listener, endpoint, free endpoint, MPA buffer lists, locks, receive-window policy, local MAC, MPA policy flags, LL2 handles, partial FPDU array, MPA buffer array, intermediate buffer, and partial-FPDU capacity.
- `enum qed_iwarp_ep_state` tracks endpoint lifecycle from `INIT` to `CLOSED`.
- `union async_output` overlays firmware MPA response and TCP async completion data in endpoint DMA memory.
- `struct qed_iwarp_ep_memory` reserves 512-byte incoming and outgoing private-data buffers plus async output storage.
- `struct qed_iwarp_ep` represents one TCP/iWARP endpoint and stores list linkage, QP association, DMA private-data memory, state, signature, CM tuple, connect mode, MPA/RTR negotiation state, CIDs, MSS, MAC addresses, passive SYN metadata, and event callback.
- `struct qed_iwarp_listener` stores listen callback context, backlog, IP address, port, VLAN, and IP version.

The exported prototypes cover allocation/setup/stop/free, firmware init, hardware init, QP create/modify/destroy/query, active connect, passive listen/accept/reject/destroy, and RTR send.

## Control flow represented by the header

The header divides iWARP behavior into three state domains. Device-level state lives in `struct qed_iwarp_info`, initialized by `qed_iwarp_alloc()` and `qed_iwarp_setup()`, and released by `qed_iwarp_stop()` plus `qed_iwarp_resc_free()`. QP-level state is represented by `enum qed_iwarp_qp_state` and manipulated through `qed_iwarp_create_qp()`, `qed_iwarp_modify_qp()`, `qed_iwarp_destroy_qp()`, and `qed_iwarp_query_qp()`. Connection-level state lives in `struct qed_iwarp_ep` and is driven by `qed_iwarp_connect()`, `qed_iwarp_create_listen()`, `qed_iwarp_accept()`, `qed_iwarp_reject()`, `qed_iwarp_destroy_listen()`, and `qed_iwarp_send_rtr()`.

The LL2 and FPDU structures expose the private machinery used by `qed_iwarp.c` to intercept passive SYNs and realign MPA traffic. The split between `qed_iwarp_ll2_buff` and `qed_iwarp_ll2_mpa_buf` allows LL2 buffer ownership to be kept separate from pending alignment metadata.

## State and persistence behavior

All declarations describe volatile kernel-driver state. There is no persistence across device teardown, module unload, or PCI reset. Runtime state is anchored below `p_hwfn->p_rdma_info->iwarp` and depends on list heads and spinlocks initialized in the implementation.

The header makes several ownership rules visible:

- Endpoint DMA memory is owned by `struct qed_iwarp_ep`.
- Listener and endpoint objects are linked into per-hwfn lists.
- Passive SYN data is retained by `struct qed_iwarp_ep` until TCP offload completion reposts the original LL2 buffer.
- Partial FPDU records are indexed by CID offset and therefore depend on CID allocation staying within `max_num_partial_fpdus`.
- The event callback and context in both listener and endpoint records are the bridge back to RDMA upper-layer code.

## Dependencies and integration points

The header depends on Linux list/spinlock/DMA types through included QED headers, firmware HSI types such as `struct unaligned_opaque_data`, `enum mpa_negotiation_mode`, `enum mpa_rtr_type`, and `enum tcp_connect_mode`, RDMA QP and connection-management structures from the QED RDMA interface, and Ethernet constants such as `ETH_ALEN`.

It is included by the iWARP implementation and by other QED RDMA setup paths that need to call iWARP allocation, setup, teardown, QP, or connection APIs.

## Risks and edge cases

- `struct qed_iwarp_ep` stores raw callback pointers and raw endpoint pointers are later passed through firmware async handles, so object lifetime and signature validation are critical.
- `QED_MAX_PRIV_DATA_LEN` is fixed at 512 bytes; callers and firmware paths must ensure private data plus MPA v2 header fit this buffer.
- `QED_IWARP_PREALLOC_CNT` fixes the passive SYN reserve. If workload or firmware assumptions change, passive connection scalability and memory consumption both change.
- Partial FPDU indexing depends on CID ranges matching `max_num_partial_fpdus`; invalid CIDs must be rejected by the implementation.
- The header exposes mutable connection information inside `struct qed_iwarp_ep`, so callback consumers must treat pointers as transient and not persistent ownership.

## Test signals

Header-level validation is mostly compile-time and integration-focused: all prototypes should match their definitions, structure fields should match firmware HSI expectations, `QED_MAX_PRIV_DATA_LEN` should be sufficient for negotiated MPA private data, endpoint state names should cover all transitions used in `qed_iwarp.c`, and LL2/FPDU structures should remain layout-compatible with the unaligned packet path.
