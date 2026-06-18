# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc_tun_gre.c

Purpose: provides GRE/GRETAP tunnel offload operations for mlx5 TC. It supports NVGRE-style encapsulation/decapsulation for Ethernet payloads and optional GRE key matching.

Important APIs and types: helpers check `nvgre_encap_decap` capability, calculate GRE header length from tunnel flags, initialize encap attributes with `MLX5_REFORMAT_TYPE_L2_TO_NVGRE`, generate GRE headers, and parse GRE protocol/key matches. The exported `gre_tunnel` uses tunnel type `GRETAP`, L3 match level, no UDP parser, generic encap equality, and protocol-specific parse/header callbacks.

Control flow: header generation sets outer IP protocol to GRE, rejects checksum and sequence flags because hardware does not calculate them, writes `ETH_P_TEB`, converts tunnel flags to GRE flags, and appends key when requested. Decap parsing forces outer IP protocol GRE, matches GRE protocol `ETH_P_TEB`, and copies optional encap keyid masks/values into misc GRE key fields.

State and persistence: no persistent state is stored here. Encap key identity comes from the common generic equality helper and the shared encap table in `tc_tun_encap.c`.

Dependencies and integration points: Linux GRE helpers, common tunnel abstraction, mlx5 eswitch capability checks, flow dissector encap keyid, and mlx5 misc match fields.

Risks and test signals: GRE checksum/sequence flags are unsupported for encap; callers must receive `-EOPNOTSUPP`. Key matching depends on exact keyid masks and mlx5 misc fields. Test with keyed and unkeyed GRETAP, checksum/sequence rejection, protocol match, capability-negative hardware, IPv4/IPv6 outer routes through common code, and encap reuse for identical GRE keys.
