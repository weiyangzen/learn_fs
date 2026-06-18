# Research: subset-b-000024

Grouped research for BuildKit llbsolver files. Each section preserves the source path and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/mounts/mount.go -->
# sources/cloud-native/buildkit/solver/llbsolver/mounts/mount.go

Purpose: implements `MountManager`, the llbsolver bridge from protobuf mount declarations to BuildKit cache, tmpfs, SSH, and secret mountables. It is central to `ExecOp` mount preparation and to `RUN --mount=type=cache|secret|ssh|tmpfs` behavior.

Important APIs/types/functions: `NewMountManager`, `MountableCache`, `MountableTmpFS`, `MountableSecret`, `MountableSSH`, `SearchCacheDir`, `CacheRefMetadata`, `cacheRefGetter`, `cacheRefs`, and `cacheRefShare`. `getRefCacheDir` decides cache sharing semantics. `secretMountInstance.Mount` materializes secret bytes into a temporary tmpfs-backed file with requested uid/gid/mode. `sshMountInstance.Mount` forwards a session SSH socket. `tmpfsMount.Mount` emits a tmpfs mount with readonly and size options.

Control flow: cache mounts build a key from cache ID plus optional parent ref ID, check per-manager active shares, then branch on `SHARED`, `PRIVATE`, or `LOCKED`. Shared mounts coordinate through global `sharedCacheRefs`; locked mounts poll while reusable refs are locked. New refs are created through `cache.Manager.New` and tagged with the `cache-dir` metadata index. Release of cloned cache refs decrements share membership and releases the underlying mutable ref only when the last clone is released.

State/persistence: cache mount state is both in-memory (`MountManager.cacheMounts`, global `sharedCacheRefs`) and persistent metadata (`cache-dir:<id>` index). Secret and SSH mount state is transient and cleaned by release callbacks. Global hijack vars are test hooks and are concurrency-sensitive.

Dependencies/integration: depends on cache manager identity mapping, session manager, secrets and sshforward session services, containerd mount primitives, metadata search, `locker`, and user namespace detection. `ExecOp` reaches this through `container.PrepareMounts`.

Risks: release ordering and lock hierarchy are high risk for deadlocks or leaked mutable refs. Secret mounts must preserve noexec/nodev/nosuid behavior and userns fallback. `SearchCacheDir` prefix matching must avoid partial-id false positives. Global shared cache refs make tests and long-lived workers sensitive to stale state.

Test signals: `mount_test.go` covers private/shared/locked cache ref reuse, blocking behavior, release reuse, and a historical shared-ref deadlock.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/mounts/mount.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/mounts/mount_test.go -->
# sources/cloud-native/buildkit/solver/llbsolver/mounts/mount_test.go

Purpose: validates cache mount reference lifecycle and concurrency behavior for `mount.go`. It builds a real containerd-backed `cache.Manager` with native snapshots, metadata DB, content store, leases, differ, applier, and mount pool.

Important APIs/types/functions: `cmOpt`, `cmOut`, `newCacheManager`, `newRefGetter`, `TestCacheMountPrivateRefs`, `TestCacheMountSharedRefs`, `TestCacheMountLockedRefs`, and `TestCacheMountSharedRefsDeadlock`. The helper constructs a full cache stack under `t.TempDir`, closes BoltDB/metadata/cache manager via cleanup, and returns a manager suitable for `cacheRefGetter`.

Control flow: tests create multiple independent `cacheRefGetter` instances and compare mutable ref IDs across cache sharing modes. Private mode shares only within one getter, shared mode shares across getters via `sharedCacheRefs`, and locked mode blocks a second getter until the first refs release. The deadlock test injects sleeps into clone/release hooks while concurrently releasing one ref and acquiring another.

State/persistence: temporary snapshot/content/metadata stores are persistent only for the test duration. Test references are real cache refs whose ID reuse after release verifies metadata index behavior and mutable ref unlock behavior.

Dependencies/integration: exercises native containerd snapshotter, BuildKit cache manager, metadata store, leases, Windows-aware differ/applier wrappers, and the package-global shared cache ref table.

Risks: tests mutate global hook vars and `sharedCacheRefs`; they use `defer` to restore hooks but parallel tests still rely on no overlapping hook mutation except the non-parallel deadlock test. Timing assertions use 500 ms and 2 s windows, so heavily loaded CI can affect lock tests.

Test signals: strong regression coverage for moby/buildkit#1322 deadlock, cache sharing contracts, locked cache blocking, and release-driven reuse. It does not cover secret/SSH/tmpfs mount materialization.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/mounts/mount_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/network.go -->
# sources/cloud-native/buildkit/solver/llbsolver/network.go

Purpose: carries the llbsolver proxy-network switch and proxy policy plumbing between jobs, bridges, source policy evaluation, and worker op resolution.

Important APIs/types/functions: `keyProxyNetwork`, `proxyNetworkForOp`, `provenanceBridge.ProxyPolicy`, `provenanceBridge.ProxyNetwork`, `llbBridge.ProxyNetwork`, `loadProxyNetwork`, and `llbBridge.ProxyPolicy`. `proxyNetworkForOp` is the key guard: only exec ops are affected, `UNSET` and `HOST` inherit the proxy setting, `NONE` disables it, and other modes error when proxy networking is enabled.

Control flow: `Solver.Solve` stores a job value under `keyProxyNetwork`. `llbBridge.ProxyNetwork` ORs bridge config with values on the solver builder. `vertex.loadWithProxyNetwork` uses `proxyNetworkForOp` to mark individual ops before digest recomputation. Worker resolution receives `worker.ProxyOpt` with both network boolean and policy callback.

State/persistence: no persistence; job/solver builder values are transient during solve. Proxy policy is loaded from source policy job values and optional policy session.

Dependencies/integration: ties to `sourcepolicy.Engine`, source policy sessions, `util/network.ProxyPolicy`, `llbBridge.policy`, and `provenanceBridge` for recording proxy metadata.

Risks: proxy-network state participates in vertex digest recomputation, so missed propagation can create incorrect cache hits. Allowing host/unset to inherit proxy while rejecting other modes preserves explicit no-network behavior but requires callers to understand mode interactions.

Test signals: `network_test.go` only asserts interface conformance for `policyEvaluator`; functional coverage is mostly indirect through vertex/provenance/network integration tests elsewhere.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/network.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/network_test.go -->
# sources/cloud-native/buildkit/solver/llbsolver/network_test.go

Purpose: compile-time assertion that `policyEvaluator` implements `network.ProxyPolicy`.

Important APIs/types/functions: the single declaration `var _ network.ProxyPolicy = (*policyEvaluator)(nil)` protects the interface contract between llbsolver source policy evaluation and the network proxy layer.

Control flow: none at runtime; the Go compiler fails if `policyEvaluator` stops satisfying the interface.

State/persistence: none.

Dependencies/integration: imports `github.com/moby/buildkit/util/network` and binds `policyEvaluator` from `policy.go` to the proxy policy interface used by workers.

Risks: this is intentionally minimal. It cannot catch semantic regressions in policy decisions, proxy-network mode validation, or session policy request behavior.

