# sources/cloud-native/buildkit/client/client_test.go lines 9245-14911

## Chunk Scope

This chunk covers the latter integration-test helper and scenario region of BuildKit's Go client tests. It starts at the tail of merge-op behavior and continues through passthrough operations, merge cache/lazy layer behavior, exporter validation, local source transfer modes, image export annotations, attestations, SBOM flows, cache export/import behavior, mount cleanup semantics, blob sources, frontend platform warnings, source policies, resolver metadata, HTTP/Git immutability edge cases, git bundle round trips, build history deletion behavior, and metadata parsing helpers.

The code is test-oriented rather than production API implementation. Its purpose is to exercise `client.Client` behavior against an `integration.Sandbox` BuildKit daemon, with many tests using gateway frontends to construct controlled `gateway.Result` objects, local registries, containerd stores, OCI layouts, and temporary Git/HTTP servers.

## Purpose And Behavioral Areas

- Merge and passthrough semantics: verifies LLB merge layering, whiteout/opaque directory behavior, passthrough dependency execution, selected passthrough outputs, and failure propagation from non-output inputs.
- Cache and laziness: validates merge-op cache export/import in inline/min/max modes while preserving lazy remote image layers; checks cache reuse does not rerun nondeterministic steps.
- Exporter contracts: validates invalid output combinations for Docker/OCI/local exporters, multi-platform annotations, attestation image layout, local/tar attestation export, OCI artifact vs image-manifest attestation modes, and multiple cache exporters.
- Local and source inputs: tests parallel local builds, metadata-only local transfer, relative mountpoints, source policies, HTTP source metadata reuse, Git source metadata, mutated Git refs, and blob sources from registry or OCI layout stores.
- Runtime and worker behavior: covers mount stub cleanup/timestamps, large mount graphs, layer limits, valid exit-code handling, custom gRPC dial options, and build history soft-delete listing.
- Supply-chain metadata: exercises provenance, SLSA attestation discovery, SBOM scanner fallback and frontend-provided SBOMs, SBOM supplements, image/blob purl provenance records, and git bundle provenance.

## Important APIs, Types, And Helpers

- `New(ctx, sb.Address())`, `Client.Solve`, `Client.Build`, `Client.Prune`, `Client.DiskUsage`, `Client.Info`, and `Client.ControlClient()` are the primary client entry points under test.
- `SolveOpt` is used extensively with `Exports`, `CacheImports`, `CacheExports`, `FrontendAttrs`, `LocalMounts`, `SourcePolicy`, `OCIStores`, and `Ref`.
- `ExportEntry` covers `ExporterLocal`, `ExporterImage`, `ExporterOCI`, `ExporterDocker`, and `ExporterTar`, including output directory vs writer validation.
- `CacheOptionsEntry` tests inline, local, and registry cache export/import combinations.
- `llb` is the dominant graph construction API: `Image`, `Scratch`, `Local`, `HTTP`, `Git`, `ImageBlob`, `OCILayoutBlob`, `Merge`, `Diff`, `Run`, `AddMount`, `Copy`, `Mkfile`, `Mkdir`, `Tmpfs`, `ValidExitCodes`, `WithLayerLimit`, `MetadataOnlyTransfer`, `GitCheckoutBundle`, `GitBundleURL`, `GitBundleOCIStore`, `KeepGitDir`, `ImageBlobOCIStore`, and passthrough helpers.
- Gateway APIs are used for frontend-like tests: `gateway.Client.Solve`, `ResolveSourceMetadata`, `ResolveImageConfig`, `gateway.NewResult`, `AddRef`, `SetRef`, `AddMeta`, and `AddAttestation`.
- OCI and registry helpers include `contentutil.ProviderFromRef`, `contentutil.IngesterFromRef`, `testutil.ReadImages`, `testutil.ReadTarToMap`, `local.NewStore`, `content.WriteBlob`, containerd image/content/snapshot/lease services, and `namespaces.WithNamespace`.
- Attestation/provenance types include `intoto.Statement`, `result.InTotoAttestation`, `gateway.Attestation`, `gatewaypb.AttestationKind_InToto`, `gatewaypb.AttestationKind_Bundle`, `provenancetypes.ProvenancePredicateSLSA1`, and policy image SLSA predicate constants.
- Source policy types include `sourcepolicypb.Policy`, `Rule`, `Selector`, `Update`, and actions `CONVERT`, `DENY`, and `ALLOW`.
- Local helper functions:
  - `solveStateToLocalDir`, `cacheMountFile`, and `requireLocalFile` simplify passthrough tests.
  - `requireContents` and `requireEqualContents` compare solved outputs and optionally verify image exports.
  - `runShellExecState`, `runShell`, and `chainRunShells` build shell-command LLB states.
  - `requiresLinux`, `ensurePruneAll`, and `checkAllReleasable` gate platform behavior and assert cleanup.
  - `fixedWriteCloser` adapts an `io.WriteCloser` to `filesync.FileOutputFunc`.
  - `newWarningsCapture`, `warningsCapture.wait`, and `warningsListOutput.String` collect status warnings.
  - `ensureFile`, `ensureFileContents`, `makeSSHAgentSock`, `readImageTimestamps`, `runInDir`, `runInDirEnv`, and `parseFSMetadata` support specific assertions.
