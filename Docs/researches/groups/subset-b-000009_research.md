# Group Research: subset-b-000009

This grouped report covers the source files assigned to `subset-b-000009`. Each section is delimited for deterministic reconciliation into the source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/mergediff_test.go -->
# sources/cloud-native/buildkit/client/mergediff_test.go

## Purpose
This integration-test source builds the merge/diff regression matrix for BuildKit LLB states. `diffOpTestCases` returns `integration.Test` cases that assert `llb.Diff`, `llb.Merge`, file operations, exec-root diffs, exec mount diffs, lazy image blobs, symlinks, hardlinks, opaque whiteouts, and nested merge graphs produce the expected filesystem result and cache behavior.

## Important APIs, Types, and Functions
- `diffOpTestCases() []integration.Test` is the entry point consumed by the broader client integration test suite.
- `verifyContents` implements `integration.Test` and solves an LLB state, exports it locally or as an image, then checks the on-disk content with `fstest` appliers.
- `verifyBlobReuse` asserts that single-layer diff exports reuse an existing layer blob instead of creating a new content blob.
- `contents`, `applyFn`, `contentsOf`, `apply`, `mergeContents`, and `empty` provide a small adapter layer between `llb.State` outputs and `fstest.Applier` assertions.
- `resetState` removes images from the buildkit containerd namespace and calls `checkAllReleasable` so cache and image state do not leak between cases.

## Control Flow
`diffOpTestCases` constructs reusable base states from `alpine` and `busybox`, appends many `verifyContents` and `verifyBlobReuse` values, and returns them to the integration runner. Each `verifyContents.Run` checks feature support, starts a client, obtains a registry, exports the result, optionally imports inline or registry cache, and validates both direct output contents and cache reimport contents. Containerd-backed runs additionally inspect image manifests and layer presence to ensure cache imports do not leave unexpected layer blobs in the worker content store.

## State and Persistence Behavior
The tests intentionally mutate BuildKit daemon state, a temporary registry, the containerd image service, and local output directories. `resetState` is critical persistence hygiene: without it, prior images and blobs could hide cache misses or make content-store reachability checks pass for the wrong reason. The tested persistent artifacts are OCI/Docker image manifests, layer blobs, registry cache exports, and local filesystem outputs.

## Dependencies and Integration Points
The file integrates with `client.Solve`, `llb` graph construction, containerd image/content APIs, the integration sandbox, worker feature gates, `fstest`, registries, and cache import/export options. It depends on Linux behavior for overlay whiteouts, device nodes, hardlinks, symlink traversal, and snapshotter semantics. Some checks require a containerd worker and are skipped for dockerd/rootless cases where the assertions are not meaningful.

## Risks and Edge Cases
The test matrix protects fragile behavior: empty diffs, scratch lower/upper states, file-vs-directory replacement, explicit whiteout conversion, unmatched deletes, deletes after merge, shuffled files that should not create diffs, FIFOs and character devices, symlink override/delete behavior, circular symlinks, hardlink copy-up semantics, diff-of-diff graphs, layered merge deletes, and opaque directory regressions. The risk is mostly environmental flakiness: registry availability, rootless limitations, containerd access, and platform-specific filesystem behavior.

## Test Signals
The file itself is a broad test signal. Passing cases show that `llb.Diff` and `llb.Merge` preserve user-visible filesystem semantics and cache equivalence across direct solves, inline cache, registry cache, and image-content validation. Failures usually indicate a differ, merge-op, exporter, or cache-import regression rather than a narrow client API failure.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/mergediff_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/ociindex/ociindex.go -->
# sources/cloud-native/buildkit/client/ociindex/ociindex.go

## Purpose
This package manages the `index.json` and `oci-layout` files for a local OCI content store used by client-side cache and image exports. It provides a small, locked API for reading an OCI image index, adding descriptors with optional image names/tags, and resolving descriptors by tag or single-manifest layout.

## Important APIs, Types, and Functions
- `StoreIndex` stores paths to `index.json`, `index.json.lock`, and `oci-layout`.
- `NameOrTag`, `Name`, and `Tag` describe how a descriptor should be annotated when inserted.
- `NewStoreIndex(storePath)` binds index management to a local content-store directory.
- `Read()` takes a shared lock, reads `index.json`, and unmarshals an `ocispecs.Index`.
- `Put(desc, names...)` takes an exclusive lock, writes `oci-layout`, reads or creates `index.json`, applies OCI defaults, inserts one descriptor per supplied name/tag, writes the JSON back at offset zero, and truncates stale bytes.
- `Get(tag)` resolves first by `io.containerd.image.name`, then by OCI `org.opencontainers.image.ref.name`.
- `GetSingle()` returns the only manifest when the index contains exactly one descriptor.
- `insertDesc` clones descriptor annotations, adds name/tag annotations, removes replaced descriptors, and appends the new descriptor.

## Control Flow
`Put` is the main mutating path. It acquires a flock, ensures an OCI layout file exists, opens the index with create permissions, decodes existing JSON if present, fills schema and media type defaults, converts missing names into a single nil insertion, and appends/replaces descriptors. `Read`, `Get`, and `GetSingle` are read-only paths, with `Get` performing two lookup passes for containerd full-image-name compatibility and OCI tag compatibility.

## State and Persistence Behavior
State is persisted entirely as JSON files in the store path. The lock file is removed after lock release. `Put` overwrites `index.json` in place and truncates it, so callers rely on flock protection for concurrent writers. The descriptor passed by the caller is copied before annotation changes, avoiding mutation of caller-owned state.

## Dependencies and Integration Points
The package depends on OCI image-spec types, containerd reference parsing, `gofrs/flock`, and POSIX-style lock errors. It is used by `client/solve.go` to update local cache stores and output stores after successful solves and by cache import logic to resolve tags into digests.

## Risks and Edge Cases
The read path tolerates `EPERM` and `EROFS` lock errors by continuing without a lock, which is useful on read-only/limited filesystems but weakens concurrency guarantees. `Put` does not use a temp-file rename, so a process crash during write could leave partial JSON. Replacement only removes descriptors whose OCI ref and containerd image-name annotations both match the new insertion semantics, so changing naming rules can create duplicates.

## Test Signals
`ociindex_test.go` covers missing indexes, reading, single descriptor writes, tag lookups, default fields, multiple names per descriptor, and replacement by image name. `solve.go` and `solve_resetcache_test.go` provide integration pressure by relying on the index for cache imports, exports, and reset reachability.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/ociindex/ociindex.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/ociindex/ociindex_test.go -->
# sources/cloud-native/buildkit/client/ociindex/ociindex_test.go

## Purpose
This unit-test source verifies the behavior of the local OCI index helper used by BuildKit client cache and image-store export flows. It focuses on index creation, descriptor insertion, tag/name annotation behavior, lookup semantics, and replacement behavior.

## Important APIs, Types, and Functions
- `TestEmptyDir` asserts `Read` on a store without `index.json` returns `os.ErrNotExist`.
- `TestReadIndex` validates unmarshalling of an existing index.
- `TestReadByTag` checks lookup by OCI ref-name annotation.
- `TestWriteSingleDescriptor` validates `Put` followed by `GetSingle`.
- `TestAddDescriptor` verifies append behavior and default `schemaVersion`/media type population.
- `TestAddDescriptorWithTag` verifies tag annotation and lookup.
- `TestAddMultipleNames` verifies multiple descriptor entries are emitted for one input descriptor with different image names.
- `TestReplaceByImageName` verifies replacing an existing named descriptor preserves unrelated descriptors.
- `randDescriptor` creates deterministic descriptors from digest seeds.

## Control Flow
The tests create temporary directories, optionally seed `index.json`, call `NewStoreIndex`, then exercise `Read`, `Put`, `Get`, or `GetSingle`. Assertions inspect both the API return values and the raw JSON persisted in the temporary index file.

## State and Persistence Behavior
Each test uses a fresh temporary store path and writes actual `index.json` data. The tests confirm `Put` persists index defaults and descriptor annotations, not just in-memory return values. There is no shared state between cases.

## Dependencies and Integration Points
The tests depend on OCI descriptor/index types, OpenContainers digests, local filesystem IO, and testify assertions. They are direct coverage for `ociindex.go`; higher-level integration occurs through `solve.go` cache/output-store index updates.

## Risks and Edge Cases
The suite does not simulate lock contention, corrupt JSON, short writes, read-only stores, or crash consistency. It does protect the core compatibility rules: tag resolution, image-name resolution, descriptor append order, and replacement without mutating unrelated index entries.

## Test Signals
Passing tests indicate stable local OCI index semantics. Failures are likely to break local cache import/export by tag or local OCI/Docker output directories whose `index.json` must point at the latest exported descriptor.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/ociindex/ociindex_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/pinrace_6731_test.go -->
# sources/cloud-native/buildkit/client/pinrace_6731_test.go

## Purpose
This integration regression test targets issue 6731, where provenance capture could observe an HTTP source `SourceOp` while its pin was still empty during an ignore-cache shifted-state race. The symptom being guarded is an empty digest reaching provenance capture and failing with an invalid checksum digest format.

## Important APIs, Types, and Functions
- `init` registers `testPinRaceIgnoreCacheShift` in the global integration test list.
- `testPinRaceIgnoreCacheShift` sets up a slow no-cache HTTP server, creates a client, and runs several deterministic race iterations.
- `runPinRaceIteration` constructs the warmup, race-creator, and walker LLB graphs and coordinates two physical `c.Build` calls.
- The test uses `llb.HTTP`, `llb.IgnoreCache`, `llb.Merge`, gateway frontends, `gateway.Client.Solve`, `Ref.Evaluate`, and provenance frontend attrs.

## Control Flow
Each iteration first runs a warmup gateway build in Job 1. That frontend solves and evaluates a non-ignore-cache chain, then blocks on `warmupHold` to keep base, mid, and root states active. A second gateway build in Job 2 then starts a racer chain using ignore-cache and a fresh copy destination, waits a head start, and evaluates a walker chain using ignore-cache and the original mid digest. The delayed HTTP server widens the window where the racer is in source cache-key resolution while the walker provenance traversal can observe the shifted state.

## State and Persistence Behavior
The test deliberately relies on daemon-resident solver state, active refs, resolver caches, and job isolation. It keeps Job 1 alive to hold state in `actives`, while Job 2 uses a separate resolver cache so the HTTP source has to perform a slow fetch. No durable artifacts are asserted; the important state is in-memory BuildKit scheduler/provenance state.

## Dependencies and Integration Points
The file integrates with the client gateway build path, HTTP source resolver, provenance capture, LLB merge/diff scheduler behavior, the integration sandbox, and worker feature compatibility for merge-diff. It skips Windows and needs timing-sensitive behavior from the BuildKit daemon.

## Risks and Edge Cases
The regression is timing-sensitive. The test mitigates flakiness with repeated iterations, a slow HTTP server, no-cache response headers, and a controlled warmup hold. Future solver optimizations may narrow or remove the race window, but the expected signal remains that the build succeeds without empty-pin provenance errors.

## Test Signals
A pass indicates provenance capture can tolerate ignore-cache shifted sources while source resolution is in flight. A failure with checksum/digest parsing or provenance source-pin errors points to a recurrence in `SourceOp` pin publication, resolver cache isolation, or provenance walking.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/pinrace_6731_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/policy_test.go -->
# sources/cloud-native/buildkit/client/policy_test.go

## Purpose
This integration-test file covers BuildKit client source policy, policy session callbacks, proxy-network behavior, provenance material capture, source metadata resolution, Git signature metadata, and HTTP checksum assist. It verifies both static source policies and interactive session providers used by `SolveOpt.SourcePolicyProvider`.

## Important APIs, Types, and Functions
- Proxy-network tests: `testProxyNetworkNoRootless`, `testProxyNetworkModesNoRootless`, `testProxyNetworkDefaultEgressNoRootless`, `proxyNetModeDefaultHasHostLoopback`, `newProxyHTTPServer`, and `testHostIP`.
- Policy-session tests: `testSourcePolicySession`, `testSourcePolicySessionDenyMessages`, `testSourceMetaPolicySession`, `testSourceMetaPolicySessionResolveAttestations`, `testSourcePolicyParallelSession`, and `testSourcePolicySessionConvert`.
- Git and checksum tests: `testSourcePolicySignedCommit`, `testSourcePolicySessionHTTPChecksumAssist`, `toPBChecksumAlgo`, `payloadWithSuffixDigest`, and `tamperDigestHex`.
- Core dependencies include `policysession.NewPolicyProvider`, gateway `ResolveSourceMetadata`, source-policy protobufs, LLB image/git/http sources, SLSA provenance types, and PGP signature helpers.

## Control Flow
The proxy tests create local HTTP servers, run LLB execs through BuildKit proxy mode, inspect status logs, validate deny/convert policy behavior, and assert provenance material completeness. Network-mode tests verify default, host, and none modes with entitlement gating. Source-policy tests build LLB graphs or gateway metadata requests, then drive policy callbacks that allow, deny, request resolved metadata, request attestation chains, convert identifiers/attrs, or deliberately loop until the request limit is hit. Git tests create a local repository with signed and unsigned refs and validate policy-driven signature requirements. HTTP checksum tests request resolver-computed digests with signature suffixes and verify positive and negative signature checks.

## State and Persistence Behavior
The tests create temporary HTTP servers, temporary Git repositories, local output directories containing exported files and `provenance.json`, and policy provider session state such as callback counters and synchronization channels. BuildKit daemon state includes source resolver metadata, provenance records, network proxy logs, and source policy decisions. Environment variables gate expensive or fixture-dependent cases: network integration and signing fixtures.

## Dependencies and Integration Points
This file is a dense integration point for client `Solve`, client `Build`, gateway frontends, source resolver APIs, BuildKit proxy networking, entitlements, provenance export, policy-helper image attestations, Git source handling, and PGP verification. It also consumes integration sandbox values such as network mode, Docker/containerd address, rootless status, and worker feature flags.

## Risks and Edge Cases
Covered risks include host-network leakage through proxy env injection, missing `network.host` entitlement enforcement, incorrect default proxy egress behavior, incomplete provenance materials, policy deny messages being lost, metadata callbacks receiving incomplete platform/source fields, attestation chain blobs missing requested predicate types, deadlocks or serialization bugs in parallel policy checks, infinite convert loops, bad Git signature policy handling, oversized checksum suffixes, and unsupported checksum algorithms.

## Test Signals
A pass indicates that source policy remains enforceable across direct solve, gateway metadata resolution, proxy HTTP fetches, Git sources, image attestations, and provenance export. Failures tend to reveal security-sensitive regressions in network isolation, source substitution, metadata verification, or provenance completeness rather than superficial client formatting issues.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/policy_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/prune.go -->
# sources/cloud-native/buildkit/client/prune.go

## Purpose
This client API wraps the BuildKit control service `Prune` RPC and streams deleted or pruned cache records back to callers as client-level `UsageInfo` values.

## Important APIs, Types, and Functions
- `Client.Prune(ctx, ch, opts...)` is the public entry point.
- `PruneOption` and `pruneOptionFunc` provide the option pattern.
- `PruneInfo` stores request fields: `All`, filter strings, keep duration, reserved/max-used/min-free space.
- `PruneAll` enables complete pruning.
- `WithKeepOpt(duration, reserved, max, free)` fills keep and space policy fields.

## Control Flow
`Prune` creates a `PruneInfo`, applies all options, maps it into `controlapi.PruneRequest`, calls `ControlClient().Prune`, and loops over streamed responses until EOF. Each response is converted into `UsageInfo` and sent to `ch` when a channel is provided. Non-EOF stream errors abort the call.

## State and Persistence Behavior
The function does not store state locally. It triggers daemon-side garbage collection and reports daemon-side records. `LastUsedAt` is converted only when the protobuf timestamp is present, preserving nil when the daemon does not know a last-used time.

## Dependencies and Integration Points
This file depends on the control API protobuf service, `UsageInfo`/`UsageRecordType` types defined elsewhere in the client package, and standard time conversion. It is the client-facing bridge for BuildKit cache cleanup tooling.

## Risks and Edge Cases
If `ch` is unbuffered or the receiver stops reading, `Prune` blocks while streaming. The code does not close `ch`, leaving channel ownership to the caller. Duration is sent as raw `int64(info.KeepDuration)`, so both client and daemon must agree on nanosecond `time.Duration` semantics.

## Test Signals
No direct tests are in this file. Indirect signals come from integration tests and cache cleanup flows that exercise `Client.Prune` and validate returned `UsageInfo` fields.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/prune.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/solve.go -->
# sources/cloud-native/buildkit/client/solve.go

## Purpose
This is the main BuildKit client solve implementation. It validates solve inputs, prepares session file sync and content-store attachments, builds control API solve requests, streams status updates, manages cache import/export metadata, updates local OCI indexes after exports, and supports local cache reset by deleting unreferenced blobs.

## Important APIs, Types, and Functions
- `SolveOpt` is the high-level solve configuration: exporters, frontend attrs/inputs, local mounts, cache import/export, sessions, entitlements, source policy, proxy network, compatibility version, and reference override.
- `ExportEntry` describes each output exporter and local file/dir/content-store target.
- `CacheOptionsEntry` describes cache import/export entries.
- `Client.Solve` validates frontend/definition exclusivity and delegates to `solve`.
- `solve` coordinates sessions, exports, status streaming, control API invocation, cache index updates, image output index updates, and cache reset.
- `prepareSyncedFiles` filters local mount filesystems and resets UID/GID to zero for sync providers.
- `parseCacheOptions` converts client cache options to control API options, opens local content stores, resolves local import tags through `ociindex`, and prepares frontend attrs for frontend/gateway cache imports.
- `resetCacheStore` walks descriptors referenced by `index.json` and deletes content-store blobs that are not reachable.

## Control Flow
`Solve` rejects empty definitions and invalid frontend+definition combinations. `solve` prepares local mounts, creates or uses a session, parses cache options, registers file-sync providers, session attachables, content stores, export targets, source policy providers, and starts the session unless preinitialized. It merges cache-import frontend attrs, then runs concurrent goroutines for the control `Solve` RPC, optional gateway callback, and status stream. After all goroutines complete, it updates local cache `index.json` entries from `cache.manifest`, updates local image output stores from exported image descriptors and names, and resets requested local cache stores.

## State and Persistence Behavior
Local persistent state includes output directories, OCI content stores, `oci-layout`, `index.json`, and cache blobs. Session state is transient and scoped to the solve unless `SharedSession` or `SessionPreInitialized` is used. Status streaming uses a separate background context and an inactivity timeout so status RPCs terminate after solve completion. Cache reset preserves all blobs reachable from index manifests and removes unreferenced blobs best-effort, logging delete failures rather than failing the solve.

## Dependencies and Integration Points
This file integrates with the BuildKit control API, LLB definitions, session transport, file sync, session content providers, local containerd content stores, OCI index helper, exporter response keys, source policy protobufs, OpenTelemetry trace propagation, and containerd image traversal. It is the central adapter between user-facing client options and daemon-side solver/exporter behavior.

