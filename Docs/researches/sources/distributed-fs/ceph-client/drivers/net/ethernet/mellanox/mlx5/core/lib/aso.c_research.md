# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/aso.c

Purpose: Provides an ASO (accelerated steering object) send queue and completion queue abstraction used by mlx5 features such as IPsec, flow meters, and MACsec to post ACCESS_ASO WQEs.

Important APIs and flow: `mlx5_aso_create()` allocates an ASO object, creates a CQ, creates an SQ, and moves the SQ to RDY. CQ creation allocates a cyclic CQ WQ, initializes CQEs, fills PAS, assigns EQ/UAR/doorbell fields, and calls core CQ creation. SQ creation allocates cyclic WQ memory, sets PD, CQ number, UAR, page info, timestamp format from `clock.h`, and calls core SQ create/modify. Data path helpers are `mlx5_aso_get_wqe()`, `mlx5_aso_build_wqe()`, `mlx5_aso_post_wqe()`, and `mlx5_aso_poll_cq()`.

State and dependencies: `struct mlx5_aso` tracks producer/consumer counters, SQ number, WQ control, UAR mapping, CQ, and doorbell state. The implementation depends on mlx5 workqueue helpers, transport object commands, BFREG/UAR resources, DMA barriers, CQ polling helpers, and timestamp format decisions from the clock library.

Risks and test signals: Correct ordering depends on `dma_wmb()`, DB record update, `wmb()`, and UAR write order. Polling returns `-ETIMEDOUT` for no CQE and logs bad CQE syndromes. Tests should cover create/destroy error paths, WQE with and without data segment, CQ overrun prevention through `cc` updates, real-time/free-running timestamp formats, and ASO command failure diagnostics.
