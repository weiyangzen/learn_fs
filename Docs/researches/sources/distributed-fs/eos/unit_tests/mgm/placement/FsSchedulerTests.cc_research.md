# sources/distributed-fs/eos/unit_tests/mgm/placement/FsSchedulerTests.cc

## sources/distributed-fs/eos/unit_tests/mgm/placement/FsSchedulerTests.cc

Purpose: tests `FSScheduler`, a higher-level scheduler wrapper that consumes cluster-manager handlers and placement strategy configuration.

Important APIs and types: `FSScheduler`, `ClusterMgr`, `ClusterMgrHandler`, `TestClusterMgrHandler`, strategy configuration methods, and placement result APIs.

Control flow: the test handler builds or exposes cluster state for the scheduler. Tests cover construction, null-handler behavior, default scheduler behavior, geo-scheduler error paths, round-robin placement, and changing placement strategies globally or per space.

State and persistence: state resides in scheduler configuration and the test cluster manager. No persistent cluster store is used.

Dependencies and integration: bridges placement schedulers with MGM-facing cluster-manager handler abstractions. It validates error handling around missing handler state and strategy changes.

Risks and test signals: this file is a contract test for integration wiring rather than deep strategy correctness. Strategy name/config changes can break expected behavior.
