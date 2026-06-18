# sources/control-plane/rook/pkg/daemon/ceph/client/command_test.go

Purpose: validates the shared Ceph command construction and execution adapter behavior that all other client files rely on.

Important test cases: `TestFinalizeCephCommandArgs` verifies standard `ceph` command flags, config path construction, timeout flag insertion, and `KeyringFileOverride`. `TestFinalizeRadosGWAdminCommandArgs` confirms `radosgw-admin` receives standard config/keyring flags but no connect-timeout exception. `TestFinalizeCephCommandArgsToolBox` sets `RunAllCephCommandsInToolboxPod` and verifies `kubectl exec -i <pod> -n <ns> -- timeout <seconds> ceph ...` wrapping. `TestNewRBDCommand` verifies normal RBD execution, Multus-triggered `RemoteExecution`, and early cancellation via `clusterInfo.Context`. `TestNewGaneshaRadosGraceCommand` ensures Ganesha uses `--cephconf`, rejects standard Ceph config/name/keyring/format flags, and honors `RunWithTimeout`.

Control flow and dependencies: tests use `exectest.MockExecutor`, fake Kubernetes clientsets for remote executor behavior, `AdminTestClusterInfo`, and mutable `exec.CephCommandsTimeout`. They inspect positional args after `FinalizeCephCommandArgs()` appends flags, so the tests are sensitive to command ordering.

Risks and coverage gaps: the tests protect the most brittle command-line surfaces, especially toolbox and Ganesha exceptions. They do not fully cover `ExecuteCephCommandWithRetry()`, remote stderr handling, `NewRadosCommand()`, or timeout branches for non-Ganesha local command execution. They also mutate globals (`RunAllCephCommandsInToolboxPod`, `exec.CephCommandsTimeout`) and manually reset only the toolbox pod, so parallel execution would require care.