- Config updater types `secModeSandbox`, `secModeInsecure`, `netModeHost`, `netModeProxyBridge`, `netModeProxyDefault`, `netModeProxyDefaultNoCNI`, `netModeProxyHost`, `netModeDefault`, and `netModeBridgeDNS` produce BuildKit daemon config fragments for security/network test variants.

## Control Flow

- Most tests follow a common pattern: create a sandbox client, construct an LLB definition, call `Marshal`, solve with targeted `SolveOpt`, then inspect filesystem output, registry/OCI artifacts, containerd content, or gateway metadata.
- Registry-oriented tests create a sandbox registry, push an image or artifact, re-resolve it via `contentutil.ProviderFromRef`, and inspect OCI index/manifest/layer structures.
- Gateway tests define an inline `frontend` closure. The closure often solves one or more LLB subgraphs, builds a `gateway.Result`, attaches refs/metadata/attestations, and returns it to `Client.Build`.
- Cache tests intentionally build, delete local image/content state, prune, and rebuild with imports to assert which layers remain remote/lazy and which layers materialize.
- HTTP and Git mutation tests resolve metadata early in a build, mutate the backing server/repo, then perform a solve in the same build to ensure the earlier resolved source remains immutable for that build.
- Git bundle tests run two-phase flows: export a bundle with `GitCheckoutBundle`, stage the bundle in an OCI layout or registry blob store, then import via `GitBundleURL` and validate checkout/provenance behavior.
- `checkAllReleasable` first deletes build history records, waits for disk-usage records to leave `InUse`, prunes all records, then optionally inspects containerd namespaces for remaining images, snapshots, content, and leases.

## State And Persistence Behavior

- Persistent cache mounts are used by passthrough tests to prove non-output dependencies execute even when their root filesystem is not exported.
- Merge cache tests depend on containerd image/content state, registry cache images, and BuildKit cache records. They explicitly delete image records and prune BuildKit state to distinguish remote lazy descriptors from locally materialized blobs.
- `checkAllReleasable` treats BuildKit cache, build history, containerd snapshots, leases, and content as persistent state requiring cleanup assertions. It accounts for asynchronous release by retrying.
- Metadata-only local transfer writes `.fsutil-metadata` containing serialized `fsutiltypes.Stat` records for the full source tree while only selected files are transferred as file contents.
- Source metadata resolution caches source identities within a build. HTTP tests assert that once metadata is resolved, later server content/etag changes do not affect subsequent use in the same build, while a new build observes new metadata.
- Git mutated-source tests assert resolved tag metadata and checkout content remain pinned to the first resolution inside a single build even after the tag is force-updated.
- Build history tests create durable build records, hold a streaming listener to force a soft-delete path, then assert list results exclude the soft-deleted ref.
- Git bundle tests persist bundle bytes as blobs in either a local OCI content store supplied through `SolveOpt.OCIStores` or a sandbox registry.

## Dependencies And Integration Points

