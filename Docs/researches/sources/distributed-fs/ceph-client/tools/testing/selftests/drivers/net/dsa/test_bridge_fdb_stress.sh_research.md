# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/dsa/test_bridge_fdb_stress.sh

Purpose: DSA-oriented bridge FDB stress test wrapper.

Important APIs/functions: `cleanup()`, local config loading, bridge/FDB manipulation through shared forwarding helpers, and stress iteration logic in the sourced test path.

Control flow: The script prepares DSA forwarding context and runs an FDB stress scenario that creates/removes many forwarding database entries, then cleans up on exit.

State and persistence: Creates transient bridge/FDB entries and possibly large numbers of dynamic/static MAC entries; cleanup removes test state.

Dependencies and integration points: Requires DSA switch FDB programming support, bridge tooling, and forwarding libraries.

Risks and test signals: Failures indicate FDB resource, aging, add/delete, or offload synchronization problems. Stress volume can expose cleanup leaks.
