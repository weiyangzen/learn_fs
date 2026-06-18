# sources/distributed-fs/eos/unit_tests/mgm/groupbalancer/StdDevBalancerEngineTests.cc

## sources/distributed-fs/eos/unit_tests/mgm/groupbalancer/StdDevBalancerEngineTests.cc

Purpose: tests `StdDevBalancerEngine`, which classifies groups by deviation from average occupancy using configurable min and max thresholds.

Important APIs and types: `StdDevBalancerEngine`, `BalancerEngine`, `calculateAvg`, threshold getters, `populateGroupsInfo`, `updateGroups`, `get_data`, and `pickGroupsforTransfer`.

Control flow: configure test checks percent parsing. The simple test populates five groups around an average of 0.85 and expects group5 as source and group1 as target. Threshold update tests reduce deviation thresholds and assert recomputed over/under sets. The multi-threshold test verifies asymmetric min/max threshold handling.

State and persistence: in-memory engine state only. Derived sets depend on configured thresholds and current group map.

Dependencies and integration: extends the common balancer engine abstraction and utility average calculation. It validates behavior used by group-balancing transfer planning.

Risks and test signals: exact and near floating-point assertions expose precision sensitivity. Comments document known boundary quirks where equality can become over-threshold because of floating-point subtraction.
