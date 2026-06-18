# sources/distributed-fs/ipfs-kubo/test/cli/testutils/requires.go

Purpose: skip-gate helpers for optional or environment-dependent CLI test categories.

Important APIs: `RequiresDocker`, `RequiresFUSE`, `RequiresExpensive`, `RequiresPlugins`, and `RequiresLinux` call `t.SkipNow` or `t.Skip` when prerequisites are absent. `isFUSEAvailable` checks platform and required unmount tool.

Control flow: Docker tests run only when `TEST_DOCKER=1`. FUSE tests skip when `TEST_FUSE=0`, always run when `TEST_FUSE=1`, otherwise auto-detect supported OS and `fusermount` on Linux or `umount` elsewhere. Expensive tests skip when `TEST_EXPENSIVE=1` or `testing.Short()` is true. Plugin tests require `TEST_PLUGIN=1`. Linux tests require `runtime.GOOS == "linux"`.

State and persistence: no persistent state; behavior is controlled by environment variables and host platform/tooling.

Dependencies and integration points: used by tests such as tracing and FUSE suites to avoid running unsupported integration tests. It imports `os`, `os/exec`, `runtime`, and `testing`.

Risks and test signals: `RequiresExpensive` appears counterintuitive because it skips when `TEST_EXPENSIVE=1`, which may be intentional inversion or a bug depending on suite conventions. Host tool detection is shallow; presence of `fusermount` does not guarantee FUSE permissions.
