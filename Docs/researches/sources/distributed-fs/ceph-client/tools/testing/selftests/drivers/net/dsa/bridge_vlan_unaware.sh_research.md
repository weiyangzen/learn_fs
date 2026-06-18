# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/dsa/bridge_vlan_unaware.sh

Purpose: DSA wrapper for bridge VLAN-unaware forwarding tests.

Important APIs/functions: Wrapper path resolution, local `forwarding.config`, `cd` to shared forwarding directory, and `source "./$testname" "$@"`.

Control flow: Delegates to the shared VLAN-unaware bridge test under DSA configuration.

State and persistence: Runtime state belongs to the shared test.

Dependencies and integration points: Requires DSA switch ports and common forwarding libraries.

Risks and test signals: Failures point at VLAN-unaware DSA bridge forwarding behavior or wrapper/config errors.
