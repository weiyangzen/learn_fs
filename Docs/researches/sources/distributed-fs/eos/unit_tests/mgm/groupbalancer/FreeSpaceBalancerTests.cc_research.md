# sources/distributed-fs/eos/unit_tests/mgm/groupbalancer/FreeSpaceBalancerTests.cc

## sources/distributed-fs/eos/unit_tests/mgm/groupbalancer/FreeSpaceBalancerTests.cc

Purpose: tests `FreeSpaceBalancerEngine` calculations that classify groups by available free space and optional blocklist configuration.

Important APIs and types: `FreeSpaceBalancerEngine`, `populateGroupsInfo`, `configure`, `recalculate`, `updateGroups`, `getGroupFreeSpace`, `getFreeSpaceULimit`, `getFreeSpaceLLimit`, and `threshold_group_set`.

Control flow: the simple case populates five ON groups with used/capacity values, checks computed average free-space target and limits, and asserts over/under-threshold sets. The blocklisting case removes configured groups from source/target eligibility, recalculates, and verifies new target/source sets and limits.

State and persistence: all state is in-memory inside the engine's group data and config map. No external persistence.

Dependencies and integration: validates interaction between engine configuration parsing and group classification. It is part of the larger group-balancer decision path that chooses transfer source and target groups.

Risks and test signals: threshold arithmetic uses integer byte examples for deterministic expectations. Naming can be counterintuitive: under-threshold groups are targets in the free-space sense. Blocklist config key spelling is important to preserve.
