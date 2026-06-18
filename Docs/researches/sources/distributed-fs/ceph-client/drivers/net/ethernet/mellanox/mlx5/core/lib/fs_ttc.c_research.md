# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/fs_ttc.c

Purpose: Implements TTC (traffic type classifier) flow tables that classify RX traffic by IP version, L4 protocol/type, tunnel protocol, and IPsec decrypted ESP attributes, then forward to caller-provided destinations.

Important APIs and flow: `mlx5_create_ttc_table()` selects outer L4-type matching support, chooses group layout including optional IPsec RSS groups, creates the flow table/groups, and generates rules for each non-ignored traffic type and optional tunnel destination. `mlx5_create_inner_ttc_table()` builds equivalent inner-header tables. `mlx5_ttc_fwd_dest()` and `mlx5_ttc_fwd_default_dest()` update destinations after creation. IPsec helpers create/destroy decrypted ESP outer and inner rules with refcounting. Support helpers expose traffic names, table handle, tunnel inner-FT support, ESP group presence, and tunnel protocol mapping.

State and dependencies: `struct mlx5_ttc_table` stores group layout, core device, FT/groups, per-TT rule/default destination, tunnel rules, IPsec refcount, and mutex. It depends on mlx5 flow namespaces, firmware field support (`outer_ip_version`, `outer_l4_type`, inner variants), Linux IP protocol constants, and caller-provided `ttc_params` destinations/ignore bitmaps.

Risks and test signals: Group sizes/order must match generated rules and decrypted ESP ranges. Destroy assumes initialized mutex and group arrays; creation error paths call full destroy. Tests should cover outer and inner TTC, L4-type supported/unsupported, IPv4/IPv6 ethertype versus ip_version matching, tunnel support matrix, ignored destinations, destination modification, IPsec RSS refcounting, and create failure cleanup.
