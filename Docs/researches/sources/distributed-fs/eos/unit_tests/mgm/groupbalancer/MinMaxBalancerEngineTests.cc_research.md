# sources/distributed-fs/eos/unit_tests/mgm/groupbalancer/MinMaxBalancerEngineTests.cc

## sources/distributed-fs/eos/unit_tests/mgm/groupbalancer/MinMaxBalancerEngineTests.cc

Purpose: tests `MinMaxBalancerEngine` threshold configuration and source/target classification based on fixed min/max occupancy limits.

Important APIs and types: `BalancerEngine`, `MinMaxBalancerEngine`, `configure`, `populateGroupsInfo`, `updateGroups`, `get_data`, `pickGroupsforTransfer`, and `threshold_group_set`.

Control flow: configuration converts percentages to fractions. The simple case uses min 80 percent and max 90 percent to classify group1 as underfilled and group5 as overfilled, then verifies transfer pair selection. The update-threshold case changes thresholds after population and calls `updateGroups()` to recompute sets.

State and persistence: engine state includes group sizes, threshold values, and derived over/under sets. No external persistence.

Dependencies and integration: part of the group-balancer engine polymorphic interface. Tests instantiate through `std::unique_ptr<BalancerEngine>` then cast to inspect implementation-specific thresholds.

Risks and test signals: boundary values expose floating-point comparison issues; comments note that values exactly at thresholds can classify unexpectedly due to subtraction precision. This is a risk for production balancing near limits.