## Risks and Edge Cases
Important guarded risks include invalid frontend/definition combinations, duplicate OCI store keys, unsupported output target combinations, missing output writers/directories, local cache imports with missing stores or missing tag digests, status goroutine leaks, gateway callback errors racing solve completion, `res` being nil if solve succeeds unexpectedly without a response, local index corruption from failed writes, and cache reset accidentally deleting reachable blobs if descriptor traversal misses a media type.

## Test Signals
`solve_resetcache_test.go` directly covers `resetCacheStore`. `ociindex_test.go` covers the index helper used here. The broader client integration suite, including merge/diff, policy, validation, and compatibility tests, exercises exporter validation, status streaming, local outputs, cache import/export, session providers, and provenance options.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/solve.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/solve_resetcache_test.go -->
# sources/cloud-native/buildkit/client/solve_resetcache_test.go

## Purpose
This unit-test source verifies `resetCacheStore`, the local cache cleanup routine in `solve.go` that deletes content-store blobs not reachable from `index.json` manifests.

## Important APIs, Types, and Functions
- `writeBlob` writes deterministic blobs into a containerd content store.
- `listDigests` lists all content-store digests for assertions.
- `setupCacheStore` creates a temporary local content store, writes config/layer/manifest blobs, and inserts the manifest into `index.json` with `ociindex.Tag`.
- `TestResetCacheStoreImageManifest`, `TestResetCacheStoreMultipleTags`, `TestResetCacheStoreNoOrphans`, `TestResetCacheStoreNestedIndex`, and `TestResetCacheStoreDockerMediaTypes` cover reachability shapes.

## Control Flow
Each test creates a local content store, writes referenced blobs and at least one orphan when relevant, writes an OCI index descriptor, calls `resetCacheStore`, and then asserts which digests remain. The nested-index and Docker media type cases ensure traversal uses containerd image children logic instead of a single hard-coded OCI manifest shape.

## State and Persistence Behavior
All state is stored under temporary directories using containerd's local content store and `ociindex` `index.json`. The function under test mutates the content store by deleting orphan blobs. Tests assert both preservation of referenced manifests/configs/layers and removal of orphan blobs.

## Dependencies and Integration Points
The tests depend on containerd content APIs, containerd image child traversal, local content-store implementation, OCI and Docker media type descriptors, and the `ociindex` helper. They are direct coverage for the cache export reset path used when local cache exporter attrs include `reset=true`.

## Risks and Edge Cases
The covered risk is data loss: reachable cache/image blobs must not be removed. The suite includes multiple tags, no-op reset, nested indexes, direct cache config descriptors, and Docker schema2 manifest lists. It does not simulate delete failures or corrupt index data.

## Test Signals
Passing tests show that cache reset is reachability-based rather than tag-count-based or media-type-specific. Failures would threaten local cache exports by either leaking old blobs or deleting current cache records.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/solve_resetcache_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/status.go -->
# sources/cloud-native/buildkit/client/status.go

## Purpose
This file converts BuildKit control API status protobufs to client-facing status structs and can marshal accumulated client status back into one or more protobuf `StatusResponse` messages. It is the client-side status adapter for solve progress, logs, warnings, and vertex metadata.

## Important APIs, Types, and Functions
- `NewSolveStatus(resp)` converts protobuf `Vertex`, `VertexStatus`, `VertexLog`, and `VertexWarning` values into `SolveStatus` fields.
- `SolveStatus.Marshal()` converts the client struct back to protobuf messages and chunks large logs.
- Helper functions convert digest slices and optional timestamps: `digestSliceFromPB`, `digestSliceToPB`, `timestampFromPB`, and `timestampToPB`.
- `emptyLogVertexSize` caches the VT protobuf size overhead used for log chunking.

## Control Flow
`NewSolveStatus` iterates each repeated protobuf field and appends converted client values. `Marshal` builds a response with all vertexes and statuses, then appends logs until the accumulated approximate log size exceeds 1 MiB. When the threshold is crossed, it clears already-emitted vertex/status fields, slices consumed logs off `ss.Logs`, appends the partial response, and repeats until all logs are emitted. Warnings are included in each generated response pass after logs are processed.

## State and Persistence Behavior
The file has no persistent storage. `Marshal` mutates the receiver when log splitting occurs by clearing `Vertexes`/`Statuses` and advancing `Logs`, so callers should not assume the original `SolveStatus` remains intact after marshaling large logs.

## Dependencies and Integration Points
It depends on the control API protobuf types, OpenContainers digests, protobuf timestamps, and status structs from the client package. `solve.go` uses `NewSolveStatus` to send streamed daemon status into the caller-provided channel.

## Risks and Edge Cases
The main behavioral risk is mutation during `Marshal`, which may surprise callers that reuse a `SolveStatus`. Timestamp conversion assumes non-nil protobuf timestamps for statuses/logs where `AsTime` is called directly. Log chunking is approximate and based on message bytes plus empty-log protobuf overhead.

## Test Signals
No direct tests are listed for this file in this work item. Indirect coverage comes from integration tests that read solve logs, such as proxy-network policy tests, and any callers that marshal status for replay or frontend communication.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/status.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/default-gzip/v10/config.json -->
# sources/cloud-native/buildkit/client/testdata/compatibility/common/default-gzip/v10/config.json

## Purpose
This JSON fixture is an image configuration document for the BuildKit client compatibility suite. It belongs to the `common/default-gzip/v10` fixture, which represents the common fixture shared by exporter compatibility tests across image layout modes and the default gzip compression baseline.

## Important Fields and Data Shape
- Platform: `linux/amd64` with created timestamp `2015-10-21T07:28:00Z`.
- Runtime config: env count `1`, command `['sh']`, working directory ``, entrypoint `None`, labels `None`.
- Root filesystem: type `layers`, diff ID count `4`, first diff ID `sha256:fe4922f0a3ca2aa70...`.
- History: `5` entries, including BuildKit exporter history comments for generated layers.
- Compatibility version directory: `v10`.

## Control Flow and Integration Role
The file is loaded as fixture data rather than executed. Compatibility tests compare generated exporter config JSON against this baseline to detect changes in platform fields, rootfs diff IDs, history ordering, Docker legacy fields, command/env defaults, and BuildKit-created history records.

## State and Persistence Behavior
The document is immutable testdata. It models persisted image configuration that would be stored as a content-addressed config blob and referenced by a manifest. Any byte-level change can alter the config digest and therefore the expected manifest descriptor.

## Dependencies and Integration Points
It integrates with image/OCI exporter compatibility tests under `client/testdata/compatibility`, the container image exporter metadata path, and manifest fixtures in adjacent directories. The config's diff IDs must align with layer descriptors in the corresponding manifest fixture.

## Risks and Edge Cases
The main risk is accidental fixture drift: changing timestamps, history text, Docker legacy fields, or diff ID ordering can break reproducibility and compatibility assertions. Variant-specific compression changes should not alter uncompressed diff IDs unless the actual filesystem content changes.

## Test Signals
A matching config indicates the exporter preserved expected image config schema, platform, rootfs, and history semantics for `default-gzip` under compatibility version `v10`. A mismatch usually signals exporter output drift rather than runtime code execution in this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/default-gzip/v10/config.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/default-gzip/v20/config.json -->
# sources/cloud-native/buildkit/client/testdata/compatibility/common/default-gzip/v20/config.json

## Purpose
This JSON fixture is an image configuration document for the BuildKit client compatibility suite. It belongs to the `common/default-gzip/v20` fixture, which represents the common fixture shared by exporter compatibility tests across image layout modes and the default gzip compression baseline.

## Important Fields and Data Shape
- Platform: `linux/amd64` with created timestamp `2015-10-21T07:28:00Z`.
- Runtime config: env count `1`, command `['sh']`, working directory ``, entrypoint `None`, labels `None`.
- Root filesystem: type `layers`, diff ID count `4`, first diff ID `sha256:fe4922f0a3ca2aa70...`.
- History: `5` entries, including BuildKit exporter history comments for generated layers.
- Compatibility version directory: `v20`.

## Control Flow and Integration Role
The file is loaded as fixture data rather than executed. Compatibility tests compare generated exporter config JSON against this baseline to detect changes in platform fields, rootfs diff IDs, history ordering, Docker legacy fields, command/env defaults, and BuildKit-created history records.

## State and Persistence Behavior
The document is immutable testdata. It models persisted image configuration that would be stored as a content-addressed config blob and referenced by a manifest. Any byte-level change can alter the config digest and therefore the expected manifest descriptor.

## Dependencies and Integration Points
It integrates with image/OCI exporter compatibility tests under `client/testdata/compatibility`, the container image exporter metadata path, and manifest fixtures in adjacent directories. The config's diff IDs must align with layer descriptors in the corresponding manifest fixture.

## Risks and Edge Cases
The main risk is accidental fixture drift: changing timestamps, history text, Docker legacy fields, or diff ID ordering can break reproducibility and compatibility assertions. Variant-specific compression changes should not alter uncompressed diff IDs unless the actual filesystem content changes.

## Test Signals
A matching config indicates the exporter preserved expected image config schema, platform, rootfs, and history semantics for `default-gzip` under compatibility version `v20`. A mismatch usually signals exporter output drift rather than runtime code execution in this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/default-gzip/v20/config.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/default-gzip/v30/config.json -->
# sources/cloud-native/buildkit/client/testdata/compatibility/common/default-gzip/v30/config.json

## Purpose
This JSON fixture is an image configuration document for the BuildKit client compatibility suite. It belongs to the `common/default-gzip/v30` fixture, which represents the common fixture shared by exporter compatibility tests across image layout modes and the default gzip compression baseline.

## Important Fields and Data Shape
- Platform: `linux/amd64` with created timestamp `2015-10-21T07:28:00Z`.
- Runtime config: env count `1`, command `['sh']`, working directory ``, entrypoint `None`, labels `None`.
- Root filesystem: type `layers`, diff ID count `4`, first diff ID `sha256:fe4922f0a3ca2aa70...`.
- History: `5` entries, including BuildKit exporter history comments for generated layers.
- Compatibility version directory: `v30`.

## Control Flow and Integration Role
The file is loaded as fixture data rather than executed. Compatibility tests compare generated exporter config JSON against this baseline to detect changes in platform fields, rootfs diff IDs, history ordering, Docker legacy fields, command/env defaults, and BuildKit-created history records.

## State and Persistence Behavior
The document is immutable testdata. It models persisted image configuration that would be stored as a content-addressed config blob and referenced by a manifest. Any byte-level change can alter the config digest and therefore the expected manifest descriptor.

## Dependencies and Integration Points
It integrates with image/OCI exporter compatibility tests under `client/testdata/compatibility`, the container image exporter metadata path, and manifest fixtures in adjacent directories. The config's diff IDs must align with layer descriptors in the corresponding manifest fixture.

## Risks and Edge Cases
The main risk is accidental fixture drift: changing timestamps, history text, Docker legacy fields, or diff ID ordering can break reproducibility and compatibility assertions. Variant-specific compression changes should not alter uncompressed diff IDs unless the actual filesystem content changes.

## Test Signals
A matching config indicates the exporter preserved expected image config schema, platform, rootfs, and history semantics for `default-gzip` under compatibility version `v30`. A mismatch usually signals exporter output drift rather than runtime code execution in this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/default-gzip/v30/config.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/default-gzip/v30/manifest.json -->
# sources/cloud-native/buildkit/client/testdata/compatibility/common/default-gzip/v30/manifest.json

## Purpose
This JSON fixture is an image manifest baseline for the BuildKit client compatibility suite. It belongs to `common/default-gzip/v30`, representing the common fixture shared by exporter compatibility tests across image layout modes and the default gzip compression baseline.

## Important Fields and Data Shape
- Schema version: `2`.
- Manifest media type: `application/vnd.oci.image.manifest.v1+json`.
- Config descriptor media type: `application/vnd.oci.image.config.v1+json`, digest `sha256:1772fd0a3b45a62fc...`, size `2295`.
- Layer count: `4`.
- Layer media types: `application/vnd.oci.image.layer.v1.tar+gzip`.
- First layer digest/size: `sha256:430ee4fa77d640d42...` / `2219886`.
- Manifest annotations present: `False`; layer descriptors with annotations: `4`.
- Compatibility version directory: `v30`.

## Control Flow and Integration Role
The file is fixture input for compatibility comparisons. Tests use it to verify that exporter output preserves expected manifest media types, config references, layer descriptors, annotations, compression choices, and compatibility-version behavior.

## State and Persistence Behavior
The manifest models persisted registry or OCI-layout metadata. It is content-addressable through its JSON bytes, and its config/layer descriptors must match adjacent config blobs and generated layer blobs. It has no runtime mutation path.

## Dependencies and Integration Points
It integrates with exporter compatibility tests, the image/OCI exporter, compression settings, OCI/Docker media-type conversion, provenance/annotation options, and adjacent `config.json` fixture files where present.

## Risks and Edge Cases
Risks include digest churn from non-deterministic timestamps or compression, wrong Docker-vs-OCI media types, dropped annotations, incorrect uncompressed/zstd media type selection, or layer order changes. For `manifest-annotation` fixtures, annotations are part of the behavior under test. For compression fixtures, descriptor sizes and digests are sensitive to compressor settings.

## Test Signals
A match means BuildKit emitted the expected manifest structure for `default-gzip` in `common` mode at compatibility version `v30`. A mismatch is a high-signal exporter compatibility regression because consumers use these descriptors to pull or load the image.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/default-gzip/v30/manifest.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/gzip-level-0/v10/config.json -->
# sources/cloud-native/buildkit/client/testdata/compatibility/common/gzip-level-0/v10/config.json

## Purpose
This JSON fixture is an image configuration document for the BuildKit client compatibility suite. It belongs to the `common/gzip-level-0/v10` fixture, which represents the common fixture shared by exporter compatibility tests across image layout modes and the gzip compression level 0 compatibility baseline.

## Important Fields and Data Shape
- Platform: `linux/amd64` with created timestamp `2015-10-21T07:28:00Z`.
- Runtime config: env count `1`, command `['sh']`, working directory ``, entrypoint `None`, labels `None`.
- Root filesystem: type `layers`, diff ID count `4`, first diff ID `sha256:fe4922f0a3ca2aa70...`.
- History: `5` entries, including BuildKit exporter history comments for generated layers.
- Compatibility version directory: `v10`.

## Control Flow and Integration Role
The file is loaded as fixture data rather than executed. Compatibility tests compare generated exporter config JSON against this baseline to detect changes in platform fields, rootfs diff IDs, history ordering, Docker legacy fields, command/env defaults, and BuildKit-created history records.

## State and Persistence Behavior
The document is immutable testdata. It models persisted image configuration that would be stored as a content-addressed config blob and referenced by a manifest. Any byte-level change can alter the config digest and therefore the expected manifest descriptor.

## Dependencies and Integration Points
It integrates with image/OCI exporter compatibility tests under `client/testdata/compatibility`, the container image exporter metadata path, and manifest fixtures in adjacent directories. The config's diff IDs must align with layer descriptors in the corresponding manifest fixture.

## Risks and Edge Cases
The main risk is accidental fixture drift: changing timestamps, history text, Docker legacy fields, or diff ID ordering can break reproducibility and compatibility assertions. Variant-specific compression changes should not alter uncompressed diff IDs unless the actual filesystem content changes.

## Test Signals
A matching config indicates the exporter preserved expected image config schema, platform, rootfs, and history semantics for `gzip-level-0` under compatibility version `v10`. A mismatch usually signals exporter output drift rather than runtime code execution in this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/gzip-level-0/v10/config.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/gzip-level-0/v20/config.json -->
# sources/cloud-native/buildkit/client/testdata/compatibility/common/gzip-level-0/v20/config.json

## Purpose
This JSON fixture is an image configuration document for the BuildKit client compatibility suite. It belongs to the `common/gzip-level-0/v20` fixture, which represents the common fixture shared by exporter compatibility tests across image layout modes and the gzip compression level 0 compatibility baseline.

## Important Fields and Data Shape
- Platform: `linux/amd64` with created timestamp `2015-10-21T07:28:00Z`.
- Runtime config: env count `1`, command `['sh']`, working directory ``, entrypoint `None`, labels `None`.
- Root filesystem: type `layers`, diff ID count `4`, first diff ID `sha256:fe4922f0a3ca2aa70...`.
- History: `5` entries, including BuildKit exporter history comments for generated layers.
- Compatibility version directory: `v20`.

## Control Flow and Integration Role
The file is loaded as fixture data rather than executed. Compatibility tests compare generated exporter config JSON against this baseline to detect changes in platform fields, rootfs diff IDs, history ordering, Docker legacy fields, command/env defaults, and BuildKit-created history records.

## State and Persistence Behavior
The document is immutable testdata. It models persisted image configuration that would be stored as a content-addressed config blob and referenced by a manifest. Any byte-level change can alter the config digest and therefore the expected manifest descriptor.

## Dependencies and Integration Points
It integrates with image/OCI exporter compatibility tests under `client/testdata/compatibility`, the container image exporter metadata path, and manifest fixtures in adjacent directories. The config's diff IDs must align with layer descriptors in the corresponding manifest fixture.

## Risks and Edge Cases
The main risk is accidental fixture drift: changing timestamps, history text, Docker legacy fields, or diff ID ordering can break reproducibility and compatibility assertions. Variant-specific compression changes should not alter uncompressed diff IDs unless the actual filesystem content changes.

## Test Signals
A matching config indicates the exporter preserved expected image config schema, platform, rootfs, and history semantics for `gzip-level-0` under compatibility version `v20`. A mismatch usually signals exporter output drift rather than runtime code execution in this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/gzip-level-0/v20/config.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/gzip-level-0/v30/config.json -->
# sources/cloud-native/buildkit/client/testdata/compatibility/common/gzip-level-0/v30/config.json

## Purpose
This JSON fixture is an image configuration document for the BuildKit client compatibility suite. It belongs to the `common/gzip-level-0/v30` fixture, which represents the common fixture shared by exporter compatibility tests across image layout modes and the gzip compression level 0 compatibility baseline.

## Important Fields and Data Shape
- Platform: `linux/amd64` with created timestamp `2015-10-21T07:28:00Z`.
- Runtime config: env count `1`, command `['sh']`, working directory ``, entrypoint `None`, labels `None`.
- Root filesystem: type `layers`, diff ID count `4`, first diff ID `sha256:fe4922f0a3ca2aa70...`.
- History: `5` entries, including BuildKit exporter history comments for generated layers.
- Compatibility version directory: `v30`.

## Control Flow and Integration Role
The file is loaded as fixture data rather than executed. Compatibility tests compare generated exporter config JSON against this baseline to detect changes in platform fields, rootfs diff IDs, history ordering, Docker legacy fields, command/env defaults, and BuildKit-created history records.

## State and Persistence Behavior
The document is immutable testdata. It models persisted image configuration that would be stored as a content-addressed config blob and referenced by a manifest. Any byte-level change can alter the config digest and therefore the expected manifest descriptor.

## Dependencies and Integration Points
It integrates with image/OCI exporter compatibility tests under `client/testdata/compatibility`, the container image exporter metadata path, and manifest fixtures in adjacent directories. The config's diff IDs must align with layer descriptors in the corresponding manifest fixture.

