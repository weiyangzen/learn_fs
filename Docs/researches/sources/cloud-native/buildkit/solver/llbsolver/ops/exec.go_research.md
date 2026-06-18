# sources/cloud-native/buildkit/solver/llbsolver/ops/exec.go

Purpose: implements LLB exec/RUN operations: cache-key computation, mount preparation, executor invocation, secret env loading, proxy capture, qemu emulation injection, resource samples, and provenance hooks.

Important APIs/types/functions: `ExecOp`, `NewExecOp`, `CacheMap`, `Exec`, `getMountDeps`, `dedupePaths`, `toSelectors`, `loadSecretEnv`, `Samples`, `ProxyCapture`, and `ProxyNetwork`. Cache identity is `buildkit.exec.v0` plus normalized exec metadata and platform. It deliberately removes extra-host IPs, proxy env, mount selectors, and most cache mount IDs/sharing from the cache key.

Control flow: `CacheMap` clones the proto, normalizes cache-affecting fields, includes platform fields, handles a backwards-compatible single-root-mount case, then creates dependency metadata. `getMountDeps` decides when content-based hashing is safe: readonly, no-output, or root selector mounts are safe; unsafe force-on is rejected. `Exec` converts inputs to worker refs, calls `container.PrepareMounts`, injects emulators when the target platform is unsupported natively, builds `executor.Meta`, appends proxy and secret env, runs the executor, logs proxy requests, commits output refs, and wraps process failures with `ExecError` context.

State/persistence: mutable output refs are committed into immutable cache refs. Active refs are released in LIFO order on success; on error they may be committed into error context or released. Resource recorder and proxy capture are retained for provenance.

Dependencies/integration: integrates mount manager, executor, cache manager, sessions/secrets, network proxy capture, worker CDI manager, qemu binfmt helper, logs, OpenTelemetry, and provenance provider walking.

Risks: ownership of refs during errors is delicate; clones are required so error contexts and caller-owned results do not double-release. Cache key normalization trades compatibility against correctness and must match Dockerfile cache mount semantics. Proxy requests may include sensitive URLs only as already captured/logged by proxy layer. Content-cache safety rules protect against selected-subtree cache unsoundness.

Test signals: `exec_test.go` covers path dedupe, proxy request logging, cache-map compatibility for mounts/cache IDs, and content-cache safety/default/force behavior. Full executor and mount commit behavior is integration-tested elsewhere.
