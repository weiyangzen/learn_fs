# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/dsa/bridge_mdb.sh

Purpose: DSA wrapper for shared bridge MDB forwarding tests.

Important APIs/functions: `readlink -f`, `basename`, source `forwarding.config`, `cd` into `net/forwarding`, and source `./bridge_mdb.sh "$@"`.

Control flow: Delegates all test cases to the common forwarding implementation under a DSA-specific configuration.

State and persistence: Delegated script creates bridge/MDB/runtime topology; wrapper persists nothing.

Dependencies and integration points: Requires DSA forwarding config and shared bridge MDB test. Exercises multicast database handling through DSA switch ports.

Risks and test signals: Failures can signal DSA MDB offload/bridge regressions or wrapper/config path problems.
