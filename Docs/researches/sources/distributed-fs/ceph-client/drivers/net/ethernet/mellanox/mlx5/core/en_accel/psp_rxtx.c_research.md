# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/psp_rxtx.c

Purpose: PSP datapath handling for TX encapsulation/WQE metadata and RX decrypted-packet validation.

Important APIs, types, and functions: `mlx5e_psp_handle_tx_skb()` obtains PSP association state and calls `psp_dev_encapsulate()`. `mlx5e_psp_tx_build_eseg()` programs SW parser offsets, metadata key id, and trailer insertion flags in the Ethernet segment. `mlx5e_psp_handle_tx_wqe()` sets inline trailer length. `mlx5e_psp_offload_handle_rx_skb()` validates CQE metadata syndrome and hands decrypted packets to `psp_dev_rcv()`. Internal helpers are `mlx5e_psp_set_state()` and `mlx5e_psp_set_swp()`.

Control flow: TX first looks up a PSP association under RCU. If absent, the packet continues as normal. If present, it records trailer length, SPI, version, and driver key id, then encapsulates the packet through the kernel PSP stack. For GSO packets it rewrites the inner TCP checksum seed. WQE build later sets SWP offsets/flags, applies a ConnectX-7 PSP LSO workaround by zeroing L3 offsets, writes key id into flow metadata, and asks hardware to insert the trailer. RX checks the PSP metadata marker/syndrome installed by flow steering; only decrypted syndrome is accepted, then `psp_dev_rcv()` strips/validates and `skb->decrypted` is set.

State and persistence: per-packet state is stored in `struct mlx5e_accel_tx_psp_state`. Persistent association/key state lives in the kernel PSP association and `pas->drv_data` created by `psp.c`. TX drop count is incremented in `priv->psp`.

Dependencies and integration points: depends on Linux SKB, IPv4/IPv6, UDP/TCP checksum helpers, kernel PSP APIs, and mlx5e TX WQE builders. It relies on PSP flow tables to interpret `keyid` metadata and RX syndrome bits.

Risks: packet parsing for inner protocols must match SKB encapsulation metadata. GSO checksum repair assumes TCP inner header. `*(u32 *)pas->drv_data` must match PSP association driver storage layout. RX currently uses fixed generation zero and drops all non-decrypted syndromes.

Test signals: TX with no association, TX association for IPv4/IPv6, transport and tunneled payloads, GSO TCP checksum correctness, encapsulation failure drop reason/counter, RX decrypted packets, RX auth/frame errors, and disabled PSP paths.
