# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/dsa/bridge_mld.sh

Purpose: DSA wrapper for shared bridge MLD snooping/forwarding tests.

Important APIs/functions: Same wrapper pattern: resolve script directory/name, source `forwarding.config`, enter `net/forwarding`, and source matching test.

Control flow: Delegates all behavior to the common `bridge_mld.sh` forwarding script.

State and persistence: Runtime bridge/MLD state is created by the delegated script and cleaned there.

Dependencies and integration points: Requires IPv6 multicast support, DSA forwarding config, and shared forwarding libraries.

Risks and test signals: Failure points at DSA MLD handling or generic forwarding test failure under DSA topology.
