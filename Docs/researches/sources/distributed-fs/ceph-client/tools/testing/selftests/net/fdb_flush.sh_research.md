# sources/distributed-fs/ceph-client/tools/testing/selftests/net/fdb_flush.sh

Purpose: this script validates `bridge fdb flush` behavior for VXLAN and bridge devices. It checks flushing by device, VNI, source VNI, destination UDP port, destination IP, nexthop id, FDB state, FDB flags, combinations of arguments, remote attributes in multicast VXLAN entries, bridge VLAN, and mixed bridge/VXLAN master/self behavior.

Important APIs and functions: it uses `ip`, `bridge`, net namespaces, VXLAN links, bridge links with VLAN filtering, nexthop objects with `fdb`, and common shell helpers from `lib.sh`. Key local helpers are `run_cmd`, `log_test`, `fdb_add_mac_pool_1`, `fdb_add_mac_pool_2`, `fdb_check_n_entries_by_dev_filter`, `nexthops_add`, `vxlan_test_flush_by_state`, `vxlan_test_flush_by_flag`, `multicast_fdb_entries_add`, `setup`, and `cleanup`.

Control flow: startup checks root, `ip`, iproute2 flush syntax support (`[no]router`), and kernel VXLAN flush support. It then iterates selected tests, running fresh `setup; test; cleanup` for each. Setup creates a namespace, two VXLAN devices, and two VLAN-filtering bridges. Individual tests add deterministic MAC pools with attributes, assert baseline entry counts via filtered `bridge fdb show`, execute `bridge fdb flush` with specific selectors, and verify only intended entries disappeared. Bridge/VXLAN mixed tests check that bridge entries can be flushed even when the VXLAN driver rejects unsupported VLAN self flush with exit 255.

State and persistence: state is namespace-local links, bridges, VXLAN devices, FDB entries, VLAN membership, and nexthop objects. No files persist. Cleanup removes created links and namespace after every test case, reducing cross-case contamination.

Dependencies and integration points: requires recent iproute2 and kernel VXLAN FDB flush support. It exercises both bridge core and VXLAN driver FDB paths, including remote lists for multicast zero-MAC entries.

Risks and test signals: `log_test` declares local counters, so its counter variables are not useful for a final summary, but the script primarily uses immediate pass/fail output and command exit status. Grep-based entry counting can be sensitive to bridge output formatting. Strong signals are expected entry counts before and after each flush and the special expected 255 return for unsupported VXLAN VLAN flush with bridge-side effects.
