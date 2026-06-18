# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/xsk/rx.c

Purpose: implements AF_XDP RX buffer allocation and CQE-to-SKB/XDP handling for both striding MPWQE and legacy cyclic RQ modes.

Important APIs/types/functions: `mlx5e_xsk_alloc_rx_mpwqe`, `mlx5e_xsk_alloc_rx_wqes_batched`, `mlx5e_xsk_alloc_rx_wqes`, `mlx5e_xsk_skb_from_cqe_mpwrq_linear`, and `mlx5e_xsk_skb_from_cqe_linear`. Local helper `xsk_buff_to_mxbuf` relies on mlx5e private fields fitting in `xdp_buff_xsk->cb`; `mlx5e_xsk_construct_skb` copies UMEM data for XDP_PASS.

Control flow and state: MPWQE allocation reserves a full batch of XSK frames, builds an ICOSQ UMR WQE according to aligned/unaligned/triple/oversized mapping mode, sets `mxbuf->rq`, clears release skip bitmap, records WQE info, and arms the doorbell. Cyclic allocation fills WQE DMA addresses from XSK frames either batched or one by one. CQE handlers set packet size, sync DMA for CPU, run the current XDP program, mark release skip when XDP consumed the frame, or copy `data_meta..data_end` into a new SKB for XDP_PASS.

Dependencies and integration: depends on xsk allocator/DMA APIs, mlx5e ICOSQ/UMR, RQ fragment metadata, XDP program execution in `xdp.h`, and RX WQE free paths honoring skip bits.

Risks and test signals: allocation shortfall paths must free partially allocated XSK buffers; UMR offset math differs by mode; metadata copy must preserve `skb_metadata_set`; oversize MPWQE packets are software dropped. Test aligned/unaligned/triple/oversized MPWQE, cyclic batched wraparound, invalid descriptors, XDP_DROP/TX/REDIRECT/PASS, metadata, and SKB allocation failure.
