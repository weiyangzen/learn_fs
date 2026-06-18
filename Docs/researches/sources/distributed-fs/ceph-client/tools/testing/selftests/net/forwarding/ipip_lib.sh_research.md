
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ipip_lib.sh

Purpose: Shared IPv4 GRE/IP-in-IP topology library for flat and hierarchical tunnel tests.

Important APIs/functions: host helpers `h1_create/destroy`, `h2_create/destroy`; switch helpers `sw1_flat_create/destroy`, `sw2_flat_create/destroy`, `sw1_hierarchical_create/destroy`, `sw2_hierarchical_create/destroy`; MTU helpers `topo_mtu_change` and `test_mtu_change`.

Control flow: callers source this after `lib.sh`, set global interface names, then call create helpers. Flat helpers place overlay and underlay in the same/default VRF on SW1 and bound VRF on SW2. Hierarchical helpers introduce `dummy1`/`dummy2` in underlay VRFs and master GRE devices to overlay VRFs.

State/persistence: creates VRFs, VLAN 111 links, GRE/IPIP tunnel devices `g1a`/`g2a`, dummy devices, IPv4 routes, and addresses. It stores no state outside kernel networking.

Dependencies/integration: expects `lib.sh` functions already loaded. Extra tunnel parameters are passed through to `tunnel_create`, enabling keyed GRE variants.

Risks: cleanup assumes exact route/address state and device names. `test_mtu_change` uses large ping size and route MTU behavior, which can vary across drivers/offloads.

Test signals: callers use ping success and MTU failure/success transition to establish forwarding and MTU propagation.
