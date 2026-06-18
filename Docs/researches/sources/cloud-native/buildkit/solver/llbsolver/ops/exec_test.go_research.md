# sources/cloud-native/buildkit/solver/llbsolver/ops/exec_test.go

Purpose: unit-tests cache-map and helper behavior for `ExecOp` without running containers.

Important APIs/types/functions: `TestDedupePaths`, `TestLogProxyRequests`, `TestLogProxyRequestsEmpty`, `TestExecOpCacheMap`, `TestExecOpContentCache`, and helper builders `newExecOp`, `withNewMount`, `withCache`, `withSelector`, `withReadonly`, `withoutOutput`, `testJobContext`.

Control flow: cache-map tests instantiate synthetic `ExecOp` values and compare resulting cache digests for mount variations. They verify empty mounts normalization, mount destination cache-key impact, cache mount type impact, cache ID clearing for non-default cache mounts, and the special Dockerfile default cache mount compatibility behavior. Content-cache tests check default/off/on behavior for unsafe submounts, readonly mounts, no-output mounts, and root selectors.

State/persistence: no cache refs or executor state; inputs are proto fields and returned cache metadata. `jobCtx` provides only a session group and stubbed methods.

Dependencies/integration: depends on `identity` for randomized selectors, `pb` mount enums, network proxy request type, and solver job interfaces.

Risks: because these are unit tests, they cannot detect regressions in actual mount preparation or executor output ownership. Randomized selectors intentionally assert selector removal from cache key.

Test signals: good coverage for cache-key compatibility and content-cache safety, both high-risk areas for incorrect cache hits. Proxy logging format is also pinned.
