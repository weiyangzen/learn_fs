# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/dsa/tc_actions.sh

Purpose: DSA wrapper for shared TC actions forwarding tests.

Important APIs/functions: Sources DSA `forwarding.config` and delegates to `net/forwarding/tc_actions.sh`.

Control flow: No local test logic; it routes execution through shared forwarding infrastructure.

State and persistence: TC filters/actions and network state are created by delegated test.

Dependencies and integration points: Requires DSA TC offload/action support as applicable, TC tooling, and forwarding helpers.

Risks and test signals: Failures indicate DSA TC action offload/forwarding regressions or missing offload support expected by config.
