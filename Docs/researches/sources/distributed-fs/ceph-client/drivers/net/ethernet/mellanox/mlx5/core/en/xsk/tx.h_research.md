# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/xsk/tx.h

Purpose: declares the AF_XDP TX data path entry points.

Important APIs/types/functions: `mlx5e_xsk_wakeup` implements netdev wakeup from AF_XDP userspace; `mlx5e_xsk_tx` drains descriptors on the XSK XDPSQ.

Control flow and state: no state lives here; the declarations expose queue wake and NAPI TX work to the broader mlx5e channel code.

Dependencies and integration: includes `en.h` for netdev/channel/SQ types. Used when NAPI handles pending `MLX5E_SQ_STATE_PENDING_XSK_TX`.

Risks and test signals: build coverage with XSK enabled and functional AF_XDP TX wakeups are the key signals.