- Tests integrate with BuildKit workers through feature gates such as `FeatureDirectPush`, `FeatureMergeDiff`, `FeatureOCIExporter`, `FeatureOCILayout`, `FeatureProvenance`, `FeatureSBOM`, `FeatureMultiCacheExport`, `FeatureInfo`, `FeatureImageExporter`, and `FeatureMultiPlatform`.
- Platform gates are common: many tests require Linux, skip Windows, or use `integration.UnixOrWindows` to select images, shell commands, paths, and expected newline behavior.
- Containerd integration is used for content-store and image-store introspection, namespace-specific cleanup, snapshotter checks, and local fallback image resolution.
- Temporary HTTP servers provide deterministic HTTP source metadata and Git-over-HTTP repositories.
- The sandbox registry is used for image export/import, registry cache, raw blob upload, SBOM scanner images, attestation images, and provenance resolver tests.
- External network dependency appears in `testImageResolveAttestationChainRequiresNetwork`, which resolves a fixed Docker Hub staging image and validates a remote attestation/signature chain.
- Provenance and package-url integration is asserted by checking resolved dependency URIs for Docker/OCI blobs and bundle blobs with `ref_type=blob` or `ref_type=bundle` qualifiers.

## Notable Test Signals

- Passthrough operation tests assert non-output inputs are built but not exported; failing non-output dependencies fail the whole solve.
- Merge-op cache tests assert unchanged layers remain lazy after cache import, changed middle layers materialize, nondeterministic output remains stable under cache reuse, and layers above merges can also reuse lazy cache.
- Exporter validation tests ensure OCI/Docker exporters require output writers and reject output directories, while local exporters require directories and reject output writers.
- Parallel local builds exercise shared client concurrency with independent local mounts.
- Metadata-only local transfer verifies selected files, omitted files, directory disappearance, stat record order, and metadata record count across source mutations.
- Layer-limit tests validate partial image materialization through `WithLayerLimit`, `llb.Diff`, and clean error behavior for a zero limit.
- Annotation tests check index, index descriptor, manifest, manifest descriptor, platform-scoped annotations, exporter attrs, created timestamp annotations, and media type preservation.
- Attestation tests verify multi-platform image indexes include base and `unknown/unknown` attestation manifests, OCI artifact subject fields when enabled, Docker-style reference annotations, in-toto subjects, local/tar exported attestation filenames, default subjects, and bundle attestations.
- SBOM tests validate default scanner fallback, frontend-supplied SBOM precedence, configured scanner args including comma-containing values, single-ref image config preservation, and layer ID supplementation for files that exist in the image.
- Mount stub tests assert tmpfs stub directories are cleaned only when empty and that parent directory timestamps survive unmount/export.
- Blob source tests validate mounted blob ownership, size, digest, and provenance purl records for both registry `ImageBlob` and client-side `OCILayoutBlob`.
- Frontend platform verification tests assert warning presence/absence for mismatched requested/result platforms and skip these warnings for lint subrequests.
- Source policy tests assert conversion to pinned image/HTTP checksums, invalid digest errors, deny behavior, and policy-aware `ResolveImageConfig`.
- Resolver metadata tests assert Git branch/tag resolution, annotated tag commit checksum handling, optional raw Git object return and parsing, HTTP digest/filename/last-modified extraction, image local fallback, provenance attestation discovery, and attestation-chain blob completeness.
- Build history soft-delete test directly targets a previous nil-pointer class by listing with a limit after a soft-deleted watched record.

## Risks And Edge Cases

- Many tests depend on worker feature availability, local registry support, containerd, Linux-specific mount behavior, or external network access; failures can indicate environment gaps rather than code regressions.
- Cache/laziness tests are sensitive to cleanup timing and content-store semantics. `ensurePruneAll` and retry loops exist because release and GC can be asynchronous.
- Tests using `/dev/urandom`, current commit/tag times, or mutable HTTP/Git servers are intentionally nondeterministic in setup but assert cached stability afterward.
- Source metadata tests rely on per-build immutability; accidental resolver cache scope changes could cause same-build mutations to leak through or cross-build changes to be ignored.
- Attestation and SBOM assertions are schema-sensitive. Changes to OCI artifact layout, subject generation, purl formatting, platform descriptors, or in-toto predicate wrapping can break many downstream expectations.
- `testImageResolveAttestationChainRequiresNetwork` is brittle by design because it reaches a fixed remote registry object and validates exact digests.
- Config updater helpers append TOML fragments as strings; syntax or entitlement name changes would affect all tests using those integration configs.
- `warningsCapture.wait` has a timeout path that closes `done`; slow status delivery could hide late warnings or create timing sensitivity.
- `runInDirEnv` shells commands through `sh -c` or PowerShell. Its callers use test-controlled temp dirs and constants, but command construction must stay test-controlled.
- `parseFSMetadata` assumes well-formed length-prefixed metadata bytes and would panic or misread on truncated input; it is appropriate for test fixtures but not defensive production parsing.