## Risks and Edge Cases
The main risk is accidental fixture drift: changing timestamps, history text, Docker legacy fields, or diff ID ordering can break reproducibility and compatibility assertions. Variant-specific compression changes should not alter uncompressed diff IDs unless the actual filesystem content changes.

## Test Signals
A matching config indicates the exporter preserved expected image config schema, platform, rootfs, and history semantics for `gzip-level-0` under compatibility version `v30`. A mismatch usually signals exporter output drift rather than runtime code execution in this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/gzip-level-0/v30/config.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/gzip-level-0/v30/manifest.json -->
# sources/cloud-native/buildkit/client/testdata/compatibility/common/gzip-level-0/v30/manifest.json

## Purpose
This JSON fixture is an image manifest baseline for the BuildKit client compatibility suite. It belongs to `common/gzip-level-0/v30`, representing the common fixture shared by exporter compatibility tests across image layout modes and the gzip compression level 0 compatibility baseline.

## Important Fields and Data Shape
- Schema version: `2`.
- Manifest media type: `application/vnd.oci.image.manifest.v1+json`.
- Config descriptor media type: `application/vnd.oci.image.config.v1+json`, digest `sha256:1772fd0a3b45a62fc...`, size `2295`.
- Layer count: `4`.
- Layer media types: `application/vnd.oci.image.layer.v1.tar+gzip`.
- First layer digest/size: `sha256:3b2645dc700f1550f...` / `4492656`.
- Manifest annotations present: `False`; layer descriptors with annotations: `4`.
- Compatibility version directory: `v30`.

## Control Flow and Integration Role
The file is fixture input for compatibility comparisons. Tests use it to verify that exporter output preserves expected manifest media types, config references, layer descriptors, annotations, compression choices, and compatibility-version behavior.

## State and Persistence Behavior
The manifest models persisted registry or OCI-layout metadata. It is content-addressable through its JSON bytes, and its config/layer descriptors must match adjacent config blobs and generated layer blobs. It has no runtime mutation path.

## Dependencies and Integration Points
It integrates with exporter compatibility tests, the image/OCI exporter, compression settings, OCI/Docker media-type conversion, provenance/annotation options, and adjacent `config.json` fixture files where present.

## Risks and Edge Cases
Risks include digest churn from non-deterministic timestamps or compression, wrong Docker-vs-OCI media types, dropped annotations, incorrect uncompressed/zstd media type selection, or layer order changes. For `manifest-annotation` fixtures, annotations are part of the behavior under test. For compression fixtures, descriptor sizes and digests are sensitive to compressor settings.

## Test Signals
A match means BuildKit emitted the expected manifest structure for `gzip-level-0` in `common` mode at compatibility version `v30`. A mismatch is a high-signal exporter compatibility regression because consumers use these descriptors to pull or load the image.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/gzip-level-0/v30/manifest.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/gzip-level-9/v10/config.json -->
# sources/cloud-native/buildkit/client/testdata/compatibility/common/gzip-level-9/v10/config.json

## Purpose
This JSON fixture is an image configuration document for the BuildKit client compatibility suite. It belongs to the `common/gzip-level-9/v10` fixture, which represents the common fixture shared by exporter compatibility tests across image layout modes and the gzip compression level 9 compatibility baseline.

## Important Fields and Data Shape
- Platform: `linux/amd64` with created timestamp `2015-10-21T07:28:00Z`.
- Runtime config: env count `1`, command `['sh']`, working directory ``, entrypoint `None`, labels `None`.
- Root filesystem: type `layers`, diff ID count `4`, first diff ID `sha256:fe4922f0a3ca2aa70...`.
- History: `5` entries, including BuildKit exporter history comments for generated layers.
- Compatibility version directory: `v10`.

## Control Flow and Integration Role
The file is loaded as fixture data rather than executed. Compatibility tests compare generated exporter config JSON against this baseline to detect changes in platform fields, rootfs diff IDs, history ordering, Docker legacy fields, command/env defaults, and BuildKit-created history records.

## State and Persistence Behavior
The document is immutable testdata. It models persisted image configuration that would be stored as a content-addressed config blob and referenced by a manifest. Any byte-level change can alter the config digest and therefore the expected manifest descriptor.

## Dependencies and Integration Points
It integrates with image/OCI exporter compatibility tests under `client/testdata/compatibility`, the container image exporter metadata path, and manifest fixtures in adjacent directories. The config's diff IDs must align with layer descriptors in the corresponding manifest fixture.

## Risks and Edge Cases
The main risk is accidental fixture drift: changing timestamps, history text, Docker legacy fields, or diff ID ordering can break reproducibility and compatibility assertions. Variant-specific compression changes should not alter uncompressed diff IDs unless the actual filesystem content changes.

## Test Signals
A matching config indicates the exporter preserved expected image config schema, platform, rootfs, and history semantics for `gzip-level-9` under compatibility version `v10`. A mismatch usually signals exporter output drift rather than runtime code execution in this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/gzip-level-9/v10/config.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/gzip-level-9/v20/config.json -->
# sources/cloud-native/buildkit/client/testdata/compatibility/common/gzip-level-9/v20/config.json

## Purpose
This JSON fixture is an image configuration document for the BuildKit client compatibility suite. It belongs to the `common/gzip-level-9/v20` fixture, which represents the common fixture shared by exporter compatibility tests across image layout modes and the gzip compression level 9 compatibility baseline.

## Important Fields and Data Shape
- Platform: `linux/amd64` with created timestamp `2015-10-21T07:28:00Z`.
- Runtime config: env count `1`, command `['sh']`, working directory ``, entrypoint `None`, labels `None`.
- Root filesystem: type `layers`, diff ID count `4`, first diff ID `sha256:fe4922f0a3ca2aa70...`.
- History: `5` entries, including BuildKit exporter history comments for generated layers.
- Compatibility version directory: `v20`.

## Control Flow and Integration Role
The file is loaded as fixture data rather than executed. Compatibility tests compare generated exporter config JSON against this baseline to detect changes in platform fields, rootfs diff IDs, history ordering, Docker legacy fields, command/env defaults, and BuildKit-created history records.

## State and Persistence Behavior
The document is immutable testdata. It models persisted image configuration that would be stored as a content-addressed config blob and referenced by a manifest. Any byte-level change can alter the config digest and therefore the expected manifest descriptor.

## Dependencies and Integration Points
It integrates with image/OCI exporter compatibility tests under `client/testdata/compatibility`, the container image exporter metadata path, and manifest fixtures in adjacent directories. The config's diff IDs must align with layer descriptors in the corresponding manifest fixture.

## Risks and Edge Cases
The main risk is accidental fixture drift: changing timestamps, history text, Docker legacy fields, or diff ID ordering can break reproducibility and compatibility assertions. Variant-specific compression changes should not alter uncompressed diff IDs unless the actual filesystem content changes.

## Test Signals
A matching config indicates the exporter preserved expected image config schema, platform, rootfs, and history semantics for `gzip-level-9` under compatibility version `v20`. A mismatch usually signals exporter output drift rather than runtime code execution in this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/gzip-level-9/v20/config.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/gzip-level-9/v30/config.json -->
# sources/cloud-native/buildkit/client/testdata/compatibility/common/gzip-level-9/v30/config.json

## Purpose
This JSON fixture is an image configuration document for the BuildKit client compatibility suite. It belongs to the `common/gzip-level-9/v30` fixture, which represents the common fixture shared by exporter compatibility tests across image layout modes and the gzip compression level 9 compatibility baseline.

## Important Fields and Data Shape
- Platform: `linux/amd64` with created timestamp `2015-10-21T07:28:00Z`.
- Runtime config: env count `1`, command `['sh']`, working directory ``, entrypoint `None`, labels `None`.
- Root filesystem: type `layers`, diff ID count `4`, first diff ID `sha256:fe4922f0a3ca2aa70...`.
- History: `5` entries, including BuildKit exporter history comments for generated layers.
- Compatibility version directory: `v30`.

## Control Flow and Integration Role
The file is loaded as fixture data rather than executed. Compatibility tests compare generated exporter config JSON against this baseline to detect changes in platform fields, rootfs diff IDs, history ordering, Docker legacy fields, command/env defaults, and BuildKit-created history records.

## State and Persistence Behavior
The document is immutable testdata. It models persisted image configuration that would be stored as a content-addressed config blob and referenced by a manifest. Any byte-level change can alter the config digest and therefore the expected manifest descriptor.

## Dependencies and Integration Points
It integrates with image/OCI exporter compatibility tests under `client/testdata/compatibility`, the container image exporter metadata path, and manifest fixtures in adjacent directories. The config's diff IDs must align with layer descriptors in the corresponding manifest fixture.

## Risks and Edge Cases
The main risk is accidental fixture drift: changing timestamps, history text, Docker legacy fields, or diff ID ordering can break reproducibility and compatibility assertions. Variant-specific compression changes should not alter uncompressed diff IDs unless the actual filesystem content changes.

## Test Signals
A matching config indicates the exporter preserved expected image config schema, platform, rootfs, and history semantics for `gzip-level-9` under compatibility version `v30`. A mismatch usually signals exporter output drift rather than runtime code execution in this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/gzip-level-9/v30/config.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/gzip-level-9/v30/manifest.json -->
# sources/cloud-native/buildkit/client/testdata/compatibility/common/gzip-level-9/v30/manifest.json

## Purpose
This JSON fixture is an image manifest baseline for the BuildKit client compatibility suite. It belongs to `common/gzip-level-9/v30`, representing the common fixture shared by exporter compatibility tests across image layout modes and the gzip compression level 9 compatibility baseline.

## Important Fields and Data Shape
- Schema version: `2`.
- Manifest media type: `application/vnd.oci.image.manifest.v1+json`.
- Config descriptor media type: `application/vnd.oci.image.config.v1+json`, digest `sha256:1772fd0a3b45a62fc...`, size `2295`.
- Layer count: `4`.
- Layer media types: `application/vnd.oci.image.layer.v1.tar+gzip`.
- First layer digest/size: `sha256:86961eaccfc75a8ee...` / `2216704`.
- Manifest annotations present: `False`; layer descriptors with annotations: `4`.
- Compatibility version directory: `v30`.

## Control Flow and Integration Role
The file is fixture input for compatibility comparisons. Tests use it to verify that exporter output preserves expected manifest media types, config references, layer descriptors, annotations, compression choices, and compatibility-version behavior.

## State and Persistence Behavior
The manifest models persisted registry or OCI-layout metadata. It is content-addressable through its JSON bytes, and its config/layer descriptors must match adjacent config blobs and generated layer blobs. It has no runtime mutation path.

## Dependencies and Integration Points
It integrates with exporter compatibility tests, the image/OCI exporter, compression settings, OCI/Docker media-type conversion, provenance/annotation options, and adjacent `config.json` fixture files where present.

## Risks and Edge Cases
Risks include digest churn from non-deterministic timestamps or compression, wrong Docker-vs-OCI media types, dropped annotations, incorrect uncompressed/zstd media type selection, or layer order changes. For `manifest-annotation` fixtures, annotations are part of the behavior under test. For compression fixtures, descriptor sizes and digests are sensitive to compressor settings.

## Test Signals
A match means BuildKit emitted the expected manifest structure for `gzip-level-9` in `common` mode at compatibility version `v30`. A mismatch is a high-signal exporter compatibility regression because consumers use these descriptors to pull or load the image.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/gzip-level-9/v30/manifest.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/manifest-annotation/v10/config.json -->
# sources/cloud-native/buildkit/client/testdata/compatibility/common/manifest-annotation/v10/config.json

## Purpose
This JSON fixture is an image configuration document for the BuildKit client compatibility suite. It belongs to the `common/manifest-annotation/v10` fixture, which represents the common fixture shared by exporter compatibility tests across image layout modes and the manifest annotation preservation baseline.

## Important Fields and Data Shape
- Platform: `linux/amd64` with created timestamp `2015-10-21T07:28:00Z`.
- Runtime config: env count `1`, command `['sh']`, working directory ``, entrypoint `None`, labels `None`.
- Root filesystem: type `layers`, diff ID count `4`, first diff ID `sha256:fe4922f0a3ca2aa70...`.
- History: `5` entries, including BuildKit exporter history comments for generated layers.
- Compatibility version directory: `v10`.

## Control Flow and Integration Role
The file is loaded as fixture data rather than executed. Compatibility tests compare generated exporter config JSON against this baseline to detect changes in platform fields, rootfs diff IDs, history ordering, Docker legacy fields, command/env defaults, and BuildKit-created history records.

## State and Persistence Behavior
The document is immutable testdata. It models persisted image configuration that would be stored as a content-addressed config blob and referenced by a manifest. Any byte-level change can alter the config digest and therefore the expected manifest descriptor.

## Dependencies and Integration Points
It integrates with image/OCI exporter compatibility tests under `client/testdata/compatibility`, the container image exporter metadata path, and manifest fixtures in adjacent directories. The config's diff IDs must align with layer descriptors in the corresponding manifest fixture.

## Risks and Edge Cases
The main risk is accidental fixture drift: changing timestamps, history text, Docker legacy fields, or diff ID ordering can break reproducibility and compatibility assertions. Variant-specific compression changes should not alter uncompressed diff IDs unless the actual filesystem content changes.

## Test Signals
A matching config indicates the exporter preserved expected image config schema, platform, rootfs, and history semantics for `manifest-annotation` under compatibility version `v10`. A mismatch usually signals exporter output drift rather than runtime code execution in this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/manifest-annotation/v10/config.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/manifest-annotation/v20/config.json -->
# sources/cloud-native/buildkit/client/testdata/compatibility/common/manifest-annotation/v20/config.json

## Purpose
This JSON fixture is an image configuration document for the BuildKit client compatibility suite. It belongs to the `common/manifest-annotation/v20` fixture, which represents the common fixture shared by exporter compatibility tests across image layout modes and the manifest annotation preservation baseline.

## Important Fields and Data Shape
- Platform: `linux/amd64` with created timestamp `2015-10-21T07:28:00Z`.
- Runtime config: env count `1`, command `['sh']`, working directory ``, entrypoint `None`, labels `None`.
- Root filesystem: type `layers`, diff ID count `4`, first diff ID `sha256:fe4922f0a3ca2aa70...`.
- History: `5` entries, including BuildKit exporter history comments for generated layers.
- Compatibility version directory: `v20`.

## Control Flow and Integration Role
The file is loaded as fixture data rather than executed. Compatibility tests compare generated exporter config JSON against this baseline to detect changes in platform fields, rootfs diff IDs, history ordering, Docker legacy fields, command/env defaults, and BuildKit-created history records.

## State and Persistence Behavior
The document is immutable testdata. It models persisted image configuration that would be stored as a content-addressed config blob and referenced by a manifest. Any byte-level change can alter the config digest and therefore the expected manifest descriptor.

## Dependencies and Integration Points
It integrates with image/OCI exporter compatibility tests under `client/testdata/compatibility`, the container image exporter metadata path, and manifest fixtures in adjacent directories. The config's diff IDs must align with layer descriptors in the corresponding manifest fixture.

## Risks and Edge Cases
The main risk is accidental fixture drift: changing timestamps, history text, Docker legacy fields, or diff ID ordering can break reproducibility and compatibility assertions. Variant-specific compression changes should not alter uncompressed diff IDs unless the actual filesystem content changes.

## Test Signals
A matching config indicates the exporter preserved expected image config schema, platform, rootfs, and history semantics for `manifest-annotation` under compatibility version `v20`. A mismatch usually signals exporter output drift rather than runtime code execution in this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/manifest-annotation/v20/config.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/manifest-annotation/v30/config.json -->
# sources/cloud-native/buildkit/client/testdata/compatibility/common/manifest-annotation/v30/config.json

## Purpose
This JSON fixture is an image configuration document for the BuildKit client compatibility suite. It belongs to the `common/manifest-annotation/v30` fixture, which represents the common fixture shared by exporter compatibility tests across image layout modes and the manifest annotation preservation baseline.

## Important Fields and Data Shape
- Platform: `linux/amd64` with created timestamp `2015-10-21T07:28:00Z`.
- Runtime config: env count `1`, command `['sh']`, working directory ``, entrypoint `None`, labels `None`.
- Root filesystem: type `layers`, diff ID count `4`, first diff ID `sha256:fe4922f0a3ca2aa70...`.
- History: `5` entries, including BuildKit exporter history comments for generated layers.
- Compatibility version directory: `v30`.

## Control Flow and Integration Role
The file is loaded as fixture data rather than executed. Compatibility tests compare generated exporter config JSON against this baseline to detect changes in platform fields, rootfs diff IDs, history ordering, Docker legacy fields, command/env defaults, and BuildKit-created history records.

## State and Persistence Behavior
The document is immutable testdata. It models persisted image configuration that would be stored as a content-addressed config blob and referenced by a manifest. Any byte-level change can alter the config digest and therefore the expected manifest descriptor.

## Dependencies and Integration Points
It integrates with image/OCI exporter compatibility tests under `client/testdata/compatibility`, the container image exporter metadata path, and manifest fixtures in adjacent directories. The config's diff IDs must align with layer descriptors in the corresponding manifest fixture.

## Risks and Edge Cases
The main risk is accidental fixture drift: changing timestamps, history text, Docker legacy fields, or diff ID ordering can break reproducibility and compatibility assertions. Variant-specific compression changes should not alter uncompressed diff IDs unless the actual filesystem content changes.

## Test Signals
A matching config indicates the exporter preserved expected image config schema, platform, rootfs, and history semantics for `manifest-annotation` under compatibility version `v30`. A mismatch usually signals exporter output drift rather than runtime code execution in this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/manifest-annotation/v30/config.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/manifest-annotation/v30/manifest.json -->
# sources/cloud-native/buildkit/client/testdata/compatibility/common/manifest-annotation/v30/manifest.json

## Purpose
This JSON fixture is an image manifest baseline for the BuildKit client compatibility suite. It belongs to `common/manifest-annotation/v30`, representing the common fixture shared by exporter compatibility tests across image layout modes and the manifest annotation preservation baseline.

## Important Fields and Data Shape
- Schema version: `2`.
- Manifest media type: `application/vnd.oci.image.manifest.v1+json`.
- Config descriptor media type: `application/vnd.oci.image.config.v1+json`, digest `sha256:1772fd0a3b45a62fc...`, size `2295`.
- Layer count: `4`.
- Layer media types: `application/vnd.oci.image.layer.v1.tar+gzip`.
- First layer digest/size: `sha256:430ee4fa77d640d42...` / `2219886`.
- Manifest annotations present: `True`; layer descriptors with annotations: `4`.
- Compatibility version directory: `v30`.

## Control Flow and Integration Role
The file is fixture input for compatibility comparisons. Tests use it to verify that exporter output preserves expected manifest media types, config references, layer descriptors, annotations, compression choices, and compatibility-version behavior.

## State and Persistence Behavior
The manifest models persisted registry or OCI-layout metadata. It is content-addressable through its JSON bytes, and its config/layer descriptors must match adjacent config blobs and generated layer blobs. It has no runtime mutation path.