Test signals: only interface conformance. Behavioral tests for proxy policy should be in policy/network integration coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/network_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/ops/build.go -->
# sources/cloud-native/buildkit/solver/llbsolver/ops/build.go

Purpose: implements nested LLB build operations. A `BuildOp` reads an LLB definition file from an input rootfs and delegates solving to the frontend LLB bridge.

Important APIs/types/functions: `BuildOp`, `NewBuildOp`, `CacheMap`, `Exec`, `Acquire`, and `IsProvenanceProvider`. Cache identity is `buildkit.build.v0` plus the serialized `pb.BuildOp`; dependency slots mirror vertex inputs. `Exec` currently accepts only `pb.LLBBuilder`.

Control flow: `Exec` finds the special LLB definition input, validates its input index and worker ref type, mounts the immutable ref readonly, opens the default or overridden LLB definition filename, reads it with `llb.ReadFrom`, unmounts, and calls `FrontendLLBBridge.Solve`. It releases all non-primary refs from the nested result and returns the primary ref result.

State/persistence: no durable state beyond cache refs produced by the delegated solve. Local mount lifecycle is carefully managed: unmount on failure via deferred cleanup, explicit unmount before nested solve on success.

Dependencies/integration: relies on `containerd/continuity/fs.RootPath`, `client/llb`, `frontend.FrontendLLBBridge`, worker refs, snapshot local mounter, and `opsutils.Validate`.

Risks: nested builds are marked as provenance providers but `captureProvenance` currently treats `BuildOp` as incomplete materials. Definition file path handling must stay rooted to prevent escape. Only one primary output is propagated; extra refs are released.

Test signals: no direct tests in this subset. Behavior is covered indirectly through frontend/build solve integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/ops/build.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/ops/diff.go -->
# sources/cloud-native/buildkit/solver/llbsolver/ops/diff.go

Purpose: implements the LLB diff op that returns a filesystem ref representing differences between lower and upper inputs.

Important APIs/types/functions: `diffOp`, `NewDiffOp`, `CacheMap`, `Exec`, and `Acquire`. The cache key is `buildkit.diff.v0` plus serialized `pb.DiffOp`; dependency count is based only on non-empty lower/upper refs.

Control flow: `Exec` maps compact input slice positions to logical lower and upper inputs, validates worker ref types, handles cheap identity cases, then calls `worker.CacheManager().Diff`. If both sides are empty it returns an empty worker ref, if lower is empty it clones upper, and if lower and upper have the same cache ref ID it returns empty.

State/persistence: creates a new diff immutable ref through the cache manager when needed. It does not maintain internal state and does not consume parallelism in `Acquire`.

Dependencies/integration: depends on worker cache manager diff implementation, `solver.ProgressControllerFromContext`, BuildKit cache refs, and `opsutils.Validate`.

Risks: input ordering is subtle because empty logical inputs are omitted from the runtime input slice. Nil or wrong `Sys()` values are hard errors. Same-ID optimization assumes cache ref identity is sufficient to represent no diff.

Test signals: no direct tests in this subset; expected coverage is integration around diff LLB operations and cache manager behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/ops/diff.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/ops/exec.go -->
# sources/cloud-native/buildkit/solver/llbsolver/ops/exec.go

Purpose: implements LLB exec/RUN operations: cache-key computation, mount preparation, executor invocation, secret env loading, proxy capture, qemu emulation injection, resource samples, and provenance hooks.

Important APIs/types/functions: `ExecOp`, `NewExecOp`, `CacheMap`, `Exec`, `getMountDeps`, `dedupePaths`, `toSelectors`, `loadSecretEnv`, `Samples`, `ProxyCapture`, and `ProxyNetwork`. Cache identity is `buildkit.exec.v0` plus normalized exec metadata and platform. It deliberately removes extra-host IPs, proxy env, mount selectors, and most cache mount IDs/sharing from the cache key.

Control flow: `CacheMap` clones the proto, normalizes cache-affecting fields, includes platform fields, handles a backwards-compatible single-root-mount case, then creates dependency metadata. `getMountDeps` decides when content-based hashing is safe: readonly, no-output, or root selector mounts are safe; unsafe force-on is rejected. `Exec` converts inputs to worker refs, calls `container.PrepareMounts`, injects emulators when the target platform is unsupported natively, builds `executor.Meta`, appends proxy and secret env, runs the executor, logs proxy requests, commits output refs, and wraps process failures with `ExecError` context.

State/persistence: mutable output refs are committed into immutable cache refs. Active refs are released in LIFO order on success; on error they may be committed into error context or released. Resource recorder and proxy capture are retained for provenance.

Dependencies/integration: integrates mount manager, executor, cache manager, sessions/secrets, network proxy capture, worker CDI manager, qemu binfmt helper, logs, OpenTelemetry, and provenance provider walking.

Risks: ownership of refs during errors is delicate; clones are required so error contexts and caller-owned results do not double-release. Cache key normalization trades compatibility against correctness and must match Dockerfile cache mount semantics. Proxy requests may include sensitive URLs only as already captured/logged by proxy layer. Content-cache safety rules protect against selected-subtree cache unsoundness.

Test signals: `exec_test.go` covers path dedupe, proxy request logging, cache-map compatibility for mounts/cache IDs, and content-cache safety/default/force behavior. Full executor and mount commit behavior is integration-tested elsewhere.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/ops/exec.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/ops/exec_binfmt.go -->
# sources/cloud-native/buildkit/solver/llbsolver/ops/exec_binfmt.go

Purpose: provides qemu-user emulator discovery and bind mounting for cross-platform exec operations when the requested platform is not natively supported.

Important APIs/types/functions: `qemuMountName`, `qemuArchMap`, `emulator`, `staticEmulatorMount`, `getEmulator`, and `ignoreSELinuxXAttrErrorHandler`. `getEmulator` compares the normalized requested platform against `archutil.SupportedPlatforms(false)` and locates `buildkit-qemu-<arch>`.

Control flow: if the requested platform matches a supported platform, no emulator is returned. For unsupported amd64 variants beyond v2, a clear unsupported-platform error is produced. Otherwise architecture is mapped to qemu binary naming, `exec.LookPath` searches the binary, and missing binaries are warned but not fatal. The mount copies the emulator into a temp directory at `/dev/.buildkit_qemu_emulator`, applies 0555 mode and optional idmap root ownership, and bind-mounts it readonly.

State/persistence: emulator temp directories are transient and removed by mount release callback. No persistent state.

Dependencies/integration: called by `ExecOp.Exec`; depends on containerd mounts, snapshot mountable interface, `fsutil/copy`, arch/platform utilities, BuildKit logging, and sys/user identity mapping.

Risks: missing qemu binaries silently disable emulation after a warning, so failures may happen later in executor. SELinux xattr handling must ignore only unsupported `security.selinux` xattrs and preserve other xattr errors. Platform normalization must stay aligned with containerd platform matching.

Test signals: `exec_binfmt_test.go` pins the SELinux xattr error handler behavior, including wrapped `ENOTSUP`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/ops/exec_binfmt.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/ops/exec_binfmt_test.go -->
# sources/cloud-native/buildkit/solver/llbsolver/ops/exec_binfmt_test.go

