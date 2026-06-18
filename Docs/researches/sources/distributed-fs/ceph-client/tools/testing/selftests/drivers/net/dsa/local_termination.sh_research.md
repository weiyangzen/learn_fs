# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/dsa/local_termination.sh

Purpose: DSA wrapper for local termination forwarding tests.

Important APIs/functions: Resolves local directory, sources `forwarding.config`, enters shared forwarding directory, sources matching `local_termination.sh`.

Control flow: Delegates all scenario setup and assertions to the shared forwarding test.

State and persistence: Delegated script manages interfaces, routes, and cleanup.

Dependencies and integration points: Exercises DSA local host termination paths through generic forwarding test infrastructure.

Risks and test signals: Failures may indicate DSA CPU-port/local-delivery regressions or incorrect config.
