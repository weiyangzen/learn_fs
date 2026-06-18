# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc_tun.h

Purpose: declares the generic tunnel-offload abstraction used by mlx5 TC. It lets protocol-specific VXLAN, GENEVE, GRE, and MPLS-over-UDP files plug capability checks, header generation, match parsing, and encap key comparison into the common route/header machinery.

Important APIs and types: tunnel type enum defines `UNKNOWN`, `VXLAN`, `GENEVE`, `GRETAP`, and `MPLSOUDP`. `struct mlx5e_encap_key` pairs an `ip_tunnel_key` with tunnel ops for hash/equality. `struct mlx5e_tc_tunnel` contains tunnel type, match level, and callbacks for `can_offload`, `calc_hlen`, `init_encap_attr`, `generate_ip_tun_hdr`, `parse_udp_ports`, `parse_tunnel`, `encap_info_equal`, and optional `get_remote_ifindex`. The header exports the four protocol ops objects and common functions for tunnel selection, encap attr init, IPv4/IPv6 header create/update, route lookup, device offload checks, parsing, UDP port parsing, and equality helpers.

Control flow: TC action parsing stores tunnel info in parse attributes, then encap attach calls `mlx5e_get_tc_tun` and `mlx5e_tc_tun_init_encap_attr`. Header construction calls the selected tunnel's length and header-generation callbacks. Decap parsing calls UDP-port and protocol-specific parsing callbacks, then common outer IP parsing. Equality callbacks are used by encap hash-table reuse.

State and persistence: no runtime state is owned here. The callback table is effectively a static vtable and must remain consistent with each protocol implementation and common encap code.

Dependencies and integration points: available under `CONFIG_MLX5_ESWITCH`; depends on netdevice, mlx5 flow steering, TC classifier, netlink extack, mlx5 `en.h`, and representor declarations. IPv6 helpers are stubbed to `-EOPNOTSUPP` when IPv6 support is unavailable.

Risks and test signals: adding a tunnel type requires filling all callbacks that common code assumes are present. Misreported `match_level` or equality behavior can cause under-matching or encap reuse bugs. Test with eswitch disabled/enabled builds, IPv6 disabled builds, protocol-specific offload gating, and hash reuse for tunnels with and without options.