Purpose: validates the narrow SELinux xattr compatibility helper used during qemu emulator copy.

Important APIs/types/functions: `TestBinfmtXAttrErrorHandler` table-tests `ignoreSELinuxXAttrErrorHandler`.

Control flow: each subtest calls the handler with destination/source/xattr key/error and asserts whether the error is returned. Cases cover `security.selinux` with `ENOTSUP`, unrelated xattrs, `security.capability`, non-`ENOTSUP`, wrapped `ENOTSUP`, and nil error.

State/persistence: none.

Dependencies/integration: uses `syscall`, `pkg/errors` wrapping, and testify `require`. It protects the `fsutil/copy.WithXAttrErrorHandler` callback contract in `exec_binfmt.go`.

Risks: does not cover actual emulator discovery, copy, idmap ownership, or bind mount cleanup. It intentionally focuses on a regression-prone SELinux edge case.

Test signals: strong for the exact xattr filtering rule: only `errors.Is(err, syscall.ENOTSUP)` for key `security.selinux` is suppressed.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/ops/exec_binfmt_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/ops/exec_test.go -->
# sources/cloud-native/buildkit/solver/llbsolver/ops/exec_test.go

Purpose: unit-tests cache-map and helper behavior for `ExecOp` without running containers.

Important APIs/types/functions: `TestDedupePaths`, `TestLogProxyRequests`, `TestLogProxyRequestsEmpty`, `TestExecOpCacheMap`, `TestExecOpContentCache`, and helper builders `newExecOp`, `withNewMount`, `withCache`, `withSelector`, `withReadonly`, `withoutOutput`, `testJobContext`.

Control flow: cache-map tests instantiate synthetic `ExecOp` values and compare resulting cache digests for mount variations. They verify empty mounts normalization, mount destination cache-key impact, cache mount type impact, cache ID clearing for non-default cache mounts, and the special Dockerfile default cache mount compatibility behavior. Content-cache tests check default/off/on behavior for unsafe submounts, readonly mounts, no-output mounts, and root selectors.

State/persistence: no cache refs or executor state; inputs are proto fields and returned cache metadata. `jobCtx` provides only a session group and stubbed methods.

Dependencies/integration: depends on `identity` for randomized selectors, `pb` mount enums, network proxy request type, and solver job interfaces.

Risks: because these are unit tests, they cannot detect regressions in actual mount preparation or executor output ownership. Randomized selectors intentionally assert selector removal from cache key.

Test signals: good coverage for cache-key compatibility and content-cache safety, both high-risk areas for incorrect cache hits. Proxy logging format is also pinned.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/ops/exec_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/ops/file.go -->
# sources/cloud-native/buildkit/solver/llbsolver/ops/file.go

Purpose: implements LLB file operations (`mkdir`, `mkfile`, `symlink`, `rm`, `copy`) as a graph of actions over BuildKit refs, including cache-key dependency selection and a reusable `FileOpSolver`.

Important APIs/types/functions: `fileOp`, `NewFileOp`, `CacheMap`, `Exec`, `FileOpSolver`, `Solve`, `validate`, `getInput`, `addSelector`, `dedupeSelectors`, `processOwner`, `isDefaultIndexes`, and `unlazyResultFunc`.

Control flow: `CacheMap` serializes each action, records action input/secondary/output indexes unless they match the historical default pattern, and computes selectors for copy sources and named user/group lookups. Selectors for inputs invalidated by mutation are skipped. `Exec` converts worker refs, builds a file backend, and delegates to `FileOpSolver`. `Solve` validates indexes, output continuity, duplicate outputs, and action dependency loops, then resolves each output in parallel. `getInput` uses flightcontrol to memoize action results, prepares primary and secondary mounts, loads user/group mounts, runs the backend action, and either commits to a ref or keeps a mount alive for downstream actions.

State/persistence: action outputs become immutable refs through `RefManager.Commit`. Intermediate mounts are released on error or after final resolution. The solver tracks `outs` and `ins` maps per instance, so instances are not reusable across independent solves.

Dependencies/integration: integrates `llbsolver/file` backend/ref manager, `fileoptypes`, worker refs, session groups, cache content hashing, errdefs wrapping, and platform-specific user readers.

Risks: file-action indexes are easy to misuse; loops and invalid indexes can otherwise recurse forever. Error wrapping commits partial mutable mounts for diagnostics, which has ownership and release risks. Cache selectors must include `/etc/passwd` and `/etc/group` for named chown but avoid hashing mutated inputs.

Test signals: `file_test.go` covers action chaining, chown mounts, copy source/destination semantics, invalid outputs/indexes/loops, multi-output, scratch roots, and parallel independent branches.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/ops/file.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/ops/file_test.go -->
# sources/cloud-native/buildkit/solver/llbsolver/ops/file_test.go

Purpose: unit-tests `FileOpSolver` graph semantics with an in-memory fake backend/ref manager.

Important APIs/types/functions: tests include `TestMkdirMkfile`, `TestChownOpt`, `TestChownCopy`, `TestInvalidNoOutput`, `TestInvalidDuplicateOutput`, `TestActionInvalidIndex`, `TestActionLoop`, `TestMultiOutput`, `TestFileFromScratch`, `TestFileCopyInputSrc`, `TestFileCopyInputRm`, and `TestFileParallelActions`. Helpers include `newTestFileSolver`, `testFileRef`, `testMount`, `testFileBackend`, and `testFileRefBackend`.

Control flow: tests build `pb.FileOp` action arrays and check the fake mount chain IDs and stored action pointers after solve. Invalid tests assert expected errors. The parallel-actions test blocks two independent branches on a callback and proves they run concurrently before joining through copy.

State/persistence: fake refs carry refcounts and mount chains; fake backend mutates string IDs and action chains instead of filesystem state. `checkReleased` asserts non-output refs and mounts are released, making lifecycle part of test validation.

Dependencies/integration: exercises `fileoptypes` interfaces directly and avoids cache manager/filesystem dependencies. It uses `atomic`, channels, and testify.

Risks: fake backend cannot detect real filesystem copy/chown behavior. It is valuable for DAG/ref lifecycle semantics but not for path security or platform-specific user resolution.

Test signals: strong coverage for solver dependency ordering, output indexing, scratch handling, release discipline, owner mount loading, and parallelism.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/ops/file_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/ops/fileoptypes/types.go -->
# sources/cloud-native/buildkit/solver/llbsolver/ops/fileoptypes/types.go

Purpose: defines narrow interfaces that decouple `FileOpSolver` from concrete BuildKit cache refs, mounts, and filesystem backends.

Important APIs/types/functions: `Ref`, `Mount`, `Backend`, and `RefManager`. `Backend` exposes file action primitives with explicit destination, source, user, and group mounts. `RefManager` prepares refs as readonly or writable mounts and commits mounts back to refs.

Control flow: no implementation; interfaces define the call contract consumed by `ops/file.go` and implemented by real `llbsolver/file` package and fake tests.

State/persistence: interface-level only. Persistence semantics are delegated to implementations: `Commit` turns mutable mount state into a ref; `Release` decrements/releases refs or mounts.

Dependencies/integration: imports `context`, `session.Group`, and `pb` file action types. This file is the abstraction boundary between generic file-action graph logic and backend filesystem mutation.

