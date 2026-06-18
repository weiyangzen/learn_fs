# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/dsa/tc_taprio.sh

Purpose: DSA wrapper for a shared TAPRIO/time-aware scheduling forwarding test.

Important APIs/functions: Wrapper path resolution, `forwarding.config`, and source of matching forwarding script in `net/forwarding`.

Control flow: Delegates scenario execution to the shared TAPRIO test with DSA-specific interfaces.

State and persistence: Delegated script manages qdiscs, schedules, links, and cleanup.

Dependencies and integration points: Requires TC TAPRIO support and DSA hardware/testbed support for the scenario.

Risks and test signals: Failures can reflect TAPRIO offload/scheduling issues in DSA or unsupported hardware features.