## Dependencies and Integration Points
It integrates with exporter compatibility tests, the image/OCI exporter, compression settings, OCI/Docker media-type conversion, provenance/annotation options, and adjacent `config.json` fixture files where present.

## Risks and Edge Cases
Risks include digest churn from non-deterministic timestamps or compression, wrong Docker-vs-OCI media types, dropped annotations, incorrect uncompressed/zstd media type selection, or layer order changes. For `manifest-annotation` fixtures, annotations are part of the behavior under test. For compression fixtures, descriptor sizes and digests are sensitive to compressor settings.

## Test Signals
A match means BuildKit emitted the expected manifest structure for `manifest-annotation` in `common` mode at compatibility version `v30`. A mismatch is a high-signal exporter compatibility regression because consumers use these descriptors to pull or load the image.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/manifest-annotation/v30/manifest.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/oci-mediatypes/v10/config.json -->
# sources/cloud-native/buildkit/client/testdata/compatibility/common/oci-mediatypes/v10/config.json

## Purpose
This JSON fixture is an image configuration document for the BuildKit client compatibility suite. It belongs to the `common/oci-mediatypes/v10` fixture, which represents the common fixture shared by exporter compatibility tests across image layout modes and the OCI media type baseline.

## Important Fields and Data Shape
- Platform: `linux/amd64` with created timestamp `2015-10-21T07:28:00Z`.
- Runtime config: env count `1`, command `['sh']`, working directory ``, entrypoint `None`, labels `None`.
- Root filesystem: type `layers`, diff ID count `4`, first diff ID `sha256:fe4922f0a3ca2aa70...`.
- History: `5` entries, including BuildKit exporter history comments for generated layers.
- Compatibility version directory: `v10`.

## Control Flow and Integration Role
The file is loaded as fixture data rather than executed. Compatibility tests compare generated exporter config JSON against this baseline to detect changes in platform fields, rootfs diff IDs, history ordering, Docker legacy fields, command/env defaults, and BuildKit-created history records.

## State and Persistence Behavior
The document is immutable testdata. It models persisted image configuration that would be stored as a content-addressed config blob and referenced by a manifest. Any byte-level change can alter the config digest and therefore the expected manifest descriptor.

## Dependencies and Integration Points
It integrates with image/OCI exporter compatibility tests under `client/testdata/compatibility`, the container image exporter metadata path, and manifest fixtures in adjacent directories. The config's diff IDs must align with layer descriptors in the corresponding manifest fixture.

## Risks and Edge Cases
The main risk is accidental fixture drift: changing timestamps, history text, Docker legacy fields, or diff ID ordering can break reproducibility and compatibility assertions. Variant-specific compression changes should not alter uncompressed diff IDs unless the actual filesystem content changes.

## Test Signals
A matching config indicates the exporter preserved expected image config schema, platform, rootfs, and history semantics for `oci-mediatypes` under compatibility version `v10`. A mismatch usually signals exporter output drift rather than runtime code execution in this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/oci-mediatypes/v10/config.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/oci-mediatypes/v10/manifest.json -->
# sources/cloud-native/buildkit/client/testdata/compatibility/common/oci-mediatypes/v10/manifest.json

## Purpose
This JSON fixture is an image manifest baseline for the BuildKit client compatibility suite. It belongs to `common/oci-mediatypes/v10`, representing the common fixture shared by exporter compatibility tests across image layout modes and the OCI media type baseline.

## Important Fields and Data Shape
- Schema version: `2`.
- Manifest media type: `application/vnd.oci.image.manifest.v1+json`.
- Config descriptor media type: `application/vnd.oci.image.config.v1+json`, digest `sha256:697cbcf20a7a20500...`, size `2295`.
- Layer count: `4`.
- Layer media types: `application/vnd.oci.image.layer.v1.tar+gzip`.
- First layer digest/size: `sha256:430ee4fa77d640d42...` / `2219886`.
- Manifest annotations present: `False`; layer descriptors with annotations: `4`.
- Compatibility version directory: `v10`.

## Control Flow and Integration Role
The file is fixture input for compatibility comparisons. Tests use it to verify that exporter output preserves expected manifest media types, config references, layer descriptors, annotations, compression choices, and compatibility-version behavior.

## State and Persistence Behavior
The manifest models persisted registry or OCI-layout metadata. It is content-addressable through its JSON bytes, and its config/layer descriptors must match adjacent config blobs and generated layer blobs. It has no runtime mutation path.

## Dependencies and Integration Points
It integrates with exporter compatibility tests, the image/OCI exporter, compression settings, OCI/Docker media-type conversion, provenance/annotation options, and adjacent `config.json` fixture files where present.

## Risks and Edge Cases
Risks include digest churn from non-deterministic timestamps or compression, wrong Docker-vs-OCI media types, dropped annotations, incorrect uncompressed/zstd media type selection, or layer order changes. For `manifest-annotation` fixtures, annotations are part of the behavior under test. For compression fixtures, descriptor sizes and digests are sensitive to compressor settings.

## Test Signals
A match means BuildKit emitted the expected manifest structure for `oci-mediatypes` in `common` mode at compatibility version `v10`. A mismatch is a high-signal exporter compatibility regression because consumers use these descriptors to pull or load the image.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/oci-mediatypes/v10/manifest.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/oci-mediatypes/v20/config.json -->
# sources/cloud-native/buildkit/client/testdata/compatibility/common/oci-mediatypes/v20/config.json

## Purpose
This JSON fixture is an image configuration document for the BuildKit client compatibility suite. It belongs to the `common/oci-mediatypes/v20` fixture, which represents the common fixture shared by exporter compatibility tests across image layout modes and the OCI media type baseline.

## Important Fields and Data Shape
- Platform: `linux/amd64` with created timestamp `2015-10-21T07:28:00Z`.
- Runtime config: env count `1`, command `['sh']`, working directory ``, entrypoint `None`, labels `None`.
- Root filesystem: type `layers`, diff ID count `4`, first diff ID `sha256:fe4922f0a3ca2aa70...`.
- History: `5` entries, including BuildKit exporter history comments for generated layers.
- Compatibility version directory: `v20`.

## Control Flow and Integration Role
The file is loaded as fixture data rather than executed. Compatibility tests compare generated exporter config JSON against this baseline to detect changes in platform fields, rootfs diff IDs, history ordering, Docker legacy fields, command/env defaults, and BuildKit-created history records.

## State and Persistence Behavior
The document is immutable testdata. It models persisted image configuration that would be stored as a content-addressed config blob and referenced by a manifest. Any byte-level change can alter the config digest and therefore the expected manifest descriptor.

## Dependencies and Integration Points
It integrates with image/OCI exporter compatibility tests under `client/testdata/compatibility`, the container image exporter metadata path, and manifest fixtures in adjacent directories. The config's diff IDs must align with layer descriptors in the corresponding manifest fixture.

## Risks and Edge Cases
The main risk is accidental fixture drift: changing timestamps, history text, Docker legacy fields, or diff ID ordering can break reproducibility and compatibility assertions. Variant-specific compression changes should not alter uncompressed diff IDs unless the actual filesystem content changes.

## Test Signals
A matching config indicates the exporter preserved expected image config schema, platform, rootfs, and history semantics for `oci-mediatypes` under compatibility version `v20`. A mismatch usually signals exporter output drift rather than runtime code execution in this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/oci-mediatypes/v20/config.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/oci-mediatypes/v20/manifest.json -->
# sources/cloud-native/buildkit/client/testdata/compatibility/common/oci-mediatypes/v20/manifest.json

## Purpose
This JSON fixture is an image manifest baseline for the BuildKit client compatibility suite. It belongs to `common/oci-mediatypes/v20`, representing the common fixture shared by exporter compatibility tests across image layout modes and the OCI media type baseline.

## Important Fields and Data Shape
- Schema version: `2`.
- Manifest media type: `application/vnd.oci.image.manifest.v1+json`.
- Config descriptor media type: `application/vnd.oci.image.config.v1+json`, digest `sha256:1772fd0a3b45a62fc...`, size `2295`.
- Layer count: `4`.
- Layer media types: `application/vnd.oci.image.layer.v1.tar+gzip`.
- First layer digest/size: `sha256:430ee4fa77d640d42...` / `2219886`.
- Manifest annotations present: `False`; layer descriptors with annotations: `4`.
- Compatibility version directory: `v20`.

## Control Flow and Integration Role
The file is fixture input for compatibility comparisons. Tests use it to verify that exporter output preserves expected manifest media types, config references, layer descriptors, annotations, compression choices, and compatibility-version behavior.

## State and Persistence Behavior
The manifest models persisted registry or OCI-layout metadata. It is content-addressable through its JSON bytes, and its config/layer descriptors must match adjacent config blobs and generated layer blobs. It has no runtime mutation path.

## Dependencies and Integration Points
It integrates with exporter compatibility tests, the image/OCI exporter, compression settings, OCI/Docker media-type conversion, provenance/annotation options, and adjacent `config.json` fixture files where present.

## Risks and Edge Cases
Risks include digest churn from non-deterministic timestamps or compression, wrong Docker-vs-OCI media types, dropped annotations, incorrect uncompressed/zstd media type selection, or layer order changes. For `manifest-annotation` fixtures, annotations are part of the behavior under test. For compression fixtures, descriptor sizes and digests are sensitive to compressor settings.

## Test Signals
A match means BuildKit emitted the expected manifest structure for `oci-mediatypes` in `common` mode at compatibility version `v20`. A mismatch is a high-signal exporter compatibility regression because consumers use these descriptors to pull or load the image.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/oci-mediatypes/v20/manifest.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/oci-mediatypes/v30/config.json -->
# sources/cloud-native/buildkit/client/testdata/compatibility/common/oci-mediatypes/v30/config.json

## Purpose
This JSON fixture is an image configuration document for the BuildKit client compatibility suite. It belongs to the `common/oci-mediatypes/v30` fixture, which represents the common fixture shared by exporter compatibility tests across image layout modes and the OCI media type baseline.

## Important Fields and Data Shape
- Platform: `linux/amd64` with created timestamp `2015-10-21T07:28:00Z`.
- Runtime config: env count `1`, command `['sh']`, working directory ``, entrypoint `None`, labels `None`.
- Root filesystem: type `layers`, diff ID count `4`, first diff ID `sha256:fe4922f0a3ca2aa70...`.
- History: `5` entries, including BuildKit exporter history comments for generated layers.
- Compatibility version directory: `v30`.

## Control Flow and Integration Role
The file is loaded as fixture data rather than executed. Compatibility tests compare generated exporter config JSON against this baseline to detect changes in platform fields, rootfs diff IDs, history ordering, Docker legacy fields, command/env defaults, and BuildKit-created history records.

## State and Persistence Behavior
The document is immutable testdata. It models persisted image configuration that would be stored as a content-addressed config blob and referenced by a manifest. Any byte-level change can alter the config digest and therefore the expected manifest descriptor.

## Dependencies and Integration Points
It integrates with image/OCI exporter compatibility tests under `client/testdata/compatibility`, the container image exporter metadata path, and manifest fixtures in adjacent directories. The config's diff IDs must align with layer descriptors in the corresponding manifest fixture.

## Risks and Edge Cases
The main risk is accidental fixture drift: changing timestamps, history text, Docker legacy fields, or diff ID ordering can break reproducibility and compatibility assertions. Variant-specific compression changes should not alter uncompressed diff IDs unless the actual filesystem content changes.

## Test Signals
A matching config indicates the exporter preserved expected image config schema, platform, rootfs, and history semantics for `oci-mediatypes` under compatibility version `v30`. A mismatch usually signals exporter output drift rather than runtime code execution in this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/oci-mediatypes/v30/config.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/oci-mediatypes/v30/manifest.json -->
# sources/cloud-native/buildkit/client/testdata/compatibility/common/oci-mediatypes/v30/manifest.json

## Purpose
This JSON fixture is an image manifest baseline for the BuildKit client compatibility suite. It belongs to `common/oci-mediatypes/v30`, representing the common fixture shared by exporter compatibility tests across image layout modes and the OCI media type baseline.

## Important Fields and Data Shape
- Schema version: `2`.
- Manifest media type: `application/vnd.oci.image.manifest.v1+json`.
- Config descriptor media type: `application/vnd.oci.image.config.v1+json`, digest `sha256:1772fd0a3b45a62fc...`, size `2295`.
- Layer count: `4`.
- Layer media types: `application/vnd.oci.image.layer.v1.tar+gzip`.
- First layer digest/size: `sha256:430ee4fa77d640d42...` / `2219886`.
- Manifest annotations present: `False`; layer descriptors with annotations: `4`.
- Compatibility version directory: `v30`.

## Control Flow and Integration Role
The file is fixture input for compatibility comparisons. Tests use it to verify that exporter output preserves expected manifest media types, config references, layer descriptors, annotations, compression choices, and compatibility-version behavior.

## State and Persistence Behavior
The manifest models persisted registry or OCI-layout metadata. It is content-addressable through its JSON bytes, and its config/layer descriptors must match adjacent config blobs and generated layer blobs. It has no runtime mutation path.

## Dependencies and Integration Points
It integrates with exporter compatibility tests, the image/OCI exporter, compression settings, OCI/Docker media-type conversion, provenance/annotation options, and adjacent `config.json` fixture files where present.

## Risks and Edge Cases
Risks include digest churn from non-deterministic timestamps or compression, wrong Docker-vs-OCI media types, dropped annotations, incorrect uncompressed/zstd media type selection, or layer order changes. For `manifest-annotation` fixtures, annotations are part of the behavior under test. For compression fixtures, descriptor sizes and digests are sensitive to compressor settings.

## Test Signals
A match means BuildKit emitted the expected manifest structure for `oci-mediatypes` in `common` mode at compatibility version `v30`. A mismatch is a high-signal exporter compatibility regression because consumers use these descriptors to pull or load the image.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/oci-mediatypes/v30/manifest.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/provenance-attestation/v10/config.json -->
# sources/cloud-native/buildkit/client/testdata/compatibility/common/provenance-attestation/v10/config.json

## Purpose
This JSON fixture is an image configuration document for the BuildKit client compatibility suite. It belongs to the `common/provenance-attestation/v10` fixture, which represents the common fixture shared by exporter compatibility tests across image layout modes and the provenance attestation compatibility baseline.

## Important Fields and Data Shape
- Platform: `linux/amd64` with created timestamp `2015-10-21T07:28:00Z`.
- Runtime config: env count `1`, command `['sh']`, working directory ``, entrypoint `None`, labels `None`.
- Root filesystem: type `layers`, diff ID count `4`, first diff ID `sha256:fe4922f0a3ca2aa70...`.
- History: `5` entries, including BuildKit exporter history comments for generated layers.
- Compatibility version directory: `v10`.

## Control Flow and Integration Role
The file is loaded as fixture data rather than executed. Compatibility tests compare generated exporter config JSON against this baseline to detect changes in platform fields, rootfs diff IDs, history ordering, Docker legacy fields, command/env defaults, and BuildKit-created history records.

## State and Persistence Behavior
The document is immutable testdata. It models persisted image configuration that would be stored as a content-addressed config blob and referenced by a manifest. Any byte-level change can alter the config digest and therefore the expected manifest descriptor.

## Dependencies and Integration Points
It integrates with image/OCI exporter compatibility tests under `client/testdata/compatibility`, the container image exporter metadata path, and manifest fixtures in adjacent directories. The config's diff IDs must align with layer descriptors in the corresponding manifest fixture.

## Risks and Edge Cases
The main risk is accidental fixture drift: changing timestamps, history text, Docker legacy fields, or diff ID ordering can break reproducibility and compatibility assertions. Variant-specific compression changes should not alter uncompressed diff IDs unless the actual filesystem content changes.

## Test Signals
A matching config indicates the exporter preserved expected image config schema, platform, rootfs, and history semantics for `provenance-attestation` under compatibility version `v10`. A mismatch usually signals exporter output drift rather than runtime code execution in this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/provenance-attestation/v10/config.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/provenance-attestation/v10/manifest.json -->
# sources/cloud-native/buildkit/client/testdata/compatibility/common/provenance-attestation/v10/manifest.json

## Purpose
This JSON fixture is an image manifest baseline for the BuildKit client compatibility suite. It belongs to `common/provenance-attestation/v10`, representing the common fixture shared by exporter compatibility tests across image layout modes and the provenance attestation compatibility baseline.

## Important Fields and Data Shape
- Schema version: `2`.
- Manifest media type: `application/vnd.oci.image.manifest.v1+json`.
- Config descriptor media type: `application/vnd.oci.image.config.v1+json`, digest `sha256:697cbcf20a7a20500...`, size `2295`.
- Layer count: `4`.
- Layer media types: `application/vnd.oci.image.layer.v1.tar+gzip`.
- First layer digest/size: `sha256:430ee4fa77d640d42...` / `2219886`.
- Manifest annotations present: `False`; layer descriptors with annotations: `4`.
- Compatibility version directory: `v10`.

## Control Flow and Integration Role
The file is fixture input for compatibility comparisons. Tests use it to verify that exporter output preserves expected manifest media types, config references, layer descriptors, annotations, compression choices, and compatibility-version behavior.

## State and Persistence Behavior
The manifest models persisted registry or OCI-layout metadata. It is content-addressable through its JSON bytes, and its config/layer descriptors must match adjacent config blobs and generated layer blobs. It has no runtime mutation path.

## Dependencies and Integration Points
It integrates with exporter compatibility tests, the image/OCI exporter, compression settings, OCI/Docker media-type conversion, provenance/annotation options, and adjacent `config.json` fixture files where present.

## Risks and Edge Cases
Risks include digest churn from non-deterministic timestamps or compression, wrong Docker-vs-OCI media types, dropped annotations, incorrect uncompressed/zstd media type selection, or layer order changes. For `manifest-annotation` fixtures, annotations are part of the behavior under test. For compression fixtures, descriptor sizes and digests are sensitive to compressor settings.

## Test Signals
A match means BuildKit emitted the expected manifest structure for `provenance-attestation` in `common` mode at compatibility version `v10`. A mismatch is a high-signal exporter compatibility regression because consumers use these descriptors to pull or load the image.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/provenance-attestation/v10/manifest.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/provenance-attestation/v20/config.json -->
# sources/cloud-native/buildkit/client/testdata/compatibility/common/provenance-attestation/v20/config.json

## Purpose
This JSON fixture is an image configuration document for the BuildKit client compatibility suite. It belongs to the `common/provenance-attestation/v20` fixture, which represents the common fixture shared by exporter compatibility tests across image layout modes and the provenance attestation compatibility baseline.

## Important Fields and Data Shape
- Platform: `linux/amd64` with created timestamp `2015-10-21T07:28:00Z`.
- Runtime config: env count `1`, command `['sh']`, working directory ``, entrypoint `None`, labels `None`.
- Root filesystem: type `layers`, diff ID count `4`, first diff ID `sha256:fe4922f0a3ca2aa70...`.
- History: `5` entries, including BuildKit exporter history comments for generated layers.
- Compatibility version directory: `v20`.