Risks: the interfaces do not encode ownership transfer precisely, so callers and implementers must follow conventions around releasing mounts after commit/error. The minimal `Ref` interface only has `Release`, so type assertions are needed elsewhere when worker/cache-specific behavior is required.

Test signals: tested indirectly by `file_test.go` fake implementations and real backend tests outside this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/ops/fileoptypes/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/ops/merge.go -->
# sources/cloud-native/buildkit/solver/llbsolver/ops/merge.go

Purpose: implements the LLB merge op, combining multiple immutable refs into one cache ref through the worker cache manager.

Important APIs/types/functions: `mergeOp`, `NewMergeOp`, `CacheMap`, `Exec`, and `Acquire`. Cache identity is `buildkit.merge.v0` plus serialized `pb.MergeOp`; dependencies match `op.Inputs`.

Control flow: `Exec` iterates runtime inputs, skips nil inputs and nil immutable refs, validates worker ref types, compacts valid refs, returns nil output when none remain, then calls `CacheManager().Merge` with progress and vertex description. The result is wrapped as a worker ref result.

State/persistence: merge creates a new immutable cache ref managed by the worker cache manager. The op itself has no mutable state and no parallelism acquisition.

Dependencies/integration: worker cache manager, BuildKit cache refs, solver progress controller, `opsutils.Validate`, and cachedigest JSON hashing.

Risks: nil output for zero refs must be expected by callers. Wrong input `Sys()` types are fatal. Merge ordering follows input order, so cache and filesystem semantics may depend on upstream ordering.

Test signals: no direct tests in this subset; integration coverage should verify merge layering semantics and cache export behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/ops/merge.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/ops/opsutils/contenthash.go -->
# sources/cloud-native/buildkit/solver/llbsolver/ops/opsutils/contenthash.go

Purpose: provides content-based cache digest calculation for selected paths of worker refs.

Important APIs/types/functions: `Selector`, `Selector.HasWildcardOrFilters`, and `NewContentHashFunc`. Selectors carry path, wildcard, symlink-following, include/exclude filters, and required paths.

Control flow: `NewContentHashFunc` returns a `solver.ResultBasedCacheFunc`. When invoked, it asserts the result is a `*worker.WorkerRef`, defaults an empty selector list to the root selector, and computes `contenthash.Checksum` for each selector concurrently through `errgroup`. Individual selector digests are joined with NUL bytes and hashed as a digest list.

State/persistence: no state is persisted here; contenthash may consult cache metadata and snapshot contents through the immutable ref. The returned closure captures the selector slice.

Dependencies/integration: used by exec and file ops for dependency cache keys. Depends on `cache/contenthash`, solver result interfaces, session group, worker refs, and `cachedigest`.

Risks: selector mutation after closure creation would affect future calls because the slice is captured. Errors include ref ID for diagnostics. Concurrent checksum calculation must be safe for the underlying ref/contenthash implementation.

Test signals: covered indirectly by exec/file cache-map tests and broader contenthash tests outside this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/ops/opsutils/contenthash.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/ops/opsutils/validate.go -->
# sources/cloud-native/buildkit/solver/llbsolver/ops/opsutils/validate.go

Purpose: central lightweight protobuf operation validation before constructing solver ops or loading vertices.

Important APIs/types/functions: `Validate(op *pb.Op) error`. It checks nil ops, required inner op structs, exec meta/args/mounts/rootfs, file actions, build/merge/diff presence, and passthrough ID/output indexes.

Control flow: computes `inputCount := len(op.Inputs)`, switches on the concrete `op.Op` oneof, and returns descriptive errors for invalid cases. Exec validation additionally requires at least one mount and a root mount. Passthrough validation ensures outputs exist and point to valid inputs when inputs are known.

State/persistence: none.

Dependencies/integration: called from op constructors and `vertex.loadLLB` before vertex materialization. It protects downstream code from nil pointer panics and missing rootfs assumptions.

Risks: validation is intentionally incomplete; many index checks remain in op-specific execution paths. Passthrough input validation is conditional when `inputCount` is zero, so callers must still handle runtime invalid indexes.

Test signals: direct tests are not in this subset. Invalid file-action graph cases are tested in `file_test.go`; exec constructor validity is mostly exercised indirectly.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/ops/opsutils/validate.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/ops/passthrough.go -->
# sources/cloud-native/buildkit/solver/llbsolver/ops/passthrough.go

Purpose: implements a passthrough op that selects and clones specified input results as outputs.

Important APIs/types/functions: `passthroughOp`, `NewPassthroughOp`, `CacheMap`, `Exec`, and `Acquire`. Cache identity is `buildkit.passthrough.v0` plus serialized `pb.PassthroughOp`; dependency count is the source vertex input count.

Control flow: constructor validates the op and records input count. `CacheMap` creates a dependency slot for each input. `Exec` allocates outputs equal to `op.Outputs`, validates each referenced input index against runtime inputs, clones non-nil inputs, and leaves nil input outputs nil.

State/persistence: no state beyond cloned result references. Cloning transfers independent ownership to callers.

Dependencies/integration: uses solver result clone semantics, cachedigest JSON hashing, `opsutils.Validate`, and protobuf passthrough op fields. Vertex names are generated in `vertex.go`.

Risks: incorrect clone/release behavior would leak or double-release refs. Runtime validation protects against stale/invalid output mappings even if constructor validation was incomplete.

Test signals: no direct tests in this subset. Behavior is small but should be covered by solver integration around frontend passthrough usage.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/ops/passthrough.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/ops/source.go -->
# sources/cloud-native/buildkit/solver/llbsolver/ops/source.go

Purpose: implements source operations that resolve external/local sources into snapshot refs and cache keys.

Important APIs/types/functions: `SourceOp`, `NewSourceOp`, `IsProvenanceProvider`, `Pin`, `instance`, `CacheMap`, `Exec`, and `Acquire`. Cache identity uses `buildkit.source.v0:<source cache key>` hashed through `cachedigest`; session sources are forced to a `random:` digest.

Control flow: `instance` lazily resolves a `source.Identifier` through `source.Manager.Identifier` and `Resolve`, caching the `SourceInstance`, identifier, and pin. `CacheMap` asks the instance for `CacheKey`, records the first pin, and returns source cache options plus completion status. `Exec` snapshots the source and wraps it as a worker ref result. `Acquire` optionally uses a weighted semaphore.

State/persistence: stores resolved source instance and pin in the op instance. Source snapshot refs and cache records are managed by source/cache layers.

Dependencies/integration: source manager, session manager, worker refs, platform constraints, solver cache maps, and provenance capture via `Pin` and source identifier `Capture`.

Risks: lazy instance state is mutex-protected but source resolution errors are not cached. Session-based cache keys deliberately randomize to avoid unsafe reuse. Pin is set only if empty, so repeated cache-map calls retain the first pin.

Test signals: no direct tests in this subset; source behavior is typically integration-tested through local/git/http/image source tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/ops/source.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/ops/user_linux.go -->
# sources/cloud-native/buildkit/solver/llbsolver/ops/user_linux.go

Purpose: resolves file operation chown users/groups on Linux by reading passwd/group files from provided snapshot mountables.

