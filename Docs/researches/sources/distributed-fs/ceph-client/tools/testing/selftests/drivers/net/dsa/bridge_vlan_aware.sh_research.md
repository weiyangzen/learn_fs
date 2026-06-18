# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/dsa/bridge_vlan_aware.sh

Purpose: DSA wrapper for bridge VLAN-aware forwarding tests.

Important APIs/functions: Local wrapper variables `libdir`/`testname`, `forwarding.config`, and sourcing `../../../net/forwarding/bridge_vlan_aware.sh`.

Control flow: Applies DSA config and delegates to the generic VLAN-aware bridge scenario.

State and persistence: Delegated test creates VLAN-aware bridge state; wrapper only changes shell working directory.

Dependencies and integration points: Requires VLAN filtering support on bridge/DSA ports and shared forwarding libs.

Risks and test signals: Failures indicate DSA VLAN-aware bridge offload/forwarding issues or config mismatch.
