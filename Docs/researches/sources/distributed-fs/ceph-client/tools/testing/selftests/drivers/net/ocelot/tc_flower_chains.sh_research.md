# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/ocelot/tc_flower_chains.sh

Purpose: Validates Ocelot TC flower chain mapping across ingress/egress lookup blocks and actions such as VLAN pop/push/modify and skb priority edit.

Important APIs/functions: Chain id helpers `IS1`, `IS2`, and `ES0` encode Ocelot lookup stages. `create_tcam_skeleton` installs goto-chain skeleton filters. Tests are `test_vlan_pop`, `test_vlan_push`, `test_vlan_ingress_modify`, `test_vlan_egress_modify`, and `test_skbedit_priority`.

Control flow: Setup brings host and switch ports up, creates a bridge and VLAN subinterfaces on `h1`, installs TC skeleton and action filters on `swp1`, and prepares traffic expectations. Each test sends traffic and verifies untagged/tagged reception or priority behavior, adding temporary filters and bridge VLAN filtering as needed.

State and persistence: Mutates TC clsact filters on switch ports, bridge VLAN filtering, VLAN subinterfaces, and bridge membership. Cleanup removes VLANs, clsact, and bridge.

Dependencies and integration: Requires Ocelot hardware TCAM offload, `tc` flower skip_sw support, forwarding helper variables, and host/switch topology.

Risks: Chain numbers encode hardware pipeline assumptions and can break if driver mapping changes. TC offload failure should be surfaced by `skip_sw`; incorrect bridge VLAN state can mask action behavior.

Test signals: Correct runs observe VLAN pop producing untagged reception, VLAN push/modify producing expected tags, egress modification on `swp2`, and skbedit priority affecting frame prioritization.
