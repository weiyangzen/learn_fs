# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/rep/tc.c

Purpose: implements TC offload plumbing for mlx5 representors, including direct and indirect block callbacks, tunnel neighbour encap attachment, flow reoffload, action offload, and representor RX metadata handling.

Important APIs/functions: `mlx5e_rep_tc_init/cleanup/enable/disable`, `mlx5e_rep_setup_tc`, `mlx5e_rep_tc_netdevice_event_register/unregister`, `mlx5e_rep_encap_entry_attach/detach`, `mlx5e_rep_update_flows`, `mlx5e_rep_tc_event_port_affinity`, and `mlx5e_rep_tc_receive`.

Control flow: direct TC setup registers ingress eswitch flower/matchall callbacks and normalizes FT offload rules into the reserved chain. TC init creates shared eswitch TC tables and unready-flow state. Indirect block registration supports tunnel devices, VLANs on the representor, macvlan passthru, bond-backed macvlan, and OVS internal-port egress when supported. Indirect flow callbacks route flower replace/destroy/stats to the uplink representor context. Action callbacks dispatch to mlx5e TC action implementations. RX handling decodes reg_c0/reg_c1 metadata, restores CT/tunnel/IPsec context, updates skb state, and forwards through `dev_queue_xmit` or GRO.

State and persistence: uplink representor state owns TC tables, unready flow list, indirect block list, tunnel entropy refs, neighbour encap links, and reoffload work. Flow hardware state persists in eswitch tables until removed.

Dependencies and integration: uses mlx5e TC core, neighbour tracking, mapping contexts, tunnel helpers, flow block APIs, fs chains, CT, sample, int-port, IPsec RX, and representor private data.

Risks: indirect block binding must reject unsupported devices and avoid duplicate binds. Encap updates require RTNL plus eswitch encap table lock. RX metadata parsing must keep bit masks aligned with firmware register layout; wrong decoding can mis-forward or drop packets.

Test signals: flower replace/delete/stats, matchall stats, FT offload chain/prio validation, indirect tunnel/VLAN/macvlan/OVS offloads, neighbour MAC changes, port-affinity reoffload, and representor RX with CT/tunnel/IPsec metadata.
