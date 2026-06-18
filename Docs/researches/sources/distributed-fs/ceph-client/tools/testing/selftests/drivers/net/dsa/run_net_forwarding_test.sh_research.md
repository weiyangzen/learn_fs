# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/dsa/run_net_forwarding_test.sh

Purpose: Generic DSA launcher that runs a named/shared net forwarding test with DSA config.

Important APIs/functions: `readlink -f`, `dirname`, source `forwarding.config`, `cd ../../../net/forwarding/`, and source a target test script.

Control flow: It is a delegation shim rather than a specific test case, allowing the DSA suite to invoke common forwarding tests consistently.

State and persistence: No own runtime network state; delegated test controls setup/cleanup.

Dependencies and integration points: Depends on local `forwarding.config` and the shared forwarding directory. Useful for tests listed as data files or ad hoc invocation.

Risks and test signals: Incorrect working directory or missing target script makes all delegated execution fail.
