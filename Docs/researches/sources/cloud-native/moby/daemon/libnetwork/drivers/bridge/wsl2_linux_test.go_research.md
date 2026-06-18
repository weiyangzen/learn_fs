# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/wsl2_linux_test.go

Purpose: Validates the WSL2 mirrored-mode detection heuristic in a temporary Linux namespace.

Important APIs and functions: `TestMirroredWSL2Workaround` table-drives four cases: no `loopback0`, valid mirrored simulation, non-executable `wslinfo`, and missing `wslinfo`. `simulateWSL2MirroredMode` creates a dummy `loopback0` and optionally points `wslinfoPath` at a temp executable.

Control flow: each subtest isolates network state, sets up simulated conditions, calls `isRunningUnderWSL2MirroredMode`, and restores `wslinfoPath` via cleanup.

State and persistence: mutates namespace link state and the package variable `wslinfoPath` only for the test duration.

Dependencies and integration points: depends on netlink dummy links and the implementation in `wsl2_linux.go`.

Risks: tests the heuristic, not real WSL2. It does not cover non-LinkNotFound netlink errors.

Test signals: gives focused coverage for the file-permission and loopback-gating behavior that prevents false positives.
