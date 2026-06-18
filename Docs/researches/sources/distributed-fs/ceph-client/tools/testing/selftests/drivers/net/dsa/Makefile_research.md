# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/dsa/Makefile

Purpose: Build/install manifest for DSA-specific wrappers around forwarding selftests.

Important APIs/variables: `TEST_PROGS`, `TEST_FILES`, `TEST_INCLUDES`, `forwarding.config`, `run_net_forwarding_test.sh`, and inclusion of `../../../lib.mk`.

Control flow: Registers bridge, MDB/MLD, VLAN aware/unaware/mcast, local termination, no-forwarding, TC action, and FDB stress tests. Most scripts are thin wrappers that source corresponding forwarding tests after applying DSA config.

State and persistence: Make-only state; runtime topology is owned by forwarding scripts.

Dependencies and integration points: Depends on `tools/testing/selftests/net/forwarding` scripts and libs, plus DSA-specific `forwarding.config`.

Risks and test signals: Missing includes or config file breaks wrappers. This Makefile is the bridge between driver DSA tests and shared net forwarding coverage.