Important APIs/types/functions: `getReadUserFn` and `readUser`. `readUser` accepts a `pb.ChownOpt` plus optional user and group mountables and returns `*copy.User`.

Control flow: numeric user sets UID and default GID to the same value; numeric group sets GID. Named user requires a user mount, mounts it locally, resolves `/etc/passwd` under the root with `fs.RootPath`, and parses entries matching the name. Named group similarly reads `/etc/group`. Missing files or `ENOTDIR` are treated as not found rather than fatal.

State/persistence: no persistent state. Local mounters are mounted and unmounted within the function.

Dependencies/integration: used by real file backend construction in `file.go`; depends on snapshot local mounter, continuity `RootPath`, `moby/sys/user` parsers, and fsutil copy `User`.

Risks: missing mount for named lookups is fatal. Path rooting is necessary for safety. UID/GID default behavior for numeric user mirrors container copy expectations and should not be changed casually.

Test signals: file solver tests cover named chown mount selection with fakes, but this Linux parser itself is not directly tested in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/ops/user_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/ops/user_other.go -->
# sources/cloud-native/buildkit/solver/llbsolver/ops/user_other.go

Purpose: non-Linux, non-Windows fallback for file operation user resolution.

Important APIs/types/functions: build tag `!linux && !windows`, `getReadUserFn`, and `readUser`.

Control flow: `getReadUserFn` returns `readUser`. `readUser` returns nil for nil chown options and otherwise errors with "only implemented in linux and windows".

State/persistence: none.

Dependencies/integration: keeps the package buildable on other platforms while making chown-by-user behavior explicitly unsupported.

Risks: any file op requiring chown resolution on unsupported platforms fails at runtime. Numeric-only chown is not implemented here even though it might be possible, so platform behavior differs from Linux/Windows.

Test signals: no direct tests in this subset; build tags are the main coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/ops/user_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/ops/user_windows.go -->
# sources/cloud-native/buildkit/solver/llbsolver/ops/user_windows.go

Purpose: Windows-specific file operation user resolution that maps a username to a Windows SID for fsutil copy ownership.

Important APIs/types/functions: `getReadUserFn` and `readUser`. The returned closure captures the worker so it can access the executor for SID resolution.

Control flow: nil chown returns nil. If a named user is present, the user mountable is mounted, `windows.ResolveUsernameToSID` resolves the name against root mounts using the worker executor, and a `copy.User{SID: sid}` is returned. Other user forms/defaults return the Container Administrator SID.

State/persistence: no persistence. Root mounts are released through the mount release callback.

Dependencies/integration: file backend ownership resolution, snapshot mountables, `util/windows`, worker executor, and fsutil copy user model.

Risks: group is ignored on Windows (`mg` is unused). Missing user mount for named lookup is fatal. Defaulting to Container Administrator is platform-specific and must align with Windows container filesystem expectations.

Test signals: no direct tests in this subset; Windows behavior is likely covered by platform-specific file backend tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/ops/user_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/policy.go -->
# sources/cloud-native/buildkit/solver/llbsolver/policy.go

Purpose: implements source policy evaluation for LLB source ops, including static policy engine decisions and optional interactive policy-session verification.

Important APIs/types/functions: `SourcePolicyEvaluator`, `policyEvaluator`, `Evaluate`, recursive `evaluate`, `mapsEqual`, platform converters, `fromPBHTTPChecksumAlgo`, `validateSourcePolicy`, `loadSourcePolicy`, and `loadSourcePolicySession`.

Control flow: `evaluate` ignores non-source ops, runs the source policy engine, then optionally contacts a `policysession.PolicyVerifier` session. The verifier can request source metadata resolution with strict identifier/attr matching and resolve options for image, OCI layout, git, or HTTP checksum metadata. It loops until a decision is returned, with a max-depth guard. `CONVERT` decisions mutate the source identifier/attrs and recursively re-evaluate; non-ALLOW decisions return wrapped deny errors.

State/persistence: policies and policy session ID are job builder values. Source ops may be mutated by conversion decisions before digest recomputation.

Dependencies/integration: sourcepolicy engine, gateway source metadata protobufs, sourceresolver options, policy sessions, session manager, and network proxy policy conformance.

Risks: policy-request loops are capped but still complex. Session metadata requests are rejected if they change source identity/attrs, which protects against confused-deputy behavior. Source mutation must be followed by digest recomputation or cache keys become stale.

Test signals: only interface conformance in `network_test.go` within this subset. Functional policy coverage should exist in broader source policy tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/policy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/proc/provenance.go -->
# sources/cloud-native/buildkit/solver/llbsolver/proc/provenance.go

Purpose: defines the post-solve processor that creates in-toto provenance attestations for each exported platform.

Important APIs/types/functions: `ProvenanceProcessor`. It returns an `llbsolver.Processor` closure parameterized by SLSA version, attestation attrs, and custom provenance environment.

Control flow: the processor parses platform metadata, reads `inline-only`, finds provenance capture and result refs for each platform ID, constructs a `ProvenanceCreator`, and adds an attestation with predicate type and lazy `ContentFunc`. The content function builds the predicate and marshals it as indented JSON when exporter code requests it.

State/persistence: mutates `llbsolver.Result` by adding attestations. Provenance JSON is generated lazily, so job completion time, layer metadata, and resource samples can be finalized at content generation.

Dependencies/integration: exporter platform metadata, gateway attestation kind, result attestation metadata keys, resources sampler, solver job, and `NewProvenanceCreator`.

Risks: missing capture or output ref for a platform is fatal. Lazy content generation means errors can surface during export/finalization rather than initial processor registration. Attribute parsing is permissive for `inline-only`: invalid bool leaves false.

Test signals: no direct tests in this subset; `provenance.go`, predicate, and store tests cover lower-level behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/proc/provenance.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/proc/sbom.go -->
# sources/cloud-native/buildkit/solver/llbsolver/proc/sbom.go

Purpose: defines the post-solve processor that generates SBOM attestations with a configured scanner image/reference.

Important APIs/types/functions: `SBOMProcessor(scannerRef, useCache, resolveMode, params)`. It returns an `llbsolver.Processor`.

Control flow: skips generation if the result already has an SBOM, starts a tracing span, parses platform metadata, creates an SBOM scanner through the solver bridge, then for each platform ref builds an LLB state from the ref definition. It optionally applies `llb.IgnoreCache`, invokes the scanner, converts scanner output to BuildKit attestations, and solves any attestation state refs through the solver bridge.

State/persistence: mutates the result by adding attestations. Any scanner-created refs are solved through the same job/bridge and become regular solver results.

Dependencies/integration: frontend SBOM helper, source resolver image resolve mode, LLB state/definition conversion, solver bridge, result attestation conversion, exporter platform metadata, and tracing.

Risks: scanner creation can return nil, producing no attestation. Missing platform refs are fatal. The conversion callback performs nested solves, so scanner definitions must be safe under the current session and cache policy.

Test signals: no direct tests in this subset; behavior depends on SBOM frontend integration tests elsewhere.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/proc/sbom.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/provenance.go -->
# sources/cloud-native/buildkit/solver/llbsolver/provenance.go

