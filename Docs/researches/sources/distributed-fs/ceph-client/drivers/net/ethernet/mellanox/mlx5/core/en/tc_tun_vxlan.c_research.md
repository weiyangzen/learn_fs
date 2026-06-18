# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc_tun_vxlan.c

Purpose: provides VXLAN tunnel operations for mlx5 TC, including registered-port validation, VXLAN header generation, VNI and GBP option parsing, and option-aware encap equality.

Important APIs and types: helpers check `vxlan_encap_decap`, calculate VXLAN header length, validate UDP destination port against the mlx5 VXLAN port registry, initialize encap attr as `MLX5_REFORMAT_TYPE_L2_TO_VXLAN`, generate VXLAN headers, parse GBP options, parse VNI, compare options, and fetch VXLAN remote ifindex. The exported `vxlan_tunnel` has L4 match level and the common UDP parser wrapper.

Control flow: encap init rejects unregistered destination ports. Header generation rejects malformed VXLAN option lengths, writes UDP destination, sets VNI flag, converts tunnel id to VNI field, and optionally builds GBP metadata. Decap parsing requires an encap keyid for VNI work; with GBP options it validates option type, length, mask, and custom tunnel-header capability, then writes GBP and shifted VNI into misc5 fields. Without options it requires `outer_vxlan_vni` support and writes VNI to misc fields. The remote-ifindex callback returns the VXLAN default destination ifindex for route lookup.

State and persistence: no local long-lived state. Port registration is held by the mlx5 VXLAN subsystem, and encap object sharing is handled by common encap code.

Dependencies and integration points: Linux VXLAN and IP tunnel helpers, mlx5 VXLAN library, common tunnel code, hardware capability fields for VXLAN VNI and custom tunnel headers, and flow dissector encap key/options.

Risks and test signals: risks include stale port registration, GBP mask validation, mixing symbolic and custom tunnel fields, and remote-ifindex routing behavior. Test registered and unregistered ports, VNI match with and without GBP, invalid GBP length/mask/type, VXLAN GBP encap, remote-ifindex route lookup, and hardware without VNI/custom header support.
