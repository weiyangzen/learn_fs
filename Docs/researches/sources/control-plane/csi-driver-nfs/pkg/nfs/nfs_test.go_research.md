# sources/control-plane/csi-driver-nfs/pkg/nfs/nfs_test.go

Purpose: tests driver helpers that are shared across identity, controller, and node tests.

Important APIs and helpers: `NewEmptyDriver`, `TestNewFakeDriver`, `TestIsCorruptedDir`, `TestRun`, `TestNewControllerServiceCapability`, `TestNewNodeServiceCapability`, and `TestReplaceWithMap`.

Control flow: `NewEmptyDriver` builds small in-memory drivers with optional missing name or version and initializes locks plus the stats cache. `TestRun` starts the gRPC server on `tcp://127.0.0.1:0` with test mode enabled so it stops itself after startup. Capability tests instantiate several enum values. Replacement tests cover empty strings, empty keys, empty values, and multiple PVC/PV placeholders.

State and persistence behavior: creates temporary directories and a symlink for corrupted-dir checks, and starts a transient local gRPC listener. No volume state is persisted.

Dependencies and integration points: depends on CSI enums, testify, filesystem helpers, and `Driver.Run`. It supplies helpers consumed by identity, fake mounter, and node tests.

Risks: `TestRun` depends on local TCP listener availability and the test-mode goroutine timing. The corrupted-dir test has limited coverage and does not force a real corrupted mount error.

Test signals: good smoke coverage for driver initialization helpers and server startup, but not a full integration test of real NFS operations.
