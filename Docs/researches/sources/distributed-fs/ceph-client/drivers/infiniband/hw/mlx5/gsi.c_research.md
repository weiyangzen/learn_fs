# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/gsi.c

## Purpose
`gsi.c` implements the mlx5 software wrapper for InfiniBand GSI/QP1 behavior. The driver creates one hardware receive-side GSI QP and, when the hardware supports programmable DETH source QPN, optional UD transmit QPs per P_Key index or per RoCE LAG transmit port. The wrapper preserves normal RDMA-core QP1 APIs while hiding the hardware split between receive QP and send QPs.

## Important APIs, Types, And Functions
`struct mlx5_ib_gsi_wr` is the private outstanding-send bookkeeping object. It embeds an `ib_cqe`, a saved `ib_wc`, and a completion flag. The public entry points are `mlx5_ib_create_gsi`, `mlx5_ib_destroy_gsi`, `mlx5_ib_gsi_modify_qp`, `mlx5_ib_gsi_query_qp`, `mlx5_ib_gsi_post_send`, `mlx5_ib_gsi_post_recv`, and `mlx5_ib_gsi_pkey_change`.

`generate_completions()` walks `gsi->outstanding_wrs` in producer/consumer order and emits saved completions through `mlx5_ib_generate_wc()`. `handle_single_completion()` is installed as the hardware CQE callback and copies the real WC into the wrapper slot while preserving the original caller `wr_id`. `setup_qp()` creates and transitions a UD transmit QP for a valid P_Key or LAG port slot. `get_tx_qp()` selects the appropriate transmit QP, falling back to the hardware GSI QP when no fanout is used.

## Control Flow
Creation allocates the transmit-QP pointer array and outstanding WR ring, allocates a private send CQ, creates the hardware GSI receive QP with type `MLX5_IB_QPT_HW_GSI`, and registers the wrapper in `dev->devr.ports[port - 1].gsi`. If DETH source-QPN setting is unavailable, `num_qps` is zero and sends go directly through `rx_qp`; otherwise IB ports size the table by `max_pkeys`, while LAG Ethernet ports size it by `dev->lag_ports`.

Modify calls are forwarded to `rx_qp`. Once the hardware QP reaches RTS, every configured transmit slot is lazily initialized by `setup_qp()`. Send posting clones each UD WR, selects a transmit QP under `gsi->lock`, records an outstanding completion slot, posts to the selected hardware QP, and rolls back the producer index on post failure. Missing transmit QPs produce a successful synthetic send completion through `mlx5_ib_gsi_silent_drop()`.

## State And Persistence Behavior
State is in memory only and lives inside `struct mlx5_ib_qp.gsi`: `rx_qp`, private CQ, transmit QP array, ring indices, saved capabilities, port number, and lock. `dev->devr.ports[].gsi` is a lifecycle integration pointer used by port P_Key event work. No persistent storage is written. Ordering is preserved by completing only consecutive ring entries from `outstanding_ci` to the first incomplete entry.

## Dependencies And Integration Points
The file depends on RDMA core QP/CQ APIs, `mlx5_ib_generate_wc()` from the CQ path, P_Key queries through `ib_query_pkey()`, and mlx5 capabilities such as `set_deth_sqpn`, port type, and LAG state. It is invoked by the QP implementation when creating/querying/modifying/posting/destroying `IB_QPT_GSI`, and by `main.c` P_Key-change work via `mlx5_ib_gsi_pkey_change()`.

## Risks
The lock protects both transmit-QP creation and outstanding WR ring state; regressions here can corrupt send completion order. `setup_qp()` must destroy failed QPs; this source has `WARN_ON_ONCE(qp)` in the error path rather than an actual destroy call, so cleanup behavior should be checked against the wider tree. Silent drops intentionally report success when a needed transmit QP is unavailable, which is protocol-sensitive and should remain limited to the wrapper's expected QP1 semantics. The ring is bounded by `cap.max_send_wr`; zero or mismatched capabilities would break modulo arithmetic.

## Test Signals
Useful tests include QP1 create/destroy on IB and Ethernet RoCE ports, P_Key table changes creating new transmit QPs, posting with invalid P_Key indexes and verifying synthetic completions, LAG xmit-port selection through AH attributes, and stress posting enough WRs to hit the ring-full path and completion ordering.