Purpose: connects solve requests, result proxies, source metadata, provider walking, and SLSA predicate creation into BuildKit's provenance attestation pipeline.

Important APIs/types/functions: `provenanceBridge`, `ResolveSourceMetadata`, `Solve`, `requests`, `findByResult`, `captureProvenance`, `ProvenanceCreator`, `NewProvenanceCreator`, `scrubMinRequest`, `incompleteMaterialsError`, `Predicate`, `addProvenanceToResult`, `getRefProvenance`, and `getProvenance`.

Control flow: `provenanceBridge.Solve` wraps definition solves with result proxies or delegates frontend solves through nested provenance bridges. It records build results and registers provenance refs. `captureProvenance` walks solver provenance providers: `SourceOp` captures source identifiers, `ExecOp` records secret/SSH use, network access, proxy material/incomplete requests, and resource samples; `BuildOp` marks materials incomplete. `addProvenanceToResult` computes captures for result refs and attestations, merges hidden refs, filters images by platform, optimizes and sorts sources. `NewProvenanceCreator` builds a SLSA v1 predicate, applies mode/min/max/reproducible/usage/complete-materials attrs, adds build config and layers in max mode, and can convert to SLSA v0.2 in `Predicate`.

State/persistence: bridge stores request context, nested builds, source images, subbridges, and provenance-store record IDs for the solve lifetime. `ResultProxy` stores captured provenance after result evaluation. Attestation content is generated later but mutates predicate finish time and optional sys usage.

Dependencies/integration: solver jobs/results, frontends, source metadata resolution, ops provenance providers, cache export, image layer descriptors, BuildKit result attestations, SLSA types, Dockerfile version, resources sampler, and errdefs.

Risks: provenance depends on correct result ownership and bridge lookup by result ID. Min mode intentionally scrubs secrets/SSH/build-args/labels and marks request incomplete. Complete-materials mode fails on local sources or proxy-incomplete requests. Layer capture depends on cache exporter metadata and must strip internal annotations.

Test signals: `provenance_test.go` covers local-source incomplete-material errors; predicate/store/type tests cover major helpers. Full bridge behavior is integration-heavy.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/provenance.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/provenance/buildconfig.go -->
# sources/cloud-native/buildkit/solver/llbsolver/provenance/buildconfig.go

Purpose: converts LLB definitions into SLSA BuildKit build configuration metadata and source location maps.

Important APIs/types/functions: `AddBuildConfig`, `digestMap`, `toBuildSteps`, and `walkDigests`.

Control flow: `AddBuildConfig` gets the result definition, converts it to ordered build steps, attaches `BuildConfig` to SLSA v1 internal parameters, and, if source metadata exists, converts source-info definitions and remaps locations from op digests to `stepN` keys. `toBuildSteps` unmarshals each LLB op, strips non-reproducible local source attrs (`local.session`, `local.unique`), identifies the synthetic last vertex, walks dependencies depth-first, maps digests to step indexes, clones ops with inputs removed, and writes input references as `stepN:index`. Optional resource usage is attached from capture samples.

State/persistence: mutates the predicate passed in; no external persistence. It reads immutable result definitions and capture samples.

Dependencies/integration: protobuf LLB definitions, provenance capture samples, SLSA typed build config, solver result proxy definitions, and digest mapping used later for layer metadata.

Risks: assumes last definition vertex is synthetic with exactly one input. Bad or missing input digests fail conversion. Stripping local attrs is important for stable/reproducible provenance.

Test signals: no direct tests in this subset; exercised indirectly through provenance creator max-mode paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/provenance/buildconfig.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/provenance/capture.go -->
# sources/cloud-native/buildkit/solver/llbsolver/provenance/capture.go

Purpose: defines the mutable capture object accumulated from solve providers before conversion into provenance predicates.

Important APIs/types/functions: `Capture`, alias `Result`, `Clone`, `Merge`, `Sort`, `OptimizeImageSources`, `AddImage`, `AddImageBlob`, `AddLocal`, `AddGit`, `AddHTTP`, `AddSecret`, `AddSSH`, `AddSamples`, and `parseRefName`.

Control flow: add methods deduplicate by stable identities while preserving meaningful distinctions: images dedupe by ref/local/platform, git sources dedupe by redacted URL plus bundle URL, secrets/SSH merge optional flags with non-optional winning, and empty SSH ID becomes `default`. `Merge` replays add methods and ORs network/incomplete flags. `OptimizeImageSources` drops digest-only image references when a tag ref for the same name:tag exists. `Sort` imposes deterministic ordering across all slices.

State/persistence: in-memory only, later embedded in `provenance.Result` and attestation predicates. `Samples` map tracks per-op resource samples by digest.

Dependencies/integration: provenance type structs, result wrapper, URL credential redaction, OCI/reference parsing, resource sample types, and digests.

Risks: dedupe keys directly affect material completeness; overly broad git/image dedupe can drop required materials. Clone copies sample map but not deep sample values. Sort assumes non-nil secret/SSH entries.

Test signals: `capture_test.go` covers image/platform dedupe, secret optional merge, SSH default ID, git redaction and bundle dedupe, merge flags, sorting, image source optimization, and sample map initialization.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/provenance/capture.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/provenance/capture_test.go -->
# sources/cloud-native/buildkit/solver/llbsolver/provenance/capture_test.go

Purpose: validates capture deduplication, redaction, merge, sorting, optimization, and sample recording behavior.

Important APIs/types/functions: tests cover `AddImage`, `AddSecret`, `AddSSH`, `AddGit`, `Merge`, `Sort`, `OptimizeImageSources`, and `AddSamples`, with a detailed `TestCaptureAddGitBundleDedup`.

Control flow: table-style and subtests construct `Capture` values, invoke add/merge operations, and assert slice lengths and key fields. Bundle tests ensure normal git and bundle-backed git sources with the same URL both survive, identical bundle URLs dedupe, and different bundle URLs are preserved.

State/persistence: no external state; tests inspect in-memory capture state.

Dependencies/integration: provenance types, OCI platform struct, digest helper, and testify.

Risks: tests do not cover nil entries in secret/SSH slices or deep-copy semantics. They intentionally pin dedupe behavior that affects SLSA materials downstream.

Test signals: strong for provenance material identity rules and credential redaction. These tests protect against silent material loss when git bundles are involved.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/provenance/capture_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/provenance/predicate.go -->
# sources/cloud-native/buildkit/solver/llbsolver/provenance/predicate.go

Purpose: converts captured BuildKit sources/request data into SLSA v1 provenance predicate fields and material descriptors.

Important APIs/types/functions: `slsaMaterials`, `parseBundleLocatorURL`, `digestSetForCommit`, `setPURLQualifier`, `findMaterial`, `NewPredicate`, `RequestProvenance`, and `FilterArgs`.

Control flow: `slsaMaterials` emits purl-backed materials for image refs and image blobs, raw URL materials for git sources, additional purl bundle materials for bundle-backed git, and URL/digest materials for HTTP sources. `NewPredicate` builds resolved dependencies, external request/config source, internal builder platform, local source request entries, VCS metadata, completeness/hermetic flags, and proxy-network metadata. `RequestProvenance` derives config source from the context arg and captured materials, removes consumed context/filename args, and redacts credentials. `FilterArgs` drops host-specific and attestation args while redacting context URLs.

