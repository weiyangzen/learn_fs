# sources/distributed-fs/beegfs/common/tests/TestTargetCapacityPools.cpp

Purpose: This regression test exercises `TargetCapacityPools::chooseTargetsInterdomain()` after a target changes capacity pool membership, specifically with empty chooser groups.

Important APIs/types/functions: It constructs `TargetCapacityPools pools(false, ...)`, calls `addOrUpdate()` twice for target `1` on node `1`, first as `CapacityPool_NORMAL` and then as `CapacityPool_LOW`, and then asks for four interdomain targets.

Control flow: Moving the target from NORMAL to LOW must remove the stale NORMAL group from the chooser. The test then expects only one chosen target and verifies it is target `1`.

State and persistence behavior: The test mutates in-memory pool membership and chooser structures only. It protects transient allocator state that is populated from management capacity-pool syncs.

Dependencies and integration: Capacity pools influence placement decisions. The interdomain chooser depends on accurate pool-to-domain membership and must not retain empty groups that distort selection.

Risks and test signals: The test catches a specific stale-group bug. It does not cover multiple domains, buddy groups, pool thresholds, concurrent updates, or weighted/randomized choice distribution. Because the expected vector size is one after asking for four targets, it also documents graceful partial fulfillment when insufficient targets exist.
