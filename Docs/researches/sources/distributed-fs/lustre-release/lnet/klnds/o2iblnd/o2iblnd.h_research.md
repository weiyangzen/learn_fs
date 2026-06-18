# sources/distributed-fs/lustre-release/lnet/klnds/o2iblnd/o2iblnd.h

## Purpose
`o2iblnd.h` is the shared internal interface for the o2iblnd driver. It pulls in Linux, RDMA, libcfs, LNet, and Lustre RDMA headers; defines tunable attributes, constants, state objects, descriptor layouts, inline helpers, compatibility wrappers, and cross-file prototypes used by `o2iblnd.c`, `o2iblnd_cb.c`, and `o2iblnd_modparams.c`.

## Important APIs, types, and functions
- Tunables: `enum kiblnd_ni_lnd_tunables_attr`, `struct kib_tunables`, external `kiblnd_tunables`, and `kib_default_tunables`.
- Device state: `struct kib_dev` for IPoIB interface/LNet device state and `struct kib_hca_dev` for active RDMA CM listener, IB device, PD, port, event handler, and HCA refcount.
- Pool state: `struct kib_pages`, `struct kib_poolset`, `struct kib_pool`, `struct kib_tx_poolset`, `struct kib_tx_pool`, `struct kib_fmr_poolset`, `struct kib_fmr_pool`, `struct kib_fmr`, and FastReg descriptors.
- Network/driver state: `struct kib_net`, `struct kib_sched_info`, and global `struct kib_data`.
- Transfer state: `struct kib_rx`, `struct kib_tx`, `struct kib_connvars`, `struct kib_conn`, and `struct kib_peer_ni`.
- Inline helpers cover timeout calculation, connection request timeout, concurrent send clamping, HCA/conn/peer refs, peer state predicates, round-robin conn selection, keepalive/NOOP credit decisions, queue names, WR ID pointer tagging, connection state barriers, message initialization, RDMA descriptor operations, DMA mapping wrappers, SG address wrappers, and RDMA CM compatibility.
- Prototypes expose pool, FMR, tunable, connd/scheduler/failover, page allocation, CM, peer/conn lifecycle, TX/RX, CQ/QP, message pack/unpack, send/recv, and device-priority APIs.

## Control flow
The header does not execute standalone control flow, but it defines the invariants followed by the implementation. Connections move through `INIT`, active or passive handshaking, `ESTABLISHED`, `CLOSING`, and `DISCONNECTED`. TX descriptors move from pool free lists to peer waiting queues, connection queues, active completions, and back to pools. RX descriptors are preposted and returned with explicit credit modes. Peers move between hash membership, active connection attempts, passive accepts, reconnect waits, connection lists, and idle destruction.

## State and persistence behavior
The file defines volatile kernel state only. Refcounted state is explicit: HCAs use `atomic_t ibh_ref`, connections use `ibc_refcount`, and peers use `kref`. The global `kib_data` owns driver-wide mutable lists and locks; each `kib_net` owns per-NI pools and counters; each peer owns connection and waiting-TX lists; each connection owns queues, credits, RX buffers, CM/QP/CQ pointers, and in-progress handshake data. The helper `kiblnd_set_conn_state()` adds a memory barrier after state changes, signaling that state transitions are synchronization-relevant.

## Dependencies and integration points
The header depends on RDMA CM/IB verbs, `lnet_rdma.h`, `lib-lnet.h`, libcfs, and `o2iblnd-idl.h` wire message definitions. It bridges kernel-version and OFED feature differences with compatibility macros for DMA SG access, RDMA connect locking, FMR pool API availability, and external OFED virtual DMA behavior. The prototypes and inline helpers couple all o2iblnd translation units.

## Risks and edge cases
- Many helpers assume locks are already held, especially peer lookup, HCA refs, connection refs, and queue operations; misuse can introduce races or use-after-free.
- WR ID pointer tagging relies on descriptor alignment and the low three bits being unused.
- Credit logic differs for protocol v1 and v2, with OOB NOOP behavior only available after v1.
- DMA mapping has a GPU path using `lnet_rdma_map_sg_attrs()` that must stay aligned with normal IB DMA mapping semantics.
- Conditional FMR/FastReg fields change struct behavior across builds; both code paths require coverage.
- Queue depth, max fragments, and message size constants must remain compatible with `o2iblnd-idl.h` and remote peers.

## Test signals
Compile tests across configurations with and without OFED FMR APIs, external OFED, IPv6, FastReg gaps, and SG DMA compatibility are essential. Runtime tests should stress refcount paths, concurrent sends, v1/v2 peers, NOOP/keepalive credit return, RDMA fragments near `IBLND_MAX_RDMA_FRAGS`, GPU and non-GPU DMA mapping, and all connection state transitions.