State/persistence: returns new typed predicate/request structures. It clones maps where needed and mutates request arg copies.

Dependencies/integration: in-toto SLSA common/v1 structs, BuildKit provenance types, Dockerfile git URL fragment utility, purl utilities, package-url parser, source type schemes, and URL redaction.

Risks: bundle locator parsing is intentionally permissive because validation happens upstream; malformed locators are skipped. Commit digest algorithm is inferred by length only. Filtering decisions define what user inputs appear in attestations and are security/privacy sensitive.

Test signals: `predicate_test.go` covers image blob purls, OCI blob purls, git bundle materials, argument filtering/redaction, commit digest choice, material lookup with subdir fragments, request preservation, config source derivation, contextsubdir retention, and proxy-network metadata.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/provenance/predicate.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/provenance/predicate_test.go -->
# sources/cloud-native/buildkit/solver/llbsolver/provenance/predicate_test.go

Purpose: unit-tests SLSA material emission, request filtering, config-source mapping, and proxy metadata generation.

Important APIs/types/functions: tests exercise `slsaMaterials`, `FilterArgs`, `digestSetForCommit`, `findMaterial`, and `NewPredicate`.

Control flow: material tests parse emitted package URLs and inspect qualifiers for image blobs and git bundles. Filtering tests verify host-specific/attestation args are removed while ordinary Dockerfile args remain and context credentials are redacted. Predicate tests build captures with requests, secrets, SSH, inputs, git sources, context subdirs, and proxy incomplete entries, then assert SLSA external parameters and metadata.

State/persistence: no external state; constructs in-memory captures and material lists.

Dependencies/integration: package-url parser, provenance types, digest helper, and testify.

Risks: tests do not cover every source type combination or invalid purl errors. They pin privacy-sensitive filtering and bundle purl behavior, which are high-value regression areas.

Test signals: strong for SLSA predicate shape, git bundle material preservation, config source derivation, completeness/hermetic flags under proxy incomplete materials, and request preservation for min/max provenance paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/provenance/predicate_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/provenance/types/types.go -->
# sources/cloud-native/buildkit/solver/llbsolver/provenance/types/types.go

Purpose: defines BuildKit-specific provenance data structures and conversion between SLSA v1 and SLSA v0.2 predicate layouts.

Important APIs/types/functions: constants `BuildKitBuildType1`, `BuildKitBuildType02`, `ProvenanceSLSA1`, `ProvenanceSLSA02`; types `BuildConfig`, `BuildStep`, source structs, `Parameters`, `RequestProvenance`, `Environment`, `BuildKitMetadata`, network metadata, SLSA predicate wrappers; methods `Validate`, `Clone`, `Equal`, `ConvertToSLSA02`, `ConvertToSLSA1`, and custom JSON marshal/unmarshal for `ProvenanceInternalParametersSLSA1` and `Environment`.

Control flow: clone/equal methods deep-copy and compare nested request structures. Conversion methods map builder, materials/resolved dependencies, config source, request parameters, build config, metadata, completeness, hermeticity, and custom environment fields between SLSA versions. Custom JSON handlers flatten unknown custom env keys into top-level JSON while preserving known fields.

State/persistence: these structs are serialized into attestation JSON. `ProvenanceCustomEnv` allows user-configured metadata but `Solver.New` forbids overriding builtin keys.

Dependencies/integration: in-toto SLSA v0.2/v1 packages, resource samples, protobuf ops/locations, OCI platform descriptors, digest types, and JSON.

Risks: JSON flattening can collide with future known fields if not guarded. Conversion is lossy for unsupported SLSA fields. Equal/Clone correctness affects provenance store ambiguity handling.

Test signals: `types_test.go` verifies custom env JSON round trips for SLSA1 internal parameters and SLSA0.2 invocation environment.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/provenance/types/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/provenance/types/types_test.go -->
# sources/cloud-native/buildkit/solver/llbsolver/provenance/types/types_test.go

Purpose: verifies custom provenance environment fields are preserved as flattened JSON in both SLSA v1 internal parameters and SLSA v0.2 invocation environment.

Important APIs/types/functions: `TestMarsalBuildDefinitionSLSA1` and `TestMarshalInvocation` exercise `ProvenanceBuildDefinitionSLSA1`, `ProvenanceInternalParametersSLSA1`, `ProvenanceInvocationSLSA02`, and `Environment` JSON marshal/unmarshal.

Control flow: each test unmarshals JSON containing known fields and arbitrary custom keys, asserts known struct fields and `ProvenanceCustomEnv` contents, marshals back, and compares JSON equivalence.

State/persistence: no external state; JSON round-trip behavior is the persistence contract for attestations.

Dependencies/integration: Go `encoding/json` and testify.

Risks: the first test name contains a typo (`Marsal`) but does not affect behavior. Coverage is focused on JSON flattening, not SLSA conversion or Clone/Equal methods.

Test signals: strong for preserving arbitrary custom keys such as strings, numbers, objects, and arrays without nesting them under an internal field.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/provenance/types/types_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/provenance_store.go -->
# sources/cloud-native/buildkit/solver/llbsolver/provenance_store.go

Purpose: tracks request provenance for frontend input definitions so nested/input provenance can be associated with later result definitions.

Important APIs/types/functions: `provenanceStore`, `provenanceRecord`, `newProvenanceStore`, `register`, `unregister`, `lookup`, `provenanceBridge.registerProvenanceRefs`, `registerProvenanceRef`, `requestProvenance`, `inputProvenance`, `rootRequestProvenance`, `hasRequestProvenance`, and `definitionHeadDigest`.

Control flow: `register` computes a definition head digest from the synthetic last vertex input, stores a cloned request under a random record ID, and indexes it by digest. `lookup` gathers records for the same digest, strips nested root request from each clone, and returns a request only if all records are equal; ambiguity returns false. Bridges register refs after solve and unregister record IDs when released. Request provenance is derived from bridge frontend request args plus looked-up frontend inputs and optional root request.

State/persistence: in-memory store protected by mutex. Records live for solve/bridge lifetime and are explicitly unregistered by `releaseProvenanceRefs`.

Dependencies/integration: frontend results, solver result proxies, provenance capture/types, LLB definitions, identity IDs, and request filtering helpers.

Risks: head digest extraction depends on the definition shape used by `llb.NewDefinitionOp` round trips. Ambiguous records intentionally suppress input provenance. Failure to unregister can leak request records across solves.

Test signals: `provenance_store_test.go` covers digest lookup, input root omission, definition round-trip lookup, unregister, ambiguity, and min-request scrubbing in related code.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/provenance_store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/provenance_store_test.go -->
# sources/cloud-native/buildkit/solver/llbsolver/provenance_store_test.go

Purpose: validates provenance store lookup semantics and related min-mode request scrubbing.

Important APIs/types/functions: tests include `TestProvenanceStoreLooksUpByDefinitionDigest`, `TestProvenanceStoreOmitsInputRoot`, `TestProvenanceStoreLookupAfterDefinitionOpRoundTrip`, `TestProvenanceStoreUnregister`, `TestProvenanceStoreAmbiguousDigest`, and `TestScrubMinRequestScrubsNestedRequests`.

