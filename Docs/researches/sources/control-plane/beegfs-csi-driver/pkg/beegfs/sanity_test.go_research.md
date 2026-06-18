# sources/control-plane/beegfs-csi-driver/pkg/beegfs/sanity_test.go

Purpose: Runs the Kubernetes CSI sanity test suite against an in-process BeeGFS driver configured with fake/sanity dependencies and an OS-backed temporary filesystem.

Important APIs/types/functions: `TestSanity` sets package filesystem globals to `afero.NewOsFs`, creates a temporary sanity directory, writes a minimal BeeGFS client config template, starts `NewBeegfsDriverSanity`, configures `sanity.NewTestConfig`, and invokes `sanity.Test`.

Control flow: The test creates controller data, staging, target, endpoint socket, and template paths under a temp directory. It starts the driver asynchronously on a Unix socket, supplies test volume parameters (`sysMgmtdHost=localhost`, `volDirBasePath=unittest`), runs the suite, and removes the temp directory.

State and persistence: Uses real temporary directories and a Unix-domain socket under the system temp directory. Cleanup removes the test root after sanity execution.

Dependencies and integration points: Depends on `github.com/kubernetes-csi/csi-test/v4/pkg/sanity`, Ginkgo reporter config, `afero`, the sanity driver constructor, and fake BeeGFS ctl behavior. It validates cross-service CSI behavior better than unit tests but still avoids real BeeGFS infrastructure.

Risks: Runs the driver in a goroutine without explicit stop coordination in the test body. It uses OS filesystem behavior, so environmental differences can surface. Sanity tests validate generic CSI contract but not BeeGFS-specific kernel module, mount namespace, or real `beegfs-ctl` behavior.

Test signals: Provides broad contract coverage across identity, controller, and node services with standard CSI sanity expectations. It is the main integration signal for unimplemented methods, idempotency, and required request validation.
