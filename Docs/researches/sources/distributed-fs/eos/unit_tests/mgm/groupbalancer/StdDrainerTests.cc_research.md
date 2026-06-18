# sources/distributed-fs/eos/unit_tests/mgm/groupbalancer/StdDrainerTests.cc

## sources/distributed-fs/eos/unit_tests/mgm/groupbalancer/StdDrainerTests.cc

Purpose: tests `StdDrainerEngine`, which selects transfers from groups in drain state to eligible online target groups.

Important APIs and types: `StdDrainerEngine`, `engine_conf_t`, `GroupStatus::DRAIN`, `GroupStatus::ON`, `pickGroupsforTransfer`, and `eos::common::pickIndexRR`.

Control flow: default config checks fallback threshold `0.0001`. The simple case classifies one draining source and two under-threshold targets. Round-robin tests populate multiple drain sources and online targets, then verify deterministic source/target selection for explicit seeds and wraparound over many iterations. `pickFS` simulates per-group filesystem selection using separate seeds.

State and persistence: engine stores group classification and thresholds in memory. The test-local `mGroupFSSeed` models independent filesystem round-robin state per source group.

Dependencies and integration: validates drain-specific balancing decisions and expected interaction with container utility round-robin helpers.

Risks and test signals: seed type is `uint8_t`; the loop explicitly checks wraparound after 5000 increments. Production code relying on small seed types must tolerate rollover.
