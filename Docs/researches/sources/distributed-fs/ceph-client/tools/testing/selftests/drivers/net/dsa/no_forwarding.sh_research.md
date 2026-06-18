# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/dsa/no_forwarding.sh

Purpose: DSA wrapper for shared no-forwarding isolation tests.

Important APIs/functions: Local config source plus forwarding script delegation.

Control flow: Executes the common no-forwarding test under DSA-specific port configuration.

State and persistence: No local state beyond shell variables; delegated test owns network state.

Dependencies and integration points: Requires DSA testbed and shared forwarding scripts.

Risks and test signals: Failures signal traffic leakage when forwarding should be disabled, DSA isolation issues, or wrapper/config failure.