## Control Flow and Integration Role
The file is loaded as fixture data rather than executed. Compatibility tests compare generated exporter config JSON against this baseline to detect changes in platform fields, rootfs diff IDs, history ordering, Docker legacy fields, command/env defaults, and BuildKit-created history records.

## State and Persistence Behavior
The document is immutable testdata. It models persisted image configuration that would be stored as a content-addressed config blob and referenced by a manifest. Any byte-level change can alter the config digest and therefore the expected manifest descriptor.

## Dependencies and Integration Points
It integrates with image/OCI exporter compatibility tests under `client/testdata/compatibility`, the container image exporter metadata path, and manifest fixtures in adjacent directories. The config's diff IDs must align with layer descriptors in the corresponding manifest fixture.

## Risks and Edge Cases
The main risk is accidental fixture drift: changing timestamps, history text, Docker legacy fields, or diff ID ordering can break reproducibility and compatibility assertions. Variant-specific compression changes should not alter uncompressed diff IDs unless the actual filesystem content changes.

## Test Signals
A matching config indicates the exporter preserved expected image config schema, platform, rootfs, and history semantics for `provenance-attestation` under compatibility version `v20`. A mismatch usually signals exporter output drift rather than runtime code execution in this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/provenance-attestation/v20/config.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/provenance-attestation/v20/manifest.json -->
# sources/cloud-native/buildkit/client/testdata/compatibility/common/provenance-attestation/v20/manifest.json

## Purpose
This JSON fixture is an image manifest baseline for the BuildKit client compatibility suite. It belongs to `common/provenance-attestation/v20`, representing the common fixture shared by exporter compatibility tests across image layout modes and the provenance attestation compatibility baseline.

## Important Fields and Data Shape
- Schema version: `2`.
- Manifest media type: `application/vnd.oci.image.manifest.v1+json`.
- Config descriptor media type: `application/vnd.oci.image.config.v1+json`, digest `sha256:1772fd0a3b45a62fc...`, size `2295`.
- Layer count: `4`.
- Layer media types: `application/vnd.oci.image.layer.v1.tar+gzip`.
- First layer digest/size: `sha256:430ee4fa77d640d42...` / `2219886`.
- Manifest annotations present: `False`; layer descriptors with annotations: `4`.
- Compatibility version directory: `v20`.

## Control Flow and Integration Role
The file is fixture input for compatibility comparisons. Tests use it to verify that exporter output preserves expected manifest media types, config references, layer descriptors, annotations, compression choices, and compatibility-version behavior.

## State and Persistence Behavior
The manifest models persisted registry or OCI-layout metadata. It is content-addressable through its JSON bytes, and its config/layer descriptors must match adjacent config blobs and generated layer blobs. It has no runtime mutation path.

## Dependencies and Integration Points
It integrates with exporter compatibility tests, the image/OCI exporter, compression settings, OCI/Docker media-type conversion, provenance/annotation options, and adjacent `config.json` fixture files where present.

## Risks and Edge Cases
Risks include digest churn from non-deterministic timestamps or compression, wrong Docker-vs-OCI media types, dropped annotations, incorrect uncompressed/zstd media type selection, or layer order changes. For `manifest-annotation` fixtures, annotations are part of the behavior under test. For compression fixtures, descriptor sizes and digests are sensitive to compressor settings.

## Test Signals
A match means BuildKit emitted the expected manifest structure for `provenance-attestation` in `common` mode at compatibility version `v20`. A mismatch is a high-signal exporter compatibility regression because consumers use these descriptors to pull or load the image.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/provenance-attestation/v20/manifest.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/provenance-attestation/v30/config.json -->
# sources/cloud-native/buildkit/client/testdata/compatibility/common/provenance-attestation/v30/config.json

## Purpose
This JSON fixture is an image configuration document for the BuildKit client compatibility suite. It belongs to the `common/provenance-attestation/v30` fixture, which represents the common fixture shared by exporter compatibility tests across image layout modes and the provenance attestation compatibility baseline.

## Important Fields and Data Shape
- Platform: `linux/amd64` with created timestamp `2015-10-21T07:28:00Z`.
- Runtime config: env count `1`, command `['sh']`, working directory ``, entrypoint `None`, labels `None`.
- Root filesystem: type `layers`, diff ID count `4`, first diff ID `sha256:fe4922f0a3ca2aa70...`.
- History: `5` entries, including BuildKit exporter history comments for generated layers.
- Compatibility version directory: `v30`.

## Control Flow and Integration Role
The file is loaded as fixture data rather than executed. Compatibility tests compare generated exporter config JSON against this baseline to detect changes in platform fields, rootfs diff IDs, history ordering, Docker legacy fields, command/env defaults, and BuildKit-created history records.

## State and Persistence Behavior
The document is immutable testdata. It models persisted image configuration that would be stored as a content-addressed config blob and referenced by a manifest. Any byte-level change can alter the config digest and therefore the expected manifest descriptor.

## Dependencies and Integration Points
It integrates with image/OCI exporter compatibility tests under `client/testdata/compatibility`, the container image exporter metadata path, and manifest fixtures in adjacent directories. The config's diff IDs must align with layer descriptors in the corresponding manifest fixture.

## Risks and Edge Cases
The main risk is accidental fixture drift: changing timestamps, history text, Docker legacy fields, or diff ID ordering can break reproducibility and compatibility assertions. Variant-specific compression changes should not alter uncompressed diff IDs unless the actual filesystem content changes.

## Test Signals
A matching config indicates the exporter preserved expected image config schema, platform, rootfs, and history semantics for `provenance-attestation` under compatibility version `v30`. A mismatch usually signals exporter output drift rather than runtime code execution in this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/provenance-attestation/v30/config.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/provenance-attestation/v30/manifest.json -->
# sources/cloud-native/buildkit/client/testdata/compatibility/common/provenance-attestation/v30/manifest.json

## Purpose
This JSON fixture is an image manifest baseline for the BuildKit client compatibility suite. It belongs to `common/provenance-attestation/v30`, representing the common fixture shared by exporter compatibility tests across image layout modes and the provenance attestation compatibility baseline.

## Important Fields and Data Shape
- Schema version: `2`.
- Manifest media type: `application/vnd.oci.image.manifest.v1+json`.
- Config descriptor media type: `application/vnd.oci.image.config.v1+json`, digest `sha256:1772fd0a3b45a62fc...`, size `2295`.
- Layer count: `4`.
- Layer media types: `application/vnd.oci.image.layer.v1.tar+gzip`.
- First layer digest/size: `sha256:430ee4fa77d640d42...` / `2219886`.
- Manifest annotations present: `False`; layer descriptors with annotations: `4`.
- Compatibility version directory: `v30`.

## Control Flow and Integration Role
The file is fixture input for compatibility comparisons. Tests use it to verify that exporter output preserves expected manifest media types, config references, layer descriptors, annotations, compression choices, and compatibility-version behavior.

## State and Persistence Behavior
The manifest models persisted registry or OCI-layout metadata. It is content-addressable through its JSON bytes, and its config/layer descriptors must match adjacent config blobs and generated layer blobs. It has no runtime mutation path.

## Dependencies and Integration Points
It integrates with exporter compatibility tests, the image/OCI exporter, compression settings, OCI/Docker media-type conversion, provenance/annotation options, and adjacent `config.json` fixture files where present.

## Risks and Edge Cases
Risks include digest churn from non-deterministic timestamps or compression, wrong Docker-vs-OCI media types, dropped annotations, incorrect uncompressed/zstd media type selection, or layer order changes. For `manifest-annotation` fixtures, annotations are part of the behavior under test. For compression fixtures, descriptor sizes and digests are sensitive to compressor settings.

## Test Signals
A match means BuildKit emitted the expected manifest structure for `provenance-attestation` in `common` mode at compatibility version `v30`. A mismatch is a high-signal exporter compatibility regression because consumers use these descriptors to pull or load the image.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/provenance-attestation/v30/manifest.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/uncompressed/v10/config.json -->
# sources/cloud-native/buildkit/client/testdata/compatibility/common/uncompressed/v10/config.json

## Purpose
This JSON fixture is an image configuration document for the BuildKit client compatibility suite. It belongs to the `common/uncompressed/v10` fixture, which represents the common fixture shared by exporter compatibility tests across image layout modes and the uncompressed layer media type baseline.

## Important Fields and Data Shape
- Platform: `linux/amd64` with created timestamp `2015-10-21T07:28:00Z`.
- Runtime config: env count `1`, command `['sh']`, working directory ``, entrypoint `None`, labels `None`.
- Root filesystem: type `layers`, diff ID count `4`, first diff ID `sha256:fe4922f0a3ca2aa70...`.
- History: `5` entries, including BuildKit exporter history comments for generated layers.
- Compatibility version directory: `v10`.

## Control Flow and Integration Role
The file is loaded as fixture data rather than executed. Compatibility tests compare generated exporter config JSON against this baseline to detect changes in platform fields, rootfs diff IDs, history ordering, Docker legacy fields, command/env defaults, and BuildKit-created history records.

## State and Persistence Behavior
The document is immutable testdata. It models persisted image configuration that would be stored as a content-addressed config blob and referenced by a manifest. Any byte-level change can alter the config digest and therefore the expected manifest descriptor.

## Dependencies and Integration Points
It integrates with image/OCI exporter compatibility tests under `client/testdata/compatibility`, the container image exporter metadata path, and manifest fixtures in adjacent directories. The config's diff IDs must align with layer descriptors in the corresponding manifest fixture.

## Risks and Edge Cases
The main risk is accidental fixture drift: changing timestamps, history text, Docker legacy fields, or diff ID ordering can break reproducibility and compatibility assertions. Variant-specific compression changes should not alter uncompressed diff IDs unless the actual filesystem content changes.

## Test Signals
A matching config indicates the exporter preserved expected image config schema, platform, rootfs, and history semantics for `uncompressed` under compatibility version `v10`. A mismatch usually signals exporter output drift rather than runtime code execution in this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/uncompressed/v10/config.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/uncompressed/v20/config.json -->
# sources/cloud-native/buildkit/client/testdata/compatibility/common/uncompressed/v20/config.json

## Purpose
This JSON fixture is an image configuration document for the BuildKit client compatibility suite. It belongs to the `common/uncompressed/v20` fixture, which represents the common fixture shared by exporter compatibility tests across image layout modes and the uncompressed layer media type baseline.

## Important Fields and Data Shape
- Platform: `linux/amd64` with created timestamp `2015-10-21T07:28:00Z`.
- Runtime config: env count `1`, command `['sh']`, working directory ``, entrypoint `None`, labels `None`.
- Root filesystem: type `layers`, diff ID count `4`, first diff ID `sha256:fe4922f0a3ca2aa70...`.
- History: `5` entries, including BuildKit exporter history comments for generated layers.
- Compatibility version directory: `v20`.

## Control Flow and Integration Role
The file is loaded as fixture data rather than executed. Compatibility tests compare generated exporter config JSON against this baseline to detect changes in platform fields, rootfs diff IDs, history ordering, Docker legacy fields, command/env defaults, and BuildKit-created history records.

## State and Persistence Behavior
The document is immutable testdata. It models persisted image configuration that would be stored as a content-addressed config blob and referenced by a manifest. Any byte-level change can alter the config digest and therefore the expected manifest descriptor.

## Dependencies and Integration Points
It integrates with image/OCI exporter compatibility tests under `client/testdata/compatibility`, the container image exporter metadata path, and manifest fixtures in adjacent directories. The config's diff IDs must align with layer descriptors in the corresponding manifest fixture.

## Risks and Edge Cases
The main risk is accidental fixture drift: changing timestamps, history text, Docker legacy fields, or diff ID ordering can break reproducibility and compatibility assertions. Variant-specific compression changes should not alter uncompressed diff IDs unless the actual filesystem content changes.

## Test Signals
A matching config indicates the exporter preserved expected image config schema, platform, rootfs, and history semantics for `uncompressed` under compatibility version `v20`. A mismatch usually signals exporter output drift rather than runtime code execution in this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/uncompressed/v20/config.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/uncompressed/v30/config.json -->
# sources/cloud-native/buildkit/client/testdata/compatibility/common/uncompressed/v30/config.json

## Purpose
This JSON fixture is an image configuration document for the BuildKit client compatibility suite. It belongs to the `common/uncompressed/v30` fixture, which represents the common fixture shared by exporter compatibility tests across image layout modes and the uncompressed layer media type baseline.

## Important Fields and Data Shape
- Platform: `linux/amd64` with created timestamp `2015-10-21T07:28:00Z`.
- Runtime config: env count `1`, command `['sh']`, working directory ``, entrypoint `None`, labels `None`.
- Root filesystem: type `layers`, diff ID count `4`, first diff ID `sha256:fe4922f0a3ca2aa70...`.
- History: `5` entries, including BuildKit exporter history comments for generated layers.
- Compatibility version directory: `v30`.

## Control Flow and Integration Role
The file is loaded as fixture data rather than executed. Compatibility tests compare generated exporter config JSON against this baseline to detect changes in platform fields, rootfs diff IDs, history ordering, Docker legacy fields, command/env defaults, and BuildKit-created history records.

## State and Persistence Behavior
The document is immutable testdata. It models persisted image configuration that would be stored as a content-addressed config blob and referenced by a manifest. Any byte-level change can alter the config digest and therefore the expected manifest descriptor.

## Dependencies and Integration Points
It integrates with image/OCI exporter compatibility tests under `client/testdata/compatibility`, the container image exporter metadata path, and manifest fixtures in adjacent directories. The config's diff IDs must align with layer descriptors in the corresponding manifest fixture.

## Risks and Edge Cases
The main risk is accidental fixture drift: changing timestamps, history text, Docker legacy fields, or diff ID ordering can break reproducibility and compatibility assertions. Variant-specific compression changes should not alter uncompressed diff IDs unless the actual filesystem content changes.

## Test Signals
A matching config indicates the exporter preserved expected image config schema, platform, rootfs, and history semantics for `uncompressed` under compatibility version `v30`. A mismatch usually signals exporter output drift rather than runtime code execution in this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/uncompressed/v30/config.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/uncompressed/v30/manifest.json -->
# sources/cloud-native/buildkit/client/testdata/compatibility/common/uncompressed/v30/manifest.json

## Purpose
This JSON fixture is an image manifest baseline for the BuildKit client compatibility suite. It belongs to `common/uncompressed/v30`, representing the common fixture shared by exporter compatibility tests across image layout modes and the uncompressed layer media type baseline.

## Important Fields and Data Shape
- Schema version: `2`.
- Manifest media type: `application/vnd.oci.image.manifest.v1+json`.
- Config descriptor media type: `application/vnd.oci.image.config.v1+json`, digest `sha256:1772fd0a3b45a62fc...`, size `2295`.
- Layer count: `4`.
- Layer media types: `application/vnd.oci.image.layer.v1.tar`.
- First layer digest/size: `sha256:fe4922f0a3ca2aa70...` / `4492288`.
- Manifest annotations present: `False`; layer descriptors with annotations: `4`.
- Compatibility version directory: `v30`.

## Control Flow and Integration Role
The file is fixture input for compatibility comparisons. Tests use it to verify that exporter output preserves expected manifest media types, config references, layer descriptors, annotations, compression choices, and compatibility-version behavior.

## State and Persistence Behavior
The manifest models persisted registry or OCI-layout metadata. It is content-addressable through its JSON bytes, and its config/layer descriptors must match adjacent config blobs and generated layer blobs. It has no runtime mutation path.

## Dependencies and Integration Points
It integrates with exporter compatibility tests, the image/OCI exporter, compression settings, OCI/Docker media-type conversion, provenance/annotation options, and adjacent `config.json` fixture files where present.

## Risks and Edge Cases
Risks include digest churn from non-deterministic timestamps or compression, wrong Docker-vs-OCI media types, dropped annotations, incorrect uncompressed/zstd media type selection, or layer order changes. For `manifest-annotation` fixtures, annotations are part of the behavior under test. For compression fixtures, descriptor sizes and digests are sensitive to compressor settings.

## Test Signals
A match means BuildKit emitted the expected manifest structure for `uncompressed` in `common` mode at compatibility version `v30`. A mismatch is a high-signal exporter compatibility regression because consumers use these descriptors to pull or load the image.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/uncompressed/v30/manifest.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/zstd-oci-types/v10/config.json -->
# sources/cloud-native/buildkit/client/testdata/compatibility/common/zstd-oci-types/v10/config.json

## Purpose
This JSON fixture is an image configuration document for the BuildKit client compatibility suite. It belongs to the `common/zstd-oci-types/v10` fixture, which represents the common fixture shared by exporter compatibility tests across image layout modes and the zstd-compressed OCI layer media type baseline.

## Important Fields and Data Shape
- Platform: `linux/amd64` with created timestamp `2015-10-21T07:28:00Z`.
- Runtime config: env count `1`, command `['sh']`, working directory ``, entrypoint `None`, labels `None`.
- Root filesystem: type `layers`, diff ID count `4`, first diff ID `sha256:fe4922f0a3ca2aa70...`.
- History: `5` entries, including BuildKit exporter history comments for generated layers.
- Compatibility version directory: `v10`.

## Control Flow and Integration Role
The file is loaded as fixture data rather than executed. Compatibility tests compare generated exporter config JSON against this baseline to detect changes in platform fields, rootfs diff IDs, history ordering, Docker legacy fields, command/env defaults, and BuildKit-created history records.

## State and Persistence Behavior
The document is immutable testdata. It models persisted image configuration that would be stored as a content-addressed config blob and referenced by a manifest. Any byte-level change can alter the config digest and therefore the expected manifest descriptor.

## Dependencies and Integration Points
It integrates with image/OCI exporter compatibility tests under `client/testdata/compatibility`, the container image exporter metadata path, and manifest fixtures in adjacent directories. The config's diff IDs must align with layer descriptors in the corresponding manifest fixture.

## Risks and Edge Cases
The main risk is accidental fixture drift: changing timestamps, history text, Docker legacy fields, or diff ID ordering can break reproducibility and compatibility assertions. Variant-specific compression changes should not alter uncompressed diff IDs unless the actual filesystem content changes.

## Test Signals
A matching config indicates the exporter preserved expected image config schema, platform, rootfs, and history semantics for `zstd-oci-types` under compatibility version `v10`. A mismatch usually signals exporter output drift rather than runtime code execution in this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/zstd-oci-types/v10/config.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/zstd-oci-types/v10/manifest.json -->
# sources/cloud-native/buildkit/client/testdata/compatibility/common/zstd-oci-types/v10/manifest.json

## Purpose
This JSON fixture is an image manifest baseline for the BuildKit client compatibility suite. It belongs to `common/zstd-oci-types/v10`, representing the common fixture shared by exporter compatibility tests across image layout modes and the zstd-compressed OCI layer media type baseline.

## Important Fields and Data Shape
- Schema version: `2`.
- Manifest media type: `application/vnd.oci.image.manifest.v1+json`.
- Config descriptor media type: `application/vnd.oci.image.config.v1+json`, digest `sha256:697cbcf20a7a20500...`, size `2295`.
- Layer count: `4`.
- Layer media types: `application/vnd.oci.image.layer.v1.tar+zstd`.
- First layer digest/size: `sha256:d6212bbd58032e7ff...` / `1999152`.
- Manifest annotations present: `False`; layer descriptors with annotations: `4`.
- Compatibility version directory: `v10`.

