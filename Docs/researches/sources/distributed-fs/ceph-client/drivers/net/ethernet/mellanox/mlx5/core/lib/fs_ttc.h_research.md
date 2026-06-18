# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/fs_ttc.h

Purpose: Declares TTC traffic types, tunnel types, parameter structure, and classifier table APIs.

Important APIs and types: `enum mlx5_traffic_types` includes IPv4/IPv6 TCP/UDP, AH/ESP, generic IPv4/IPv6/ANY, and decrypted ESP outer/inner L4 variants. `enum mlx5_tunnel_types` covers GRE, IPIP, and IPv4/IPv6-over-IPv4/IPv6. `struct ttc_params` supplies namespace, flow table attributes, per-traffic destinations, ignore bitmaps, inner TTC tunnel destinations, and IPsec RSS flag. Exports create/destroy, destination forwarding, tunnel support, IPsec rule creation/destruction, and decrypted ESP predicate.

State and dependencies: `struct mlx5_ttc_table` is opaque; callers own destination objects and table lifecycle through this API. Depends on mlx5 flow steering definitions.

Risks and test signals: Traffic-type enum order is used for array indexing and decrypted ESP range checks. Tests should validate enum additions against arrays in `fs_ttc.c`, ignore bitmap bounds, and callers that assume `MLX5_NUM_INDIR_TIRS = MLX5_TT_ANY`.
