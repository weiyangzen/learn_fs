# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc_tun_geneve.c

Purpose: provides the `mlx5e_tc_tunnel` implementation for GENEVE. It gates offload on flex-parser support, builds GENEVE UDP headers including VNI and options, parses GENEVE decap match keys, and compares encap keys including options.

Important APIs and types: static helpers include capability check, header length calculation, UDP destination-port validation, encap attr init, tunnel-id-to-VNI conversion, header generation, VNI parsing, option parsing, OAM/protocol parsing, and option-aware equality. The exported object is `geneve_tunnel` with `MLX5E_TC_TUNNEL_TYPE_GENEVE` and L4 match level.

Control flow: encap init selects VXLAN-style L2-to-VXLAN reformat because hardware inserts a software-provided tunnel header at the same point. Header generation writes UDP destination, GENEVE version, option length, OAM and critical bits, VNI, protocol type `ETH_P_TEB`, and optional TLV bytes. Decap parse first requires valid UDP destination port, then forces OAM off and optionally protocol type, parses VNI when requested and supported, and parses a single GENEVE option into mlx5 misc/misc3 fields after creating a firmware TLV option object.

State and persistence: this file owns no long-lived state, but `mlx5_geneve_tlv_option_add` creates hardware/parser state for option matching. Encap equality inspects option bytes stored adjacent to `ip_tunnel_info`.

Dependencies and integration points: Linux GENEVE definitions, mlx5 geneve library, common tunnel parse/header code, hardware capability fields for GENEVE VNI, OAM, protocol type, option length, TLV option data, and TLV existence.

Risks and test signals: limitations include default GENEVE port only, one option match, unsupported zero option-data matches, unsupported option lengths, and dependency on flex parser capabilities. Test with default/nondefault port, VNI match, no options, one valid option, excessive option length, critical/OAM flags, and capability-negative hardware.