## Control Flow and Integration Role
The file is fixture input for compatibility comparisons. Tests use it to verify that exporter output preserves expected manifest media types, config references, layer descriptors, annotations, compression choices, and compatibility-version behavior.

## State and Persistence Behavior
The manifest models persisted registry or OCI-layout metadata. It is content-addressable through its JSON bytes, and its config/layer descriptors must match adjacent config blobs and generated layer blobs. It has no runtime mutation path.

## Dependencies and Integration Points
It integrates with exporter compatibility tests, the image/OCI exporter, compression settings, OCI/Docker media-type conversion, provenance/annotation options, and adjacent `config.json` fixture files where present.

## Risks and Edge Cases
Risks include digest churn from non-deterministic timestamps or compression, wrong Docker-vs-OCI media types, dropped annotations, incorrect uncompressed/zstd media type selection, or layer order changes. For `manifest-annotation` fixtures, annotations are part of the behavior under test. For compression fixtures, descriptor sizes and digests are sensitive to compressor settings.

## Test Signals
A match means BuildKit emitted the expected manifest structure for `zstd-oci-types` in `common` mode at compatibility version `v10`. A mismatch is a high-signal exporter compatibility regression because consumers use these descriptors to pull or load the image.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/zstd-oci-types/v10/manifest.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/zstd-oci-types/v20/config.json -->
# sources/cloud-native/buildkit/client/testdata/compatibility/common/zstd-oci-types/v20/config.json

## Purpose
This JSON fixture is an image configuration document for the BuildKit client compatibility suite. It belongs to the `common/zstd-oci-types/v20` fixture, which represents the common fixture shared by exporter compatibility tests across image layout modes and the zstd-compressed OCI layer media type baseline.

## Important Fields and Data Shape
- Platform: `linux/amd64` with created timestamp `2015-10-21T07:28:00Z`.
- Runtime config: env count `1`, command `['sh']`, working directory ``, entrypoint `None`, labels `None`.
- Root filesystem: type `layers`, diff ID count `4`, first diff ID `sha256:fe4922f0a3ca2aa70...`.
- History: `5` entries, including BuildKit exporter history comments for generated layers.
- Compatibility version directory: `v20`.

## Control Flow and Integration Role
The file is loaded as fixture data rather than executed. Compatibility tests compare generated exporter config JSON against this baseline to detect changes in platform fields, rootfs diff IDs, history ordering, Docker legacy fields, command/env defaults, and BuildKit-created history records.

## State and Persistence Behavior
The document is immutable testdata. It models persisted image configuration that would be stored as a content-addressed config blob and referenced by a manifest. Any byte-level change can alter the config digest and therefore the expected manifest descriptor.

## Dependencies and Integration Points
It integrates with image/OCI exporter compatibility tests under `client/testdata/compatibility`, the container image exporter metadata path, and manifest fixtures in adjacent directories. The config's diff IDs must align with layer descriptors in the corresponding manifest fixture.

## Risks and Edge Cases
The main risk is accidental fixture drift: changing timestamps, history text, Docker legacy fields, or diff ID ordering can break reproducibility and compatibility assertions. Variant-specific compression changes should not alter uncompressed diff IDs unless the actual filesystem content changes.

## Test Signals
A matching config indicates the exporter preserved expected image config schema, platform, rootfs, and history semantics for `zstd-oci-types` under compatibility version `v20`. A mismatch usually signals exporter output drift rather than runtime code execution in this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/zstd-oci-types/v20/config.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/zstd-oci-types/v20/manifest.json -->
# sources/cloud-native/buildkit/client/testdata/compatibility/common/zstd-oci-types/v20/manifest.json

## Purpose
This JSON fixture is an image manifest baseline for the BuildKit client compatibility suite. It belongs to `common/zstd-oci-types/v20`, representing the common fixture shared by exporter compatibility tests across image layout modes and the zstd-compressed OCI layer media type baseline.

## Important Fields and Data Shape
- Schema version: `2`.
- Manifest media type: `application/vnd.oci.image.manifest.v1+json`.
- Config descriptor media type: `application/vnd.oci.image.config.v1+json`, digest `sha256:1772fd0a3b45a62fc...`, size `2295`.
- Layer count: `4`.
- Layer media types: `application/vnd.oci.image.layer.v1.tar+zstd`.
- First layer digest/size: `sha256:732ad1c88bfbc8aa6...` / `1997110`.
- Manifest annotations present: `False`; layer descriptors with annotations: `4`.
- Compatibility version directory: `v20`.

## Control Flow and Integration Role
The file is fixture input for compatibility comparisons. Tests use it to verify that exporter output preserves expected manifest media types, config references, layer descriptors, annotations, compression choices, and compatibility-version behavior.

## State and Persistence Behavior
The manifest models persisted registry or OCI-layout metadata. It is content-addressable through its JSON bytes, and its config/layer descriptors must match adjacent config blobs and generated layer blobs. It has no runtime mutation path.

## Dependencies and Integration Points
It integrates with exporter compatibility tests, the image/OCI exporter, compression settings, OCI/Docker media-type conversion, provenance/annotation options, and adjacent `config.json` fixture files where present.

## Risks and Edge Cases
Risks include digest churn from non-deterministic timestamps or compression, wrong Docker-vs-OCI media types, dropped annotations, incorrect uncompressed/zstd media type selection, or layer order changes. For `manifest-annotation` fixtures, annotations are part of the behavior under test. For compression fixtures, descriptor sizes and digests are sensitive to compressor settings.

## Test Signals
A match means BuildKit emitted the expected manifest structure for `zstd-oci-types` in `common` mode at compatibility version `v20`. A mismatch is a high-signal exporter compatibility regression because consumers use these descriptors to pull or load the image.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/zstd-oci-types/v20/manifest.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/zstd-oci-types/v30/config.json -->
# sources/cloud-native/buildkit/client/testdata/compatibility/common/zstd-oci-types/v30/config.json

## Purpose
This JSON fixture is an image configuration document for the BuildKit client compatibility suite. It belongs to the `common/zstd-oci-types/v30` fixture, which represents the common fixture shared by exporter compatibility tests across image layout modes and the zstd-compressed OCI layer media type baseline.

## Important Fields and Data Shape
- Platform: `linux/amd64` with created timestamp `2015-10-21T07:28:00Z`.
- Runtime config: env count `1`, command `['sh']`, working directory ``, entrypoint `None`, labels `None`.
- Root filesystem: type `layers`, diff ID count `4`, first diff ID `sha256:fe4922f0a3ca2aa70...`.
- History: `5` entries, including BuildKit exporter history comments for generated layers.
- Compatibility version directory: `v30`.

## Control Flow and Integration Role
The file is loaded as fixture data rather than executed. Compatibility tests compare generated exporter config JSON against this baseline to detect changes in platform fields, rootfs diff IDs, history ordering, Docker legacy fields, command/env defaults, and BuildKit-created history records.

## State and Persistence Behavior
The document is immutable testdata. It models persisted image configuration that would be stored as a content-addressed config blob and referenced by a manifest. Any byte-level change can alter the config digest and therefore the expected manifest descriptor.

## Dependencies and Integration Points
It integrates with image/OCI exporter compatibility tests under `client/testdata/compatibility`, the container image exporter metadata path, and manifest fixtures in adjacent directories. The config's diff IDs must align with layer descriptors in the corresponding manifest fixture.

## Risks and Edge Cases
The main risk is accidental fixture drift: changing timestamps, history text, Docker legacy fields, or diff ID ordering can break reproducibility and compatibility assertions. Variant-specific compression changes should not alter uncompressed diff IDs unless the actual filesystem content changes.

## Test Signals
A matching config indicates the exporter preserved expected image config schema, platform, rootfs, and history semantics for `zstd-oci-types` under compatibility version `v30`. A mismatch usually signals exporter output drift rather than runtime code execution in this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/zstd-oci-types/v30/config.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/zstd-oci-types/v30/manifest.json -->
# sources/cloud-native/buildkit/client/testdata/compatibility/common/zstd-oci-types/v30/manifest.json

## Purpose
This JSON fixture is an image manifest baseline for the BuildKit client compatibility suite. It belongs to `common/zstd-oci-types/v30`, representing the common fixture shared by exporter compatibility tests across image layout modes and the zstd-compressed OCI layer media type baseline.

## Important Fields and Data Shape
- Schema version: `2`.
- Manifest media type: `application/vnd.oci.image.manifest.v1+json`.
- Config descriptor media type: `application/vnd.oci.image.config.v1+json`, digest `sha256:1772fd0a3b45a62fc...`, size `2295`.
- Layer count: `4`.
- Layer media types: `application/vnd.oci.image.layer.v1.tar+zstd`.
- First layer digest/size: `sha256:732ad1c88bfbc8aa6...` / `1997110`.
- Manifest annotations present: `False`; layer descriptors with annotations: `4`.
- Compatibility version directory: `v30`.

## Control Flow and Integration Role
The file is fixture input for compatibility comparisons. Tests use it to verify that exporter output preserves expected manifest media types, config references, layer descriptors, annotations, compression choices, and compatibility-version behavior.

## State and Persistence Behavior
The manifest models persisted registry or OCI-layout metadata. It is content-addressable through its JSON bytes, and its config/layer descriptors must match adjacent config blobs and generated layer blobs. It has no runtime mutation path.

## Dependencies and Integration Points
It integrates with exporter compatibility tests, the image/OCI exporter, compression settings, OCI/Docker media-type conversion, provenance/annotation options, and adjacent `config.json` fixture files where present.

## Risks and Edge Cases
Risks include digest churn from non-deterministic timestamps or compression, wrong Docker-vs-OCI media types, dropped annotations, incorrect uncompressed/zstd media type selection, or layer order changes. For `manifest-annotation` fixtures, annotations are part of the behavior under test. For compression fixtures, descriptor sizes and digests are sensitive to compressor settings.

## Test Signals
A match means BuildKit emitted the expected manifest structure for `zstd-oci-types` in `common` mode at compatibility version `v30`. A mismatch is a high-signal exporter compatibility regression because consumers use these descriptors to pull or load the image.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/common/zstd-oci-types/v30/manifest.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/image/default-gzip/v10/manifest.json -->
# sources/cloud-native/buildkit/client/testdata/compatibility/image/default-gzip/v10/manifest.json

## Purpose
This JSON fixture is an image manifest baseline for the BuildKit client compatibility suite. It belongs to `image/default-gzip/v10`, representing the Docker image media-type fixture for image exporter compatibility and the default gzip compression baseline.

## Important Fields and Data Shape
- Schema version: `2`.
- Manifest media type: `application/vnd.docker.distribution.manifest.v2+json`.
- Config descriptor media type: `application/vnd.docker.container.image.v1+json`, digest `sha256:697cbcf20a7a20500...`, size `2295`.
- Layer count: `4`.
- Layer media types: `application/vnd.docker.image.rootfs.diff.tar.gzip`.
- First layer digest/size: `sha256:430ee4fa77d640d42...` / `2219886`.
- Manifest annotations present: `False`; layer descriptors with annotations: `0`.
- Compatibility version directory: `v10`.

## Control Flow and Integration Role
The file is fixture input for compatibility comparisons. Tests use it to verify that exporter output preserves expected manifest media types, config references, layer descriptors, annotations, compression choices, and compatibility-version behavior.

## State and Persistence Behavior
The manifest models persisted registry or OCI-layout metadata. It is content-addressable through its JSON bytes, and its config/layer descriptors must match adjacent config blobs and generated layer blobs. It has no runtime mutation path.

## Dependencies and Integration Points
It integrates with exporter compatibility tests, the image/OCI exporter, compression settings, OCI/Docker media-type conversion, provenance/annotation options, and adjacent `config.json` fixture files where present.

## Risks and Edge Cases
Risks include digest churn from non-deterministic timestamps or compression, wrong Docker-vs-OCI media types, dropped annotations, incorrect uncompressed/zstd media type selection, or layer order changes. For `manifest-annotation` fixtures, annotations are part of the behavior under test. For compression fixtures, descriptor sizes and digests are sensitive to compressor settings.

## Test Signals
A match means BuildKit emitted the expected manifest structure for `default-gzip` in `image` mode at compatibility version `v10`. A mismatch is a high-signal exporter compatibility regression because consumers use these descriptors to pull or load the image.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/image/default-gzip/v10/manifest.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/image/default-gzip/v20/manifest.json -->
# sources/cloud-native/buildkit/client/testdata/compatibility/image/default-gzip/v20/manifest.json

## Purpose
This JSON fixture is an image manifest baseline for the BuildKit client compatibility suite. It belongs to `image/default-gzip/v20`, representing the Docker image media-type fixture for image exporter compatibility and the default gzip compression baseline.

## Important Fields and Data Shape
- Schema version: `2`.
- Manifest media type: `application/vnd.docker.distribution.manifest.v2+json`.
- Config descriptor media type: `application/vnd.docker.container.image.v1+json`, digest `sha256:1772fd0a3b45a62fc...`, size `2295`.
- Layer count: `4`.
- Layer media types: `application/vnd.docker.image.rootfs.diff.tar.gzip`.
- First layer digest/size: `sha256:430ee4fa77d640d42...` / `2219886`.
- Manifest annotations present: `False`; layer descriptors with annotations: `0`.
- Compatibility version directory: `v20`.

## Control Flow and Integration Role
The file is fixture input for compatibility comparisons. Tests use it to verify that exporter output preserves expected manifest media types, config references, layer descriptors, annotations, compression choices, and compatibility-version behavior.

## State and Persistence Behavior
The manifest models persisted registry or OCI-layout metadata. It is content-addressable through its JSON bytes, and its config/layer descriptors must match adjacent config blobs and generated layer blobs. It has no runtime mutation path.

## Dependencies and Integration Points
It integrates with exporter compatibility tests, the image/OCI exporter, compression settings, OCI/Docker media-type conversion, provenance/annotation options, and adjacent `config.json` fixture files where present.

## Risks and Edge Cases
Risks include digest churn from non-deterministic timestamps or compression, wrong Docker-vs-OCI media types, dropped annotations, incorrect uncompressed/zstd media type selection, or layer order changes. For `manifest-annotation` fixtures, annotations are part of the behavior under test. For compression fixtures, descriptor sizes and digests are sensitive to compressor settings.

## Test Signals
A match means BuildKit emitted the expected manifest structure for `default-gzip` in `image` mode at compatibility version `v20`. A mismatch is a high-signal exporter compatibility regression because consumers use these descriptors to pull or load the image.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/image/default-gzip/v20/manifest.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/image/gzip-level-0/v10/manifest.json -->
# sources/cloud-native/buildkit/client/testdata/compatibility/image/gzip-level-0/v10/manifest.json

## Purpose
This JSON fixture is an image manifest baseline for the BuildKit client compatibility suite. It belongs to `image/gzip-level-0/v10`, representing the Docker image media-type fixture for image exporter compatibility and the gzip compression level 0 compatibility baseline.

## Important Fields and Data Shape
- Schema version: `2`.
- Manifest media type: `application/vnd.docker.distribution.manifest.v2+json`.
- Config descriptor media type: `application/vnd.docker.container.image.v1+json`, digest `sha256:697cbcf20a7a20500...`, size `2295`.
- Layer count: `4`.
- Layer media types: `application/vnd.docker.image.rootfs.diff.tar.gzip`.
- First layer digest/size: `sha256:3b2645dc700f1550f...` / `4492656`.
- Manifest annotations present: `False`; layer descriptors with annotations: `0`.
- Compatibility version directory: `v10`.

## Control Flow and Integration Role
The file is fixture input for compatibility comparisons. Tests use it to verify that exporter output preserves expected manifest media types, config references, layer descriptors, annotations, compression choices, and compatibility-version behavior.

## State and Persistence Behavior
The manifest models persisted registry or OCI-layout metadata. It is content-addressable through its JSON bytes, and its config/layer descriptors must match adjacent config blobs and generated layer blobs. It has no runtime mutation path.

## Dependencies and Integration Points
It integrates with exporter compatibility tests, the image/OCI exporter, compression settings, OCI/Docker media-type conversion, provenance/annotation options, and adjacent `config.json` fixture files where present.

## Risks and Edge Cases
Risks include digest churn from non-deterministic timestamps or compression, wrong Docker-vs-OCI media types, dropped annotations, incorrect uncompressed/zstd media type selection, or layer order changes. For `manifest-annotation` fixtures, annotations are part of the behavior under test. For compression fixtures, descriptor sizes and digests are sensitive to compressor settings.

## Test Signals
A match means BuildKit emitted the expected manifest structure for `gzip-level-0` in `image` mode at compatibility version `v10`. A mismatch is a high-signal exporter compatibility regression because consumers use these descriptors to pull or load the image.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/image/gzip-level-0/v10/manifest.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/image/gzip-level-0/v20/manifest.json -->
# sources/cloud-native/buildkit/client/testdata/compatibility/image/gzip-level-0/v20/manifest.json

## Purpose
This JSON fixture is an image manifest baseline for the BuildKit client compatibility suite. It belongs to `image/gzip-level-0/v20`, representing the Docker image media-type fixture for image exporter compatibility and the gzip compression level 0 compatibility baseline.

## Important Fields and Data Shape
- Schema version: `2`.
- Manifest media type: `application/vnd.docker.distribution.manifest.v2+json`.
- Config descriptor media type: `application/vnd.docker.container.image.v1+json`, digest `sha256:1772fd0a3b45a62fc...`, size `2295`.
- Layer count: `4`.
- Layer media types: `application/vnd.docker.image.rootfs.diff.tar.gzip`.
- First layer digest/size: `sha256:3b2645dc700f1550f...` / `4492656`.
- Manifest annotations present: `False`; layer descriptors with annotations: `0`.
- Compatibility version directory: `v20`.

## Control Flow and Integration Role
The file is fixture input for compatibility comparisons. Tests use it to verify that exporter output preserves expected manifest media types, config references, layer descriptors, annotations, compression choices, and compatibility-version behavior.

## State and Persistence Behavior
The manifest models persisted registry or OCI-layout metadata. It is content-addressable through its JSON bytes, and its config/layer descriptors must match adjacent config blobs and generated layer blobs. It has no runtime mutation path.

## Dependencies and Integration Points
It integrates with exporter compatibility tests, the image/OCI exporter, compression settings, OCI/Docker media-type conversion, provenance/annotation options, and adjacent `config.json` fixture files where present.

## Risks and Edge Cases
Risks include digest churn from non-deterministic timestamps or compression, wrong Docker-vs-OCI media types, dropped annotations, incorrect uncompressed/zstd media type selection, or layer order changes. For `manifest-annotation` fixtures, annotations are part of the behavior under test. For compression fixtures, descriptor sizes and digests are sensitive to compressor settings.