Control flow: tests generate simple LLB definitions with `llb.Scratch().File(...)`, register request provenance, and assert lookup behavior for same, different, round-tripped, unregistered, and ambiguous definitions. The scrub test builds nested `Parameters` with build args, labels, secrets, SSH, inputs, and root request, then asserts min-mode removal and retained structural args.

State/persistence: in-memory store only. Tests assert registration does not mutate the original protobuf definition.

Dependencies/integration: BuildKit LLB client, provenance types, and testify.

Risks: tests use simple file definitions, so complex multi-output definitions are not covered. They pin ambiguity behavior that can hide input provenance when multiple conflicting requests share a digest.

Test signals: strong for lifecycle and equality semantics of request provenance records, plus recursive min-mode scrubbing.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/provenance_store_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/provenance_test.go -->
# sources/cloud-native/buildkit/solver/llbsolver/provenance_test.go

Purpose: tests user-facing incomplete-materials error construction for provenance complete-materials mode.

Important APIs/types/functions: `TestIncompleteMaterialsErrorIncludesLocalSources` exercises `incompleteMaterialsError`.

Control flow: constructs a capture containing a local source named `context`, calls the error builder, asserts the error unwraps/ascribes to `errdefs.ProvenanceMaterialsIncompleteError`, and checks detail fields and message text.

State/persistence: none.

Dependencies/integration: llbsolver provenance capture, provenance types, solver errdefs, and testify.

Risks: coverage is narrow: only local-source incomplete details are tested, not proxy incomplete requests or empty details.

Test signals: protects complete-materials diagnostics so users see which local source prevented complete provenance and machine-readable incomplete detail includes reason `local_source`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/provenance_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/result.go -->
# sources/cloud-native/buildkit/solver/llbsolver/result.go

Purpose: defines llbsolver result wrappers and lazy result proxy evaluation, including provenance capture and source-location error enrichment.

Important APIs/types/functions: `Result`, `Attestation`, `workerRefResolver`, `resultProxy`, `newResultProxy`, `ID`, `Definition`, `Provenance`, `Release`, `wrapError`, `loadResult`, and `Result`.

Control flow: `resultProxy.Result` uses a flightcontrol group to run evaluation once, refuses access after release, calls bridge `loadResult`, borrows refs embedded in `ExecError`, captures provenance on success, stores result/error, and releases loaded results if a concurrent release wins. `wrapError` enriches vertex errors with source ranges from definition source metadata. `Release` releases borrowed error refs and cached result refs, warning on double release.

State/persistence: proxy caches one `solver.CachedResult`, error, borrowed error results, and captured provenance in memory. It owns release of those refs.

Dependencies/integration: frontend result proxies, solver cached results/provenance providers, BuildKit worker refs/remotes, cache ref config, session groups, errdefs, flightcontrol, and logging.

Risks: ownership around `ExecError` is delicate; `OwnerBorrowed` prevents double-finalizer release. Race between evaluation and release is guarded by mutex but must be preserved. Source-location enrichment depends on matching vertex digest keys.

Test signals: no direct tests in this subset; ownership invariants are referenced by comments and likely covered in worker/result tests outside this scope.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/result.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/solver.go -->
# sources/cloud-native/buildkit/solver/llbsolver/solver.go

Purpose: top-level BuildKit LLB solver orchestration: constructs solver/bridge state, resolves worker ops, runs frontend/definition solves, records history, applies processors, exports results/cache, and exposes status.

Important APIs/types/functions: `ExporterRequest`, `RemoteCacheExporter`, `ResolveWorkerFunc`, `Opt`, `Solver`, `Processor`, `New`, `Close`, `resolver`, `bridge`, `Bridge`, `Solve`, `leaseManager`, `Status`, `defaultResolver`, `allWorkers`, `inBuilderContext`, and `notifyStarted`.

Control flow: `New` validates provenance env reserved keys, initializes metrics, provenance store, system sampler, and the underlying solver with a worker-backed resolve function. `Solve` normalizes gateway dockerfile requests, creates a job, starts usage sampling, sets entitlements/proxy/source policy/compatibility/session values, builds a provenance bridge, optionally registers a gateway forwarder, records history, solves via forwarder or bridge, captures frontend opts, evaluates all refs, attaches provenance, runs post-processors, converts refs to cache refs, creates a lease, augments session exporters, runs exporters, then finalizes image exporters and cache exporters in parallel.

State/persistence: stores long-lived solver dependencies, provenance store, metrics, and resource sampler. Per-solve state includes job values, leases, history records, result refs, descriptor refs, and releasers. History and cache/exporters persist outside this file.

Dependencies/integration: worker controller, BuildKit solver core, gateway forwarder, frontends, cache import/export, exporters, verifier, result conversion, entitlements, source policy, leases, progress, history, metrics, and processors such as provenance/SBOM.

Risks: cleanup ordering is critical for refs, descriptor refs, leases, gateway registration, and history finalization. Export finalization and cache export run concurrently and share content created by exporters. Provenance env reserved keys prevent users from overriding builtins.

Test signals: no direct tests in this subset; this is integration-heavy and validated by solve/export/status suites elsewhere.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/solver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/vertex.go -->
# sources/cloud-native/buildkit/solver/llbsolver/vertex.go

Purpose: loads protobuf LLB definitions into solver vertices, applies load options, validates capabilities/entitlements, evaluates source policy, normalizes platforms, and recomputes digests after policy/proxy mutations.

Important APIs/types/functions: `vertex`, `LoadOpt`, `WithValidateCaps`, `WithCacheSources`, `WithLinuxResourcesMetadata`, `NormalizeRuntimePlatforms`, `ValidateEntitlements`, `detectPrunedCacheID`, `Load`, `loadWithProxyNetwork`, `vertexOptions`, `newVertex`, `recomputeDigests`, `op`, `loadLLB`, `llbOpName`, and `fileOpName`.

Control flow: `loadLLB` unmarshals each definition op, records source ops, attaches metadata, optionally computes per-op proxy-network flags, evaluates source policies concurrently, recomputes digests recursively after mutations, strips the synthetic last vertex, and recursively materializes reachable vertices through a cache. `newVertex` applies load options, computes a display name, and resolves input edges. Entitlement validation checks exec host network, insecure security, and CDI device requests, including aliasing, auto-allow devices, and forbidden device reporting.

State/persistence: no durable state. It mutates in-memory protobuf ops during platform normalization, policy conversion, device filtering, proxy marking, and digest recomputation.

Dependencies/integration: solver vertex interfaces, protobuf LLB definitions, source policy evaluator, BuildKit API caps, entitlements, CDI manager, linux resources metadata, platform normalization, and op validation.

Risks: digest recomputation must include proxy-network marker and all mutated input digests to avoid stale cache keys. Synthetic last vertex assumptions are strict. Entitlement/device rewriting mutates requested device lists and must remain auditable.

Test signals: no direct tests in this subset, but vertex loading is exercised by most solve tests. Names for source/exec/file/build/merge/diff/passthrough ops affect progress UI and diagnostics.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/vertex.go -->
