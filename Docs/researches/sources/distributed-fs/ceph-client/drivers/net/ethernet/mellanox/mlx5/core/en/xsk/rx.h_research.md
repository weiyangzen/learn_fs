# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/xsk/rx.h

Purpose: declares the XSK RX allocation and CQE conversion entry points consumed by mlx5e RX handlers.

Important APIs/types/functions: prototypes cover MPWQE allocation, batched and scalar cyclic WQE allocation, and MPWQE/cyclic `sk_buff` construction from CQEs.

Control flow and state: the header does not store state; it defines the boundary where common RX code delegates to AF_XDP-specific buffer ownership logic.

Dependencies and integration: includes `en.h` for RQ, WQE, CQE, and mlx5e MPWQE types. Callers must pass queue-local `rq`, WQE indices, CQE byte counts, and fragment/page references from the active XSK RQ.

Risks and test signals: mismatched prototypes or wrong caller assumptions about ownership can leak UMEM frames. Build with AF_XDP enabled and exercise both striding and cyclic RQ receive paths.