## Test Signals
A match means BuildKit emitted the expected manifest structure for `gzip-level-0` in `image` mode at compatibility version `v20`. A mismatch is a high-signal exporter compatibility regression because consumers use these descriptors to pull or load the image.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/image/gzip-level-0/v20/manifest.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/image/gzip-level-9/v10/manifest.json -->
# sources/cloud-native/buildkit/client/testdata/compatibility/image/gzip-level-9/v10/manifest.json

## Purpose
This JSON fixture is an image manifest baseline for the BuildKit client compatibility suite. It belongs to `image/gzip-level-9/v10`, representing the Docker image media-type fixture for image exporter compatibility and the gzip compression level 9 compatibility baseline.

## Important Fields and Data Shape
- Schema version: `2`.
- Manifest media type: `application/vnd.docker.distribution.manifest.v2+json`.
- Config descriptor media type: `application/vnd.docker.container.image.v1+json`, digest `sha256:697cbcf20a7a20500...`, size `2295`.
- Layer count: `4`.
- Layer media types: `application/vnd.docker.image.rootfs.diff.tar.gzip`.
- First layer digest/size: `sha256:86961eaccfc75a8ee...` / `2216704`.
- Manifest annotations present: `False`; layer descriptors with annotations: `0`.
- Compatibility version directory: `v10`.

## Control Flow and Integration Role
The file is fixture input for compatibility comparisons. Tests use it to verify that exporter output preserves expected manifest media types, config references, layer descriptors, annotations, compression choices, and compatibility-version behavior.

## State and Persistence Behavior
The manifest models persisted registry or OCI-layout metadata. It is content-addressable through its JSON bytes, and its config/layer descriptors must match adjacent config blobs and generated layer blobs. It has no runtime mutation path.

## Dependencies and Integration Points
It integrates with exporter compatibility tests, the image/OCI exporter, compression settings, OCI/Docker media-type conversion, provenance/annotation options, and adjacent `config.json` fixture files where present.

## Risks and Edge Cases
Risks include digest churn from non-deterministic timestamps or compression, wrong Docker-vs-OCI media types, dropped annotations, incorrect uncompressed/zstd media type selection, or layer order changes. For `manifest-annotation` fixtures, annotations are part of the behavior under test. For compression fixtures, descriptor sizes and digests are sensitive to compressor settings.

## Test Signals
A match means BuildKit emitted the expected manifest structure for `gzip-level-9` in `image` mode at compatibility version `v10`. A mismatch is a high-signal exporter compatibility regression because consumers use these descriptors to pull or load the image.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/image/gzip-level-9/v10/manifest.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/image/gzip-level-9/v20/manifest.json -->
# sources/cloud-native/buildkit/client/testdata/compatibility/image/gzip-level-9/v20/manifest.json

## Purpose
This JSON fixture is an image manifest baseline for the BuildKit client compatibility suite. It belongs to `image/gzip-level-9/v20`, representing the Docker image media-type fixture for image exporter compatibility and the gzip compression level 9 compatibility baseline.

## Important Fields and Data Shape
- Schema version: `2`.
- Manifest media type: `application/vnd.docker.distribution.manifest.v2+json`.
- Config descriptor media type: `application/vnd.docker.container.image.v1+json`, digest `sha256:1772fd0a3b45a62fc...`, size `2295`.
- Layer count: `4`.
- Layer media types: `application/vnd.docker.image.rootfs.diff.tar.gzip`.
- First layer digest/size: `sha256:86961eaccfc75a8ee...` / `2216704`.
- Manifest annotations present: `False`; layer descriptors with annotations: `0`.
- Compatibility version directory: `v20`.

## Control Flow and Integration Role
The file is fixture input for compatibility comparisons. Tests use it to verify that exporter output preserves expected manifest media types, config references, layer descriptors, annotations, compression choices, and compatibility-version behavior.

## State and Persistence Behavior
The manifest models persisted registry or OCI-layout metadata. It is content-addressable through its JSON bytes, and its config/layer descriptors must match adjacent config blobs and generated layer blobs. It has no runtime mutation path.

## Dependencies and Integration Points
It integrates with exporter compatibility tests, the image/OCI exporter, compression settings, OCI/Docker media-type conversion, provenance/annotation options, and adjacent `config.json` fixture files where present.

## Risks and Edge Cases
Risks include digest churn from non-deterministic timestamps or compression, wrong Docker-vs-OCI media types, dropped annotations, incorrect uncompressed/zstd media type selection, or layer order changes. For `manifest-annotation` fixtures, annotations are part of the behavior under test. For compression fixtures, descriptor sizes and digests are sensitive to compressor settings.

## Test Signals
A match means BuildKit emitted the expected manifest structure for `gzip-level-9` in `image` mode at compatibility version `v20`. A mismatch is a high-signal exporter compatibility regression because consumers use these descriptors to pull or load the image.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/image/gzip-level-9/v20/manifest.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/image/manifest-annotation/v10/manifest.json -->
# sources/cloud-native/buildkit/client/testdata/compatibility/image/manifest-annotation/v10/manifest.json

## Purpose
This JSON fixture is an image manifest baseline for the BuildKit client compatibility suite. It belongs to `image/manifest-annotation/v10`, representing the Docker image media-type fixture for image exporter compatibility and the manifest annotation preservation baseline.

## Important Fields and Data Shape
- Schema version: `2`.
- Manifest media type: `application/vnd.docker.distribution.manifest.v2+json`.
- Config descriptor media type: `application/vnd.docker.container.image.v1+json`, digest `sha256:697cbcf20a7a20500...`, size `2295`.
- Layer count: `4`.
- Layer media types: `application/vnd.docker.image.rootfs.diff.tar.gzip`.
- First layer digest/size: `sha256:430ee4fa77d640d42...` / `2219886`.
- Manifest annotations present: `True`; layer descriptors with annotations: `0`.
- Compatibility version directory: `v10`.

## Control Flow and Integration Role
The file is fixture input for compatibility comparisons. Tests use it to verify that exporter output preserves expected manifest media types, config references, layer descriptors, annotations, compression choices, and compatibility-version behavior.

## State and Persistence Behavior
The manifest models persisted registry or OCI-layout metadata. It is content-addressable through its JSON bytes, and its config/layer descriptors must match adjacent config blobs and generated layer blobs. It has no runtime mutation path.

## Dependencies and Integration Points
It integrates with exporter compatibility tests, the image/OCI exporter, compression settings, OCI/Docker media-type conversion, provenance/annotation options, and adjacent `config.json` fixture files where present.

## Risks and Edge Cases
Risks include digest churn from non-deterministic timestamps or compression, wrong Docker-vs-OCI media types, dropped annotations, incorrect uncompressed/zstd media type selection, or layer order changes. For `manifest-annotation` fixtures, annotations are part of the behavior under test. For compression fixtures, descriptor sizes and digests are sensitive to compressor settings.

## Test Signals
A match means BuildKit emitted the expected manifest structure for `manifest-annotation` in `image` mode at compatibility version `v10`. A mismatch is a high-signal exporter compatibility regression because consumers use these descriptors to pull or load the image.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/image/manifest-annotation/v10/manifest.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/image/manifest-annotation/v20/manifest.json -->
# sources/cloud-native/buildkit/client/testdata/compatibility/image/manifest-annotation/v20/manifest.json

## Purpose
This JSON fixture is an image manifest baseline for the BuildKit client compatibility suite. It belongs to `image/manifest-annotation/v20`, representing the Docker image media-type fixture for image exporter compatibility and the manifest annotation preservation baseline.

## Important Fields and Data Shape
- Schema version: `2`.
- Manifest media type: `application/vnd.docker.distribution.manifest.v2+json`.
- Config descriptor media type: `application/vnd.docker.container.image.v1+json`, digest `sha256:1772fd0a3b45a62fc...`, size `2295`.
- Layer count: `4`.
- Layer media types: `application/vnd.docker.image.rootfs.diff.tar.gzip`.
- First layer digest/size: `sha256:430ee4fa77d640d42...` / `2219886`.
- Manifest annotations present: `True`; layer descriptors with annotations: `0`.
- Compatibility version directory: `v20`.

## Control Flow and Integration Role
The file is fixture input for compatibility comparisons. Tests use it to verify that exporter output preserves expected manifest media types, config references, layer descriptors, annotations, compression choices, and compatibility-version behavior.

## State and Persistence Behavior
The manifest models persisted registry or OCI-layout metadata. It is content-addressable through its JSON bytes, and its config/layer descriptors must match adjacent config blobs and generated layer blobs. It has no runtime mutation path.

## Dependencies and Integration Points
It integrates with exporter compatibility tests, the image/OCI exporter, compression settings, OCI/Docker media-type conversion, provenance/annotation options, and adjacent `config.json` fixture files where present.

## Risks and Edge Cases
Risks include digest churn from non-deterministic timestamps or compression, wrong Docker-vs-OCI media types, dropped annotations, incorrect uncompressed/zstd media type selection, or layer order changes. For `manifest-annotation` fixtures, annotations are part of the behavior under test. For compression fixtures, descriptor sizes and digests are sensitive to compressor settings.

## Test Signals
A match means BuildKit emitted the expected manifest structure for `manifest-annotation` in `image` mode at compatibility version `v20`. A mismatch is a high-signal exporter compatibility regression because consumers use these descriptors to pull or load the image.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/image/manifest-annotation/v20/manifest.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/image/uncompressed/v10/manifest.json -->
# sources/cloud-native/buildkit/client/testdata/compatibility/image/uncompressed/v10/manifest.json

## Purpose
This JSON fixture is an image manifest baseline for the BuildKit client compatibility suite. It belongs to `image/uncompressed/v10`, representing the Docker image media-type fixture for image exporter compatibility and the uncompressed layer media type baseline.

## Important Fields and Data Shape
- Schema version: `2`.
- Manifest media type: `application/vnd.docker.distribution.manifest.v2+json`.
- Config descriptor media type: `application/vnd.docker.container.image.v1+json`, digest `sha256:697cbcf20a7a20500...`, size `2295`.
- Layer count: `4`.
- Layer media types: `application/vnd.docker.image.rootfs.diff.tar`.
- First layer digest/size: `sha256:fe4922f0a3ca2aa70...` / `4492288`.
- Manifest annotations present: `False`; layer descriptors with annotations: `0`.
- Compatibility version directory: `v10`.

## Control Flow and Integration Role
The file is fixture input for compatibility comparisons. Tests use it to verify that exporter output preserves expected manifest media types, config references, layer descriptors, annotations, compression choices, and compatibility-version behavior.

## State and Persistence Behavior
The manifest models persisted registry or OCI-layout metadata. It is content-addressable through its JSON bytes, and its config/layer descriptors must match adjacent config blobs and generated layer blobs. It has no runtime mutation path.

## Dependencies and Integration Points
It integrates with exporter compatibility tests, the image/OCI exporter, compression settings, OCI/Docker media-type conversion, provenance/annotation options, and adjacent `config.json` fixture files where present.

## Risks and Edge Cases
Risks include digest churn from non-deterministic timestamps or compression, wrong Docker-vs-OCI media types, dropped annotations, incorrect uncompressed/zstd media type selection, or layer order changes. For `manifest-annotation` fixtures, annotations are part of the behavior under test. For compression fixtures, descriptor sizes and digests are sensitive to compressor settings.

## Test Signals
A match means BuildKit emitted the expected manifest structure for `uncompressed` in `image` mode at compatibility version `v10`. A mismatch is a high-signal exporter compatibility regression because consumers use these descriptors to pull or load the image.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/image/uncompressed/v10/manifest.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/image/uncompressed/v20/manifest.json -->
# sources/cloud-native/buildkit/client/testdata/compatibility/image/uncompressed/v20/manifest.json

## Purpose
This JSON fixture is an image manifest baseline for the BuildKit client compatibility suite. It belongs to `image/uncompressed/v20`, representing the Docker image media-type fixture for image exporter compatibility and the uncompressed layer media type baseline.

## Important Fields and Data Shape
- Schema version: `2`.
- Manifest media type: `application/vnd.docker.distribution.manifest.v2+json`.
- Config descriptor media type: `application/vnd.docker.container.image.v1+json`, digest `sha256:1772fd0a3b45a62fc...`, size `2295`.
- Layer count: `4`.
- Layer media types: `application/vnd.docker.image.rootfs.diff.tar`.
- First layer digest/size: `sha256:fe4922f0a3ca2aa70...` / `4492288`.
- Manifest annotations present: `False`; layer descriptors with annotations: `0`.
- Compatibility version directory: `v20`.

## Control Flow and Integration Role
The file is fixture input for compatibility comparisons. Tests use it to verify that exporter output preserves expected manifest media types, config references, layer descriptors, annotations, compression choices, and compatibility-version behavior.

## State and Persistence Behavior
The manifest models persisted registry or OCI-layout metadata. It is content-addressable through its JSON bytes, and its config/layer descriptors must match adjacent config blobs and generated layer blobs. It has no runtime mutation path.

## Dependencies and Integration Points
It integrates with exporter compatibility tests, the image/OCI exporter, compression settings, OCI/Docker media-type conversion, provenance/annotation options, and adjacent `config.json` fixture files where present.

## Risks and Edge Cases
Risks include digest churn from non-deterministic timestamps or compression, wrong Docker-vs-OCI media types, dropped annotations, incorrect uncompressed/zstd media type selection, or layer order changes. For `manifest-annotation` fixtures, annotations are part of the behavior under test. For compression fixtures, descriptor sizes and digests are sensitive to compressor settings.

## Test Signals
A match means BuildKit emitted the expected manifest structure for `uncompressed` in `image` mode at compatibility version `v20`. A mismatch is a high-signal exporter compatibility regression because consumers use these descriptors to pull or load the image.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/image/uncompressed/v20/manifest.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/oci/default-gzip/v10/manifest.json -->
# sources/cloud-native/buildkit/client/testdata/compatibility/oci/default-gzip/v10/manifest.json

## Purpose
This JSON fixture is an image manifest baseline for the BuildKit client compatibility suite. It belongs to `oci/default-gzip/v10`, representing the OCI media-type fixture for OCI exporter compatibility and the default gzip compression baseline.

## Important Fields and Data Shape
- Schema version: `2`.
- Manifest media type: `application/vnd.oci.image.manifest.v1+json`.
- Config descriptor media type: `application/vnd.oci.image.config.v1+json`, digest `sha256:697cbcf20a7a20500...`, size `2295`.
- Layer count: `4`.
- Layer media types: `application/vnd.oci.image.layer.v1.tar+gzip`.
- First layer digest/size: `sha256:430ee4fa77d640d42...` / `2219886`.
- Manifest annotations present: `False`; layer descriptors with annotations: `4`.
- Compatibility version directory: `v10`.

## Control Flow and Integration Role
The file is fixture input for compatibility comparisons. Tests use it to verify that exporter output preserves expected manifest media types, config references, layer descriptors, annotations, compression choices, and compatibility-version behavior.

## State and Persistence Behavior
The manifest models persisted registry or OCI-layout metadata. It is content-addressable through its JSON bytes, and its config/layer descriptors must match adjacent config blobs and generated layer blobs. It has no runtime mutation path.

## Dependencies and Integration Points
It integrates with exporter compatibility tests, the image/OCI exporter, compression settings, OCI/Docker media-type conversion, provenance/annotation options, and adjacent `config.json` fixture files where present.

## Risks and Edge Cases
Risks include digest churn from non-deterministic timestamps or compression, wrong Docker-vs-OCI media types, dropped annotations, incorrect uncompressed/zstd media type selection, or layer order changes. For `manifest-annotation` fixtures, annotations are part of the behavior under test. For compression fixtures, descriptor sizes and digests are sensitive to compressor settings.

## Test Signals
A match means BuildKit emitted the expected manifest structure for `default-gzip` in `oci` mode at compatibility version `v10`. A mismatch is a high-signal exporter compatibility regression because consumers use these descriptors to pull or load the image.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/oci/default-gzip/v10/manifest.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/oci/default-gzip/v20/manifest.json -->
# sources/cloud-native/buildkit/client/testdata/compatibility/oci/default-gzip/v20/manifest.json

## Purpose
This JSON fixture is an image manifest baseline for the BuildKit client compatibility suite. It belongs to `oci/default-gzip/v20`, representing the OCI media-type fixture for OCI exporter compatibility and the default gzip compression baseline.

## Important Fields and Data Shape
- Schema version: `2`.
- Manifest media type: `application/vnd.oci.image.manifest.v1+json`.
- Config descriptor media type: `application/vnd.oci.image.config.v1+json`, digest `sha256:1772fd0a3b45a62fc...`, size `2295`.
- Layer count: `4`.
- Layer media types: `application/vnd.oci.image.layer.v1.tar+gzip`.
- First layer digest/size: `sha256:430ee4fa77d640d42...` / `2219886`.
- Manifest annotations present: `False`; layer descriptors with annotations: `4`.
- Compatibility version directory: `v20`.

## Control Flow and Integration Role
The file is fixture input for compatibility comparisons. Tests use it to verify that exporter output preserves expected manifest media types, config references, layer descriptors, annotations, compression choices, and compatibility-version behavior.

## State and Persistence Behavior
The manifest models persisted registry or OCI-layout metadata. It is content-addressable through its JSON bytes, and its config/layer descriptors must match adjacent config blobs and generated layer blobs. It has no runtime mutation path.

## Dependencies and Integration Points
It integrates with exporter compatibility tests, the image/OCI exporter, compression settings, OCI/Docker media-type conversion, provenance/annotation options, and adjacent `config.json` fixture files where present.

## Risks and Edge Cases
Risks include digest churn from non-deterministic timestamps or compression, wrong Docker-vs-OCI media types, dropped annotations, incorrect uncompressed/zstd media type selection, or layer order changes. For `manifest-annotation` fixtures, annotations are part of the behavior under test. For compression fixtures, descriptor sizes and digests are sensitive to compressor settings.

## Test Signals
A match means BuildKit emitted the expected manifest structure for `default-gzip` in `oci` mode at compatibility version `v20`. A mismatch is a high-signal exporter compatibility regression because consumers use these descriptors to pull or load the image.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/oci/default-gzip/v20/manifest.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/oci/gzip-level-0/v10/manifest.json -->
# sources/cloud-native/buildkit/client/testdata/compatibility/oci/gzip-level-0/v10/manifest.json

## Purpose
This JSON fixture is an image manifest baseline for the BuildKit client compatibility suite. It belongs to `oci/gzip-level-0/v10`, representing the OCI media-type fixture for OCI exporter compatibility and the gzip compression level 0 compatibility baseline.

## Important Fields and Data Shape
- Schema version: `2`.
- Manifest media type: `application/vnd.oci.image.manifest.v1+json`.
- Config descriptor media type: `application/vnd.oci.image.config.v1+json`, digest `sha256:697cbcf20a7a20500...`, size `2295`.
- Layer count: `4`.
- Layer media types: `application/vnd.oci.image.layer.v1.tar+gzip`.
- First layer digest/size: `sha256:3b2645dc700f1550f...` / `4492656`.
- Manifest annotations present: `False`; layer descriptors with annotations: `4`.
- Compatibility version directory: `v10`.

