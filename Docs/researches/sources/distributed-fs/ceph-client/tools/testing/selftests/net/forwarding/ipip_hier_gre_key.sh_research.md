
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ipip_hier_gre_key.sh

Purpose: Hierarchical IPv4 GRE test with shared key `22`, combining underlay/overlay VRF separation with keyed tunnel lookup.

Important APIs/functions: `setup_prepare` passes `key 22` to both hierarchical create helpers; `gre_hier4` uses `ping_test`; `gre_mtu_change` uses `test_mtu_change gre`.

Control flow: creates host VRFs, hierarchical GRE topology, then executes keyed tunnel reachability and MTU transition tests.

State/persistence: creates keyed GRE devices bound through dummy underlay endpoints, VLANs, VRFs, routes, and forwarding sysctls. Cleanup reverses the topology and route-rule changes.

Dependencies/integration: imports `lib.sh` and `ipip_lib.sh`; requires iproute2 and kernel support for `gre key` plus VRF device binding.

Risks: shared key path can expose offload or lookup issues not covered by unkeyed hierarchical GRE. Cleanup must run after `pre_cleanup` even when tests fail.

Test signals: ping through "gre hierarchical with key" succeeds, and MTU behavior passes common assertions.
