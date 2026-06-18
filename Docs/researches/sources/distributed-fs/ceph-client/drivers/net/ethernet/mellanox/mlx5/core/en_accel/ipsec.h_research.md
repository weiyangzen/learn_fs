# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/ipsec.h

Purpose: defines the IPsec offload data model and public mlx5e IPsec API.

Important APIs/types/functions: key structs include `aes_gcm_keymat`, `mlx5_accel_esp_xfrm_attrs`, `mlx5_accel_pol_xfrm_attrs`, `mlx5e_ipsec`, `mlx5e_ipsec_sa_entry`, `mlx5e_ipsec_pol_entry`, `mlx5e_ipsec_rule`, `mlx5e_ipsec_ft`, `mlx5e_ipsec_aso`, HW/SW stats, ESN/lifetime state, and flow table create attrs. It declares lifecycle, flow steering, SA context, ASO, stats, attrs, and devcom event APIs plus disabled stubs.

Control flow and state: persistent state is rooted at `priv->ipsec`, with SADB xarray mapping hardware object IDs to SAs, optional object-ID mapping for uplink reps, refcounted flow-table groups, ASO DMA context protected by spinlock, and workqueue/completion for async events.

Dependencies and integration: includes mlx5 device, XFRM, ID/xarray-related state, ASO, and devcom. It is consumed by IPsec core, flow steering, rxtx, offload, stats, and netdev build code.

Risks and test signals: bitfield attrs and metadata handle widths must stay aligned with hardware and `ipsec_rxtx.h`; disabled stubs must preserve non-IPsec builds. Build with and without `CONFIG_MLX5_EN_IPSEC`, and test object ID limits, stats layout, and uplink rep paths.
