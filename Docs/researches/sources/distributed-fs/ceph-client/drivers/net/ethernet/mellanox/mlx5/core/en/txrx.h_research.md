# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/txrx.h

Purpose: collects core inline helpers, constants, WQE bookkeeping structures, and function declarations for mlx5e TX/RX datapaths. It is a shared low-level contract for normal TX, RX, ICO SQ, XDP SQ, trap RX, checksum/SWP, and CQ handling.

Important APIs and types: defines maximum TX WQE sizes and stop-room calculations, KSM UMR sizing, RX error CQE macro, `mlx5e_xmit_data`, `mlx5e_xmit_data_frags`, TX WQE info, ICO SQ WQE info, skb FIFO helpers, DMA FIFO helpers, SW parser spec, CQ arm, error CQE dump, RQ WQ accessors, and posting helpers. Declares polling and cleanup functions for CQ/RQ/TX/ICO. Inline WQE helpers include `mlx5e_txqsq_get_next_pi`, `mlx5e_icosq_get_next_pi`, `mlx5e_notify_hw`, `mlx5e_post_nop`, and stop-room helpers.

Control flow: TX and ICO callers reserve cyclic WQ space, fill NOPs at page boundaries so WQEs do not wrap, write WQE control/data segments, push DMA bookkeeping, and notify hardware through ordered doorbell writes. CQ pollers consume completions and use WQE info to free descriptors. RX callers use WQ accessors and reset helpers for cyclic or linked-list striding RQs. SW parser helpers set checksum/parser offsets and adjust partial checksums for GSO encapsulation.

State and persistence: state is held in queue doorbell counters (`pc`, `cc`), WQE info arrays, DMA FIFOs, skb FIFOs, CQ work queues, and per-queue stats. The header itself owns no global state but defines invariants for queue memory and DMA ownership.

Dependencies and integration points: mlx5 WQ/CQ primitives, netdev/skbuff, page-pool netmem, TCP/UDP checksum helpers, TLS conditionals, RX/TX implementation files, XDP code, trap code, and params helpers.

Risks and test signals: off-by-one stop room, WQE page-boundary wrapping, missing memory barriers before doorbell, DMA unmap type mismatches, and incorrect SWP offsets are high-risk. Test signals include heavy TX with max fragments and IPsec inline size, MPWQE, ICO UMR posting, CQ error injection, striding and cyclic RQ resets, GSO checksum with tunnels, and sparse/lockdep builds.
