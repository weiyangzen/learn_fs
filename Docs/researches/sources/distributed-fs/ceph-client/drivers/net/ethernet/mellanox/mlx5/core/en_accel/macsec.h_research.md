# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/macsec.h

Purpose: mlx5e MACsec acceleration interface and disabled-build stubs.

Important APIs, types, and functions: declares initialization, cleanup, netdev setup, TX SKB validation, TX Ethernet segment metadata build, and RX offload handling. `mlx5e_macsec_skb_is_offload()` recognizes SKBs with `METADATA_MACSEC` destinations. `mlx5e_macsec_is_rx_flow()` checks CQE flow-table metadata for the MACsec marker.

Control flow: the main netdevice setup path calls `mlx5e_macsec_build_netdev()` to attach `macsec_ops` and feature bits when supported. TX checks metadata dst before invoking MACsec-specific validation and metadata insertion. RX checks CQE metadata marker before attaching MACsec metadata to the SKB.

State and persistence: the header owns no state. It exposes `struct mlx5e_macsec` as opaque to callers and relies on `priv->macsec` allocated in the implementation.

Dependencies and integration points: depends on Linux MACsec, destination metadata, mlx5 driver headers, and `lib/macsec_fs` metadata marker helpers. It lets generic mlx5e datapath code compile with or without MACsec offload.

Risks: disabled stubs must make callers behave as if no offload exists. Metadata marker interpretation must stay aligned with `lib/macsec_fs`. Callers must not dereference the opaque MACsec pointer when the feature is unavailable.

Test signals: build with `CONFIG_MLX5_MACSEC` on/off, verify MACsec feature flags only on capable devices, and validate TX/RX marker checks against actual CQE/SKB metadata.