## Control Flow and Integration Role
The file is fixture input for compatibility comparisons. Tests use it to verify that exporter output preserves expected manifest media types, config references, layer descriptors, annotations, compression choices, and compatibility-version behavior.

## State and Persistence Behavior
The manifest models persisted registry or OCI-layout metadata. It is content-addressable through its JSON bytes, and its config/layer descriptors must match adjacent config blobs and generated layer blobs. It has no runtime mutation path.

## Dependencies and Integration Points
It integrates with exporter compatibility tests, the image/OCI exporter, compression settings, OCI/Docker media-type conversion, provenance/annotation options, and adjacent `config.json` fixture files where present.

## Risks and Edge Cases
Risks include digest churn from non-deterministic timestamps or compression, wrong Docker-vs-OCI media types, dropped annotations, incorrect uncompressed/zstd media type selection, or layer order changes. For `manifest-annotation` fixtures, annotations are part of the behavior under test. For compression fixtures, descriptor sizes and digests are sensitive to compressor settings.

## Test Signals
A match means BuildKit emitted the expected manifest structure for `gzip-level-0` in `oci` mode at compatibility version `v10`. A mismatch is a high-signal exporter compatibility regression because consumers use these descriptors to pull or load the image.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/oci/gzip-level-0/v10/manifest.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/oci/gzip-level-0/v20/manifest.json -->
# sources/cloud-native/buildkit/client/testdata/compatibility/oci/gzip-level-0/v20/manifest.json

## Purpose
This JSON fixture is an image manifest baseline for the BuildKit client compatibility suite. It belongs to `oci/gzip-level-0/v20`, representing the OCI media-type fixture for OCI exporter compatibility and the gzip compression level 0 compatibility baseline.

## Important Fields and Data Shape
- Schema version: `2`.
- Manifest media type: `application/vnd.oci.image.manifest.v1+json`.
- Config descriptor media type: `application/vnd.oci.image.config.v1+json`, digest `sha256:1772fd0a3b45a62fc...`, size `2295`.
- Layer count: `4`.
- Layer media types: `application/vnd.oci.image.layer.v1.tar+gzip`.
- First layer digest/size: `sha256:3b2645dc700f1550f...` / `4492656`.
- Manifest annotations present: `False`; layer descriptors with annotations: `4`.
- Compatibility version directory: `v20`.

## Control Flow and Integration Role
The file is fixture input for compatibility comparisons. Tests use it to verify that exporter output preserves expected manifest media types, config references, layer descriptors, annotations, compression choices, and compatibility-version behavior.

## State and Persistence Behavior
The manifest models persisted registry or OCI-layout metadata. It is content-addressable through its JSON bytes, and its config/layer descriptors must match adjacent config blobs and generated layer blobs. It has no runtime mutation path.

## Dependencies and Integration Points
It integrates with exporter compatibility tests, the image/OCI exporter, compression settings, OCI/Docker media-type conversion, provenance/annotation options, and adjacent `config.json` fixture files where present.

## Risks and Edge Cases
Risks include digest churn from non-deterministic timestamps or compression, wrong Docker-vs-OCI media types, dropped annotations, incorrect uncompressed/zstd media type selection, or layer order changes. For `manifest-annotation` fixtures, annotations are part of the behavior under test. For compression fixtures, descriptor sizes and digests are sensitive to compressor settings.

## Test Signals
A match means BuildKit emitted the expected manifest structure for `gzip-level-0` in `oci` mode at compatibility version `v20`. A mismatch is a high-signal exporter compatibility regression because consumers use these descriptors to pull or load the image.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/oci/gzip-level-0/v20/manifest.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/oci/gzip-level-9/v10/manifest.json -->
# sources/cloud-native/buildkit/client/testdata/compatibility/oci/gzip-level-9/v10/manifest.json

## Purpose
This JSON fixture is an image manifest baseline for the BuildKit client compatibility suite. It belongs to `oci/gzip-level-9/v10`, representing the OCI media-type fixture for OCI exporter compatibility and the gzip compression level 9 compatibility baseline.

## Important Fields and Data Shape
- Schema version: `2`.
- Manifest media type: `application/vnd.oci.image.manifest.v1+json`.
- Config descriptor media type: `application/vnd.oci.image.config.v1+json`, digest `sha256:697cbcf20a7a20500...`, size `2295`.
- Layer count: `4`.
- Layer media types: `application/vnd.oci.image.layer.v1.tar+gzip`.
- First layer digest/size: `sha256:86961eaccfc75a8ee...` / `2216704`.
- Manifest annotations present: `False`; layer descriptors with annotations: `4`.
- Compatibility version directory: `v10`.

## Control Flow and Integration Role
The file is fixture input for compatibility comparisons. Tests use it to verify that exporter output preserves expected manifest media types, config references, layer descriptors, annotations, compression choices, and compatibility-version behavior.

## State and Persistence Behavior
The manifest models persisted registry or OCI-layout metadata. It is content-addressable through its JSON bytes, and its config/layer descriptors must match adjacent config blobs and generated layer blobs. It has no runtime mutation path.

## Dependencies and Integration Points
It integrates with exporter compatibility tests, the image/OCI exporter, compression settings, OCI/Docker media-type conversion, provenance/annotation options, and adjacent `config.json` fixture files where present.

## Risks and Edge Cases
Risks include digest churn from non-deterministic timestamps or compression, wrong Docker-vs-OCI media types, dropped annotations, incorrect uncompressed/zstd media type selection, or layer order changes. For `manifest-annotation` fixtures, annotations are part of the behavior under test. For compression fixtures, descriptor sizes and digests are sensitive to compressor settings.

## Test Signals
A match means BuildKit emitted the expected manifest structure for `gzip-level-9` in `oci` mode at compatibility version `v10`. A mismatch is a high-signal exporter compatibility regression because consumers use these descriptors to pull or load the image.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/oci/gzip-level-9/v10/manifest.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/oci/gzip-level-9/v20/manifest.json -->
# sources/cloud-native/buildkit/client/testdata/compatibility/oci/gzip-level-9/v20/manifest.json

## Purpose
This JSON fixture is an image manifest baseline for the BuildKit client compatibility suite. It belongs to `oci/gzip-level-9/v20`, representing the OCI media-type fixture for OCI exporter compatibility and the gzip compression level 9 compatibility baseline.

## Important Fields and Data Shape
- Schema version: `2`.
- Manifest media type: `application/vnd.oci.image.manifest.v1+json`.
- Config descriptor media type: `application/vnd.oci.image.config.v1+json`, digest `sha256:1772fd0a3b45a62fc...`, size `2295`.
- Layer count: `4`.
- Layer media types: `application/vnd.oci.image.layer.v1.tar+gzip`.
- First layer digest/size: `sha256:86961eaccfc75a8ee...` / `2216704`.
- Manifest annotations present: `False`; layer descriptors with annotations: `4`.
- Compatibility version directory: `v20`.

## Control Flow and Integration Role
The file is fixture input for compatibility comparisons. Tests use it to verify that exporter output preserves expected manifest media types, config references, layer descriptors, annotations, compression choices, and compatibility-version behavior.

## State and Persistence Behavior
The manifest models persisted registry or OCI-layout metadata. It is content-addressable through its JSON bytes, and its config/layer descriptors must match adjacent config blobs and generated layer blobs. It has no runtime mutation path.

## Dependencies and Integration Points
It integrates with exporter compatibility tests, the image/OCI exporter, compression settings, OCI/Docker media-type conversion, provenance/annotation options, and adjacent `config.json` fixture files where present.

## Risks and Edge Cases
Risks include digest churn from non-deterministic timestamps or compression, wrong Docker-vs-OCI media types, dropped annotations, incorrect uncompressed/zstd media type selection, or layer order changes. For `manifest-annotation` fixtures, annotations are part of the behavior under test. For compression fixtures, descriptor sizes and digests are sensitive to compressor settings.

## Test Signals
A match means BuildKit emitted the expected manifest structure for `gzip-level-9` in `oci` mode at compatibility version `v20`. A mismatch is a high-signal exporter compatibility regression because consumers use these descriptors to pull or load the image.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/oci/gzip-level-9/v20/manifest.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/oci/manifest-annotation/v10/manifest.json -->
# sources/cloud-native/buildkit/client/testdata/compatibility/oci/manifest-annotation/v10/manifest.json

## Purpose
This JSON fixture is an image manifest baseline for the BuildKit client compatibility suite. It belongs to `oci/manifest-annotation/v10`, representing the OCI media-type fixture for OCI exporter compatibility and the manifest annotation preservation baseline.

## Important Fields and Data Shape
- Schema version: `2`.
- Manifest media type: `application/vnd.oci.image.manifest.v1+json`.
- Config descriptor media type: `application/vnd.oci.image.config.v1+json`, digest `sha256:697cbcf20a7a20500...`, size `2295`.
- Layer count: `4`.
- Layer media types: `application/vnd.oci.image.layer.v1.tar+gzip`.
- First layer digest/size: `sha256:430ee4fa77d640d42...` / `2219886`.
- Manifest annotations present: `True`; layer descriptors with annotations: `4`.
- Compatibility version directory: `v10`.

## Control Flow and Integration Role
The file is fixture input for compatibility comparisons. Tests use it to verify that exporter output preserves expected manifest media types, config references, layer descriptors, annotations, compression choices, and compatibility-version behavior.

## State and Persistence Behavior
The manifest models persisted registry or OCI-layout metadata. It is content-addressable through its JSON bytes, and its config/layer descriptors must match adjacent config blobs and generated layer blobs. It has no runtime mutation path.

## Dependencies and Integration Points
It integrates with exporter compatibility tests, the image/OCI exporter, compression settings, OCI/Docker media-type conversion, provenance/annotation options, and adjacent `config.json` fixture files where present.

## Risks and Edge Cases
Risks include digest churn from non-deterministic timestamps or compression, wrong Docker-vs-OCI media types, dropped annotations, incorrect uncompressed/zstd media type selection, or layer order changes. For `manifest-annotation` fixtures, annotations are part of the behavior under test. For compression fixtures, descriptor sizes and digests are sensitive to compressor settings.

## Test Signals
A match means BuildKit emitted the expected manifest structure for `manifest-annotation` in `oci` mode at compatibility version `v10`. A mismatch is a high-signal exporter compatibility regression because consumers use these descriptors to pull or load the image.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/oci/manifest-annotation/v10/manifest.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/oci/manifest-annotation/v20/manifest.json -->
# sources/cloud-native/buildkit/client/testdata/compatibility/oci/manifest-annotation/v20/manifest.json

## Purpose
This JSON fixture is an image manifest baseline for the BuildKit client compatibility suite. It belongs to `oci/manifest-annotation/v20`, representing the OCI media-type fixture for OCI exporter compatibility and the manifest annotation preservation baseline.

## Important Fields and Data Shape
- Schema version: `2`.
- Manifest media type: `application/vnd.oci.image.manifest.v1+json`.
- Config descriptor media type: `application/vnd.oci.image.config.v1+json`, digest `sha256:1772fd0a3b45a62fc...`, size `2295`.
- Layer count: `4`.
- Layer media types: `application/vnd.oci.image.layer.v1.tar+gzip`.
- First layer digest/size: `sha256:430ee4fa77d640d42...` / `2219886`.
- Manifest annotations present: `True`; layer descriptors with annotations: `4`.
- Compatibility version directory: `v20`.

## Control Flow and Integration Role
The file is fixture input for compatibility comparisons. Tests use it to verify that exporter output preserves expected manifest media types, config references, layer descriptors, annotations, compression choices, and compatibility-version behavior.

## State and Persistence Behavior
The manifest models persisted registry or OCI-layout metadata. It is content-addressable through its JSON bytes, and its config/layer descriptors must match adjacent config blobs and generated layer blobs. It has no runtime mutation path.

## Dependencies and Integration Points
It integrates with exporter compatibility tests, the image/OCI exporter, compression settings, OCI/Docker media-type conversion, provenance/annotation options, and adjacent `config.json` fixture files where present.

## Risks and Edge Cases
Risks include digest churn from non-deterministic timestamps or compression, wrong Docker-vs-OCI media types, dropped annotations, incorrect uncompressed/zstd media type selection, or layer order changes. For `manifest-annotation` fixtures, annotations are part of the behavior under test. For compression fixtures, descriptor sizes and digests are sensitive to compressor settings.

## Test Signals
A match means BuildKit emitted the expected manifest structure for `manifest-annotation` in `oci` mode at compatibility version `v20`. A mismatch is a high-signal exporter compatibility regression because consumers use these descriptors to pull or load the image.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/oci/manifest-annotation/v20/manifest.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/oci/uncompressed/v10/manifest.json -->
# sources/cloud-native/buildkit/client/testdata/compatibility/oci/uncompressed/v10/manifest.json

## Purpose
This JSON fixture is an image manifest baseline for the BuildKit client compatibility suite. It belongs to `oci/uncompressed/v10`, representing the OCI media-type fixture for OCI exporter compatibility and the uncompressed layer media type baseline.

## Important Fields and Data Shape
- Schema version: `2`.
- Manifest media type: `application/vnd.oci.image.manifest.v1+json`.
- Config descriptor media type: `application/vnd.oci.image.config.v1+json`, digest `sha256:697cbcf20a7a20500...`, size `2295`.
- Layer count: `4`.
- Layer media types: `application/vnd.oci.image.layer.v1.tar`.
- First layer digest/size: `sha256:fe4922f0a3ca2aa70...` / `4492288`.
- Manifest annotations present: `False`; layer descriptors with annotations: `4`.
- Compatibility version directory: `v10`.

## Control Flow and Integration Role
The file is fixture input for compatibility comparisons. Tests use it to verify that exporter output preserves expected manifest media types, config references, layer descriptors, annotations, compression choices, and compatibility-version behavior.

## State and Persistence Behavior
The manifest models persisted registry or OCI-layout metadata. It is content-addressable through its JSON bytes, and its config/layer descriptors must match adjacent config blobs and generated layer blobs. It has no runtime mutation path.

## Dependencies and Integration Points
It integrates with exporter compatibility tests, the image/OCI exporter, compression settings, OCI/Docker media-type conversion, provenance/annotation options, and adjacent `config.json` fixture files where present.

## Risks and Edge Cases
Risks include digest churn from non-deterministic timestamps or compression, wrong Docker-vs-OCI media types, dropped annotations, incorrect uncompressed/zstd media type selection, or layer order changes. For `manifest-annotation` fixtures, annotations are part of the behavior under test. For compression fixtures, descriptor sizes and digests are sensitive to compressor settings.

## Test Signals
A match means BuildKit emitted the expected manifest structure for `uncompressed` in `oci` mode at compatibility version `v10`. A mismatch is a high-signal exporter compatibility regression because consumers use these descriptors to pull or load the image.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/oci/uncompressed/v10/manifest.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/oci/uncompressed/v20/manifest.json -->
# sources/cloud-native/buildkit/client/testdata/compatibility/oci/uncompressed/v20/manifest.json

## Purpose
This JSON fixture is an image manifest baseline for the BuildKit client compatibility suite. It belongs to `oci/uncompressed/v20`, representing the OCI media-type fixture for OCI exporter compatibility and the uncompressed layer media type baseline.

## Important Fields and Data Shape
- Schema version: `2`.
- Manifest media type: `application/vnd.oci.image.manifest.v1+json`.
- Config descriptor media type: `application/vnd.oci.image.config.v1+json`, digest `sha256:1772fd0a3b45a62fc...`, size `2295`.
- Layer count: `4`.
- Layer media types: `application/vnd.oci.image.layer.v1.tar`.
- First layer digest/size: `sha256:fe4922f0a3ca2aa70...` / `4492288`.
- Manifest annotations present: `False`; layer descriptors with annotations: `4`.
- Compatibility version directory: `v20`.

## Control Flow and Integration Role
The file is fixture input for compatibility comparisons. Tests use it to verify that exporter output preserves expected manifest media types, config references, layer descriptors, annotations, compression choices, and compatibility-version behavior.

## State and Persistence Behavior
The manifest models persisted registry or OCI-layout metadata. It is content-addressable through its JSON bytes, and its config/layer descriptors must match adjacent config blobs and generated layer blobs. It has no runtime mutation path.

## Dependencies and Integration Points
It integrates with exporter compatibility tests, the image/OCI exporter, compression settings, OCI/Docker media-type conversion, provenance/annotation options, and adjacent `config.json` fixture files where present.

## Risks and Edge Cases
Risks include digest churn from non-deterministic timestamps or compression, wrong Docker-vs-OCI media types, dropped annotations, incorrect uncompressed/zstd media type selection, or layer order changes. For `manifest-annotation` fixtures, annotations are part of the behavior under test. For compression fixtures, descriptor sizes and digests are sensitive to compressor settings.

## Test Signals
A match means BuildKit emitted the expected manifest structure for `uncompressed` in `oci` mode at compatibility version `v20`. A mismatch is a high-signal exporter compatibility regression because consumers use these descriptors to pull or load the image.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/testdata/compatibility/oci/uncompressed/v20/manifest.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/validation_test.go -->
# sources/cloud-native/buildkit/client/validation_test.go

## Purpose
This integration-test source verifies that invalid exporter and source-policy metadata is rejected with clear errors. It focuses on OCI image export validation and source-policy validation from both client solve options and gateway frontend solve requests.

## Important APIs, Types, and Functions
- `validationTests` registers the validation cases for the integration suite.
- `testValidateNullConfig` injects `containerimage.config` as JSON `null` and expects export rejection.
- `testValidateInvalidConfig` injects an image config with architecture but missing OS and expects platform validation failure.
- `testValidatePlatformsEmpty` injects null `refs.platforms` metadata and expects empty platforms index rejection.
- `testValidatePlatformsInvalid` covers empty platform IDs and platform entries missing OS/architecture values.
- `testValidateSourcePolicy` covers malformed source policies provided through `SolveOpt.SourcePolicy` and through gateway `SolveRequest.SourcePolicies`.

## Control Flow
Each image validation case opens a client, runs a gateway frontend that solves a scratch state, injects bad exporter metadata into the gateway result, and then exports through the OCI exporter to a discard writer. Source-policy validation builds an alpine image solve and runs each malformed policy once as a client option and once as a frontend-provided source policy.

## State and Persistence Behavior
The tests use no durable outputs; OCI exports write to a discard writer. The important state is metadata attached to gateway results and policy protobufs passed into the solver/exporter validation path.

## Dependencies and Integration Points
The file integrates with gateway frontends, LLB scratch/image states, OCI exporter validation, containerimage exporter metadata keys, source-policy protobuf validation, integration sandbox clients, and worker feature gates for OCI export. It requires Linux for the covered exporter path.

## Risks and Edge Cases
The tests guard against accepting malformed image configs, partial platform values, empty platform indexes, nil policy selectors, unknown policy actions, and convert policies without destinations. These are important because invalid metadata can create broken image outputs or ambiguous source-policy decisions.

## Test Signals
Passing tests indicate invalid exporter metadata and invalid source policies are rejected consistently whether supplied by the client or a frontend. Failures point to validation gaps in the exporter, gateway result handling, or policy protobuf validation.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/validation_test.go -->
