# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/psp_rxtx.h

Purpose: PSP datapath interface, metadata decoding macros, TX state carrier, checksum helper, and disabled-build fallbacks.

Important APIs, types, and functions: metadata macros decode marker bits, syndrome, and handle from CQE `ft_metadata`. `struct mlx5e_accel_tx_psp_state` carries trailer length, key id, SPI, inner protocol, and PSP version. Inline helpers detect offload state, detect SKB association, compute ID/trailer length, test RX flow metadata, and set checksum flags in TX WQE Ethernet segment.

Control flow: TX classification calls `mlx5e_psp_is_offload()`; SKB processing fills state; WQE build uses `mlx5e_psp_txwqe_build_eseg_csum()` to set outer L3 and inner L3/L4 checksum flags depending on inner protocol. RX uses `mlx5e_psp_is_rx_flow()` before invoking the RX handler.

State and persistence: only transient per-packet TX state is defined here. All persistent PSP state is in `priv->psp` and kernel PSP associations.

Dependencies and integration points: depends on SKB, XFRM/PSP headers, mlx5e TX/RX queues, and IP protocol constants. It provides no-op behavior when PSP is not compiled.

Risks: checksum flag choices are tightly coupled to `psp_rxtx.c` SWP offset parsing. Metadata bit positions must match flow-steering actions in `psp.c`. Disabled fallback omits declarations for some TX functions, so callers must be config-gated.

Test signals: compile PSP enabled/disabled, validate metadata decoding with synthetic values, and inspect checksum flags for transport and tunneled PSP packets.
