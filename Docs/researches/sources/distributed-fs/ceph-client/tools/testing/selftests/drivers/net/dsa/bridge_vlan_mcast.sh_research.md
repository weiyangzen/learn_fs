# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/dsa/bridge_vlan_mcast.sh

Purpose: DSA wrapper for VLAN multicast bridge forwarding tests.

Important APIs/functions: Sources local `forwarding.config` then sources the shared forwarding test named by the wrapper basename.

Control flow: All test logic is delegated to `net/forwarding/bridge_vlan_mcast.sh`.

State and persistence: Bridge VLAN/multicast state is managed by the delegated script.

Dependencies and integration points: Requires DSA driver VLAN multicast support and generic forwarding helper stack.

Risks and test signals: Failures usually reflect multicast VLAN offload/forwarding regressions in DSA or missing testbed config.
