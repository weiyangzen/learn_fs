# sources/control-plane/rook/pkg/daemon/ceph/client/mon_test.go

Purpose: validates Ceph command argument construction from a monitor-related perspective and tests stretch monitor operations and mon dump parsing.

Important test cases: `TestCephArgs` checks standard args for `ceph` and `rbd`, timeout flags, config/keyring paths, toolbox `kubectl` wrapping, and config-dir variants. `TestStretchElectionStrategy` asserts `mon set election_strategy connectivity`. `TestStretchClusterMonTiebreaker` asserts `mon enable_stretch_mode` and `mon set_new_tiebreaker` commands. `TestMonDump` parses a realistic mon dump fixture and checks election strategy, CRUSH location, mon names/ranks, and quorum size.

Control flow and dependencies: tests use `exec.CephCommandsTimeout`, `RunAllCephCommandsInToolboxPod`, mock executors, and `AdminTestClusterInfo()`. They reset the toolbox global after use.

Risks and coverage gaps: there is no direct test for `GetMonQuorumStatus()`, `CreateDefaultStretchCrushRule()`, idempotent stretch-mode already-engaged error handling, invalid JSON, or command errors. Like command tests, this file mutates globals and must be run carefully if tests become parallelized.
